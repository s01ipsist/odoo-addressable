# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # Stored as ir.config_parameter records via the ``config_parameter`` attr.
    addressable_api_key = fields.Char(
        string="Addressable API Key",
        config_parameter="addressable_autocomplete.api_key",
        help="Your Addressable API key. A free tier is available — "
             "sign up at https://www.addressable.dev.",
    )
    addressable_base_url = fields.Char(
        string="Addressable API Base URL",
        config_parameter="addressable_autocomplete.base_url",
        default="https://api.addressable.dev",
        help="Base URL of the Addressable API. Leave as the default unless you "
             "are pointing at a staging or self-hosted endpoint.",
    )
    addressable_default_country = fields.Char(
        string="Default Country Code",
        config_parameter="addressable_autocomplete.default_country",
        default="nz",
        help="Two-letter country code (e.g. nz, au, se) used when the contact "
             "has no country set yet. When the contact already has a country, "
             "that country is used instead.",
    )
