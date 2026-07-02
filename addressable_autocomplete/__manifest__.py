# -*- coding: utf-8 -*-
{
    "name": "Addressable Autocomplete",  # <= 25 chars (Odoo Apps Store rule)
    # Bare x.y.z so Odoo auto-prefixes the running series (installs on 17, 18, …).
    # When publishing to the Apps Store, cut a per-series branch and prefix the
    # version there (e.g. 17.0.1.0.0, 18.0.1.0.0).
    "version": "1.0.0",
    "summary": "Address autocomplete & verification for AU, NZ and the Nordics, "
               "powered by Addressable (addressable.dev)",
    "description": """
Addressable Autocomplete
========================

Add fast, accurate address autocomplete to the street field on contacts,
customers and vendors. As you type, Addressable suggests real, verified
addresses and, on selection, fills in street, city, state, postcode and
geo-coordinates for you.

A privacy-friendly alternative to Google Places, with first-class coverage of
Australia, New Zealand and the Nordics, built on open address data.

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
