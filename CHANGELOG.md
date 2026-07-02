# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The `version` in `addressable_autocomplete/__manifest__.py` is the single source
of truth for x.y.z; the per-series upload branches (`17.0`, `18.0`, …) prefix it
with the Odoo series. See [docs/releasing.md](docs/releasing.md).

## [Unreleased]

## [1.1.0] - 2026-07-03

### Added
- Capture geo-coordinates onto the contact: `partner_latitude` /
  `partner_longitude` are populated on selection and persist (read-only, shown
  once set).
- Country-scoped search: uses the contact's existing country, falling back to the
  configured default country.
- Full field mapping for all live API countries. Administrative fields are
  resolved to the state and never dropped — `district` / `municipality`
  (Nordics/Baltics) are preserved, and a distinct suburb is kept in Street 2.
- Listing screenshots (dropdown, completed form, settings) and a coverage
  section naming every supported country.

### Changed
- Dropdown now shows full addresses instead of truncated snippets.
- Store searchability: summary and description include the terms users search
  (lookup, autofill, validation, verification, finder, geocoding) plus explicit
  country names.
- Listing assets (icon, banner) are generated reproducibly from the brand SVG.

### Fixed
- Icon appeared as a black box on the Apps Store (was a transparent
  grayscale+alpha PNG); now rendered on an opaque tile.
- Description text showed mojibake from non-ASCII characters; replaced with
  ASCII-safe HTML entities.

## [1.0.0] - 2026-07-02

### Added
- Initial release: address autocomplete on the contact **Street** field, powered
  by the Addressable API, filling street, city, state, postcode and geo-fields
  on selection.
- Server-side proxy controller — the API key is stored in Odoo and never exposed
  to the browser.
- Settings for API key, API base URL, and default country code.
- Support for Odoo 17.0, 18.0 and 19.0 from a single codebase.
