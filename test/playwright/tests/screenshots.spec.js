// @ts-check
// Generates the Apps Store listing screenshots. Skipped in normal runs; enabled
// with CAPTURE=1 (see test/capture-screenshots.sh). Output lands in
// artifacts/screenshots/ and is copied into static/description/ by the wrapper.
// Two separate tests so each starts from a fresh page (the dirty new-contact
// form otherwise blocks navigation to Settings via the unsaved-changes guard).
const { test } = require("@playwright/test");

test.use({ viewport: { width: 1400, height: 900 } });

test.beforeEach(async ({ page }) => {
    test.skip(process.env.CAPTURE !== "1", "set CAPTURE=1 to generate screenshots");
    await page.goto("/web/login");
    await page.fill('input[name="login"]', "admin");
    await page.fill('input[name="password"]', "admin");
    await Promise.all([
        page.waitForLoadState("networkidle"),
        page.click('button[type="submit"]'),
    ]);
});

test("screenshot: autocomplete dropdown", async ({ page }) => {
    await page.goto("/web#action=contacts.action_contacts");
    await page.waitForSelector(".o_control_panel", { timeout: 30000 });
    await page
        .getByRole("button", { name: "New", exact: true })
        .and(page.locator(":visible"))
        .first()
        .click();
    const street = page.locator(".o_addressable_autocomplete input");
    await street.waitFor({ state: "visible", timeout: 30000 });
    await street.click();
    await street.fill("71B Marua");
    await page
        .locator(".o_addressable_dropdown .dropdown-item")
        .first()
        .waitFor({ state: "visible" });
    await page.waitForTimeout(300);
    await page.screenshot({ path: "artifacts/screenshots/autocomplete.png" });
});

test("screenshot: settings block", async ({ page }) => {
    await page.goto("/web#action=base_setup.action_general_configuration");
    await page.waitForSelector(".o_form_view", { timeout: 30000 });

    // Isolate our section (hides unrelated settings clutter).
    await page.getByPlaceholder("Search...").fill("Addressable");
    await page.waitForTimeout(500);

    // Show the real default base URL instead of the test mock (display only —
    // not saved, and this is the last test so nothing depends on it).
    await page
        .locator("[name='addressable_base_url'] input")
        .fill("https://api.addressable.dev");

    const heading = page
        .locator("h2", { hasText: "Addressable Autocomplete" })
        .first();
    await heading.scrollIntoViewIfNeeded();
    await page.waitForTimeout(300);
    await page.screenshot({ path: "artifacts/screenshots/settings.png" });
});
