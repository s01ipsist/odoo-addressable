# CLAUDE.md

Guidance for Claude Code (claude.ai/code) working in this repository.

## What this is

A free, open-source **Odoo module** (Python + OWL JS) that adds address
autocomplete to the contact **Street** field, backed by the Addressable API
(`addressable.dev`). Published on the **Odoo Apps Store**. It's a connector — it
requires an Addressable API key (free tier available); the address data comes
from the API. **One codebase runs on Odoo 17.0, 18.0 and 19.0.**

The module lives in `addressable_autocomplete/`.

## Commands (Docker-based — no host Ruby/Node/Python needed)

```bash
cd test && ./run.sh              # e2e suite on Odoo 17 (default)
cd test && ./run.sh 18           # …on 18 (or 19)
cd test && ./capture-screenshots.sh 17   # regenerate listing screenshots
tools/gen-listing-assets.sh      # regenerate icon + banner from the brand SVG
tools/release.sh [--push]        # regenerate per-series branches (usually automatic)
```

`run.sh` spins up Postgres + a mock Addressable API + Odoo + Playwright, installs
the module and runs the suite. **Requires Docker (compose v2)** and nothing else.
Asset scripts need `rsvg-convert` (librsvg) + ImageMagick (`magick`).

## Architecture

- **Widget** — `static/src/{js,xml,scss}/addressable_autocomplete_field.*`: an OWL
  field extending `CharField`, applied to `street`. Debounce + min-chars, keyboard
  nav + ARIA, request race-safety + caching. Calls the controller via `fetch`.
- **Controller** — `controllers/main.py`: server-side proxy to the API's
  `/v2/autocomplete` (keeps the API key server-side). `_normalize()` maps API
  fields → `res.partner` fields and is **field-driven, not country-driven**.
- **Settings** — `models/res_config_settings.py` + `views/res_config_settings_views.xml`
  (API key, base URL, default country).
- **Form** — `views/res_partner_views.xml`: applies the widget and adds
  `partner_latitude` / `partner_longitude`.

## Releases & branches — IMPORTANT

- **Develop on `main` only.** The manifest `version` is a bare `x.y.z` (single
  source of truth).
- `17.0` / `18.0` / `19.0` are **generated** from `main` (version-prefixed) and
  force-pushed by CI (`.github/workflows/release-branches.yml`). **Never edit a
  series branch by hand** — changes are lost on the next regenerate.
- **Cut a release:** bump `version`, move `CHANGELOG.md` `[Unreleased]` → the new
  version, open a PR, **squash-merge** (merge commits are disabled on the repo).
- **New Odoo series:** add it to the `e2e.yml` matrix and `SERIES` in
  `tools/release.sh`; `odoo-version-watch.yml` flags new majors automatically.
- Full detail: `docs/releasing.md`.

## Gotchas

- **Handle version differences at runtime, not by forking branches.** Existing
  cases: many2one value shape (`[id, name]` on 17/18 vs `{id, display_name}` on
  19), and using `fetch` instead of the `rpc` service (its import moved in 18).
  Detect via `session.server_version_info`.
- **Coerce `lat`/`lon` to float** — the API returns them as strings.
- **Do not trim the query** — trailing whitespace is significant to look-ahead.
- **A field must be in the form view for `record.update()` to persist it** — that's
  why the geo fields are added to `res_partner_views.xml`.
- **Listing `static/description/index.html` must be ASCII** (the store mis-decodes
  UTF-8 → mojibake; use HTML entities). The **icon must be opaque** (a transparent
  grayscale+alpha PNG renders as a black box on the store).
- Manifest `name` ≤ 25 chars; description & screenshots in English.

## More docs

`docs/releasing.md` · `docs/country-mapping.md` · `docs/listing-assets.md` ·
`docs/odoo-apps-compliance.md` · `CHANGELOG.md`.
