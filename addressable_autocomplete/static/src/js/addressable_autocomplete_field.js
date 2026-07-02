/** @odoo-module **/

import { registry } from "@web/core/registry";
import { CharField, charField } from "@web/views/fields/char/char_field";
import { useState } from "@odoo/owl";

const DEBOUNCE_MS = 300;
const MIN_QUERY_LENGTH = 3;

/**
 * A drop-in replacement for the `char` widget on the `street` field.
 * As the user types, it queries the Addressable proxy controller and shows a
 * dropdown of verified address suggestions. Selecting one fills in the related
 * address fields (city, zip, state_id, country_id, geo-coordinates).
 */
export class AddressableAutocompleteField extends CharField {
    static template = "addressable_autocomplete.AutocompleteField";

    setup() {
        super.setup();
        this.state = useState({
            suggestions: [],
            open: false,
            loading: false,
        });
        this._debounceHandle = null;
        this._blurHandle = null;
    }

    get value() {
        return this.props.record.data[this.props.name] || "";
    }

    onInput(ev) {
        const value = ev.target.value;
        // Keep the underlying char field in sync so a plain save still works.
        this.props.record.update({ [this.props.name]: value });

        clearTimeout(this._debounceHandle);
        if (!value || value.length < MIN_QUERY_LENGTH) {
            this.state.suggestions = [];
            this.state.open = false;
            return;
        }
        this._debounceHandle = setTimeout(
            () => this._fetchSuggestions(value),
            DEBOUNCE_MS
        );
    }

    async _fetchSuggestions(query) {
        this.state.loading = true;
        this.state.open = true;

        // If the contact already has a country, pass its ISO code so results are
        // scoped correctly; otherwise the server falls back to the configured
        // default country.
        const country = this.props.record.data.country_id;
        const countryCode = country && country[1] ? undefined : undefined;

        let result;
        try {
            // Call the JSON controller with a plain fetch rather than the `rpc`
            // service: the service's import path changed between Odoo 17 and 18,
            // whereas fetch against the JSON-RPC route is version-independent.
            // The session cookie is sent automatically (same origin); type=json
            // routes are CSRF-exempt.
            const response = await fetch("/addressable_autocomplete/suggest", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    jsonrpc: "2.0",
                    method: "call",
                    params: { query, country_code: countryCode },
                }),
            });
            const payload = await response.json();
            result = payload.result || {};
        } catch {
            this.state.loading = false;
            this.state.suggestions = [];
            this.state.open = false;
            return;
        }

        this.state.loading = false;
        this.state.suggestions = (result && result.suggestions) || [];
        this.state.open = this.state.suggestions.length > 0;
    }

    async onSelectSuggestion(suggestion) {
        clearTimeout(this._blurHandle);
        // Strip out empty relational values so we don't clobber existing data
        // with `false` when Addressable couldn't resolve a state/country.
        const values = { ...suggestion.values };
        for (const key of ["state_id", "country_id"]) {
            if (!values[key]) {
                delete values[key];
            }
        }
        await this.props.record.update(values);
        this.state.open = false;
        this.state.suggestions = [];
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
