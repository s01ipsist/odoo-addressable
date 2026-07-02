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
    def suggest(self, query=None, country_id=None, country_code=None,
                max_results=8, **kwargs):
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

        # Scope the search to the contact's own country when it has one, so an
        # AU contact gets AU results without the user picking a country. Falls
        # back to an explicit country_code, then the configured default.
        country_code = self._resolve_country_code(
            country_id, country_code, default_country
        )

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
    def _resolve_country_code(self, country_id, country_code, default_country):
        """Prefer the contact's own country, then an explicit code, then the
        configured default. Returns a lowercase two-letter code."""
        if country_id:
            try:
                country = request.env["res.country"].sudo().browse(int(country_id))
                if country.exists() and country.code:
                    return country.code.lower()
            except (ValueError, TypeError):
                pass
        return (country_code or default_country or "nz").strip().lower()
    # ------------------------------------------------------------------
    # Administrative-area fields returned by the API, most-significant first.
    # Used to fill Odoo's single state_id; whichever ones don't resolve to a
    # res.country.state are preserved in street2 rather than dropped. Add a new
    # key here if the API introduces another admin-level field for a country.
    ADMIN_KEYS = ("region", "district", "municipality")

    def _normalize(self, result, country_code):
        """Map an Addressable result to res.partner field values.

        The API returns different field sets per country (all a subset of):
          street_number, street, unit_details, building_name, locality, city,
          region, district, municipality, postcode, meshblock, lon, lat,
          formatted
        Mapping is field-name driven, not country-driven, so a new country works
        with no change as long as it reuses these field names.

          street   <- street_number + street
          street2  <- unit_details + building_name + suburb + leftover admin
          city     <- city, else locality (the town)
          suburb   <- locality when a distinct `city` field is also present
          state_id <- first of region/district/municipality that resolves
          zip      <- postcode
          geo      <- lat / lon    (meshblock has no Odoo field; ignored)
        """
        def val(key):
            return (result.get(key) or "").strip() if result.get(key) else ""

        street_number = val("street_number")
        street_name = val("street")
        street = " ".join(p for p in [street_number, street_name] if p).strip()

        # NZ/US have both `locality` (suburb) and `city` (town); AU, CA and the
        # Nordics/Baltics only have `locality`, which IS the town. So the town
        # goes in `city`, and a distinct suburb is kept in street2 (Odoo has no
        # suburb field). Using city=suburb would lose the real town where it
        # differs from the region (e.g. suburb Chartwell / city Hamilton).
        city = val("city") or val("locality")
        suburb = val("locality") if (val("city") and val("locality") != val("city")) else ""

        zip_code = val("postcode")

        country = request.env["res.country"].sudo().search(
            [("code", "=", country_code.upper())], limit=1
        )

        # Resolve state_id from the most significant admin field that maps to a
        # res.country.state; keep the rest for street2 so nothing is lost.
        admin_values = [val(k) for k in self.ADMIN_KEYS if val(k)]
        state_pair = False
        used_admin = None
        if country:
            for admin in admin_values:
                state = request.env["res.country.state"].sudo().search(
                    [
                        ("country_id", "=", country.id),
                        "|",
                        ("name", "=ilike", admin),
                        ("code", "=ilike", admin),
                    ],
                    limit=1,
                )
                if state:
                    state_pair = [state.id, state.display_name]
                    used_admin = admin
                    break
        leftover_admin = [a for a in admin_values if a != used_admin]

        # street2 = sub-address detail (AU unit/building), suburb, and any admin
        # fields not consumed by state_id.
        street2 = ", ".join(
            p for p in [val("unit_details"), val("building_name"), suburb, *leftover_admin] if p
        )

        formatted = val("formatted") or ", ".join(
            p for p in [street, city, *admin_values, zip_code] if p
        )

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
