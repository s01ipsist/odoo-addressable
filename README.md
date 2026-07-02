# Addressable for Odoo

Free, open-source Odoo modules that bring [Addressable](https://www.addressable.dev)
address autocomplete and verification to Odoo. A privacy-friendly alternative to
Google Places, with first-class coverage of Australia, New Zealand and the
Nordics, built on open address data.

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

Targets **Odoo 17.0**. The JS uses the OWL fields framework and the `rpc`
service. For 16.0 / 18.0 the field-registry and `rpc` import conventions differ
slightly — maintain a branch per Odoo series (`17.0`, `18.0`, …), which is also
how the Odoo Apps Store expects modules to be organised.

## License

LGPL-3. See [LICENSE](LICENSE).

## Status

Scaffold — not yet tested against a live Odoo instance. See
[CONTRIBUTING / testing notes](addressable_autocomplete/) before publishing to
the Odoo Apps Store.
