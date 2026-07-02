/** @odoo-module **/

import { registry } from "@web/core/registry";
import { CharField, charField } from "@web/views/fields/char/char_field";
import { session } from "@web/session";
import { useState } from "@odoo/owl";

const DEBOUNCE_MS = 300; // wait for typing to pause before querying
const MIN_QUERY_LENGTH = 3; // don't query on 1-2 chars (noise, cost)
const MAX_CACHE_ENTRIES = 50; // cap the per-session result cache

// Unique id source for ARIA wiring (combobox <-> listbox <-> options).
let uidSeq = 0;

// Odoo 19 changed the many2one value shape for record.update() from a
// [id, display_name] pair to a { id, display_name } object. Detect the running
// series and emit the right shape.
const ODOO_MAJOR = (session.server_version_info || [])[0] || 0;

function toMany2one(pair) {
    if (!pair) {
        return false;
    }
    const [id, display_name] = pair;
    return ODOO_MAJOR >= 19 ? { id, display_name } : [id, display_name];
}

// Read the record id from a many2one datapoint, whichever shape the running
// series uses (17/18: [id, name] pair; 19+: { id, display_name } object).
function many2oneId(value) {
    if (!value) {
        return false;
    }
    return value.id ?? value[0] ?? false;
}

/**
 * A drop-in replacement for the `char` widget on the `street` field.
 * As the user types, it queries the Addressable proxy controller and shows a
 * dropdown of verified address suggestions. Selecting one fills in the related
 * address fields (city, zip, state_id, country_id, geo-coordinates).
 *
 * Autocomplete best practices implemented here:
 *  - debounce + minimum query length (avoid noisy, costly requests)
 *  - send the query as typed (trailing whitespace matters for look-ahead);
 *    cache results per query+country to skip duplicate network calls
 *  - race-safety: cancel the in-flight request and ignore stale responses so a
 *    slow earlier reply can never overwrite a newer one
 *  - keyboard navigation (Up/Down/Enter/Escape) and ARIA combobox roles
 */
export class AddressableAutocompleteField extends CharField {
    static template = "addressable_autocomplete.AutocompleteField";

    setup() {
        super.setup();
        this.state = useState({
            suggestions: [],
            open: false,
            loading: false,
            activeIndex: -1, // highlighted option for keyboard nav
        });
        this._debounceHandle = null;
        this._blurHandle = null;
        this._abort = null; // AbortController for the in-flight request
        this._reqSeq = 0; // monotonic id to discard stale responses
        this._cache = new Map(); // `${countryKey}:${query}` -> suggestions
        this.listboxId = `o_addr_listbox_${++uidSeq}`;
    }

    get value() {
        return this.props.record.data[this.props.name] || "";
    }

    // ------------------------------------------------------------------
    // Input handling
    // ------------------------------------------------------------------
    onInput(ev) {
        // Keep the underlying char field in sync so a plain save still works.
        this.props.record.update({ [this.props.name]: ev.target.value });
        this._scheduleSearch(ev.target.value);
    }

    _scheduleSearch(rawValue) {
        clearTimeout(this._debounceHandle);
        const value = rawValue || "";
        // Gate on meaningful length, but send the query AS TYPED. Trailing
        // whitespace is significant to a look-ahead search: it signals the end
        // of a token and can shift results to the next address level, so we must
        // not trim it away before querying.
        if (value.trim().length < MIN_QUERY_LENGTH) {
            this._cancelInFlight();
            this._reset();
            return;
        }
        this._debounceHandle = setTimeout(
            () => this._fetchSuggestions(value),
            DEBOUNCE_MS
        );
    }

    _countryKey() {
        return many2oneId(this.props.record.data.country_id) || "default";
    }

    async _fetchSuggestions(query) {
        // New request supersedes any previous one.
        this._cancelInFlight();
        const seq = ++this._reqSeq;

        // Serve from cache when possible (e.g. the user deleted a char and
        // retyped) -- no network round-trip.
        const cacheKey = `${this._countryKey()}:${query}`;
        if (this._cache.has(cacheKey)) {
            this._apply(this._cache.get(cacheKey), seq);
            return;
        }

        this.state.loading = true;
        this.state.open = true;

        const controller = new AbortController();
        this._abort = controller;

        let result;
        try {
            // Plain fetch against the JSON route (version-independent, unlike the
            // `rpc` service whose import path changed between Odoo 17 and 18).
            // The session cookie is sent automatically; type=json is CSRF-exempt.
            const response = await fetch("/addressable_autocomplete/suggest", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    jsonrpc: "2.0",
                    method: "call",
                    params: { query, country_id: this._countryKey() === "default" ? false : this._countryKey() },
                }),
                signal: controller.signal,
            });
            const payload = await response.json();
            result = payload.result || {};
        } catch (error) {
            if (error.name === "AbortError") {
                return; // superseded by a newer request; ignore
            }
            if (seq === this._reqSeq) {
                this.state.loading = false;
                this._reset();
            }
            return;
        }

        const suggestions = (result && result.suggestions) || [];
        this._cacheSet(cacheKey, suggestions);
        this._apply(suggestions, seq);
    }

    /** Apply results only if they belong to the most recent request. */
    _apply(suggestions, seq) {
        if (seq !== this._reqSeq) {
            return; // a newer request has since fired; drop this stale result
        }
        this.state.loading = false;
        this.state.suggestions = suggestions;
        this.state.activeIndex = -1;
        this.state.open = true; // keep open to show results or "No matches"
    }

    _cacheSet(key, suggestions) {
        if (this._cache.size >= MAX_CACHE_ENTRIES) {
            this._cache.delete(this._cache.keys().next().value); // drop oldest
        }
        this._cache.set(key, suggestions);
    }

    _cancelInFlight() {
        if (this._abort) {
            this._abort.abort();
            this._abort = null;
        }
    }

    _reset() {
        this.state.suggestions = [];
        this.state.open = false;
        this.state.activeIndex = -1;
    }

    // ------------------------------------------------------------------
    // Keyboard & mouse navigation
    // ------------------------------------------------------------------
    onKeydown(ev) {
        if (!this.state.open || !this.state.suggestions.length) {
            return;
        }
        const n = this.state.suggestions.length;
        switch (ev.key) {
            case "ArrowDown":
                ev.preventDefault();
                this.state.activeIndex = (this.state.activeIndex + 1) % n;
                break;
            case "ArrowUp":
                ev.preventDefault();
                this.state.activeIndex = (this.state.activeIndex - 1 + n) % n;
                break;
            case "Enter":
                if (this.state.activeIndex >= 0) {
                    ev.preventDefault(); // don't submit/save the form
                    this.onSelectSuggestion(
                        this.state.suggestions[this.state.activeIndex]
                    );
                }
                break;
            case "Escape":
                this._reset();
                break;
        }
    }

    onHover(index) {
        this.state.activeIndex = index;
    }

    async onSelectSuggestion(suggestion) {
        clearTimeout(this._blurHandle);
        this._cancelInFlight();
        // Convert relational values to the per-version many2one shape. Strip
        // empty ones so we don't clobber existing data with `false` when
        // Addressable couldn't resolve a state/country.
        const values = { ...suggestion.values };
        for (const key of ["state_id", "country_id"]) {
            if (values[key]) {
                values[key] = toMany2one(values[key]);
            } else {
                delete values[key];
            }
        }
        await this.props.record.update(values);
        this._reset();
    }

    onBlur() {
        // Delay so a mousedown on a suggestion is processed before we close.
        this._blurHandle = setTimeout(() => {
            this.state.open = false;
        }, 200);
    }
}

export const addressableAutocompleteField = {
    ...charField,
    component: AddressableAutocompleteField,
    displayName: "Addressable Autocomplete",
    supportedTypes: ["char"],
};

registry
    .category("fields")
    .add("addressable_autocomplete", addressableAutocompleteField);
