// @ts-check
const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
    testDir: "./tests",
    timeout: 90000,
    expect: { timeout: 20000 },
    retries: 0,
    reporter: [["list"], ["html", { outputFolder: "artifacts/report", open: "never" }]],
    outputDir: "artifacts/results",
    use: {
        baseURL: process.env.BASE_URL || "http://localhost:8069",
        headless: true,
        screenshot: "only-on-failure",
        trace: "retain-on-failure",
        video: "retain-on-failure",
    },
});
