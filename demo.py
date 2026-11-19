"""Dostawca danych demo - działa całkowicie offline.

Dzięki niemu OmniFoto ma co pokazać od razu po uruchomieniu, nawet gdy nie ma
internetu lub użytkownik nie wpisał jeszcze kluczy API. Miniatury są generowane
jako grafika SVG w formie „data URI” (nie zapisują niczego na dysku).
"""

from __future__ import annotations

import base64
import html
import re
from datetime import datetime, timedelta, timezone
from typing import Any

from ..constants import DEFAULT_CATEGORIES
from ..models import DeviceType, Wallpaper
from ..utils import keyword_category
from .base import SearchProvider

PALETTES = [
    ("#0f2027", "#2c5364", "🌌"),
    ("#141e30", "#243b55", "🌃"),
    ("#1d2b64", "#f8cdda", "🌸"),
    ("#134e5e", "#71b280", "🌿"),
    ("#2b1055", "#7597de", "✨"),
    ("#232526", "#414345", "🖤"),
    ("#ff512f", "#dd2476", "🔥"),
    ("#005aa7", "#fffde4", "🌊"),
    ("#3a1c71", "#d76d77", "🎨"),
    ("#0b486b", "#f56217", "🏜️"),
    ("#1d976c", "#93f9b9", "🍃"),
    ("#870000", "#190a05", "🌋"),
]

DEMO_ITEMS = [
    ("Azureus w kosmosie", "3840x2160", "WebP", 4.2, 9.1, "nature", "🐸 niebieska żabka w galaktyce, gwiazdy, mgławica", ["azureus", "space", "nebula"]),
    ("Niebieskie światło", "2560x1440", "JPG", 1.8, 8.7, "abstract", "Abstrakcyjne niebieskie linie i światło", ["blue", "abstract", "glow"]),
    ("Górski zachód", "3840x2160", "JPG", 5.6, 9.4, "landscapes", "Zachód słońca nad górami", ["mountain", "sunset", "nature"]),
    ("Laptop na biurku", "1920x1200", "PNG", 2.3, 8.2, "technology", "Nowoczesne stanowisko pracy", ["laptop", "desk", "tech"]),
    ("Neonowe miasto", "3440x1440", "WebP", 3.1, 8.9, "architecture", "Ultrapanorama neonowego miasta nocą", ["city", "neon", "ultrawide"]),
    ("Złota gwiazda", "1080x2400", "PNG", 1.2, 7.8, "abstract", "Złota gwiazda na ciemnym tle - tapeta na telefon", ["star", "gold", "mobile"]),
    ("Kwiat wiśni", "1179x2556", "JPG", 2.7, 9.0, "nature", "Kwiaty wiśni wiosną", ["sakura", "flower", "iphone"]),
    ("Silnik gry", "2560x1440", "AVIF", 4.0, 8.5, "games", "Fantastyczny silnik gry fantasy", ["game", "fantasy", "car"]),
    ("Pustynia 8K", "7680x4320", "JPG", 12.4, 9.6, "landscapes", "Wydmy pustyni w wysokiej rozdzielczości", ["desert", "8k", "sand"]),
    ("Kot w cieniu", "1920x1080", "JPG", 1.1, 8.1, "animals", "Kot w ciepłym świetle", ["cat", "animal", "pet"]),
    ("System Linux", "3840x2160", "PNG", 3.8, 8.8, "os", "Tapeta systemu Linux z motywem terminala", ["linux", "os", "terminal"]),
    ("Fale oceanu", "5120x2880", "WebP", 6.7, 9.2, "nature", "Spokojne fale oceanu 5K", ["ocean", "waves", "5k"]),
    ("Abstrakcja 3D", "2560x1600", "SVG", 0.9, 7.4, "abstract", "Geometryczna abstrakcja wektorowa", ["vector", "geometry", "3d"]),
    ("Muzyka nocą", "1440x3200", "WebP", 2.2, 8.3, "music", "Konto głośnika i światła sceny", ["music", "concert", "mobile"]),
    ("Sampler graficzny", "5120x1440", "AVIF", 5.1, 8.6, "technology", "Super ultrawide - dwa monitory QHD", ["ultrawide", "setup", "32:9"]),
    ("Animowana mgławica", "1920x1080", "WebP", 2.9, 8.0, "abstract", "Animowana tapeta z wirującą mgławicą", ["animated", "nebula", "live"]),
    ("Wygaszacz ekranu", "3840x2160", "HEIC", 4.4, 7.9, "os", "Elegancki wygaszacz ekranu z zegarem", ["screensaver", "clock", "dark"]),
    ("Samochód sportowy", "2560x1440", "JPG", 3.3, 8.4, "automotive", "Samochód sportowy na torze", ["car", "sport", "race"]),
    ("Architektura nowoczesna", "3440x1440", "JPG", 4.7, 8.7, "architecture", "Szklane wieżowce w świetle dziennym", ["building", "modern", "city"]),
    ("Dzika przyroda", "1080x2340", "PNG", 1.6, 7.7, "animals", "Lis w zimowym lesie", ["fox", "winter", "mobile"]),
    ("Gradient Azureus", "3840x2160", "SVG", 0.4, 7.2, "abstract", "Niebieski gradient inspirowany żabką Azureus", ["gradient", "blue", "vector"]),
    ("Leśna ścieżka", "3840x2160", "JPG", 7.8, 9.1, "nature", "Słoneczna ścieżka w lesie, wysokie drzewa", ["forest", "trees", "nature", "las", "path"]),
    ("Rzeczny brzeg", "2560x1440", "WebP", 4.6, 8.8, "landscapes", "Spokojna rzeka i zalesiony brzeg", ["river", "water", "forest", "nature", "rzeka"]),
    ("Dzikie zwierzęta", "1920x1080", "JPG", 2.1, 8.3, "animals", "Sarna w lesie o świcie", ["animals", "wildlife", "deer", "forest", "zwierzęta"]),
    ("Kosmiczny horyzont", "1920x1080", "WebP", 1.9, 8.5, "games", "Horyzont planety w grze sci-fi", ["space", "game", "planet"]),
    ("Rośliny w donicach", "2048x2732", "JPG", 2.5, 7.6, "nature", "Rośliny i światło poranne - iPad", ["plants", "ipad", "nature"]),
    ("Retro konsola", "2560x1600", "PNG", 2.8, 8.0, "games", "Retro konsola i kartridże", ["retro", "console", "game"]),
]


def make_demo_svg(title: str, palette: tuple[str, str, str], width: int, height: int) -> str:
    """Tworzy ładną miniaturę SVG jako data URI (base64)."""
    c1, c2, icon = palette
    safe_title = html.escape(title[:34])
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 640 360">
<defs>
 <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/>
 </linearGradient>
 <radialGradient id="r"><stop offset="0" stop-color="#ffffff" stop-opacity=".35"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></radialGradient>
</defs>
<rect width="640" height="360" fill="url(#g)"/>
<circle cx="500" cy="90" r="180" fill="url(#r)"/>
<circle cx="110" cy="300" r="140" fill="url(#r)"/>
<text x="320" y="150" font-size="64" text-anchor="middle">{icon}</text>
<text x="320" y="215" font-size="24" font-family="sans-serif" font-weight="bold" fill="#ffffff" text-anchor="middle" opacity=".95">{safe_title}</text>
<text x="320" y="250" font-size="14" font-family="sans-serif" fill="#ffffff" text-anchor="middle" opacity=".6">OmniFoto • demo</text>
</svg>"""
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


class DemoProvider(SearchProvider):
    id = "demo"
    name = "Dane demo (offline)"
    kind = "demo"
    needs_key = False

    def search(self, query: str, limit: int = 40, **kwargs: Any) -> list[Wallpaper]:
        q = (query or "").lower().strip()
        if q in ("wallpaper", "tapeta", "tapety"):
            q = ""  # fraza ogólna - pokaż wszystkie pozycje demo
        cat = kwargs.get("category") or ""
        # „natura" -> „nature" itd. (polskie nazwy kategorii)
        cat_names = {name.lower(): cid for cid, _icon, name in DEFAULT_CATEGORIES}
        if not cat and q in cat_names:
            cat = cat_names[q]
            q = ""
        # fraza może mieć wiele słów (np. „las forest nature") - szukaj dowolnego
        tokens = [t for t in re.split(r"\W+", q) if len(t) >= 3]
        now = datetime.now(timezone.utc)
        results: list[Wallpaper] = []
        for index, (title, res, fmt, mp, rating, category, desc, tags) in enumerate(DEMO_ITEMS):
            w, h = (int(x) for x in res.lower().split("x"))
            hay = " ".join([title.lower(), desc.lower(), category, *tags]).lower()
            if tokens and not any(t in hay for t in tokens):
                continue
            if cat and cat != "all" and cat != category:
                continue
            palette = PALETTES[index % len(PALETTES)]
            thumb = make_demo_svg(title, palette, 640, 360)
            animated = "animowan" in desc.lower()
            screensaver = "wygaszacz" in desc.lower()
            devices = []
            ratio = w / h
            if ratio >= 1.5:
                devices = [DeviceType.DESKTOP, DeviceType.LAPTOP]
            elif ratio <= 0.9:
                devices = [DeviceType.MOBILE]
            else:
                devices = [DeviceType.TABLET, DeviceType.DESKTOP]
            results.append(self.make(
                title=title,
                url=thumb,
                thumb_url=thumb,
                source_page="",
                width=w, height=h,
                format=fmt,
                file_size=int(mp * 1024 * 1024 / 3),
                author="1bypl (demo)",
                published=now - timedelta(days=index * 3),
                rating=rating,
                downloads=1000 + index * 137,
                tags=tags,
                description=desc,
                category=category,
                devices=devices,
                colors=[palette[0], palette[1]],
                is_animated=animated,
                is_screensaver=screensaver,
                source_kind="demo",
            ))
            if len(results) >= limit:
                break
        return results
