#!/usr/bin/env bash
# OmniFoto - instalator dla Fedory (RPM + zależności z repozytorium)
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VERSION="1.0.0"

echo "==> OmniFoto $VERSION — instalacja na Fedorze"
echo "Katalog źródeł: $PROJECT_DIR"

echo "==> Instaluję zależności systemowe (wymagane hasło administratora)..."
sudo dnf install -y python3 python3-pyside6 python3-pysocks krb5-libs

echo "==> Buduję pakiet RPM..."
"$SCRIPT_DIR/build_rpm.sh"

RPM=$(find "$HOME/rpmbuild/RPMS/noarch" -maxdepth 1 -name "omnifoto-${VERSION}-*.rpm" | head -n1)
if [[ -z "$RPM" ]]; then
    echo "BŁĄD: nie znaleziono zbudowanego RPM." >&2
    exit 1
fi

echo "==> Instaluję $RPM ..."
sudo dnf install -y "$RPM"

echo ""
echo "GOTOWE. Uruchom:  omnifoto"
echo "lub z menu KDE:  OmniFoto"
echo "Odinstalowanie:  sudo dnf remove omnifoto"
