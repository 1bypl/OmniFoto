"""Stałe używane w całej aplikacji: źródła, formaty, rozdzielczości, motywy."""

from __future__ import annotations

# --- Informacje o programie -------------------------------------------------
APP_NAME = "OmniFoto"
APP_ID = "pl.1bypl.omnifoto"
VERSION = "1.0.0"
AUTHOR = "1bypl"
GITHUB_URL = "https://github.com/1bypl"
LICENSE_NAME = "GNU General Public License v3.0 lub późniejsza"

# --- Języki ----------------------------------------------------------------
LANGUAGES = {
    "pl": "Polski",
    "en": "English",
    "fr": "Français",
    "de": "Deutsch",
    "ru": "Русский",
    "es": "Español",
    "it": "Italiano",
}

# --- Formaty graficzne -----------------------------------------------------
# (rozszerzenie, opis, czy obsługuje animację, czy obsługuje przezroczystość)
IMAGE_FORMATS = [
    ("JPEG", "Joint Photographic Experts Group - zdjęcia", False, False),
    ("JPG", "JPEG - najpopularniejszy format zdjęć", False, False),
    ("PNG", "Portable Network Graphics - bezstratny, przezroczystość", False, True),
    ("WebP", "Nowoczesny format Google - lekki, animacje, alfa", True, True),
    ("AVIF", "Następca WebP - HDR, świetna kompresja", True, True),
    ("HEIC", "High Efficiency Image Format - urządzenia Apple", False, False),
    ("HEIF", "High Efficiency Image Format - sekwencje obrazów", True, False),
    ("SVG", "Scalable Vector Graphics - grafika wektorowa", False, True),
]

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".heic", ".heif", ".svg"}

# --- Rozdzielczości --------------------------------------------------------
DESKTOP_RESOLUTIONS = [
    ("1920x1080", "Full HD / 1080p", "16:9"),
    ("2560x1440", "QHD / 2K", "16:9"),
    ("3840x2160", "4K UHD", "16:9"),
    ("5120x2880", "5K", "16:9"),
    ("7680x4320", "8K UHD", "16:9"),
    ("1920x1200", "WUXGA", "16:10"),
    ("2560x1600", "WQXGA", "16:10"),
    ("3440x1440", "UWQHD - ultrapanoramiczny", "21:9"),
    ("5120x1440", "Super Ultrawide", "32:9"),
]

MOBILE_RESOLUTIONS = [
    ("1080x2400", "FHD+ - Android", "20:9"),
    ("1080x2340", "Android", "19.5:9"),
    ("1440x3200", "QHD+ - flagowy Android", "20:9"),
    ("1179x2556", "iPhone 14/15/16 Pro", "19.5:9"),
    ("1290x2796", "iPhone Pro Max", "19.5:9"),
    ("2048x2732", "iPad Pro", "4:3"),
]

# --- Kategorie -------------------------------------------------------------
DEFAULT_CATEGORIES = [
    ("games", "🎮", "Gry"),
    ("technology", "💻", "Technologia"),
    ("os", "🖥️", "Systemy operacyjne"),
    ("music", "🎵", "Muzyka"),
    ("nature", "🌿", "Natura"),
    ("landscapes", "🏔️", "Krajobrazy"),
    ("abstract", "🎨", "Abstrakcje"),
    ("automotive", "🚗", "Motoryzacja"),
    ("animals", "🐾", "Zwierzęta"),
    ("architecture", "🏛️", "Architektura"),
]

# --- Domyślne źródła -------------------------------------------------------
# kind: "api" (oficjalne API), "scrape" (best-effort), "demo" (dane lokalne)
# key: czy wymaga klucza API wpisanego w ustawieniach
DEFAULT_SOURCES = [
    {
        "id": "wallhaven", "name": "Wallhaven", "url": "https://wallhaven.cc",
        "kind": "api", "key": False, "enabled": True,
        "note": "Gigantyczna baza, świetna wyszukiwarka, filtrowanie po rozdzielczości.",
    },
    {
        "id": "unsplash", "name": "Unsplash", "url": "https://unsplash.com",
        "kind": "api", "key": True, "enabled": True,
        "note": "Profesjonalna fotografia. Wymaga darmowego klucza API (Client ID).",
    },
    {
        "id": "pexels", "name": "Pexels", "url": "https://www.pexels.com",
        "kind": "api", "key": True, "enabled": True,
        "note": "Zdjęcia i krótkie wideo (ruchome tapety). Wymaga klucza API.",
    },
    {
        "id": "pixabay", "name": "Pixabay", "url": "https://pixabay.com",
        "kind": "api", "key": True, "enabled": True,
        "note": "Zdjęcia, ilustracje i grafika AI. Wymaga klucza API.",
    },
    {
        "id": "reddit", "name": "Reddit", "url": "https://www.reddit.com",
        "kind": "api", "key": False, "enabled": True,
        "note": "Społeczności r/wallpapers, r/WidescreenWallpaper, r/MobileWallpaper.",
    },
    {
        "id": "wikimedia", "name": "Wikimedia Commons", "url": "https://commons.wikimedia.org",
        "kind": "api", "key": False, "enabled": True,
        "note": "Miliony darmowych zdjęć CC - ogromny zasięg, bez klucza API.",
    },
    {
        "id": "nasa", "name": "NASA Images", "url": "https://images.nasa.gov",
        "kind": "api", "key": False, "enabled": True,
        "note": "Archiwum NASA: kosmos, Ziemia, technologia - bez klucza API.",
    },
    {
        "id": "flickr", "name": "Flickr (publiczny feed)", "url": "https://www.flickr.com",
        "kind": "api", "key": False, "enabled": False,
        "note": "Publiczny feed tagów - bez klucza API.",
    },
    {
        "id": "openverse", "name": "Openverse", "url": "https://openverse.org",
        "kind": "api", "key": False, "enabled": False,
        "note": "Wolne zdjęcia z wielu repozytoriów (bywa przeciążony).",
    },
    {
        "id": "wallpaperflare", "name": "WallpaperFlare", "url": "https://www.wallpaperflare.com",
        "kind": "scrape", "key": False, "enabled": False,
        "note": "Dopasowywanie tapety do rozdzielczości ekranu (best-effort).",
    },
    {
        "id": "wallpaperhub", "name": "WallpaperHub", "url": "https://wallpaperhub.app",
        "kind": "scrape", "key": False, "enabled": False,
        "note": "Tapety Windows/Surface w 4K/5K (best-effort).",
    },
    {
        "id": "backdrops", "name": "Backdrops", "url": "https://backdrops.io",
        "kind": "scrape", "key": False, "enabled": False,
        "note": "Minimalistyczne tapety na smartfony (best-effort).",
    },
    {
        "id": "basicappleguy", "name": "Basic Apple Guy", "url": "https://basicappleguy.com",
        "kind": "scrape", "key": False, "enabled": False,
        "note": "Tapety w estetyce Apple (best-effort).",
    },
    {
        "id": "deviantart", "name": "DeviantArt", "url": "https://www.deviantart.com",
        "kind": "scrape", "key": False, "enabled": False,
        "note": "Społeczność artystów cyfrowych (best-effort, często blokuje API).",
    },
    {
        "id": "google_images", "name": "Grafika Google", "url": "https://images.google.com",
        "kind": "scrape", "key": False, "enabled": False,
        "note": "Największy zasięg. Wyniki best-effort, zależne od zgody serwisu.",
    },
    {
        "id": "bing_images", "name": "Obrazy Bing", "url": "https://www.bing.com/images",
        "kind": "scrape", "key": False, "enabled": False,
        "note": "Wygodny podgląd pełnego rozmiaru (best-effort).",
    },
    {
        "id": "demo", "name": "Dane demo (offline)", "url": "",
        "kind": "demo", "key": False, "enabled": True,
        "note": "Przykładowe wpisy - program działa również bez internetu.",
    },
]

# --- Motywy ----------------------------------------------------------------
# każdy motyw to słownik zmiennych użytych później w QSS
THEMES = {
    "azureus": {
        "name": "Azureus (niebieski)",
        "bg": "#0e1726", "bg2": "#16233a", "panel": "#1b2b47",
        "card": "#213355", "text": "#e8f0ff", "muted": "#9db2d4",
        "accent": "#3b9dff", "accent2": "#6ec6ff", "border": "#2c4470",
        "good": "#2ecc71", "warn": "#f1c40f", "bad": "#e74c3c",
        "gold": "#ffd54a",
    },
    "dark": {
        "name": "Ciemny nowoczesny",
        "bg": "#121212", "bg2": "#1e1e1e", "panel": "#252525",
        "card": "#2c2c2c", "text": "#f5f5f5", "muted": "#aaaaaa",
        "accent": "#00bcd4", "accent2": "#4dd0e1", "border": "#3a3a3a",
        "good": "#2ecc71", "warn": "#f1c40f", "bad": "#e74c3c",
        "gold": "#ffd54a",
    },
    "light": {
        "name": "Jasny",
        "bg": "#f4f6fb", "bg2": "#ffffff", "panel": "#ffffff",
        "card": "#ffffff", "text": "#1d2733", "muted": "#6b7a90",
        "accent": "#2f6fed", "accent2": "#5b8ff7", "border": "#dce3ef",
        "good": "#27ae60", "warn": "#e1a100", "bad": "#d64545",
        "gold": "#e6a900",
    },
    "green": {
        "name": "Zielony las",
        "bg": "#0d1f17", "bg2": "#152b20", "panel": "#1c3a2b",
        "card": "#234733", "text": "#eafff2", "muted": "#a3c9b4",
        "accent": "#3ddc84", "accent2": "#7ff0b0", "border": "#2c5a40",
        "good": "#2ecc71", "warn": "#f1c40f", "bad": "#e74c3c",
        "gold": "#ffd54a",
    },
    "violet": {
        "name": "Fioletowy",
        "bg": "#160f26", "bg2": "#221636", "panel": "#2b1d45",
        "card": "#352454", "text": "#f3ebff", "muted": "#b9a7d4",
        "accent": "#a56bff", "accent2": "#c79bff", "border": "#46315f",
        "good": "#2ecc71", "warn": "#f1c40f", "bad": "#e74c3c",
        "gold": "#ffd54a",
    },
    "sunset": {
        "name": "Pomarańczowy zachód",
        "bg": "#24150f", "bg2": "#332017", "panel": "#402a1e",
        "card": "#4d3324", "text": "#fff1e8", "muted": "#d4b3a0",
        "accent": "#ff8c42", "accent2": "#ffb37a", "border": "#63432f",
        "good": "#2ecc71", "warn": "#f1c40f", "bad": "#e74c3c",
        "gold": "#ffd54a",
    },
}

# --- Progi jakości (w megapikselach) ---------------------------------------
QUALITY_THRESHOLDS = {
    "high": 6.0,   # >= 6 MP -> zielony
    "medium": 2.0, # >= 2 MP -> żółty
    # poniżej -> czerwony
}

#.zamiast pulsującego paska - proste, czytelne kropki
QUALITY_EMOJI = {"high": "🟢", "medium": "🟡", "low": "🔴"}
QUALITY_LABEL = {
    "high": "wysoka jakość",
    "medium": "średnia jakość",
    "low": "niska jakość",
}

# Plakietki urządzeń - krótkie i zrozumiałe
DEVICE_BADGE = {
    "desktop": ("🖥", "PC", "Komputer stacjonarny / duży monitor"),
    "laptop": ("💻", "LAP", "Laptop"),
    "mobile": ("📱", "TEL", "Telefon"),
    "tablet": ("📟", "TAB", "Tablet"),
}

# Kolejność przełączania skórek jednym kliknięciem
THEME_CYCLE_ORDER = ["azureus", "dark", "light", "green", "violet", "sunset"]

# --- Domyślne ustawienia ---------------------------------------------------
DEFAULT_SETTINGS = {
    "language": "pl",
    "theme": "azureus",
    "view_mode": "tiles",          # "tiles" | "list"
    "page_size": 80,
    "privacy_mode": True,
    "download_onclick": False,     # True = kliknięcie pobiera od razu
    "download_dir": "",
    "proxy_enabled": False,
    "proxy_host": "127.0.0.1",
    "proxy_port": 9050,
    "proxy_type": "socks5",
    "user_agent": "",
    "sources": DEFAULT_SOURCES,
    "categories": [
        {"id": c[0], "icon": c[1], "name": c[2]} for c in DEFAULT_CATEGORIES
    ],
    "api_keys": {"unsplash": "", "pexels": "", "pixabay": ""},
    "recent_limit": 30,
    "favorites": [],
    "history": [],
    "collections": [],   # własne kolekcje: [{"id", "name", "items": [wallpaper...]}]
}
