"""Dostawca Wallhaven - oficjalne, darmowe API (bez klucza)."""

from __future__ import annotations

from typing import Any

from ..models import Wallpaper
from ..utils import parse_date
from .base import SearchProvider


class WallhavenProvider(SearchProvider):
    id = "wallhaven"
    name = "Wallhaven"
    kind = "api"
    needs_key = False

    API = "https://wallhaven.cc/api/v1/search"

    def search(self, query: str, limit: int = 40, **kwargs: Any) -> list[Wallpaper]:
        params: dict[str, Any] = {
            "q": query or "",
            "categories": "111",
            "purity": "100",       # tylko „czyste” treści (bezpieczne przeglądanie)
            "sorting": self._sorting(kwargs.get("sort")),
            "order": "desc",
        }
        atleast = kwargs.get("atleast")
        if atleast:
            params["atleast"] = atleast
        out: list[Wallpaper] = []
        # Wallhaven daje 24 wyniki na stronę - czytaj kilka stron, gdy potrzeba
        cancel = kwargs.get("cancel")
        for page in range(1, 4):
            if len(out) >= limit:
                break
            if cancel is not None and cancel.is_set():
                break
            try:
                data = self.session.get_json(self.API, params={**params, "page": page})
            except Exception:
                break
            items = data.get("data", []) if isinstance(data, dict) else []
            if not items:
                break
            out.extend(self._parse(items, limit - len(out)))
            meta = data.get("meta") or {}
            if page >= int(meta.get("last_page", 1)):
                break
        return out[:limit]

    def _parse(self, items: list[dict], limit: int) -> list[Wallpaper]:
        out = []
        for it in items[:limit]:
            try:
                w, h = self._resolution(it.get("resolution", ""))
                thumbs = it.get("thumbs") or {}
                tags = [t.get("name", "") for t in (it.get("tags") or []) if t.get("name")]
                mime = str(it.get("file_type", ""))
                fmt = mime.split("/")[-1].upper() if "/" in mime else self.ext_from_url(it.get("path", ""))
                out.append(self.make(
                    title=it.get("id") or "Wallpaper",
                    url=it.get("path", ""),
                    thumb_url=thumbs.get("large") or thumbs.get("original") or it.get("path", ""),
                    source_page=it.get("short_url") or f"https://wallhaven.cc/w/{it.get('id','')}",
                    width=w, height=h,
                    format=fmt,
                    file_size=int(it.get("file_size") or 0) or None,
                    author=str(it.get("uploader", {}).get("username", "")) if isinstance(it.get("uploader"), dict) else "",
                    published=parse_date(it.get("created_at")),
                    rating=None,
                    downloads=int(it.get("views") or 0) or None,
                    tags=tags[:12],
                    description="Tapeta z Wallhaven" + (f" • {it.get('category','')}" if it.get("category") else ""),
                    colors=it.get("colors") or [],
                    source_kind="api",
                ))
            except Exception:
                continue
        return out

    @staticmethod
    def _resolution(text: str) -> tuple[int, int]:
        parts = str(text).lower().split("x")
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            return int(parts[0]), int(parts[1])
        return 0, 0

    @staticmethod
    def _sorting(value: str | None) -> str:
        mapping = {
            "quality": "top", "popularity": "top", "date": "date",
            "relevance": "relevance", "downloads": "views",
        }
        return mapping.get(value or "", "relevance")
