# Country coverage & field mapping

How the module maps Addressable API results to Odoo `res.partner` fields, and
what (if anything) needs to change here as Addressable adds countries.

## Design: the module is country-agnostic

There is **no hardcoded country list** in this module. The widget sends the
contact's `country_id`; the controller resolves it to an ISO code and forwards
the query; the API returns whatever fields that country uses. Mapping is
**driven by field name, not by country**, so a newly enabled API country works
with no code change *as long as it reuses the known field names below*.

## API fields → Odoo fields

| Odoo field | Sourced from | Notes |
| --- | --- | --- |
| `street` | `street_number` + `street` | |
| `street2` | `unit_details`, `building_name`, suburb, + leftover admin | see below |
| `city` | `city`, else `locality` | `locality` is the town where there's no `city` |
| (suburb) | `locality` when a distinct `city` also exists | → `street2` (Odoo has no suburb field) |
| `state_id` | first of `region` → `district` → `municipality` that resolves | `ADMIN_KEYS` in `controllers/main.py` |
| `zip` | `postcode` | |
| `partner_latitude` / `partner_longitude` | `lat` / `lon` | |
| — | `meshblock` | ignored (no Odoo equivalent) |
| label | `formatted` | shown in the dropdown |

**Admin fields are never dropped.** Odoo has a single `state_id`, but countries
can return up to three admin levels (`region`, `district`, `municipality`). We
fill `state_id` from the most significant one that matches a
`res.country.state`, and put the rest into `street2`. If none resolves (Odoo
ships no states for that country), they all go to `street2` — lossless.

## Current coverage (live API, verified against openapi.yml)

Supported: **AU, CA, DK, EE, FI, FO, GL, IS, NO, NZ, SE**.
(`LT`, `LV`, `US` exist in the API codebase but are not in the published spec.)

| Country | Fields returned | Fully mapped? |
| --- | --- | --- |
| NZ | street_number, street, locality, city, region, postcode, meshblock, lon, lat, formatted | ✅ (suburb→street2) |
| AU | building_name, unit_details, street_number, street, locality, region, postcode, meshblock, lon, lat, formatted | ✅ (unit/building→street2) |
| CA | street_number, street, locality, region, postcode, lon, lat, formatted | ✅ |
| DK, FO, GL, IS, NO | street_number, street, locality, postcode, region, municipality, lon, lat, formatted | ✅ region→state; municipality→street2 |
| EE, SE | street_number, street, locality, postcode, district, municipality, lon, lat, formatted | ✅ district→state (if present); municipality→street2 |
| FI | street_number, street, locality, postcode, municipality, lon, lat, formatted | ✅ municipality→state or street2 |
| US* | street_number, street, locality, city, region, postcode, lon, lat, formatted | ✅ (like NZ) |

\* not in the published spec yet.

> Whether `state_id` actually populates depends on Odoo shipping
> `res.country.state` records for that country. Where it doesn't, the admin
> value is preserved in `street2` instead. This is expected behaviour, not a bug.

## Adding a country — what to change here

For a country the API already serves with the **existing field names**:

- **Nothing.** It works as soon as it's enabled on the API. The
  `Default Country Code` setting is free text, and mapping is field-driven.

You only touch this repo when:

1. **A brand-new field name appears** (e.g. `county`, `ward`, `prefecture`):
   - Admin-level field → add it to `ADMIN_KEYS` in
     `addressable_autocomplete/controllers/main.py`.
   - Sub-address field (like `unit_details`) → add it to the `street2` assembly
     in `_normalize`.
2. **You want test coverage** for the new shape → add a mock entry in
   `test/mock_api.py` and a case in
   `test/playwright/tests/autocomplete.spec.js`.
3. **Marketing copy** → update the coverage line in the banner
   (`tools/gen-listing-assets.sh`, then regenerate) and in
   `static/description/index.html` / the manifest `summary`.

Keep this table and the copy in sync with `openapi.yml` when the live list
changes.
