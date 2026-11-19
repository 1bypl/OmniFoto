"""Modele danych. Nie zależą od Qt, dzięki czemu można je testować bez GUI."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from .constants import QUALITY_EMOJI, QUALITY_LABEL, QUALITY_THRESHOLDS


class DeviceType(str, Enum):
    DESKTOP = "desktop"
    LAPTOP = "laptop"
    MOBILE = "mobile"
    TABLET = "tablet"


class Quality(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SortKey(str, Enum):
    RELEVANCE = "relevance"
    QUALITY = "quality"
    RESOLUTION = "resolution"
    DATE = "date"
    SIZE = "size"
    FORMAT = "format"
    POPULARITY = "popularity"
    DOWNLOADS = "downloads"


class TimeRange(str, Enum):
    ALL = "all"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class ViewMode(str, Enum):
    TILES = "tiles"
    LIST = "list"


DEVICE_ICONS = {
    DeviceType.DESKTOP: "🖥️",
    DeviceType.LAPTOP: "💻",
    DeviceType.MOBILE: "📱",
    DeviceType.TABLET: "📟",
}


def _stable_id(value: str) -> str:
    """Krótki, powtarzalny identyfikator z dowolnego ciągu (np. URL)."""
    return hashlib.sha1(value.encode("utf-8", "ignore")).hexdigest()[:16]


@dataclass
class Wallpaper:
    """Jedna tapeta w wynikach wyszukiwania."""

    id: str = ""
    title: str = ""
    url: str = ""                 # bezpośredni link do pliku (używany do pobrania)
    thumb_url: str = ""           # miniatura (jeśli pusta, użyj url)
    source_page: str = ""         # link do strony źródłowej
    source_name: str = ""
    width: int = 0
    height: int = 0
    format: str = ""
    file_size: int | None = None  # w bajtach
    author: str = ""
    published: datetime | None = None
    rating: float | None = None   # 0-10 lub 0-5
    downloads: int | None = None
    tags: list[str] = field(default_factory=list)
    description: str = ""
    category: str = ""
    devices: list[DeviceType] = field(default_factory=list)
    colors: list[str] = field(default_factory=list)
    is_animated: bool = False
    is_screensaver: bool = False
    source_kind: str = "api"

    def __post_init__(self) -> None:
        if not self.id:
            self.id = _stable_id(self.url or self.title)
        if not self.thumb_url:
            self.thumb_url = self.url
        if not self.format and self.url:
            ext = self.url.split("?")[0].rsplit(".", 1)[-1].lower()
            self.format = ext.upper() if len(ext) <= 5 else ""
        if not self.devices:
            self.devices = self.infer_devices()

    # --- Właściwości pomocnicze --------------------------------------------
    @property
    def resolution(self) -> str:
        if self.width and self.height:
            return f"{self.width}×{self.height}"
        return "—"

    @property
    def aspect_ratio(self) -> str:
        if not self.width or not self.height:
            return "—"
        from math import gcd
        g = gcd(self.width, self.height)
        if not g:
            return "—"
        return f"{self.width // g}:{self.height // g}"

    @property
    def megapixels(self) -> float:
        return round((self.width * self.height) / 1_000_000, 2)

    @property
    def quality(self) -> Quality:
        mp = self.megapixels
        if mp >= QUALITY_THRESHOLDS["high"]:
            return Quality.HIGH
        if mp >= QUALITY_THRESHOLDS["medium"]:
            return Quality.MEDIUM
        return Quality.LOW

    @property
    def quality_color(self) -> str:
        # zwracana nazwa klucza; motyw przypisuje konkretny kolor
        return self.quality.value

    @property
    def quality_emoji(self) -> str:
        return QUALITY_EMOJI[self.quality.value]

    @property
    def quality_label(self) -> str:
        return QUALITY_LABEL[self.quality.value]

    @property
    def size_text(self) -> str:
        if not self.file_size:
            return "—"
        size = float(self.file_size)
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024 or unit == "GB":
                return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
            size /= 1024
        return "—"

    @property
    def date_text(self) -> str:
        if not self.published:
            return "—"
        return self.published.strftime("%Y-%m-%d")

    @property
    def device_icons(self) -> str:
        return " ".join(DEVICE_ICONS.get(d, "") for d in self.devices).strip()

    @property
    def special_icons(self) -> str:
        out = []
        if self.is_animated:
            out.append("🎞️")
        if self.is_screensaver:
            out.append("🌙")
        return " ".join(out)

    @property
    def file_ext(self) -> str:
        return (self.format or "").upper()

    # --- Klasyfikacja urządzeń ---------------------------------------------
    def infer_devices(self) -> list[DeviceType]:
        """Na podstawie proporcji i rozdzielczości dobiera pasujące urządzenia."""
        if not self.width or not self.height:
            return [DeviceType.DESKTOP, DeviceType.LAPTOP]
        ratio = self.width / self.height
        devices: list[DeviceType] = []
        if ratio >= 1.5:  # poziome - desktop / laptop / ultrawide
            devices.append(DeviceType.DESKTOP)
            devices.append(DeviceType.LAPTOP)
            if ratio >= 2.0:  # ultrawide
                devices.append(DeviceType.DESKTOP)
        elif ratio <= 0.9:  # pionowe - telefon / tablet
            devices.append(DeviceType.MOBILE)
            if ratio >= 0.65:
                devices.append(DeviceType.TABLET)
        else:  # kwadrat / 4:3 - tablet i komputer
            devices.append(DeviceType.TABLET)
            devices.append(DeviceType.DESKTOP)
        # unikalność z zachowaniem kolejności
        seen: set[DeviceType] = set()
        unique = []
        for d in devices:
            if d not in seen:
                seen.add(d)
                unique.append(d)
        return unique

    # --- Metadane tekstowe --------------------------------------------------
    def effective_description(self) -> str:
        if self.description:
            return self.description
        parts = [self.title]
        if self.category:
            parts.append(f"Kategoria: {self.category}")
        if self.tags:
            parts.append("Tagi: " + ", ".join(self.tags[:8]))
        return " • ".join(p for p in parts if p)

    # --- Serializacja (ulubione, historia) ----------------------------------
    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["published"] = self.published.isoformat() if self.published else None
        d["devices"] = [x.value for x in self.devices]
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Wallpaper":
        d = dict(data)
        pub = d.get("published")
        if isinstance(pub, str):
            try:
                d["published"] = datetime.fromisoformat(pub)
            except ValueError:
                d["published"] = None
        devs = d.get("devices") or []
        d["devices"] = [DeviceType(x) if isinstance(x, str) and x in DeviceType._value2member_map_ else x for x in devs]
        allowed = {f for f in cls.__dataclass_fields__}  # type: ignore[attr-defined]
        d = {k: v for k, v in d.items() if k in allowed}
        return cls(**d)


def make_demo_wallpaper(**kwargs: Any) -> Wallpaper:
    """Pomocnik tworzący przykładowy wpis (używany przez dostawcę demo)."""
    base = {
        "id": "",
        "title": "Demo",
        "url": "",
        "source_name": "Demo",
        "source_kind": "demo",
        "published": datetime.now(timezone.utc),
    }
    base.update(kwargs)
    return Wallpaper(**base)
