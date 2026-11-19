"""Testy logiki bez interfejsu graficznego. Uruchom: python3 -m unittest discover -s tests -v"""

from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from omnifoto.i18n import Translator
from omnifoto.models import DeviceType, Quality, SortKey, Wallpaper
from omnifoto.privacy import PrivacySession
from omnifoto.search import SearchManager
from omnifoto.settings import Settings
from omnifoto.utils import (
    matches_wallpaper, parse_resolution, parse_size, prepare_query,
    relevance_score, safe_filename, sort_wallpapers,
)


def make_wallpaper(**kwargs):
    base = dict(title="Test", url="https://example.com/a.jpg", width=1920, height=1080)
    base.update(kwargs)
    return Wallpaper(**base)


class TestModels(unittest.TestCase):
    def test_quality_thresholds(self):
        self.assertEqual(make_wallpaper(width=3840, height=2160).quality, Quality.HIGH)
        self.assertEqual(make_wallpaper(width=1920, height=1080).quality, Quality.MEDIUM)
        self.assertEqual(make_wallpaper(width=800, height=600).quality, Quality.LOW)

    def test_resolution_and_megapixels(self):
        w = make_wallpaper(width=3840, height=2160)
        self.assertEqual(w.resolution, "3840×2160")
        self.assertEqual(w.aspect_ratio, "16:9")
        self.assertEqual(w.megapixels, 8.29)

    def test_device_inference(self):
        self.assertIn(DeviceType.MOBILE, make_wallpaper(width=1080, height=2400).devices)
        self.assertIn(DeviceType.DESKTOP, make_wallpaper(width=3440, height=1440).devices)
        self.assertEqual(len(make_wallpaper(width=1080, height=2400).devices), 1)

    def test_serialization_roundtrip(self):
        w = make_wallpaper(published=datetime(2026, 1, 2, tzinfo=timezone.utc))
        restored = Wallpaper.from_dict(w.to_dict())
        self.assertEqual(restored.id, w.id)
        self.assertEqual(restored.published, w.published)
        self.assertEqual(restored.devices, w.devices)


class TestSettings(unittest.TestCase):
    def test_defaults_and_persistence(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            s = Settings(path)
            self.assertEqual(s.get("language"), "pl")
            s.set("language", "en")
            s.save()
            s2 = Settings(path)
            self.assertEqual(s2.get("language"), "en")

    def test_favorites_full_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = Settings(Path(tmp) / "s.json")
            s.set("privacy_mode", False)
            w = make_wallpaper()
            s.add_favorite(w)
            self.assertTrue(s.is_favorite(w.id))
            s.remove_favorite(w.id)
            self.assertFalse(s.is_favorite(w.id))

    def test_private_history_not_saved(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "s.json"
            s = Settings(path)
            s.set("privacy_mode", True)
            s.add_history(make_wallpaper())
            self.assertEqual(len(s.get("history")), 1)
            self.assertFalse(path.exists())


class TestUtils(unittest.TestCase):
    def test_parsers(self):
        self.assertEqual(parse_resolution("1920x1080"), (1920, 1080))
        self.assertEqual(parse_size("2.5 MB"), int(2.5 * 1024 * 1024))
        self.assertTrue(safe_filename("Zdjęcie: test?!").startswith("Zdjęcie_ test"))

    def test_sorting(self):
        items = [
            make_wallpaper(title="mała", width=800, height=600),
            make_wallpaper(title="duża", width=3840, height=2160),
        ]
        out = sort_wallpapers(items, SortKey.QUALITY)
        self.assertEqual(out[0].title, "duża")


class TestSearchPrecision(unittest.TestCase):
    def test_polish_query_translation(self):
        prepared = prepare_query("las", "nature")
        self.assertIn("las", prepared["user_words"])
        self.assertIn("forest", prepared["user_words"])
        self.assertIn("nature", prepared["cat_words"])

    def test_unrelated_result_rejected(self):
        prepared = prepare_query("las", "all")
        related = make_wallpaper(title="Leśna ścieżka", tags=["forest", "trees"])
        unrelated = make_wallpaper(title="Księżyc", tags=["space", "moon"])
        self.assertTrue(matches_wallpaper(related, prepared))
        self.assertFalse(matches_wallpaper(unrelated, prepared))
        self.assertGreater(relevance_score(related, prepared), relevance_score(unrelated, prepared))


class TestCollections(unittest.TestCase):
    def test_create_import_remove(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = Settings(Path(tmp) / "s.json")
            s.set("privacy_mode", False)
            w = make_wallpaper()
            col = s.add_collection("Moje tapety", [w.to_dict()])
            self.assertEqual(len(s.collections()), 1)
            s.add_to_collection(col["id"], w)
            self.assertEqual(len(s.collections()[0]["items"]), 1)
            s.remove_collection(col["id"])
            self.assertEqual(s.collections(), [])


class TestI18n(unittest.TestCase):
    def test_all_languages_have_key(self):
        tr = Translator("de")
        self.assertIn("Suchen", tr.t("search"))
        for lang in ("pl", "en", "fr", "de", "ru", "es", "it"):
            t = Translator(lang)
            self.assertTrue(t.t("app_name"))
            self.assertIn("{n}", t.t("results_found"))


class TestSearchManager(unittest.TestCase):
    def test_demo_offline_search(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = Settings(Path(tmp) / "s.json")
            s.set("privacy_mode", True)
            s.set("sources", [src for src in s.get("sources") if src["id"] == "demo"])
            manager = SearchManager(PrivacySession(s), s)
            result = manager.search("niebieski", limit=5)
            self.assertGreater(result.count, 0)
            self.assertLessEqual(result.count, 5)
            self.assertTrue(all(w.source_kind == "demo" for w in result.items))

    def test_failing_source_is_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = Settings(Path(tmp) / "s.json")
            s.set("privacy_mode", True)
            s.set("sources", [
                {"id": "nieistniejace", "name": "Martwa baza", "kind": "api",
                 "key": False, "enabled": True, "url": "", "note": ""},
                {"id": "demo", "name": "Demo", "kind": "demo", "key": False,
                 "enabled": True, "url": "", "note": ""},
            ])
            manager = SearchManager(PrivacySession(s), s)
            result = manager.search("kot", limit=3)
            self.assertTrue(result.items)
            self.assertGreaterEqual(result.sources_ok, 1)


if __name__ == "__main__":
    unittest.main()
