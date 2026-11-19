"""Zarządzanie ustawieniami w pliku JSON (bez zależności od Qt)."""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path
from typing import Any

from .constants import DEFAULT_SETTINGS


def config_dir() -> Path:
    """Katalog konfiguracji zgodny ze specyfikacją XDG (Linux)."""
    base = os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
    return Path(base) / "OmniFoto"


def data_dir() -> Path:
    base = os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))
    return Path(base) / "OmniFoto"


def cache_dir() -> Path:
    base = os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))
    return Path(base) / "OmniFoto"


class Settings:
    """Prosty, bezpieczny magazyn ustawień z automatycznym scalaniem domyślnych."""

    FILE_NAME = "settings.json"

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or (config_dir() / self.FILE_NAME)
        self._data = copy.deepcopy(DEFAULT_SETTINGS)
        self.load()

    # --- odczyt / zapis -----------------------------------------------------
    def load(self) -> None:
        try:
            if self.path.exists():
                raw = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(raw, dict):
                    self._merge(self._data, raw)
        except (OSError, json.JSONDecodeError):
            # uszkodzony plik -> zostają domyślne wartości
            pass
        self._migrate()

    def _migrate(self) -> None:
        """Dodaje nowe źródła/klucze do starszych plików ustawień (bez utraty wyboru)."""
        sources = self._data.get("sources", [])
        ids = {s.get("id") for s in sources if isinstance(s, dict)}
        for default in DEFAULT_SETTINGS.get("sources", []):
            if default["id"] not in ids:
                sources.append(copy.deepcopy(default))
        self._data["sources"] = sources
        if "collections" not in self._data:
            self._data["collections"] = []
        if int(self._data.get("page_size", 0)) < 80:
            self._data["page_size"] = 80
        # jednorazowo wyłącz scraperzy i Flickr - dawały reklamy i losowe zdjęcia
        if not self._data.get("_v11_scrapers_off", False):
            junk = {"google_images", "bing_images", "wallpaperflare", "flickr"}
            for src in sources:
                if src.get("id") in junk:
                    src["enabled"] = False
            self._data["_v11_scrapers_off"] = True
        if not self._data.get("_v12_flickr_off", False):
            for src in sources:
                if src.get("id") == "flickr":
                    src["enabled"] = False
            self._data["_v12_flickr_off"] = True

    @staticmethod
    def _merge(base: dict[str, Any], incoming: dict[str, Any]) -> None:
        for key, value in incoming.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                Settings._merge(base[key], value)
            else:
                base[key] = value

    def save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".json.tmp")
            tmp.write_text(
                json.dumps(self._data, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            os.replace(tmp, self.path)
        except OSError:
            pass

    # --- dostęp -------------------------------------------------------------
    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def update(self, **kwargs: Any) -> None:
        self._data.update(kwargs)

    @property
    def all(self) -> dict[str, Any]:
        return self._data

    # --- wygoda -------------------------------------------------------------
    @property
    def privacy_mode(self) -> bool:
        return bool(self._data.get("privacy_mode", True))

    @property
    def api_keys(self) -> dict[str, str]:
        return dict(self._data.get("api_keys", {}))

    @staticmethod
    def _fav_id(entry: Any) -> str:
        return entry.get("id", "") if isinstance(entry, dict) else str(entry)

    def add_favorite(self, wallpaper: Any) -> None:
        """Dodaje ulubione. Przyjmuje Wallpaper, słownik albo sam identyfikator."""
        if hasattr(wallpaper, "to_dict"):
            entry = wallpaper.to_dict()
        elif isinstance(wallpaper, dict):
            entry = dict(wallpaper)
        else:
            entry = str(wallpaper)
        favs = [f for f in self._data.get("favorites", []) if self._fav_id(f) != self._fav_id(entry)]
        favs.append(entry)
        self._data["favorites"] = favs
        if not self.privacy_mode:
            self.save()

    def remove_favorite(self, wallpaper_id: str) -> None:
        favs = [f for f in self._data.get("favorites", []) if self._fav_id(f) != wallpaper_id]
        self._data["favorites"] = favs
        if not self.privacy_mode:
            self.save()

    def is_favorite(self, wallpaper_id: str) -> bool:
        return any(self._fav_id(f) == wallpaper_id for f in self._data.get("favorites", []))

    def add_history(self, wallpaper: Any) -> None:
        """Dodaje do ostatnio przeglądanych (pełne dane; w trybie prywatnym
        historia żyje tylko w pamięci)."""
        if hasattr(wallpaper, "to_dict"):
            entry = wallpaper.to_dict()
        elif isinstance(wallpaper, dict):
            entry = dict(wallpaper)
        else:
            entry = str(wallpaper)
        eid = self._fav_id(entry)
        limit = int(self._data.get("recent_limit", 30))
        hist = [h for h in self._data.get("history", []) if self._fav_id(h) != eid]
        hist.insert(0, entry)
        self._data["history"] = hist[:limit]
        # w trybie prywatnym nie zapisujemy historii na dysku
        if self.privacy_mode:
            return
        self.save()

    # --- własne kolekcje tapet ---------------------------------------------
    def collections(self) -> list[dict[str, Any]]:
        return list(self._data.get("collections", []))

    @staticmethod
    def _collection_id(name: str) -> str:
        import hashlib
        return hashlib.sha1(name.encode("utf-8", "ignore")).hexdigest()[:10]

    def add_collection(self, name: str, items: list | None = None) -> dict[str, Any]:
        name = (name or "").strip() or "Moja kolekcja"
        cid = self._collection_id(name)
        collections = self.collections()
        for col in collections:
            if col.get("id") == cid:
                col["items"] = list(col.get("items", [])) + list(items or [])
                self._data["collections"] = collections
                if not self.privacy_mode:
                    self.save()
                return col
        entry = {"id": cid, "name": name, "items": list(items or [])}
        collections.append(entry)
        self._data["collections"] = collections
        if not self.privacy_mode:
            self.save()
        return entry

    def remove_collection(self, cid: str) -> None:
        self._data["collections"] = [c for c in self.collections() if c.get("id") != cid]
        if not self.privacy_mode:
            self.save()

    def add_to_collection(self, cid: str, wallpaper: Any) -> None:
        if hasattr(wallpaper, "to_dict"):
            entry = wallpaper.to_dict()
        elif isinstance(wallpaper, dict):
            entry = dict(wallpaper)
        else:
            return
        collections = self.collections()
        for col in collections:
            if col.get("id") == cid:
                items = col.get("items", [])
                if not any(i.get("id") == entry.get("id") for i in items if isinstance(i, dict)):
                    items.append(entry)
                col["items"] = items
                break
        self._data["collections"] = collections
        if not self.privacy_mode:
            self.save()

    def reset(self) -> None:
        self._data = copy.deepcopy(DEFAULT_SETTINGS)
        self.save()
