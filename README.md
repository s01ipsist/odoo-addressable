# Addressable for Odoo

Free, open-source Odoo modules that bring [Addressable](https://www.addressable.dev)
address autocomplete and verification to Odoo. A privacy-friendly alternative to
Google Places, with first-class coverage of Australia, New Zealand, Canada and
the Nordics & Baltics, built on open address data.

Coverage is field-driven and country-agnostic — see
[docs/country-mapping.md](docs/country-mapping.md) for the per-country field
mapping and what changes (usually nothing) when Addressable adds a country.

> **An Addressable API key is required.** A **free tier** is available — sign up
> at [addressable.dev](https://www.addressable.dev). The modules here are the
> connector; the address data comes from the Addressable API.

## Modules

| Module | Description |
| --- | --- |
| [`addressable_autocomplete`](addressable_autocomplete/) | Autocomplete on the contact **Street** field. On selection, fills street, city, state, postcode and geo-coordinates. |

## How it works

```
Street field (OWL widget)
  → POST /addressable_autocomplete/suggest   (Odoo controller, server-side)
    → GET https://api.addressable.dev/v2/autocomplete?api_key=…&country_code=…&q=…
      → normalised into res.partner field values → applied to the record
```

The API key lives in `ir.config_parameter` on the server and is **never sent to
the browser** — the widget only ever talks to the in-Odoo proxy controller.

## Install

1. Copy `addressable_autocomplete/` into your Odoo `addons` path (or add this
   repo to it).
2. `pip install requests` (bundled with Odoo already, listed for completeness).
3. Update the apps list and install **Addressable Autocomplete**.
4. Go to **Settings → General Settings → Addressable Autocomplete**, paste your
   API key, set the default country code (`nz`, `au`, `se`, …), and save.
5. Open any contact and start typing in the **Street** field.

## Configuration

| Setting | `ir.config_parameter` key | Default |
| --- | --- | --- |
| API Key | `addressable_autocomplete.api_key` | — (required) |
| API Base URL | `addressable_autocomplete.base_url` | `https://api.addressable.dev` |
| Default Country Code | `addressable_autocomplete.default_country` | `nz` |

## Version support

End-to-end tested on **Odoo 17.0, 18.0 and 19.0** — the on-premise series under
[standard support](https://www.odoo.com/documentation/19.0/administration/standard_extended_support.html)
(see [`test/`](test/)). The widget calls its JSON controller with `fetch` (not
the version-specific `rpc` service), detects the running series to emit the
correct many2one value shape (Odoo 19 switched from `[id, name]` pairs to
`{ id, display_name }` objects), and the manifest uses a bare version that Odoo
auto-prefixes per series — so a single tree installs and runs across series.

For the Odoo Apps Store, cut a per-series branch and prefix the manifest version
there (`17.0.1.0.0`, `18.0.1.0.0`), which is how the store organises modules.

## Testing

```bash
cd test && ./run.sh 17     # or: ./run.sh 18
```

Dockerized Playwright suite that installs the module, points it at a mock API,
and drives the real web client. See [`test/README.md`](test/README.md). CI runs
the same suite across an Odoo-version matrix ([`.github/workflows/e2e.yml`](.github/workflows/e2e.yml)).

## License

LGPL-3. See [LICENSE](LICENSE).

## Listing assets

The icon and banner are generated from the brand SVG via
`tools/gen-listing-assets.sh`. See [docs/listing-assets.md](docs/listing-assets.md)
for the exact recipe and how to restyle them.

## Status

Installs cleanly and passes the e2e suite on Odoo 17, 18 & 19. When a contact
already has a country, the search is scoped to it; otherwise the configured
default country is used. Listing icon and banner are in place.
