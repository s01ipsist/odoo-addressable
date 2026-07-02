"""Minimal stand-in for the Addressable API used by the e2e tests.

Serves GET /v2/autocomplete and returns canned, country-aware results in the
same shape the real API produces (array of per-country display-field objects).
"""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

DATA = {
    "nz": [
        {
            "street_number": "71B", "street": "Marua Road",
            "locality": "Ellerslie", "city": "Auckland", "region": "Auckland",
            "postcode": "1051", "lat": -36.9, "lon": 174.8,
            "formatted": "71B Marua Road, Ellerslie, Auckland 1051",
        }
    ],
    "au": [
        {
            "building_name": "", "unit_details": "Unit 5",
            "street_number": "12", "street": "Collins Street",
            "locality": "Melbourne", "region": "Victoria", "postcode": "3000",
            "lat": -37.8, "lon": 144.9,
            "formatted": "5/12 Collins Street, Melbourne VIC 3000",
        }
    ],
    # Nordic/Baltic shape: locality (town) + district + municipality, no city.
    "se": [
        {
            "street_number": "12", "street": "Storgatan",
            "locality": "Stockholm", "postcode": "111 51",
            "district": "Stockholms län", "municipality": "Stockholms kommun",
            "lat": 59.33, "lon": 18.06,
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
