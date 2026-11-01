# -*- coding: utf-8 -*-
{
    "name": "Addressable Autocomplete",  # <= 25 chars (Odoo Apps Store rule)
    # Single source of truth for the module's x.y.z version. The per-series
    # upload branches are generated from main by tools/release.sh, which
    # prefixes the running series. Bump this to cut a release. See
    # docs/releasing.md.
    "version": "17.0.1.2.0",
    "summary": "Address lookup, autocomplete, autofill & verification for "
               "Australia, New Zealand, Canada, the Nordics & Baltics - a "
               "Google Places alternative",
    "description": """
Address Lookup & Autocomplete
=============================

Add fast, accurate address lookup and autocomplete to the street field on
contacts, customers and vendors. As you type, Addressable suggests real,
verified addresses and, on selection, fills in street, suburb, city, state,
postcode and geo-coordinates (latitude/longitude) for you.

Also known as: address lookup, address autocomplete, address autofill, address
validation, address verification, address finder, address search, postcode and
ZIP lookup, and geocoding. A privacy-friendly alternative to Google Places and
other paid address-lookup services, built on open address data.

Coverage
--------

Australia, New Zealand, Canada, Denmark, Sweden, Norway, Finland, Iceland,
Estonia, the Faroe Islands and Greenland - with more countries added over time.

Requirements
------------

This module is a free, open-source connector. It requires an Addressable API
key to work, and a free tier is available. Sign up at
https://www.addressable.dev and paste your key into Settings, General Settings,
Addressable Autocomplete.

No address data is sent anywhere until you provide a key. When enabled, the
partial address text you type is sent to the Addressable API to retrieve
suggestions.
""",
    "category": "Productivity",
    "author": "Addressable",
    "maintainer": "Addressable",
    "website": "https://www.addressable.dev",
    "support": "support@addressable.dev",
    "license": "LGPL-3",
    "depends": ["base", "base_setup", "contacts"],
    "external_dependencies": {"python": ["requests"]},
    "data": [
        "views/res_config_settings_views.xml",
        "views/res_partner_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "addressable_autocomplete/static/src/scss/addressable_autocomplete.scss",
            "addressable_autocomplete/static/src/js/addressable_autocomplete_field.js",
            "addressable_autocomplete/static/src/xml/addressable_autocomplete_field.xml",
        ],
    },
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": False,
}
