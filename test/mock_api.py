"""Minimal stand-in for the Addressable API used by the e2e tests.

Serves GET /v2/autocomplete and returns canned, country-aware results in the
same shape the real API produces (array of per-country display-field objects).
"""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# Shapes mirror the real API, incl. lat/lon returned as STRINGS and a meshblock.
DATA = {
    # Real multi-result response for a "71B Marua" NZ lookup.
    "nz": [
        {
            "street_number": "71B", "street": "Marua Road",
            "locality": "Ellerslie", "city": "Auckland", "region": "Auckland",
            "postcode": "1051", "meshblock": "4006113",
            "lon": "174.821423", "lat": "-36.891356",
            "formatted": "71B Marua Road, Ellerslie, Auckland",
        },
        {
            "street_number": "71", "street": "Marua Road",
            "locality": "Hikurangi", "city": "Hikurangi", "region": "Northland",
            "postcode": "0114", "meshblock": "0064501",
            "lon": "174.29641", "lat": "-35.584355",
            "formatted": "71 Marua Road, Hikurangi",
        },
        {
            "street_number": "71C", "street": "Marua Road",
            "locality": "Ellerslie", "city": "Auckland", "region": "Auckland",
            "postcode": "1051", "meshblock": "4006113",
            "lon": "174.821481", "lat": "-36.891373",
            "formatted": "71C Marua Road, Ellerslie, Auckland",
        },
        {
            "street_number": "71A", "street": "Marua Road",
            "locality": "Ellerslie", "city": "Auckland", "region": "Auckland",
            "postcode": "1051", "meshblock": "4006113",
            "lon": "174.821362", "lat": "-36.89134",
            "formatted": "71A Marua Road, Ellerslie, Auckland",
        },
        {
            "street_number": "71", "street": "Mt Marua Way",
            "locality": "Timberlea", "city": "Upper Hutt", "region": "Wellington",
            "postcode": "5018", "meshblock": "4003063",
            "lon": "175.123965", "lat": "-41.098204",
            "formatted": "71 Mt Marua Way, Timberlea, Upper Hutt",
        },
    ],
    "au": [
        {
            "building_name": "", "unit_details": "Unit 5",
            "street_number": "12", "street": "Collins Street",
            "locality": "Melbourne", "region": "Victoria", "postcode": "3000",
            "meshblock": "20603113000",
            "lon": "144.966280", "lat": "-37.813807",
            "formatted": "5/12 Collins Street, Melbourne VIC 3000",
        }
    ],
    # Nordic/Baltic shape: locality (town) + district + municipality, no city.
    "se": [
        {
            "street_number": "12", "street": "Storgatan",
            "locality": "Stockholm", "postcode": "111 51",
            "district": "Stockholms län", "municipality": "Stockholms kommun",
            "lon": "18.068581", "lat": "59.329323",
            "formatted": "Storgatan 12, 111 51 Stockholm",
        }
    ],
}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        qs = parse_qs(urlparse(self.path).query)
        country = (qs.get("country_code", ["nz"])[0] or "nz").lower()
        body = json.dumps(DATA.get(country, DATA["nz"])).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):  # keep the test output quiet
        pass


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
