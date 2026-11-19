#!/usr/bin/env bash
# Buduje pakiet RPM dla Fedory (omnifoto-1.0.0-1.fcXX.noarch.rpm)
set -euo pipefail

VERSION="1.0.0"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "==> Sprawdzam narzędzia rpm-build..."
if ! command -v rpmbuild >/dev/null 2>&1; then
    echo "Instaluję rpm-build i rpmdevtools (wymagane hasło administratora):"
    sudo dnf install -y rpm-build rpmdevtools
fi

echo "==> Przygotowuję drzewo ~/rpmbuild..."
rpmdev-setuptree

STAGE="$(mktemp -d /tmp/opencode/omnifoto-rpm.XXXXXX)"
trap 'rm -rf "$STAGE"' EXIT
SRC_DIR="$STAGE/omnifoto-$VERSION"
mkdir -p "$SRC_DIR"

cp -a "$PROJECT_DIR/omnifoto" "$SRC_DIR/"
cp -a "$PROJECT_DIR/packaging" "$SRC_DIR/"
cp -a "$PROJECT_DIR/README.md" "$PROJECT_DIR/LICENSE" "$PROJECT_DIR/info.txt" \
      "$PROJECT_DIR/requirements.txt" "$PROJECT_DIR/run.sh" "$SRC_DIR/"

echo "==> Tworzę archiwum źródeł..."
tar -czf "$HOME/rpmbuild/SOURCES/omnifoto-$VERSION.tar.gz" \
    -C "$STAGE" "omnifoto-$VERSION"

cp "$PROJECT_DIR/packaging/omnifoto.spec" "$HOME/rpmbuild/SPECS/omnifoto.spec"

echo "==> Buduję pakiet..."
rpmbuild -ba "$HOME/rpmbuild/SPECS/omnifoto.spec"

echo ""
echo "GOTOWE! Pakiet znajdziesz tutaj:"
ls -lh "$HOME/rpmbuild/RPMS/noarch/"omnifoto-*.rpm
echo ""
echo "Instalacja: sudo dnf install ~/rpmbuild/RPMS/noarch/omnifoto-$VERSION-1.fc*.noarch.rpm"
