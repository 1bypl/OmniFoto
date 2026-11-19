"""Dostawcy darmowych banków zdjęć: Unsplash, Pexels, Pixabay.

Wymagają darmowego klucza API. Klucz wpisuje się w: Ustawienia -> Klucze API.
Jeśli klucza nie ma, dostawca zwraca pustą listę i silnik pomija go bez błędu.
"""

from __future__ import annotations

from typing import Any

from ..models import Wallpaper
from ..utils import parse_date
from .base import SearchProvider


class UnsplashProvider(SearchProvider):
    id = "unsplash"
    name = "Unsplash"
    kind = "api"
    needs_key = True
    API = "https://api.unsplash.com/search/photos"

    def search(self, query: str, limit: int = 40, **kwargs: Any) -> list[Wallpaper]:
        key = self.api_key()
        if not key:
            return []
        data = self.session.get_json(
            self.API,
            params={"query": query or "wallpaper", "per_page": min(limit, 30), "orientation": "landscape"},
            headers={"Authorization": f"Client-ID {key}"},
        )
        out = []
        for it in (data.get("results") or [])[:limit]:
            try:
                urls = it.get("urls") or {}
                user = it.get("user") or {}
                out.append(self.make(
                    title=(it.get("alt_description") or it.get("description") or "Unsplash photo")[:90],
                    url=urls.get("raw") or urls.get("full", ""),
                    thumb_url=urls.get("small") or urls.get("regular", ""),
                    source_page=it.get("links", {}).get("html", ""),
                    width=int(it.get("width") or 0), height=int(it.get("height") or 0),
                    format="JPG",
                    author=user.get("name", ""),
                    published=parse_date(it.get("created_at")),
                    rating=None,
                    downloads=None,
                    tags=[t.get("title", "") for t in (it.get("tags") or []) if isinstance(t, dict)][:10],
                    description=(it.get("description") or it.get("alt_description") or ""),
                    category="landscapes" if "nature" in str(it.get("tags", "")).lower() else "",
                    colors=[it.get("color", "")] if it.get("color") else [],
                ))
            except Exception:
                continue
        return out


class PexelsProvider(SearchProvider):
    id = "pexels"
    name = "Pexels"
    kind = "api"
    needs_key = True
    API = "https://api.pexels.com/v1/search"

    def search(self, query: str, limit: int = 40, **kwargs: Any) -> list[Wallpaper]:
        key = self.api_key()
        if not key:
            return []
        data = self.session.get_json(
            self.API,
            params={"query": query or "wallpaper", "per_page": min(limit, 80)},
            headers={"Authorization": key},
        )
        out = []
        for it in (data.get("photos") or [])[:limit]:
            try:
                src = it.get("src") or {}
                out.append(self.make(
                    title=(it.get("alt") or "Pexels photo")[:90],
                    url=src.get("original") or src.get("large2x", ""),
                    thumb_url=src.get("medium") or src.get("large", ""),
                    source_page=it.get("url", ""),
                    width=int(it.get("width") or 0), height=int(it.get("height") or 0),
                    format="JPG",
                    author=it.get("photographer", ""),
                    published=parse_date(it.get("created_at")),
                    tags=[],
                    description=it.get("alt", ""),
                    is_animated=False,
                ))
            except Exception:
                continue
        return out


class PixabayProvider(SearchProvider):
    id = "pixabay"
    name = "Pixabay"
    kind = "api"
    needs_key = True
    API = "https://pixabay.com/api/"

    def search(self, query: str, limit: int = 40, **kwargs: Any) -> list[Wallpaper]:
        key = self.api_key()
        if not key:
            return []
        data = self.session.get_json(
            self.API,
            params={
                "key": key, "q": query or "wallpaper",
                "image_type": "photo", "per_page": min(limit, 200),
                "safesearch": "true",
            },
        )
        out = []
        for it in (data.get("hits") or [])[:limit]:
            try:
                out.append(self.make(
                    title=(it.get("tags") or "Pixabay image")[:90],
                    url=it.get("imageURL") or it.get("imageURLLarge", ""),
                    thumb_url=it.get("previewURL") or it.get("webformatURL", ""),
                    source_page=it.get("pageURL", ""),
                    width=int(it.get("imageWidth") or it.get("webformatWidth") or 0),
                    height=int(it.get("imageHeight") or it.get("webformatHeight") or 0),
                    format=self.ext_from_url(it.get("imageURL", "")),
                    author=it.get("user", ""),
                    published=None,
                    rating=it.get("rating"),
                    downloads=it.get("downloads"),
                    tags=[t.strip() for t in str(it.get("tags", "")).split(",") if t.strip()][:12],
                    description=str(it.get("tags", "")),
                ))
            except Exception:
                continue
        return out
