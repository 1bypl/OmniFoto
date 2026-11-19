#!/usr/bin/env bash
# OmniFoto - instalator dla Debiana / Ubuntu (pakiet .deb + zależności)
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VERSION="1.0.0"
DEB="$PROJECT_DIR/dist/omnifoto_${VERSION}_all.deb"

echo "==> OmniFoto $VERSION — instalacja na Debianie/Ubuntu"
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "System: ${PRETTY_NAME:-$ID}"
fi

echo "==> Aktualizuję listy pakietów (wymagane hasło administratora)..."
sudo apt update

echo "==> Instaluję podstawowe zależności..."
sudo apt install -y python3 python3-pip dpkg-dev

echo "==> Sprawdzam PySide6 (Qt)..."
if ! python3 -c 'import PySide6' >/dev/null 2>&1; then
    # nazwy pakietów różnią się między dystrybucjami - próbujemy kilku wariantów
    if ! sudo apt install -y python3-pyside6.qtwidgets python3-pyside6.qtsvg python3-pyside6.qtnetwork 2>/dev/null; then
        if ! sudo apt install -y python3-pyside6 2>/dev/null; then
            echo "Brak PySide6 w repozytorium — instaluję przez pip..."
            python3 -m pip install --break-system-packages -r "$PROJECT_DIR/requirements.txt"
        fi
    fi
fi

echo "==> Buduję pakiet .deb..."
"$SCRIPT_DIR/build_deb.sh"

echo "==> Instaluję $DEB ..."
sudo apt install -y "$DEB"

echo ""
echo "GOTOWE. Uruchom:  omnifoto"
echo "lub z menu aplikacji:  OmniFoto"
echo "Odinstalowanie:  sudo apt remove omnifoto"
