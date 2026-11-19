"""Funkcje pomocnicze niezależne od interfejsu."""

from __future__ import annotations

import html
import re
from datetime import datetime, timedelta, timezone
from typing import Iterable

from .models import SortKey, TimeRange, Wallpaper


def parse_size(text: str | None) -> int | None:
    """Parsuje '1.2 MB' / '1920x1080' -> liczbę bajtów (dla rozmiaru pliku)."""
    if not text:
        return None
    m = re.search(r"([\d.,]+)\s*(B|KB|MB|GB)", str(text), re.I)
    if not m:
        return None
    try:
        value = float(m.group(1).replace(",", "."))
    except ValueError:
        return None
    unit = m.group(2).upper()
    factors = {"B": 1, "KB": 1024, "MB": 1024 ** 2, "GB": 1024 ** 3}
    return int(value * factors.get(unit, 1))


def parse_resolution(text: str | None) -> tuple[int, int]:
    """Parsuje '1920x1080' -> (1920, 1080)."""
    if not text:
        return (0, 0)
    m = re.search(r"(\d{2,5})\s*[x×]\s*(\d{2,5})", str(text))
    if not m:
        return (0, 0)
    return int(m.group(1)), int(m.group(2))


def parse_date(text: str | None) -> datetime | None:
    """Próbuje rozpoznać różne formaty daty z API."""
    if not text:
        return None
    s = str(text).strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        pass
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d.%m.%Y", "%Y/%m/%d"):
        try:
            dt = datetime.strptime(s, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def strip_html(text: str) -> str:
    """Usuwa znaczniki HTML i dekoduje encje."""
    clean = re.sub(r"<[^>]+>", " ", text or "")
    clean = html.unescape(clean)
    return re.sub(r"\s+", " ", clean).strip()


def unique_by(items: Iterable[Wallpaper]) -> list[Wallpaper]:
    """Usuwa duplikaty po identyfikatorze, zachowując kolejność."""
    seen: set[str] = set()
    out = []
    for item in items:
        key = item.id or item.url
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def sort_wallpapers(items: list[Wallpaper], key: SortKey, reverse: bool = True) -> list[Wallpaper]:
    """Sortuje listę tapet według wybranego klucza."""
    def sort_key(w: Wallpaper) -> tuple:
        if key == SortKey.QUALITY:
            return (w.megapixels, w.rating or 0)
        if key == SortKey.RESOLUTION:
            return (w.width * w.height,)
        if key == SortKey.DATE:
            return (w.published.timestamp() if w.published else 0,)
        if key == SortKey.SIZE:
            return (w.file_size or 0,)
        if key == SortKey.FORMAT:
            return (w.format.lower(),)
        if key == SortKey.POPULARITY:
            return (w.rating or 0,)
        if key == SortKey.DOWNLOADS:
            return (w.downloads or 0,)
        # relevance - zachowaj kolejność źródeł
        return (0,)

    # format ma sens rosnąco (alfabet) przy reverse=False
    rev = reverse if key != SortKey.FORMAT else not reverse
    return sorted(items, key=sort_key, reverse=rev)


def filter_by_time(items: list[Wallpaper], rng: TimeRange) -> list[Wallpaper]:
    if rng == TimeRange.ALL:
        return items
    now = datetime.now(timezone.utc)
    days = {TimeRange.DAY: 1, TimeRange.WEEK: 7, TimeRange.MONTH: 30, TimeRange.YEAR: 365}[rng]
    limit = now - timedelta(days=days)
    return [w for w in items if w.published and w.published >= limit]


def filter_by_category(items: list[Wallpaper], category: str | None) -> list[Wallpaper]:
    if not category or category == "all":
        return items
    return [w for w in items if w.category == category or category in [t.lower() for t in w.tags]]


def keyword_category(text: str) -> str:
    """Bardzo proste rozpoznawanie kategorii z frazy (użyteczn[e] przy wyszukiwaniu)."""
    t = (text or "").lower()
    rules = {
        "games": ("game", " gaming", "gry", "grę"),
        "technology": ("tech", "code", "program", "technolog"),
        "os": ("windows", "linux", "macos", "ubuntu", "fedora", "system"),
        "music": ("music", "muzyk", "audio", "spotify"),
        "nature": ("nature", "forest", "natury", "las", "rzek", "przyrod"),
        "landscapes": ("landscape", "mountain", "krajobraz", "gór", "rzek"),
        "abstract": ("abstract", "abstrak", "gradient"),
        "automotive": ("car", "auto", "motoryz", "samoch"),
        "animals": ("animal", "cat", "dog", "zwierz", "kot", "pies"),
        "architecture": ("architecture", "city", "build", "architek", "miasto"),
    }
    for cat, words in rules.items():
        if any(w in t for w in words):
            return cat
    return ""


# --- Precypja wyszukiwania (adaptacja logiki z projektu TorreUp) -----------
# Polskie słowa zamieniamy na angielskie, bo większość API i indeksów obrazów
# rozpoznaje angielskie frazy znacznie lepiej.
PL_TO_EN = {
    "las": "forest", "lasy": "forest", "leśny": "forest", "drzewa": "trees",
    "rzeka": "river", "rzeki": "river", "rzeczny": "river", "woda": "water",
    "zwierze": "animals", "zwierzeta": "animals", "zwierzęta": "animals",
    "zwierzęcy": "animal", "kot": "cat", "koty": "cats", "pies": "dog",
    "gory": "mountains", "góry": "mountains", "gorski": "mountain",
    "krajobraz": "landscape", "krajobrazy": "landscape",
    "natury": "nature", "natura": "nature", "przyroda": "nature",
    "kwiaty": "flowers", "kwiat": "flower", "nebo": "sky", "niebo": "sky",
    "morze": "sea", "ocean": "ocean", "plaza": "beach", "plaża": "beach",
    "miasto": "city", "architektura": "architecture", "budynki": "buildings",
    "samochod": "car", "samochód": "car", "auto": "car", "motoryzacja": "car",
    "technologia": "technology", "komputer": "computer", "laptop": "laptop",
    "telefon": "phone", "telefonu": "phone", "system": "os", "muzyka": "music", "gry": "game",
    "laptopa": "laptop", "laptopie": "laptop", "laptopów": "laptop",
    "komputera": "computer", "komputerze": "computer", "monitora": "monitor",
    "grę": "game", "abstrakcja": "abstract", "abstrakcyjny": "abstract",
    "tapeta": "wallpaper", "tapety": "wallpaper", "tło": "background",
    "animowana": "animated", "wygaszacz": "screensaver",
    "kosmos": "space", "kosmiczny": "space", "przestrzeń": "space",
    "mars": "mars", "planeta": "planet", "planety": "planet",
    "galaktyka": "galaxy", "gwiazda": "star", "gwiazdy": "stars",
    "księżyc": "moon", "ksiezyc": "moon", "asteroida": "asteroid",
    "teleskop": "telescope", "orbita": "orbit", "orbit": "orbit",
}

CATEGORY_WORDS = {
    "games": ["game", "gaming", "video game"],
    "technology": ["technology", "tech", "computer"],
    "os": ["operating system", "windows", "linux", "macos"],
    "music": ["music", "audio", "concert"],
    "nature": ["nature", "forest", "trees", "flowers"],
    "landscapes": ["landscape", "mountains", "river", "nature"],
    "abstract": ["abstract", "gradient", "geometric"],
    "automotive": ["car", "automotive", "vehicle"],
    "animals": ["animals", "wildlife", "pet"],
    "architecture": ["architecture", "city", "building"],
}


SOURCE_HINTS = {"nasa", "unsplash", "pexels", "pixabay", "wallhaven",
                "reddit", "flickr", "openverse"}

# słowa, które nie niosą tematu - nie mogą zawężać zapytania
STOPWORDS = {
    "dla", "by", "for", "the", "of", "and", "with", "w", "na", "do", "i", "z",
    "ze", "od", "tapeta", "tapety", "wallpaper", "wallpapers", "obraz",
    "grafika", "zdjecie", "zdjęcie", "tło", "background", "program", "pobierz",
}
TYPO_FIX = {"parot": "parrot", "elefant": "elephant", "elephants": "elephant",
            "newyork": "new york", "waszawa": "warsaw", "kosmos": "space"}


def prepare_query(query: str, category: str = "all") -> dict:
    """Przygotowuje czystą frazę do API i słowa do weryfikacji trafności.

    Ważne: nazwa źródła (np. „nasa") nie jest częścią zapytania do API,
    lecz wskazówką, które źródło preferować. Słowa kategorii też nie są
    dorzucane do zapytania - wcześniej drastycznie zawężały wyniki.
    """
    raw = re.split(r"[^a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ0-9]+", (query or "").lower())
    tokens: list[str] = []
    for token in raw:
        if len(token) < 2 or token in STOPWORDS:
            continue
        token = TYPO_FIX.get(token, token)
        if token not in tokens:
            tokens.append(token)
        translated = PL_TO_EN.get(token)
        if translated and translated not in tokens:
            tokens.append(translated)

    preferred = [t for t in tokens if t in SOURCE_HINTS]
    user_words = [t for t in tokens if t not in SOURCE_HINTS]

    # Do API wysyłamy tylko 2-3 najważniejsze słowa (bez cyfr wersji).
    # Pełna fraza - z „45", „KDE", „night" - zostaje w user_words i służy
    # do oceny trafności. Dzięki temu dopisywanie słów nie zabija wyników.
    core: list[str] = []
    for word in user_words:
        if word.isdigit():
            continue
        # wolimy angielski odpowiednik niż polską odmianę (laptopa -> laptop)
        if word in PL_TO_EN and PL_TO_EN[word] != word and PL_TO_EN[word] in user_words:
            continue
        candidate = word if word.isascii() else PL_TO_EN.get(word, word)
        if candidate not in core:
            core.append(candidate)
    search_words = core[:3]
    if not search_words:
        search_words = [w for w in user_words if w.isdigit()]

    cat_words = list(CATEGORY_WORDS.get(category, [])) if category != "all" else []
    if not search_words:
        search_words = list(dict.fromkeys(cat_words))   # puste zapytanie = kategoria

    return {
        "search": " ".join(search_words) if search_words else "wallpaper",
        "user_words": user_words,
        "cat_words": cat_words,
        "preferred_sources": preferred,
    }


def matches_wallpaper(wallpaper: Wallpaper, prepared: dict) -> bool:
    """Wymaga, aby fraza pojawiła się w TYTULE albo w co najmniej 2 tagach.

    To odrzuca przypadkowe zdjęcia, których opis tylko „przewija" słowo
    zapytania (np. NASA przy frazze „elephant" zwraca „Blowin in the Stellar Wind").
    """
    user_words = prepared.get("user_words", [])
    cat_words = prepared.get("cat_words", [])
    if not user_words:
        if not cat_words:
            return True
        hay = f"{wallpaper.title} {' '.join(wallpaper.tags)} {wallpaper.category}".lower()
        return any(word in hay for word in cat_words)

    title = wallpaper.title.lower()
    tags = " ".join(wallpaper.tags).lower()
    title_hits = sum(1 for word in user_words if word in title)
    tag_hits = sum(1 for word in user_words if word in tags)
    # trafność w tytule jest najmocniejsza; jeden trafny tag też wystarcza
    # (tagi są kuratorskie, a tłumaczenia PL/EN mnożą liczbę słów zapytania)
    return title_hits >= 1 or tag_hits >= 1


def is_wallpaper_quality(wallpaper: Wallpaper) -> bool:
    """Odrzuca małe infografiki, reklamy i miniatury - ma być tapeta, nie znaczek."""
    if wallpaper.width and wallpaper.height:
        return (
            wallpaper.width >= 900
            and wallpaper.height >= 600
            and (wallpaper.width * wallpaper.height) >= 700_000
        )
    # gdy API nie podaje wymiarów (np. Flickr), ufam źródłowi oficjalnemu
    return wallpaper.source_kind in ("api", "demo", "local")


def relevance_score(wallpaper: Wallpaper, prepared: dict) -> int:
    """Im więcej słów z frazy użytkownika, tym wyżej w trafności."""
    hay = " ".join([
        wallpaper.title, " ".join(wallpaper.tags), wallpaper.description,
        wallpaper.category, wallpaper.source_name, wallpaper.url,
    ]).lower()
    title = wallpaper.title.lower()
    score = 0
    for word in prepared.get("user_words", []):
        if word in title:
            # cyfra wersji (45, 13) jest bardzo wyróżniająca
            score += 5 if word.isdigit() else 3
        elif word in hay:
            score += 1
    for source in prepared.get("preferred_sources", []):
        if source in wallpaper.source_name.lower() or source in wallpaper.url.lower():
            score += 4
    for word in prepared.get("cat_words", []):
        if word in hay:
            score += 1
    return score


def safe_filename(name: str, max_len: int = 120) -> str:
    """Zamienia tekst na bezpieczną nazwę pliku."""
    cleaned = re.sub(r"[^\w\-. ]+", "_", name, flags=re.UNICODE).strip(" .")
    return (cleaned or "wallpaper")[:max_len]
