"""Dostawca Reddit - publiczne endpointy .json (bez klucza API)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..models import Wallpaper
from .base import SearchProvider

SUBREDDITS = ["wallpapers", "WidescreenWallpaper", "MobileWallpaper", "Amoledbackgrounds"]


class RedditProvider(SearchProvider):
    id = "reddit"
    name = "Reddit"
    kind = "api"
    needs_key = False

    def search(self, query: str, limit: int = 40, **kwargs: Any) -> list[Wallpaper]:
        out: list[Wallpaper] = []
        per_sub = max(5, limit // len(SUBREDDITS))
        cancel = kwargs.get("cancel")
        for sub in SUBREDDITS:
            if cancel is not None and cancel.is_set():
                break
            try:
                url = f"https://www.reddit.com/r/{sub}/search.json"
                data = self.session.get_json(
                    url,
                    params={
                        "q": query or "wallpaper",
                        "restrict_sr": "1",
                        "sort": "relevance",
                        "t": "year",
                        "limit": per_sub,
                        "raw_json": "1",
                    },
                )
                children = (data.get("data") or {}).get("children", [])
                for child in children[:per_sub]:
                    d = child.get("data") or {}
                    try:
                        image_url = d.get("url_overridden_by_dest") or d.get("url", "")
                        if not self._looks_like_image(image_url):
                            continue
                        preview = d.get("preview") or {}
                        images = preview.get("images") or []
                        source = (images[0].get("source") or {}) if images else {}
                        thumb = images[0].get("thumbnail") or {} if images else {}
                        w = int(source.get("width") or 0)
                        h = int(source.get("height") or 0)
                        created = d.get("created_utc")
                        published = datetime.fromtimestamp(created, tz=timezone.utc) if created else None
                        title = str(d.get("title", ""))[:90]
                        out.append(self.make(
                            title=title,
                            url=image_url,
                            thumb_url=(thumb.get("url") if isinstance(thumb, dict) else "") or source.get("url", "") or image_url,
                            source_page=f"https://www.reddit.com{d.get('permalink','')}",
                            width=w, height=h,
                            format=self.ext_from_url(image_url),
                            author=d.get("author", ""),
                            published=published,
                            rating=max(0.0, min(10.0, float(d.get("score") or 0) / 100.0)) if d.get("score") else None,
                            downloads=None,
                            tags=[f"r/{sub}"],
                            description=title,
                            category=self._category(sub),
                        ))
                    except Exception:
                        continue
            except Exception:
                # niedostępny subreddit -> po cichu pomijamy (zgodnie z wymaganiem)
                continue
            if len(out) >= limit:
                break
        return out[:limit]

    @staticmethod
    def _looks_like_image(url: str) -> bool:
        u = url.lower()
        return any(u.rstrip("/").endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif")) or "i.redd.it" in u or "i.imgur.com" in u

    @staticmethod
    def _category(sub: str) -> str:
        mapping = {
            "wallpapers": "", "widescreenwallpaper": "landscapes",
            "mobilewallpaper": "technology", "amoledbackgrounds": "abstract",
        }
        return mapping.get(sub.lower(), "")
