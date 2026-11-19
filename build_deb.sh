#!/usr/bin/env bash
# Buduje pakiet .deb (Architektura: all) z katalogu projektu.
set -euo pipefail

VERSION="1.0.0"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
OUT_DIR="$PROJECT_DIR/dist"
PKG="$OUT_DIR/omnifoto_${VERSION}_all"

if ! command -v dpkg-deb >/dev/null 2>&1; then
    echo "BŁĄD: dpkg-deb nie jest dostępny. Zainstaluj: sudo apt install dpkg-dev" >&2
    exit 2
fi

echo "==> Przygotowuję strukturę pakietu .deb..."
rm -rf "$PKG"
mkdir -p \
    "$PKG/DEBIAN" \
    "$PKG/usr/share/omnifoto/omnifoto" \
    "$PKG/usr/bin" \
    "$PKG/usr/share/applications" \
    "$PKG/usr/share/icons/hicolor/scalable/apps" \
    "$PKG/usr/share/doc/omnifoto"

cp -a "$PROJECT_DIR/omnifoto/." "$PKG/usr/share/omnifoto/omnifoto/"
find "$PKG" -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true

cat > "$PKG/DEBIAN/control" <<EOF
Package: omnifoto
Version: $VERSION
Section: graphics
Priority: optional
Architecture: all
Depends: python3 (>= 3.10)
Recommends: python3-pyside6, python3-pysocks
Maintainer: 1bypl <1bypl@users.noreply.github.com>
Homepage: https://github.com/1bypl
Description: Local, privacy-focused wallpaper browser
 OmniFoto searches many free wallpaper sources, shows results as tiles or a
 list, supports favorites, custom collections, slideshow with zoom and
 seven interface languages. It runs entirely on the user's computer, stores
 no telemetry and is licensed under GPL-3.0-or-later.
EOF

cat > "$PKG/usr/bin/omnifoto" <<'EOF'
#!/usr/bin/python3
import sys
sys.path.insert(0, "/usr/share/omnifoto")
from omnifoto.app import main
raise SystemExit(main())
EOF
chmod 0755 "$PKG/usr/bin/omnifoto"

cp "$PROJECT_DIR/packaging/omnifoto.desktop" "$PKG/usr/share/applications/omnifoto.desktop"
cp "$PROJECT_DIR/omnifoto/assets/app_icon.svg" "$PKG/usr/share/icons/hicolor/scalable/apps/omnifoto.svg"
cp "$PROJECT_DIR/README.md" "$PROJECT_DIR/LICENSE" "$PROJECT_DIR/info.txt" "$PKG/usr/share/doc/omnifoto/"

echo "==> Buduję archiwum..."
mkdir -p "$OUT_DIR"
dpkg-deb --build --root-owner-group "$PKG"

echo ""
echo "GOTOWE: $PKG.deb"
echo "Instalacja: sudo apt install $PKG.deb"
