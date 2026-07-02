# End-to-end tests

Dockerized Playwright harness that drives the module in a real Odoo web client.
Parametrized by Odoo version so the same suite runs against any series.

## Run

```bash
cd test
./run.sh          # Odoo 17 (default)
./run.sh 18       # Odoo 18
```

Requires Docker (with Compose v2). No host Node or Python needed — everything
runs in containers.

## What it does

`run.sh` orchestrates a throwaway stack (`docker-compose.yml`):

1. **db** — Postgres 16.
2. **mock** — `mock_api.py`, a stand-in for the Addressable API returning canned
   NZ/AU results. Tests never hit the real service.
3. **odoo** — `odoo:${ODOO_VERSION}`, with the repo mounted as an addons path.
   The module is installed (`-i … --stop-after-init`) and seeded (`seed.py`
   points it at the mock and sets a known admin password).
4. **playwright** — `mcr.microsoft.com/playwright`, runs `tests/*.spec.js`
   against `http://odoo:8069`.

The stack is torn down (`down -v`) on exit, pass or fail.

## Tests (`playwright/tests/autocomplete.spec.js`)

- **street autocomplete fills the address fields** — type into Street → dropdown
  appears → click a suggestion → asserts street/city/zip/country are populated
  (incl. `country_id` resolved to a real record).
- **short queries do not open the dropdown** — the `< 3` char guard.

## Adding an Odoo version

1. Add it to the matrix in `.github/workflows/e2e.yml`.
2. Locally: `./run.sh <version>`.

Nothing else changes — the module uses a bare manifest version (auto-prefixed
per series) and calls its JSON controller with `fetch` (no version-specific RPC
API), so a single tree installs and runs across series. If a future series
changes the OWL field API or control-panel markup, adjust the widget /
selectors and pin per-series branches for the Apps Store.

## Artifacts

On failure, screenshots, video and traces land in
`playwright/artifacts/` (and are uploaded by CI). View a trace with:

```bash
cd test/playwright && npx playwright show-trace artifacts/results/<test>/trace.zip
```
