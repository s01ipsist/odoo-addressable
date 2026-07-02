#!/usr/bin/env bash
#
# Regenerate the Apps Store listing assets (icon + banner) from the brand SVG.
# Idempotent — safe to re-run after editing the variables below.
#
# Requirements: rsvg-convert (librsvg) and ImageMagick (`magick`).
#   Arch:   sudo pacman -S librsvg imagemagick
#   Debian: sudo apt-get install librsvg2-bin imagemagick
#
# Usage:  tools/gen-listing-assets.sh
set -euo pipefail
cd "$(dirname "$0")/.."  # repo root

SVG="tools/brand/addressable-a.svg"
DESC="addressable_autocomplete/static/description"

# --- brand / copy -----------------------------------------------------------
WORDMARK="Addressable"
TAGLINE="Address autocomplete for Odoo"
COVERAGE="Australia, NZ, Canada, Nordics, Baltics & more"

# --- palette ----------------------------------------------------------------
INK="#1a1a1a"       # wordmark
MUTED="#5a6570"     # tagline
ACCENT="#18BC9C"    # coverage line + stripe (Bootswatch Flatly teal)

# --- fonts (must exist in `magick -list font`) ------------------------------
FONT_BOLD="Liberation-Sans-Bold"
FONT_REG="NimbusSans-Regular"

mkdir -p "$DESC"

# --- icon: 512x512, logo centred on a solid white tile, ~32px padding -------
# rsvg -w 448 scales proportionally (SVG is ~1.02:1), leaving padding on 512.
# Use an OPAQUE white background (not transparent): a transparent grayscale+alpha
# PNG renders as a black box in viewers that flatten alpha onto black (as the
# Odoo Apps Store did). -flatten/-alpha off/-type TrueColor => opaque RGB.
rsvg-convert -w 448 "$SVG" -o /tmp/a_icon.png
magick /tmp/a_icon.png -background white -gravity center -extent 512x512 \
  -flatten -alpha off -colorspace sRGB -type TrueColor -depth 8 -strip \
  "$DESC/icon.png"

# --- banner: 1200x600, mark left + text block right + accent stripe ---------
# Mark rendered to 380px tall, placed at (90,110) so it's vertically centred.
# -annotate offsets (gravity NorthWest) are top-of-text; tuned for no overlap.
rsvg-convert -h 380 "$SVG" -o /tmp/a_mark.png
magick -size 1200x600 xc:white \
  /tmp/a_mark.png -gravity NorthWest -geometry +90+110 -composite \
  -font "$FONT_BOLD" -fill "$INK"   -pointsize 90 \
    -gravity NorthWest -annotate +540+205 "$WORDMARK" \
  -font "$FONT_REG"  -fill "$MUTED" -pointsize 38 \
    -annotate +546+330 "$TAGLINE" \
  -font "$FONT_REG"  -fill "$ACCENT" -pointsize 26 \
    -annotate +546+398 "$COVERAGE" \
  -fill "$ACCENT" -draw 'rectangle 0,588 1200,600' \
  -depth 8 -strip "$DESC/banner.png"

echo "Regenerated:"
echo "  $DESC/icon.png   ($(identify -format '%wx%h' "$DESC/icon.png"))"
echo "  $DESC/banner.png ($(identify -format '%wx%h' "$DESC/banner.png"))"
