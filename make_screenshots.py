#!/usr/bin/env python3
"""Generuje zrzuty ekranu OmniFoto (tryb offscreen, dane demo).

Uruchomienie:
    QT_QPA_PLATFORM=offscreen python3 packaging/make_screenshots.py

Jeśli w środowisku brakuje bibliotek systemowych QtNetwork, skrypt używa
bezpiecznego zastępstwa tylko na czas robienia zrzutów (dane demo nie
wymagają sieci).
"""

from __future__ import annotations

import os
import sys
import tempfile
import time
import types
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
OUT = ROOT / "docs" / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)


def _install_network_stub() -> None:
    """Tylko gdy prawdziwy QtNetwork nie daje się zaimportować."""
    try:
        import PySide6.QtNetwork  # noqa: F401
        return
    except ImportError:
        pass
    fake = types.ModuleType("PySide6.QtNetwork")

    class Sig:
        def connect(self, *a, **k):
            pass

        def emit(self, *a, **k):
            pass

    class Dummy:
        def __init__(self, *a, **k):
            pass

        def __getattr__(self, name):
            return Sig()

    class QNetworkReply(Dummy):
        class NetworkError:
            NoError = 0

    class QNetworkRequest(Dummy):
        class Attribute:
            CacheLoadControlAttribute = 1

        class CacheLoadControl:
            AlwaysNetwork = 0

        class KnownHeaders:
            ContentTypeHeader = 1

    fake.QNetworkAccessManager = Dummy
    fake.QNetworkReply = QNetworkReply
    fake.QNetworkRequest = QNetworkRequest
    sys.modules["PySide6.QtNetwork"] = fake


_install_network_stub()

from PySide6.QtCore import QSize  # noqa: E402
from PySide6.QtGui import QImage  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from omnifoto.i18n import Translator  # noqa: E402
from omnifoto.models import ViewMode  # noqa: E402
from omnifoto.settings import Settings  # noqa: E402
from omnifoto.ui.collections_dialog import CollectionsDialog, images_from_paths  # noqa: E402
from omnifoto.ui.dialogs import AboutDialog, SettingsDialog  # noqa: E402
from omnifoto.ui.main_window import MainWindow  # noqa: E402


def pump(app: QApplication, seconds: float = 0.6) -> None:
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        app.processEvents()
        time.sleep(0.02)


def main() -> int:
    app = QApplication([])
    with tempfile.TemporaryDirectory() as tmp:
        settings_path = Path(tmp) / "settings.json"
        settings = Settings(settings_path)
        settings.set("privacy_mode", True)
        settings.set("sources", [s for s in settings.get("sources") if s["id"] == "demo"])
        translator = Translator("pl")

        window = MainWindow(app, translator, settings)
        window.resize(1440, 900)
        window.show()
        pump(app, 0.4)

        # 1) kafelki z wynikami
        window.start_search("")
        pump(app, 1.0)
        window.grab().save(str(OUT / "01-wyniki-kafelki.png"))

        # 2) widok listy
        window.results.set_mode(ViewMode.LIST)
        pump(app, 0.4)
        window.grab().save(str(OUT / "02-wyniki-lista.png"))
        window.results.set_mode(ViewMode.TILES)
        pump(app, 0.3)

        # 3) panel szczegółów + pokaz slajdów
        window.preview_wallpaper(window.current_results[0])
        pump(app, 0.6)
        window.grab().save(str(OUT / "03-szczegoly-i-podglad.png"))
        window.slideshow.showNormal()
        window.slideshow.resize(1280, 800)
        pump(app, 0.4)
        window.slideshow.grab().save(str(OUT / "04-pokaz-slajdow.png"))
        window.slideshow.close()

        # 4) ustawienia
        dlg = SettingsDialog(translator, settings, window)
        dlg.show()
        pump(app, 0.4)
        dlg.grab().save(str(OUT / "05-ustawienia.png"))
        dlg.close()

        # 5) kolekcje z lokalnych plików
        folder = Path(tmp) / "Moje tapety"
        folder.mkdir()
        for i, color in enumerate((0x2A5DAA, 0x7A3AA8, 0x2E8B6B)):
            image = QImage(1280, 800, QImage.Format.Format_RGB32)
            image.fill(color)
            image.save(str(folder / f"tapeta_{i + 1}.png"))
        items = images_from_paths([folder])
        settings.add_collection("Moje tapety", items)
        window.sidebar.refresh_collections()
        pump(app, 0.3)
        col_dlg = CollectionsDialog(translator, settings, window)
        col_dlg.show()
        pump(app, 0.4)
        col_dlg.grab().save(str(OUT / "06-kolekcje.png"))
        col_dlg.close()

        # 6) okno „O programie"
        about = AboutDialog(translator, window)
        about.show()
        pump(app, 0.3)
        about.grab().save(str(OUT / "07-o-programie.png"))
        about.close()

        window.close()

    for path in sorted(OUT.glob("*.png")):
        print(f"{path.name}: {path.stat().st_size // 1024} KB")
    print(f"Zrzuty zapisane w: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
