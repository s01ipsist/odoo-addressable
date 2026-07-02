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
    await expect(page.locator("[name='city'] input")).toHaveValue("Auckland");
    await expect(page.locator("[name='zip'] input")).toHaveValue("1051");
    await expect(page.locator("[name='country_id'] input")).toHaveValue(
        "New Zealand"
    );
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
