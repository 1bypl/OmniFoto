"""Punkt wejścia aplikacji OmniFoto.

Uruchomienie z katalogu projektu:
    python3 -m omnifoto
"""

from __future__ import annotations

import sys


def main() -> int:
    try:
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QApplication, QMessageBox
    except ImportError:
        print(
            "BŁĄD: brak biblioteki PySide6.\n"
            "Na Fedorze zainstaluj:  sudo dnf install python3-pyside6\n"
            "Następnie uruchom ponownie:  python3 -m omnifoto",
            file=sys.stderr,
        )
        return 2

    from . import APP_NAME, __version__
    from .i18n import Translator
    from .settings import Settings
    from .ui.main_window import MainWindow

    QApplication.setApplicationName(APP_NAME)
    QApplication.setApplicationVersion(__version__)
    QApplication.setOrganizationName("1bypl")

    app = QApplication(sys.argv)
    try:
        app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    except AttributeError:
        pass  # atrybut usunięty w nowszych wersjach Qt - nie jest potrzebny

    settings = Settings()
    translator = Translator(settings.get("language", "pl"))
    window = MainWindow(app, translator, settings)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
