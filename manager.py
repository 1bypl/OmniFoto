"""Orkiestrator wyszukiwania: łączy źródła, toleruje błędy, liczy postęp."""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from threading import Event
from typing import Callable

from ..models import SortKey, TimeRange, Wallpaper
from ..privacy import PrivacySession
from ..settings import Settings
from ..utils import (
    filter_by_category, filter_by_time, is_wallpaper_quality,
    matches_wallpaper, prepare_query, relevance_score, sort_wallpapers,
    unique_by,
)
from .base import SearchProvider
from .demo import DemoProvider
from .open_sources import FlickrProvider, NasaProvider, OpenverseProvider, WikimediaProvider
from .reddit import RedditProvider
from .scrapers import (
    BackdropsProvider, BasicAppleGuyProvider, BingImagesProvider,
    DeviantArtProvider, GoogleImagesProvider, WallpaperFlareProvider,
    WallpaperHubProvider,
)
from .stock_providers import PixabayProvider, PexelsProvider, UnsplashProvider
from .wallhaven import WallhavenProvider

PROVIDERS: dict[str, type[SearchProvider]] = {
    "wallhaven": WallhavenProvider,
    "unsplash": UnsplashProvider,
    "pexels": PexelsProvider,
    "pixabay": PixabayProvider,
    "reddit": RedditProvider,
    "wikimedia": WikimediaProvider,
    "nasa": NasaProvider,
    "flickr": FlickrProvider,
    "openverse": OpenverseProvider,
    "wallpaperflare": WallpaperFlareProvider,
    "wallpaperhub": WallpaperHubProvider,
    "backdrops": BackdropsProvider,
    "basicappleguy": BasicAppleGuyProvider,
    "deviantart": DeviantArtProvider,
    "google_images": GoogleImagesProvider,
    "bing_images": BingImagesProvider,
    "demo": DemoProvider,
}

ProgressCallback = Callable[[str, int, bool], None]
# callback(nazwa_źródła, liczba_znalezionych_w_tym_źródle, czy_sukces)


@dataclass
class SearchResult:
    items: list[Wallpaper] = field(default_factory=list)
    sources_total: int = 0
    sources_ok: int = 0
    elapsed: float = 0.0
    errors: list[str] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.items)


class SearchManager:
    """Uruchamia wiele dostawców równolegle i scala ich wyniki."""

    def __init__(self, session: PrivacySession, settings: Settings) -> None:
        self.session = session
        self.settings = settings

    def _provider_for(self, source: dict) -> SearchProvider | None:
        cls = PROVIDERS.get(source.get("id", ""))
        if cls is None:
            return None
        if cls.needs_key and not self.settings.api_keys.get(cls.id):
            return None
        return cls(self.session, self.settings)

    def search(
        self,
        query: str,
        limit: int | None = None,
        sort: SortKey = SortKey.RELEVANCE,
        category: str = "all",
        time_range: TimeRange = TimeRange.ALL,
        progress: ProgressCallback | None = None,
        cancel: Event | None = None,
    ) -> SearchResult:
        started = time.monotonic()
        # Qt/QVariant potrafi zwrócić zwykły string zamiast Enum - uodpornijmy się
        if not isinstance(sort, SortKey):
            sort = SortKey(sort)
        if not isinstance(time_range, TimeRange):
            time_range = TimeRange(time_range)
        limit = limit or int(self.settings.get("page_size", 40))
        prepared = prepare_query(query, category)
        query_for_apis = prepared["search"]
        enabled_sources = [s for s in self.settings.get("sources", []) if s.get("enabled", True)]
        tasks: list[tuple[dict, SearchProvider]] = []
        for src in enabled_sources:
            provider = self._provider_for(src)
            if provider is not None:
                tasks.append((src, provider))

        result = SearchResult(sources_total=len(enabled_sources))
        if not tasks:
            result.elapsed = time.monotonic() - started
            return result

        collected: list[Wallpaper] = []
        # Każde źródło dostaje własny, duży limit - inaczej program pokazuje
        # kilka wyników zamiast setek (wzorzec: Variety / Hydra Paper).
        per_source = max(60, limit * 2)

        if cancel is not None and cancel.is_set():
            result.elapsed = time.monotonic() - started
            return result

        with ThreadPoolExecutor(max_workers=8, thread_name_prefix="omni-search") as pool:
            futures = {
                pool.submit(
                    provider.search,
                    query_for_apis,
                    per_source,
                    category=category,
                    sort=sort.value,
                    cancel=cancel,
                ): (src, provider)
                for src, provider in tasks
            }
            for future in as_completed(futures):
                if cancel is not None and cancel.is_set():
                    future.cancel()
                    continue
                src, provider = futures[future]
                try:
                    items = future.result() or []
                    collected.extend(items)
                    result.sources_ok += 1
                    if progress:
                        progress(provider.name, len(items), True)
                except Exception as exc:  # niedostępne źródło -> pomijamy
                    result.errors.append(f"{src.get('name', provider.name)}: {exc}")
                    if progress:
                        progress(provider.name, 0, False)

        items = unique_by(collected)
        # Odrzucamy małe infografiki i reklamy - zostają prawdziwe tapety.
        items = [w for w in items if is_wallpaper_quality(w)]
        # znaczki, plakaty, ulotki i logo to nie są tapety
        bad_titles = ("stamp", "poster", "logo", "infographic", "advert", "flyer",
                      "banner", "etiquette", "label", "znaczek", "plakat", "ulotka")
        items = [
            w for w in items
            if not any(word in w.title.lower() for word in bad_titles)
        ]
        # Wallhaven nie zwraca tagów w API, więc jemu ufamy; pozostałe źródła
        # sprawdzamy pod kątem fraz wpisanych przez użytkownika.
        items = [
            w for w in items
            if w.source_name == "Wallhaven" or matches_wallpaper(w, prepared)
        ]
        # Kategoria to miękka wskazówka (podbicie w relevance_score), a nie
        # twardy filtr - twardy filtr wcześniej wycinał trafne wyniki.
        items = filter_by_time(items, time_range)
        # najpierw trafność wobec słów wpisanych przez użytkownika
        if prepared["user_words"]:
            items.sort(key=lambda w: relevance_score(w, prepared), reverse=True)
        if sort == SortKey.RELEVANCE:
            # przeplataj źródła, żeby jedno (np. NASA) nie zdominowało
            # pierwszego ekranu wyników
            by_source: dict[str, list[Wallpaper]] = {}
            for w in items:
                by_source.setdefault(w.source_name, []).append(w)
            mixed: list[Wallpaper] = []
            while any(by_source.values()):
                for name in list(by_source):
                    if by_source[name]:
                        mixed.append(by_source[name].pop(0))
            items = mixed
        items = sort_wallpapers(items, sort, reverse=True)
        result.items = items[:limit]
        result.elapsed = time.monotonic() - started
        return result

    def best(
        self,
        category: str = "all",
        time_range: TimeRange = TimeRange.WEEK,
        limit: int | None = None,
        progress: ProgressCallback | None = None,
    ) -> SearchResult:
        """Zwraca najpopularniejsze wyniki (dzisiejsze / tygodniowe / itd.)."""
        return self.search(
            query="wallpaper",
            limit=limit,
            sort=SortKey.POPULARITY,
            category=category,
            time_range=time_range,
            progress=progress,
        )
