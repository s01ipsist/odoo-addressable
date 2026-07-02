#!/usr/bin/env bash
#
# Generate the Apps Store listing screenshots and copy them into the module's
# static/description folder. Runs the full e2e stack with CAPTURE=1 so the
# (normally skipped) screenshots spec fires.
#
#     ./capture-screenshots.sh          # Odoo 17
#     ./capture-screenshots.sh 18
set -euo pipefail
cd "$(dirname "$0")"

CAPTURE=1 ./run.sh "${1:-17}"

SRC=playwright/artifacts/screenshots
DEST=../addressable_autocomplete/static/description
cp "$SRC/autocomplete.png" "$DEST/screenshot-autocomplete.png"
cp "$SRC/completed.png"    "$DEST/screenshot-completed.png"
cp "$SRC/settings.png"     "$DEST/screenshot-settings.png"
echo "Copied screenshots into $DEST:"
echo "  screenshot-autocomplete.png"
echo "  screenshot-completed.png"
echo "  screenshot-settings.png"
