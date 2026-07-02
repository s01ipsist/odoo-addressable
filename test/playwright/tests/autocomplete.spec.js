// @ts-check
const { test, expect } = require("@playwright/test");

async function login(page) {
    await page.goto("/web/login");
    await page.fill('input[name="login"]', "admin");
    await page.fill('input[name="password"]', "admin");
    await Promise.all([
        page.waitForLoadState("networkidle"),
        page.click('button[type="submit"]'),
    ]);
}

/**
 * Open a fresh res.partner form by going through the Contacts action and
 * clicking "New". Stable across 16/17/18. Odoo renders desktop + mobile copies
 * of the control-panel buttons, so we intersect with :visible to avoid clicking
 * the hidden one.
 */
async function openNewContact(page) {
    const street = page.locator(".o_addressable_autocomplete input");

    await page.goto("/web#action=contacts.action_contacts");
    await page.waitForSelector(".o_control_panel", { timeout: 30000 });
    await page
        .getByRole("button", { name: "New", exact: true })
        .and(page.locator(":visible"))
        .first()
        .click();
    await street.waitFor({ state: "visible", timeout: 30000 });
    return street;
}

test("street autocomplete fills the address fields", async ({ page }) => {
    await login(page);
    const street = await openNewContact(page);

    await street.click();
    await street.fill("71B Marua");

    // Dropdown appears (widget → fetch → mock API → suggestions).
    const item = page.locator(".o_addressable_dropdown .dropdown-item").first();
    await expect(item).toBeVisible();
    await expect(item).toContainText("Marua Road");
    await item.click();

    // Selecting a suggestion fills the related fields.
    await expect(street).toHaveValue("71B Marua Road");
    // Suburb (locality) is kept in street2, distinct from the city.
    await expect(page.locator("[name='street2'] input")).toHaveValue("Ellerslie");
    await expect(page.locator("[name='city'] input")).toHaveValue("Auckland");
    await expect(page.locator("[name='zip'] input")).toHaveValue("1051");
    await expect(page.locator("[name='country_id'] input")).toHaveValue(
        "New Zealand"
    );
    // Geo-coordinates are captured onto partner_latitude/longitude and persist
    // (the fields are in the view, so record.update() saves them). They're
    // read-only, so they render as text rather than <input>.
    await expect(page.locator("[name='partner_latitude']")).toContainText("-36.891356");
    await expect(page.locator("[name='partner_longitude']")).toContainText("174.821423");
});

test("short queries do not open the dropdown", async ({ page }) => {
    await login(page);
    const street = await openNewContact(page);

    await street.click();
    await street.fill("71");
    // Give the debounce time to (not) fire.
    await page.waitForTimeout(800);
    await expect(
        page.locator(".o_addressable_dropdown")
    ).toHaveCount(0);
});

test("search is scoped to the contact's existing country", async ({ page }) => {
    await login(page);
    const street = await openNewContact(page);

    // Set Country = Australia first. The mock returns AU data only when the
    // request carries country_code=au, so AU results prove the contact's
    // country_id was sent and resolved server-side (without it, the default
    // country NZ would be used and we'd get "Marua Road").
    const countryInput = page.locator("[name='country_id'] input");
    await countryInput.click();
    await countryInput.fill("Australia");
    await page
        .locator(".o-autocomplete--dropdown-item", { hasText: "Australia" })
        .first()
        .click();
    await expect(countryInput).toHaveValue("Australia");

    await street.click();
    await street.fill("12 Collins");

    const item = page.locator(".o_addressable_dropdown .dropdown-item").first();
    await expect(item).toBeVisible();
    await expect(item).toContainText("Collins Street");
    await item.click();

    await expect(street).toHaveValue("12 Collins Street");
    // AU carries the unit in street2; locality is the city (no separate suburb).
    await expect(page.locator("[name='street2'] input")).toHaveValue("Unit 5");
    await expect(page.locator("[name='city'] input")).toHaveValue("Melbourne");
    await expect(page.locator("[name='zip'] input")).toHaveValue("3000");
});

test("Nordic admin fields (municipality/district) are not dropped", async ({ page }) => {
    await login(page);
    const street = await openNewContact(page);

    const countryInput = page.locator("[name='country_id'] input");
    await countryInput.click();
    await countryInput.fill("Sweden");
    await page
        .locator(".o-autocomplete--dropdown-item", { hasText: "Sweden" })
        .first()
        .click();
    await expect(countryInput).toHaveValue("Sweden");

    await street.click();
    await street.fill("12 Storgatan");
    const item = page.locator(".o_addressable_dropdown .dropdown-item").first();
    await expect(item).toBeVisible();
    await item.click();

    await expect(street).toHaveValue("12 Storgatan");
    // locality is the town; municipality is preserved in street2 (not dropped)
    // whether or not Odoo has a matching res.country.state for the district.
    await expect(page.locator("[name='city'] input")).toHaveValue("Stockholm");
    await expect(page.locator("[name='zip'] input")).toHaveValue("111 51");
    await expect(page.locator("[name='street2'] input")).toHaveValue(/kommun/);
});
