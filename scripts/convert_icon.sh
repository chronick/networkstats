#!/usr/bin/env bash
# Usage: scripts/convert_icon.sh assets/globe.png
# Converts a PNG icon to a macOS .icns file for app bundling.
# Requires: sips, iconutil (macOS built-in)

set -e

if [ $# -ne 1 ]; then
  echo "Usage: $0 <icon.png>"
  exit 1
fi

ICON_PNG="$1"
ICON_NAME=$(basename "$ICON_PNG" .png)
ICONSET_DIR="assets/${ICON_NAME}.iconset"
ICNS_FILE="assets/${ICON_NAME}.icns"

# Remove any previous iconset directory
rm -rf "$ICONSET_DIR"
mkdir -p "$ICONSET_DIR"

# Generate all required icon sizes for macOS
sips -z 16 16     "$ICON_PNG" --out "$ICONSET_DIR/icon_16x16.png"
sips -z 32 32     "$ICON_PNG" --out "$ICONSET_DIR/icon_16x16@2x.png"
sips -z 32 32     "$ICON_PNG" --out "$ICONSET_DIR/icon_32x32.png"
sips -z 64 64     "$ICON_PNG" --out "$ICONSET_DIR/icon_32x32@2x.png"
sips -z 128 128   "$ICON_PNG" --out "$ICONSET_DIR/icon_128x128.png"
sips -z 256 256   "$ICON_PNG" --out "$ICONSET_DIR/icon_128x128@2x.png"
sips -z 256 256   "$ICON_PNG" --out "$ICONSET_DIR/icon_256x256.png"
sips -z 512 512   "$ICON_PNG" --out "$ICONSET_DIR/icon_256x256@2x.png"
sips -z 512 512   "$ICON_PNG" --out "$ICONSET_DIR/icon_512x512.png"
sips -z 1024 1024 "$ICON_PNG" --out "$ICONSET_DIR/icon_512x512@2x.png"

# Convert the iconset to .icns
iconutil -c icns "$ICONSET_DIR" -o "$ICNS_FILE"

# Clean up iconset directory
rm -rf "$ICONSET_DIR"

echo "Created $ICNS_FILE" 