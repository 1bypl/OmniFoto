"""Darmowe, otwarte bazy grafik bez klucza API (wzorzec: Variety / Hydra Paper).

Wszystkie poniższe źródła są publiczne i nie wymagają rejestracji:
  * Wikimedia Commons - miliony zdjęć na licencjach CC,
  * NASA Images - potężne archiwum kosmiczne i ziemskie,
  * Flickr - publiczny feed tagów,
  * Openverse - agregator wolnych licencji (bywa przeciążony).
"""

from __future__ import annotations

from typing import Any

from ..models import Wallpaper
from ..utils import parse_date, strip_html
from .base import SearchProvider

MIME_OK = {"image/jpeg", "image/jpg", "image/png", "image/webp", "image/avif"}


class WikimediaProvider(SearchProvider):
    id = "wikimedia"
    name = "Wikimedia Commons"
    kind = "api"
    needs_key = False
    API = "https://commons.wikimedia.org/w/api.php"

    def search(self, query: str, limit: int = 40, **kwargs: Any) -> list[Wallpaper]:
        """Kilka prostych zapytań intitle zamiast jednego zbyt wąskiego.

        Dzięki temu „Fedora 45 KDE" (które jako całość daje 0 trafień)
        znajduje tapety Fedory i KDE, a pełna fraza decyduje o kolejności.
        """
        out: list[Wallpaper] = []
        seen: set[str] = set()
        cancel = kwargs.get("cancel")
        words = [w for w in query.split() if len(w) > 1][:3]

        queries: list[str] = []
        if len(words) >= 2:
            queries.append('intitle:"' + " ".join(words[:2]) + '" filetype:bitmap')
        for word in words:
            candidate = f"intitle:{word} filetype:bitmap"
            if candidate not in queries:
                queries.append(candidate)
        if not queries:
            queries.append(query + " filetype:bitmap")

        for title_query in queries[:4]:
            if len(out) >= limit:
                break
            if cancel is not None and cancel.is_set():
                break
            params: dict[str, Any] = {
                "action": "query", "generator": "search",
                "gsrsearch": title_query, "gsrnamespace": 6,
                "gsrlimit": min(50, limit), "prop": "imageinfo",
                "iiprop": "url|size|mime|extmetadata", "iiurlwidth": 640,
                "format": "json",
            }
            try:
                data = self.session.get_json(self.API, params=params)
            except Exception:
                continue
            pages = (data.get("query") or {}).get("pages") or {}
            for page in sorted(pages.values(), key=lambda p: p.get("index", 99)):
                try:
                    info = (page.get("imageinfo") or [{}])[0]
                    mime = str(info.get("mime", "")).lower()
                    image_url = info.get("url", "")
                    if mime not in MIME_OK or not image_url or image_url in seen:
                        continue
                    seen.add(image_url)
                    meta = info.get("extmetadata") or {}
                    author = strip_html(str((meta.get("Artist") or {}).get("value", "")))[:80]
                    desc = strip_html(str((meta.get("ImageDescription") or {}).get("value", "")))[:300]
                    title = str(page.get("title", "")).replace("File:", "")[:90]
                    out.append(self.make(
                        title=title,
                        url=info.get("url", ""),
                        thumb_url=info.get("thumburl") or info.get("url", ""),
                        source_page=info.get("descriptionurl", ""),
                        width=int(info.get("width") or 0),
                        height=int(info.get("height") or 0),
                        format=self.ext_from_url(info.get("url", "")),
                        file_size=int(info.get("size") or 0) or None,
                        author=author,
                        published=parse_date((meta.get("DateTimeOriginal") or {}).get("value")),
                        tags=[t.strip() for t in title.replace(".jpg", "").replace(".png", "").split() if len(t.strip()) > 3][:10],
                        description=desc,
                        colors=[],
                    ))
                except Exception:
                    continue
        return out[:limit]


class NasaProvider(SearchProvider):
    id = "nasa"
    name = "NASA Images"
    kind = "api"
    needs_key = False
    API = "https://images-api.nasa.gov/search"

    def search(self, query: str, limit: int = 40, **kwargs: Any) -> list[Wallpaper]:
        try:
            data = self.session.get_json(self.API, params={
                "q": query, "media_type": "image", "page_size": min(limit, 100),
            })
        except Exception:
            return []
        out = []
        for item in (data.get("collection") or {}).get("items", [])[:limit]:
            try:
                meta = (item.get("data") or [{}])[0]
                links = item.get("links") or []
                canonical = next((l for l in links if l.get("rel") == "canonical"), None)
                thumb = next((l for l in links if l.get("rel") in ("thumb", "preview")), None)
                url = (canonical or links[0]).get("href", "") if links else ""
                keywords = meta.get("keywords") or []
                out.append(self.make(
                    title=str(meta.get("title", "NASA"))[:90],
                    url=url,
                    thumb_url=(thumb or {}).get("href", url),
                    source_page=f"https://images.nasa.gov/details/{meta.get('nasa_id','')}",
                    width=int((canonical or {}).get("width") or 0),
                    height=int((canonical or {}).get("height") or 0),
                    format=self.ext_from_url(url) or "JPG",
                    file_size=int((canonical or {}).get("size") or 0) or None,
                    author=meta.get("secondary_creator") or meta.get("center") or "NASA",
                    published=parse_date(meta.get("date_created")),
                    tags=[str(k) for k in keywords][:12],
                    description=strip_html(str(meta.get("description", "")))[:300],
                ))
            except Exception:
                continue
        return out[:limit]


class FlickrProvider(SearchProvider):
    id = "flickr"
    name = "Flickr (publiczny feed)"
    kind = "api"
    needs_key = False
    API = "https://www.flickr.com/services/feeds/photos_public.gne"

    def search(self, query: str, limit: int = 40, **kwargs: Any) -> list[Wallpaper]:
        words = [w for w in query.split() if len(w) > 2][:6]
        try:
            data = self.session.get_json(self.API, params={
                "tags": ",".join(words) or "wallpaper",
                "tagmode": "any", "format": "json", "nojsoncallback": "1",
            })
        except Exception:
            return []
        out = []
        for item in (data.get("items") or [])[:limit]:
            try:
                media = item.get("media") or {}
                thumb = media.get("m", "")
                url = thumb.replace("_m.jpg", "_b.jpg").replace("_m.png", "_b.png")
                tags = [t.strip() for t in str(item.get("tags", "")).split() if t.strip()][:12]
                out.append(self.make(
                    title=strip_html(str(item.get("title", "Flickr")))[:90],
                    url=url, thumb_url=thumb,
                    source_page=item.get("link", ""),
                    width=0, height=0,
                    format=self.ext_from_url(url) or "JPG",
                    author=strip_html(str(item.get("author", ""))),
                    published=parse_date(item.get("date_taken")),
                    tags=tags,
                    description=strip_html(str(item.get("description", "")))[:250],
                ))
            except Exception:
                continue
        return out[:limit]


class OpenverseProvider(SearchProvider):
    id = "openverse"
    name = "Openverse"
    kind = "api"
    needs_key = False
    API = "https://api.openverse.org/v1/images/"

    def search(self, query: str, limit: int = 40, **kwargs: Any) -> list[Wallpaper]:
        try:
            data = self.session.get_json(self.API, params={
                "q": query, "page_size": min(limit, 50), "license_type": "commercial,modification",
            })
        except Exception:
            return []
        out = []
        for it in (data.get("results") or [])[:limit]:
            try:
                out.append(self.make(
                    title=strip_html(str(it.get("title") or "Openverse"))[:90],
                    url=it.get("url", ""),
                    thumb_url=it.get("thumbnail") or it.get("url", ""),
                    source_page=it.get("foreign_landing_url", ""),
                    width=int(it.get("width") or 0), height=int(it.get("height") or 0),
                    format=self.ext_from_url(it.get("url", "")),
                    author=it.get("creator") or "",
                    tags=[str(t) for t in (it.get("tags") or [])][:10],
                    description=strip_html(str(it.get("title") or "")),
                ))
            except Exception:
                continue
        return out[:limit]
