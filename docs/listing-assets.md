# Apps Store listing assets

The module's icon and banner are **generated from the brand SVG**, not hand-made,
so they can be reproduced or restyled at any time by re-running one script.

## Files

| Asset | Path | Size | Notes |
| --- | --- | --- | --- |
| Source logo | `tools/brand/addressable-a.svg` | ~522×513 vector | Black "A" mark on transparent. The single source of truth. |
| Icon | `addressable_autocomplete/static/description/icon.png` | 512×512 | Auto-detected by Odoo at this path (no manifest entry). Transparent. |
| Banner | `addressable_autocomplete/static/description/banner.png` | 1200×600 | Referenced by the manifest `images` key. White background. |

## Regenerating

```bash
tools/gen-listing-assets.sh
```

The script is the exact, authoritative recipe — edit the variables at the top
(copy, palette, fonts) and re-run to restyle. It rebuilds **both** the icon and
the banner from the SVG.

### Requirements

- `rsvg-convert` (librsvg) — renders the SVG to PNG preserving aspect ratio.
- ImageMagick (`magick`) — canvas, compositing, text.

```bash
# Arch
sudo pacman -S librsvg imagemagick
# Debian/Ubuntu
sudo apt-get install librsvg2-bin imagemagick
```

## How it works (what the script does)

### Icon — 512×512, transparent, centred with padding

```bash
rsvg-convert -w 448 tools/brand/addressable-a.svg -o /tmp/a_icon.png
magick /tmp/a_icon.png -background none -gravity center -extent 512x512 \
  -depth 8 -strip addressable_autocomplete/static/description/icon.png
```

- `rsvg-convert -w 448` scales proportionally (the SVG is ~1.02:1), so the mark
  is ~448×440 — leaving ~32 px padding once centred on the 512² canvas.
- `-background none -gravity center -extent 512x512` centres it on a transparent
  square. Verify transparency with
  `magick identify -format '%[channels]' …` → `graya`.
- Why 512²: Odoo's own core icons are mostly 100×100, but the store upscales, so
  a larger square stays crisp. Square is required — non-square gets cropped.

### Banner — 1200×600, mark left + text block right + accent stripe

```bash
rsvg-convert -h 380 tools/brand/addressable-a.svg -o /tmp/a_mark.png
magick -size 1200x600 xc:white \
  /tmp/a_mark.png -gravity NorthWest -geometry +90+110 -composite \
  -font Liberation-Sans-Bold -fill '#1a1a1a' -pointsize 90 \
    -gravity NorthWest -annotate +540+205 'Addressable' \
  -font NimbusSans-Regular  -fill '#5a6570' -pointsize 38 \
    -annotate +546+330 'Address autocomplete for Odoo' \
  -font NimbusSans-Regular  -fill '#18BC9C' -pointsize 26 \
    -annotate +546+398 'Australia, NZ, Canada, Nordics, Baltics & more' \
  -fill '#18BC9C' -draw 'rectangle 0,588 1200,600' \
  -depth 8 -strip addressable_autocomplete/static/description/banner.png
```

Layout notes:

- The mark is rendered 380 px tall and placed at `(90, 110)` so it's vertically
  centred on the 600 px canvas.
- Text uses **gravity NorthWest**, so `-annotate +X+Y` offsets are measured from
  the top-left; `Y` is the *top* of the text, not the baseline. The three `Y`
  values (205 / 330 / 398) are tuned to avoid overlap — if you change the
  wordmark point size, re-check spacing.
- `-pointsize 26` on the coverage line keeps the longer text within the canvas
  width. Shorten the copy or drop a point or two if it's ever clipped.

## Palette & fonts

| Token | Value | Use |
| --- | --- | --- |
| Ink | `#1a1a1a` | Wordmark |
| Muted | `#5a6570` | Tagline |
| Accent | `#18BC9C` | Coverage line + bottom stripe (Bootswatch Flatly teal, matching the app UI) |

Fonts must exist in `magick -list font`: **Liberation-Sans-Bold** (wordmark),
**NimbusSans-Regular** (tagline/coverage). Swap in the script if unavailable.
