"""Testy pomocniczych funkcji silnika wyszukiwania."""

from __future__ import annotations

import unittest

from omnifoto.search.demo import make_demo_svg
from omnifoto.search.scrapers import extract_image_urls
from omnifoto.search.wallhaven import WallhavenProvider


class TestScrapers(unittest.TestCase):
    def test_extract_image_urls(self):
        page = '<img src="https://images.example.com/photo_1.jpg"><a href="https://x/y/logo.png">'
        urls = extract_image_urls(page, limit=10)
        self.assertIn("https://images.example.com/photo_1.jpg", urls)
        self.assertFalse(any("logo" in u for u in urls))

    def test_extract_bing_murl(self):
        page = '{"murl":"https://cdn.example.com/big.jpeg"}'
        urls = extract_image_urls(page)
        self.assertIn("https://cdn.example.com/big.jpeg", urls)


class TestDemoData(unittest.TestCase):
    def test_svg_data_uri(self):
        uri = make_demo_svg("Test", ("#000000", "#ffffff", "⭐"), 640, 360)
        self.assertTrue(uri.startswith("data:image/svg+xml;base64,"))
        self.assertGreater(len(uri), 100)


class TestWallhavenHelpers(unittest.TestCase):
    def test_resolution_parsing(self):
        self.assertEqual(WallhavenProvider._resolution("3840x2160"), (3840, 2160))
        self.assertEqual(WallhavenProvider._resolution(""), (0, 0))

    def test_sorting_mapping(self):
        self.assertEqual(WallhavenProvider._sorting("date"), "date")
        self.assertEqual(WallhavenProvider._sorting("quality"), "top")
        self.assertEqual(WallhavenProvider._sorting(None), "relevance")


if __name__ == "__main__":
    unittest.main()
