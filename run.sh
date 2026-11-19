#!/usr/bin/env bash
# OmniFoto - skrypt uruchamiający (Fedora / Debian / Ubuntu)
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if ! python3 -c 'import PySide6' >/dev/null 2>&1; then
    echo "BŁĄD: nie znaleziono PySide6."
    echo "Fedora:  sudo dnf install python3-pyside6"
    echo "Debian/Ubuntu: sudo apt install python3-pyside6.qtwidgets python3-pyside6.qtsvg python3-pyside6.qtnetwork"
    echo "Alternatywa:   python3 -m pip install -r requirements.txt"
    exit 2
fi

exec python3 -m omnifoto "$@"
