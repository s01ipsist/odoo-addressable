#!/usr/bin/env bash
#
# End-to-end test runner. Spins up Postgres + a mock Addressable API + Odoo,
# installs & seeds the module, then runs the Playwright suite against the real
# web client. Parametrized by Odoo version:
#
#     ./run.sh            # defaults to Odoo 17
#     ./run.sh 18         # Odoo 18
#     ODOO_VERSION=18 ./run.sh
#
# Requires: docker (compose v2) and python3 (to read the Playwright version).
set -euo pipefail
cd "$(dirname "$0")"

export ODOO_VERSION="${1:-${ODOO_VERSION:-17}}"
DB=test
DC="docker compose"

# Keep the Playwright container image in lock-step with the @playwright/test
# version in package.json. Dependabot only bumps the npm dep; the runner and the
# image's bundled browsers must match, so derive the tag from the single source.
export PLAYWRIGHT_VERSION="$(python3 -c "import json,re; v=json.load(open('playwright/package.json'))['devDependencies']['@playwright/test']; print(re.sub(r'^[^0-9]*','',v))")"
echo "== Playwright ${PLAYWRIGHT_VERSION} =="

echo "== Odoo ${ODOO_VERSION} e2e =="

cleanup() { $DC down -v --remove-orphans >/dev/null 2>&1 || true; }
trap cleanup EXIT
cleanup

echo "== start db + mock =="
$DC up -d db mock

echo "== install module + seed (stop-after-init) =="
# Override entrypoint so we can chain install + shell; pass db flags explicitly
# because bypassing the entrypoint skips its HOST/USER/PASSWORD translation.
$DC run --rm --entrypoint bash odoo -c "
  set -e
  odoo -d ${DB} --db_host=db --db_user=odoo --db_password=odoo \
    --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/repo \
    -i addressable_autocomplete --without-demo=all --stop-after-init --log-level=warn
  odoo shell -d ${DB} --db_host=db --db_user=odoo --db_password=odoo \
    --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/repo \
    --log-level=error < /mnt/repo/test/seed.py
"

echo "== start odoo server =="
$DC up -d odoo

echo "== wait for odoo http =="
for i in $(seq 1 60); do
  if curl -sf -o /dev/null "http://localhost:8069/web/login"; then
    echo "odoo up"; break
  fi
  [ "$i" = "60" ] && { echo "odoo did not come up"; $DC logs odoo | tail -40; exit 1; }
  sleep 2
done

echo "== run playwright =="
set +e
$DC run --rm -e CAPTURE="${CAPTURE:-}" playwright \
  bash -lc "npm install --no-audit --no-fund --silent && npx playwright test"
rc=$?
set -e

echo "== done (exit ${rc}); html report at test/playwright/artifacts/report =="
exit $rc
