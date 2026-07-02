# Releasing & per-series branches

The Odoo Apps Store wants **one branch per Odoo series** (`17.0`, `18.0`, `19.0`),
each with a manifest `version` prefixed by that series (`17.0.1.0.0`, …). We do
this with the least maintenance possible.

## The model: develop on master, generate the rest

- **`master` is the only branch you edit.** It holds the whole module with a
  bare `version` (`1.0.0` — the single source of truth for x.y.z).
- **`17.0` / `18.0` / `19.0` are generated**, never edited by hand. Each is just
  `master` + the manifest `version` rewritten to `<series>.<x.y.z>`.
- They are **force-pushed** from master, so treat them as build artifacts.

This works because the code is genuinely cross-version: version differences are
handled at **runtime** (`session.server_version_info` in the widget, Odoo's
auto-prefixing of the bare manifest version), not by forking the code. The e2e
suite proves one codebase runs on 17/18/19.

## How it stays in sync — automatically

`.github/workflows/release-branches.yml` runs on every push to `master` and
regenerates + force-pushes the series branches via `tools/release.sh`. So:

- Merge to `master` → the series branches update themselves. Nothing to do.

To do it by hand (or from a machine):

```bash
tools/release.sh          # update local 17.0/18.0/19.0 branches
tools/release.sh --push   # …and force-push them
```

## Cutting a release

1. Make your changes on `master`; ensure `test/run.sh` passes on each series.
2. Bump `version` (x.y.z) in `addressable_autocomplete/__manifest__.py` per
   semver (increase on any DB-schema change).
3. Push `master`. The branches regenerate as `17.0.<x.y.z>`, etc.
4. In the Apps Store, each series listing points at the repo + its branch and
   picks up the new version.

## Adding a new Odoo series (e.g. 20.0)

1. Add `"20"` to the matrix in `.github/workflows/e2e.yml` and run
   `test/run.sh 20` — fix anything it surfaces (prefer **runtime** detection on
   master over a branch fork; see below).
2. Add `"20.0"` to `SERIES` in `tools/release.sh`.
3. Push `master`. The `20.0` branch is created automatically.

That's it — two one-line edits.

## If a series ever needs different *code*

First try to handle it on `master` with a runtime check (as we already do for
the many2one value shape). Only if that's truly impossible should a series
branch carry a real patch — and then:

- Remove that series from `tools/release.sh` (so it isn't auto-overwritten), and
- Maintain it by rebasing its patch onto master at release time.

Avoid this if at all possible: keeping every series on one `master` is the whole
point of the low-maintenance model.

## Rules

- **Never commit to a series branch** — changes there are lost on the next
  regenerate/force-push.
- The series branches are **not** e2e-tested in CI (identical code to master);
  master + PRs are.
