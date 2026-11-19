"""Wspólny interfejs wszystkich dostawców wyników wyszukiwania."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Any
from urllib.parse import urlparse

from ..models import Wallpaper
from ..privacy import PrivacySession
from ..settings import Settings


class SearchProvider(ABC):
    """Abstrakcyjny dostawca. Każdy zwraca listę obiektów Wallpaper."""

    id: str = "base"
    name: str = "Base"
    kind: str = "api"
    needs_key: bool = False

    def __init__(self, session: PrivacySession, settings: Settings) -> None:
        self.session = session
        self.settings = settings

    @abstractmethod
    def search(self, query: str, limit: int = 40, **kwargs: Any) -> list[Wallpaper]:
        """Zwraca wyniki. Każdy błąd powinien zostać złapany przez SearchManager."""
        raise NotImplementedError

    # --- wspólne pomocniki --------------------------------------------------
    def api_key(self) -> str:
        return str(self.settings.api_keys.get(self.id, "") or "")

    def enabled(self) -> bool:
        for src in self.settings.get("sources", []):
            if src.get("id") == self.id:
                return bool(src.get("enabled", True))
        return True

    @staticmethod
    def domain_of(url: str) -> str:
        try:
            return urlparse(url).netloc.lower()
        except Exception:
            return ""

    @staticmethod
    def ext_from_url(url: str) -> str:
        path = url.split("?")[0].lower()
        m = re.search(r"\.(jpg|jpeg|png|webp|avif|heic|heif|svg)$", path)
        return m.group(1).upper() if m else ""

    def make(self, **kwargs: Any) -> Wallpaper:
        """Fabryka z domyślnymi wartościami dla tego dostawcy."""
        kwargs.setdefault("source_name", self.name)
        kwargs.setdefault("source_kind", self.kind)
        return Wallpaper(**kwargs)
