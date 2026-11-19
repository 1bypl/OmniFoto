"""Dostawcy „best-effort” - strony bez wygodnego oficjalnego API.

Analizują publicznie dostępny HTML wyszukiwarki obrazów / serwisu. Gdy serwis
blokuje żądanie albo zmieni strukturę strony, dostawca zwraca pustą listę, a
SearchManager po prostu przechodzi do pozostałych źródeł. Nie obchodzimy żadnych
zabezpieczeń ani blokad - szanujemy dostępność serwisu.
"""

from __future__ import annotations

import html as html_mod
import json
import re
from typing import Any
from urllib.parse import quote_plus

from ..models import Wallpaper
from ..utils import keyword_category, parse_resolution
from .base import SearchProvider

IMG_RE = re.compile(
    r"https?://[^\s\"'<>\\]+?\.(?:jpg|jpeg|png|webp|avif)(?:\?[^\s\"'<>\\]*)?",
    re.IGNORECASE,
)
BAD_WORDS = ("logo", "icon", "sprite", "avatar", "button", "banner", "placeholder", "pixel", " blank", "transparent")


def extract_image_urls(page: str, limit: int = 40) -> list[str]:
    """Wyciąga prawdopodobne adresy obrazów z kodu HTML / wbudowanego JSON."""
    text = page.replace("\\/", "/").replace("\\u003d", "=").replace("\\u0026", "&")
    text = html_mod.unescape(text)
    urls: list[str] = []

    # Bing: pole "murl" w JSON-ie z wynikami
    for m in re.finditer(r'"murl"\s*:\s*"(https?://[^"]+)"', text):
        urls.append(m.group(1))

    # Google / ogólne: ciągi z rozszerzeniem obrazu
    for m in IMG_RE.finditer(text):
        urls.append(m.group(0))

    out: list[str] = []
    seen: set[str] = set()
    for u in urls:
        u = u.strip().rstrip("),;]}")
        low = u.lower()
        if any(b in low for b in BAD_WORDS):
            continue
        if u in seen:
            continue
        seen.add(u)
        out.append(u)
        if len(out) >= limit:
            break
    return out


class HtmlSearchProvider(SearchProvider):
    """Bazowa klasa dla prostych scraperów."""

    kind = "scrape"
    search_url = ""
    query_param = "q"
    extra_params: dict[str, str] = {}

    def _fetch_page(self, query: str) -> str:
        params = {self.query_param: query, **self.extra_params}
        return self.session.get_text(self.search_url, params=params)

    def _to_wallpapers(self, urls: list[str], query: str, limit: int) -> list[Wallpaper]:
        out = []
        for u in urls[:limit]:
            try:
                out.append(self.make(
                    title=self._title_from_url(u, query),
                    url=u,
                    thumb_url=u,
                    source_page=self.search_url,
                    width=0, height=0,
                    format=self.ext_from_url(u),
                    tags=[query] if query else [],
                    description=f"Wynik best-effort ze źródła {self.name}",
                    category=keyword_category(query),
                    source_kind="scrape",
                ))
            except Exception:
                continue
        return out

    @staticmethod
    def _title_from_url(url: str, query: str) -> str:
        name = url.split("?")[0].rsplit("/", 1)[-1]
        name = re.sub(r"[-_]+", " ", name)
        name = re.sub(r"\.\w+$", "", name).strip()
        name = name[:70] or query or "Wallpaper"
        return name[:1].upper() + name[1:]

    def search(self, query: str, limit: int = 40, **kwargs: Any) -> list[Wallpaper]:
        try:
            page = self._fetch_page(query or "wallpaper")
            return self._to_wallpapers(extract_image_urls(page, limit), query, limit)
        except Exception:
            return []


class GoogleImagesProvider(HtmlSearchProvider):
    id = "google_images"
    name = "Grafika Google"
    search_url = "https://www.google.com/search"
    query_param = "q"
    extra_params = {"tbm": "isch", "safe": "on"}

    def search(self, query: str, limit: int = 40, **kwargs: Any) -> list[Wallpaper]:
        page = ""
        try:
            # images.google.com/search działa podobnie, ale bywa blokowany
            page = self.session.get_text(
                "https://www.google.com/search",
                params={"q": f"{query} wallpaper", "tbm": "isch", "safe": "on"},
            )
        except Exception:
            return []
        urls = extract_image_urls(page, limit)
        # Google czasem zwraca adresy jako "https...jpg" w tablicach - wyciągnij je
        if not urls:
            for m in re.finditer(r'"(https?://[^"\\]+?\.(?:jpg|jpeg|png|webp))"', page.replace("\\/", "/"), re.I):
                urls.append(m.group(1))
        return self._to_wallpapers(list(dict.fromkeys(urls))[:limit], query, limit)


class BingImagesProvider(HtmlSearchProvider):
    id = "bing_images"
    name = "Obrazy Bing"
    search_url = "https://www.bing.com/images/search"
    query_param = "q"
    extra_params = {"safeSearch": "Strict", "form": "HDRSC2"}

    def search(self, query: str, limit: int = 40, **kwargs: Any) -> list[Wallpaper]:
        try:
            page = self._fetch_page(f"{query} wallpaper")
        except Exception:
            return []
        urls: list[str] = []
        for m in re.finditer(r'murl&quot;:&quot;(https?://[^&"]+)&quot;', page):
            urls.append(html_mod.unescape(m.group(1)))
        for m in re.finditer(r'"murl":"(https?://[^"]+)"', page):
            urls.append(m.group(1))
        urls.extend(extract_image_urls(page, limit))
        uniq = list(dict.fromkeys(u for u in urls if not any(b in u.lower() for b in BAD_WORDS)))
        return self._to_wallpapers(uniq[:limit], query, limit)


class WallpaperFlareProvider(HtmlSearchProvider):
    id = "wallpaperflare"
    name = "WallpaperFlare"
    search_url = "https://www.wallpaperflare.com/search"
    query_param = "wallpaper"


class WallpaperHubProvider(HtmlSearchProvider):
    id = "wallpaperhub"
    name = "WallpaperHub"
    search_url = "https://wallpaperhub.app/search"
    query_param = "q"


class BackdropsProvider(HtmlSearchProvider):
    id = "backdrops"
    name = "Backdrops"
    search_url = "https://backdrops.io/search"
    query_param = "q"


class BasicAppleGuyProvider(HtmlSearchProvider):
    id = "basicappleguy"
    name = "Basic Apple Guy"
    search_url = "https://basicappleguy.com/search"
    query_param = "q"


class DeviantArtProvider(HtmlSearchProvider):
    id = "deviantart"
    name = "DeviantArt"
    search_url = "https://www.deviantart.com/search"
    query_param = "q"
    extra_params = {"art_type": "wallpaper"}

    def _to_wallpapers(self, urls: list[str], query: str, limit: int) -> list[Wallpaper]:
        # DeviantArt hostuje miniatury na images-wixmp...; odfiltruj resztę
        urls = [u for u in urls if "wixmp" in u or "deviantart" in u]
        return super()._to_wallpapers(urls, query, limit)
