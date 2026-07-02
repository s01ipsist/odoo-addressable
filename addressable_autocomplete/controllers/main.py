# -*- coding: utf-8 -*-
import logging

import requests

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://api.addressable.dev"
AUTOCOMPLETE_PATH = "/v2/autocomplete"
REQUEST_TIMEOUT = 5  # seconds
MIN_QUERY_LENGTH = 3


class AddressableController(http.Controller):
    """Server-side proxy to the Addressable API.

    The API key is kept on the server (in ir.config_parameter) and never sent to
    the browser. The JS field widget calls ``/addressable_autocomplete/suggest``
    and receives suggestions already normalised into res.partner field values.
    """

    @http.route(
        "/addressable_autocomplete/suggest",
        type="json",
        auth="user",
        methods=["POST"],
    )
    def suggest(self, query=None, country_code=None, max_results=8, **kwargs):
        query = (query or "").strip()
        if len(query) < MIN_QUERY_LENGTH:
            return {"suggestions": []}

        params = request.env["ir.config_parameter"].sudo()
        api_key = params.get_param("addressable_autocomplete.api_key")
        base_url = params.get_param(
            "addressable_autocomplete.base_url"
        ) or DEFAULT_BASE_URL
        default_country = params.get_param(
            "addressable_autocomplete.default_country"
        ) or "nz"

        if not api_key:
            return {"error": "missing_api_key", "suggestions": []}

        country_code = (country_code or default_country or "").strip().lower()

        try:
            response = requests.get(
                base_url.rstrip("/") + AUTOCOMPLETE_PATH,
                params={
                    "api_key": api_key,
                    "country_code": country_code,
                    "q": query,
                    "max_results": max_results,
                },
                timeout=REQUEST_TIMEOUT,
            )
        except requests.RequestException as exc:
            _logger.warning("Addressable request failed: %s", exc)
            return {"error": "request_failed", "suggestions": []}

        if response.status_code == 401:
            return {"error": "invalid_api_key", "suggestions": []}
        if response.status_code == 403:
            return {"error": "country_not_in_plan", "suggestions": []}
        if response.status_code == 429:
            return {"error": "rate_limited", "suggestions": []}
        if response.status_code != 200:
            _logger.warning(
                "Addressable returned HTTP %s: %s",
                response.status_code, response.text[:200],
            )
            return {"error": "request_failed", "suggestions": []}

        try:
            results = response.json()
        except ValueError:
            return {"suggestions": []}

        if not isinstance(results, list):
            return {"suggestions": []}

        return {
            "suggestions": [
                self._normalize(result, country_code) for result in results
            ]
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _normalize(self, result, country_code):
        """Map an Addressable result to res.partner field values.

        Addressable returns per-country display fields, e.g.
        NZ: street_number, street, locality, city, region, postcode, lon, lat,
            formatted
        AU: building_name, unit_details, street_number, street, locality,
            region, postcode, lon, lat, formatted
        """
        def val(key):
            return (result.get(key) or "").strip() if result.get(key) else ""

        street_number = val("street_number")
        street_name = val("street")
        street = " ".join(p for p in [street_number, street_name] if p).strip()

        # AU carries sub-address detail in these; fall back to empty elsewhere.
        street2 = val("unit_details") or val("building_name")

        # NZ distinguishes locality (suburb) from city; other countries only
        # populate locality. Prefer the most city-like value available.
        city = val("city") or val("locality")

        region = val("region")
        zip_code = val("postcode")
        formatted = val("formatted") or ", ".join(
            p for p in [street, city, region, zip_code] if p
        )

        country = request.env["res.country"].sudo().search(
            [("code", "=", country_code.upper())], limit=1
        )

        state_pair = False
        if country and region:
            state = request.env["res.country.state"].sudo().search(
                [
                    ("country_id", "=", country.id),
                    "|",
                    ("name", "=ilike", region),
                    ("code", "=ilike", region),
                ],
                limit=1,
            )
            if state:
                state_pair = [state.id, state.display_name]

        values = {
            "street": street,
            "street2": street2,
            "city": city,
            "zip": zip_code,
            "state_id": state_pair,
            "country_id": [country.id, country.display_name] if country else False,
        }

        # partner_latitude / partner_longitude exist on res.partner in base.
        lat, lon = result.get("lat"), result.get("lon")
        if lat is not None:
            values["partner_latitude"] = lat
        if lon is not None:
            values["partner_longitude"] = lon

        return {"label": formatted, "values": values}
