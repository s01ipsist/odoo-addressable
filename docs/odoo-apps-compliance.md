# Odoo Apps Store — compliance controls

Controls register for publishing **Addressable Autocomplete** to the Odoo Apps
Store, derived from Odoo's own rules and reviewed against the current module.

**Sources**
- Vendor Guidelines — https://apps.odoo.com/apps/vendor-guidelines
- Apps FAQ, "I am an App Maintainer" (rules R1–R6, publishing, versions,
  repository access) — https://apps.odoo.com/apps/faq

**Reviewed:** 2026-07-02 · **Module version:** 1.0.0 · **Odoo series tested:** 17.0, 18.0, 19.0

**Status legend:** ✅ Met · 🟡 Partial · ❌ Gap · ⚙️ Process (action at/after upload) · N/A

---

## Priority gaps (do before upload)

Closed 2026-07-02: **B8** (delinked description), **A6** (support email),
**B5** (screenshots added + embedded), **B9** (feature list), **D3** (privacy
reference). Remaining:

| # | Control | Why it matters |
| --- | --- | --- |
| 1 | **H1 / H3** — dev account + repo access | Needed to publish; private repos must grant `online-odoo` access. External process. |
| 2 | **A1** — module name contains company name | Guidelines say *avoid including the name of your company*; our name is the brand. Decision needed (recommend keep). |
| 3 | **A2** — per-series version prefix | Prefix `17.0.x` / `18.0.x` / `19.0.x` on the upload branches. |
| 4 | **G2** — support monitored | Email is set; ensure `support@addressable.dev` is actually staffed. |

Everything else is Met or a routine process item.

---

## A. Manifest & metadata

| ID | Control (requirement) | Status | Evidence / Gap & action |
| --- | --- | --- | --- |
| A1 | Name explicit, ≤25 chars, **avoid company name & adjectives** | 🟡 | "Addressable Autocomplete" = 24 chars ✅, but "Addressable" is the company/brand name, which the guidelines discourage. **Action:** decide to keep (brand value, consistent with peers like "Google Places" connectors) or rename (e.g. "Address Autocomplete AU/NZ/EU"). Recommend keeping but be ready to rename if flagged. |
| A2 | Version present; major-minor-bugfix semantics; increases with schema updates | 🟡 | Currently bare `1.0.0`. Installs on all series (auto-prefixed). **Action:** at upload, use per-series prefix `17.0.1.0.0`, `18.0.1.0.0`, `19.0.1.0.0` (see G1). |
| A3 | License set in manifest | ✅ | `"license": "LGPL-3"`. |
| A4 | Dependencies complete & existing | ✅ | `base, base_setup, contacts` (all core). `requests` ships with Odoo. |
| A5 | Summary of features | ✅ | Summary set in manifest. |
| A6 | Support email (field optional, but R6 support is mandatory) | ✅ | `"support": "support@addressable.dev"` set in manifest. Ensure it is staffed (see G2). |
| A7 | Author / website | ✅ | `author`/`maintainer`/`website` set. |
| A8 | Category | ✅ | `"Productivity"`. |

## B. Listing / description page

| ID | Control | Status | Evidence / Gap & action |
| --- | --- | --- | --- |
| B1 | Description & screenshots in **English** | ✅ | All English. |
| B2 | Rich HTML description at `static/description/index.html` | ✅ | Present. |
| B3 | Icon at `static/description/icon.png` | ✅ | 512×512 transparent PNG. |
| B4 | Cover image via manifest `images` | ✅ | `banner.png` (1200×600), referenced by `images`. |
| B5 | Screenshots of functionality | ✅ | `screenshot-autocomplete.png` + `screenshot-settings.png` generated from the Playwright run (`test/capture-screenshots.sh`) and embedded in `index.html`. |
| B6 | Description images: png/gif/jpeg only | ✅ | None embedded; when adding B5, keep to allowed formats. |
| B7 | No JS injection, no static tags/widgets/modals, Bootstrap classes only | ✅ | `index.html` uses `oe_*` classes, no scripts. |
| B8 | No links to other app stores/external platforms; only allowed links (static/description, YouTube canonical, MS Teams, `mailto:`, `skype:`) | ✅ | Hyperlink removed from `index.html`; `addressable.dev` now plain text. URL lives in the manifest `website` field. |
| B9 | Accurate, non-misleading info + **detailed feature list** | ✅ | `index.html` now has a bulleted Features section (autocomplete on Street; fills city/state/zip/geo; country-scoped; server-side key; AU/NZ/CA/Nordics/Baltics; graceful fallback). |
| B10 | Technical doc at `doc/index.rst` (optional, auto-loaded) | ⚙️ | Optional. Consider adding a short setup doc. |

## C. Pricing & commercial

| ID | Control | Status | Evidence / Gap & action |
| --- | --- | --- | --- |
| C1 | Price ≤ price on any other platform | ✅ | Free; not sold elsewhere. |
| C2 | Currency EUR/USD; ≥9 EUR if paid | N/A | Free (no `price` key). |
| C3 | Accept Odoo customer refund policy | ✅ | Applies; no cost exposure while free. Re-review if monetized. |
| C4 | Commission 30% sales / 25% IAP | N/A | Informational; relevant only if we later charge or offer IAP. |

## D. Data protection & privacy

| ID | Control | Status | Evidence / Gap & action |
| --- | --- | --- | --- |
| D1 | Explicitly disclose data collected **and** external transmission, in manifest **and** store page (R4) | ✅ | Manifest description and `index.html` both state that typed address text is sent to the Addressable API over HTTPS, and nothing is sent without a key. |
| D2 | User opt-in before transmitting data | ✅* | Nothing is transmitted until an admin enters an API key — an explicit configuration step = opt-in. *Strengthen by wording the settings help as an explicit consent statement. |
| D3 | Link to a Data Privacy Policy (recommended) | ✅ | `index.html` references Addressable's privacy policy & terms (addressable.dev/pages/terms) and `support@addressable.dev` as plain text (respecting B8). |
| D4 | Customer owns their data; no vendor lock-in | ✅ | Module stores nothing of its own; addresses live in the customer's Odoo. Uninstalling leaves data intact. |
| D5 | App must not require an **activation key** to execute | ✅ | The module runs without any key and degrades to manual entry; the Addressable API key unlocks the **external service**, not the module code (same pattern as Google Places connectors). Distinct from a code-activation lock. |

## E. Security & intellectual property

| ID | Control | Status | Evidence / Gap & action |
| --- | --- | --- | --- |
| E1 | No obfuscated/encrypted code | ✅ | Plain Python/JS/XML. |
| E2 | No downloading/installing/launching executable code (R2) | ✅ | Controller fetches **JSON data** from the API — not code; nothing is executed. |
| E3 | Own code; no plagiarism; respect dependency licenses | ✅ | Original; LGPL-3 compatible with core deps. |
| E4 | No data theft / secret monitoring / harm (R1) | ✅ | Only the typed query is sent, on explicit config; disclosed. |
| E5 | Don't remove/uninstall data or features without user request | ✅ | No destructive behaviour. |
| E6 | Don't alter Enterprise validity check or portal/internal separation | ✅ | Not touched. |
| E7 | Not a clone of an Enterprise module | ✅ | No Enterprise address-autocomplete equivalent; distinct BYO-key approach. |

## F. Quality & technical

| ID | Control | Status | Evidence / Gap & action |
| --- | --- | --- | --- |
| F1 | Bug-free, stable, complete; version ≥1.0 for stable | ✅ | `1.0.0`; e2e suite green on 17/18/19. |
| F2 | Installable by copy to addons; deps satisfied; no alt install | ✅ | Standard module; verified via clean install. |
| F3 | External service dependency clearly advertised | ✅ | Stated in manifest, description, README. |
| F4 | No undocumented/hidden features (R3) | ✅ | Behaviour matches description. |

## G. Versioning & maintenance

| ID | Control | Status | Evidence / Gap & action |
| --- | --- | --- | --- |
| G1 | Per-series branches; version prefixed per series (13.0+ sold/served separately) | ⚙️ | Documented in manifest & `test/README.md`. **Action:** cut `17.0`/`18.0`/`19.0` branches with prefixed versions for upload. |
| G2 | Provide customer support (R6) | 🟡 | Support email set (A6) and shown on the description page. **Action:** ensure `support@addressable.dev` is monitored/staffed. |
| G3 | Increase version on schema changes | ⚙️ | No persisted models today (config params only), so low risk. Follow semver on future model changes. |
| G4 | Maintain across new Odoo releases | ⚙️ | Multi-version harness + CI matrix. **Action:** add each new series to `.github/workflows/e2e.yml` and run before publishing. |

## H. Publishing process & repository

| ID | Control | Status | Evidence / Gap & action |
| --- | --- | --- | --- |
| H1 | Repository URL (SSH URI) + access for `online-odoo` (GitHub) / `OdooApps` (GitLab) | ❌ | Repo is local only. **Action:** push to a hosted repo; if private, authorise `online-odoo`, else make public. |
| H2 | Listing scoring: icon, cover, license set, HTML description, ≥3★ | ✅ | Icon ✅, cover ✅, license ✅, HTML ✅. Rating N/A (new). |
| H3 | Registered Odoo developer account | ❌ | **Action:** create/register the publisher account before upload. |

## I. Conduct (behavioural commitments)

| ID | Control | Status | Notes |
| --- | --- | --- | --- |
| I1 | No ranking/rating manipulation (R1) | ✅ | Committed. |
| I2 | No advertising on other vendors' pages; no reputation-harming imagery (R5) | ✅ | Committed. |
| I3 | Fair business practices | ✅ | Committed. |

---

## Summary

Of 48 controls (after the 2026-07-02 fixes): **37 Met ✅ · 2 Gap ❌ · 3 Partial 🟡 · 4 Process ⚙️ · 2 N/A**.

- **Met:** core technical, security, IP, data-transparency, and all listing
  content/assets (description, feature list, icon, banner, screenshots,
  privacy reference, support email) are satisfied.
- **Gaps (external process, 2):** H1 (hosted repo + `online-odoo` access) and
  H3 (registered developer account).
- **Partial (decisions/tweaks):** A1 (keep vs rename brand name), A2 (per-series
  version prefix at upload), G2 (staff the support inbox).
- **Process items:** versioning per series (G1), release maintenance (G4),
  optional technical doc (B10).

None of the gaps are architectural — they are listing/metadata and
publishing-process items. The module code itself already conforms to Odoo's
security, data-protection, and quality rules.
