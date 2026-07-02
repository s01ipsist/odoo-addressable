#!/usr/bin/env bash
#
# Regenerate the per-series Apps Store branches from master.
#
# The module is a single codebase that runs on every supported Odoo series
# (differences are handled at runtime). The ONLY per-series difference is the
# manifest `version`, which Odoo requires to be prefixed with the series
# (17.0.x, 18.0.x, …). So each series branch is just:  master + version bump.
#
# Branches are DERIVED — never commit to them directly; they are reset and
# force-pushed from master. Develop on master only.
#
# Usage:
#   tools/release.sh            # update local series branches (no push)
#   tools/release.sh --push     # …and force-push them to origin
#   PUSH=1 tools/release.sh      # same as --push (used by CI)
set -euo pipefail
cd "$(dirname "$0")/.."

MANIFEST="addressable_autocomplete/__manifest__.py"
SERIES=("17.0" "18.0" "19.0")   # add a new series here — nothing else changes
PUSH="${PUSH:-0}"
[ "${1:-}" = "--push" ] && PUSH=1

if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "error: working tree not clean — commit or stash first" >&2
    exit 1
fi

BASE_SHA=$(git rev-parse HEAD)
ORIG=$(git branch --show-current || true)

# Single source of truth for x.y.z — read from the manifest's version line only
# (the '"version"' filter avoids matching version-like numbers in comments).
BASE=$(git show "${BASE_SHA}:${MANIFEST}" \
    | grep -E '"version"' | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
[ -n "$BASE" ] || { echo "error: no x.y.z version found in $MANIFEST" >&2; exit 1; }

echo "Base ${BASE_SHA:0:7} · version ${BASE}"
for s in "${SERIES[@]}"; do
    full="${s}.${BASE}"                       # e.g. 17.0.1.0.0
    git switch -q -C "$s" "$BASE_SHA"
    sed -i -E "s/(\"version\"[[:space:]]*:[[:space:]]*\")[^\"]*(\")/\1${full}\2/" "$MANIFEST"
    git commit -aqm "Release ${full} (generated from master ${BASE_SHA:0:7})"
    echo "  ${s}  ->  ${full}"
done

[ -n "$ORIG" ] && git switch -q "$ORIG"

if [ "$PUSH" = "1" ]; then
    git push -f origin "${SERIES[@]}"
    echo "pushed: ${SERIES[*]}"
else
    echo "local only — push with:  git push -f origin ${SERIES[*]}"
fi
