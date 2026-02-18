import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright Configuration Template
 *
 * Production-ready configuration for Playwright E2E tests.
 * Customize baseURL, timeout values, and projects based on your needs.
 */

export default defineConfig({
    // Test directory
    testDir: './e2e',

    // Maximum time one test can run (30 seconds)
    timeout: 30000,

    // Expect timeout for assertions (5 seconds)
    expect: {
        timeout: 5000,
    },

    // Run tests in files in parallel
    fullyParallel: true,

    // Fail the build on CI if you accidentally left test.only in the source code
    forbidOnly: !!process.env.CI,

    // Retry on CI only
    retries: process.env.CI ? 2 : 0,

    // Reporter to use
    reporter: [
        ['html'],
        ['list'],
        ...(process.env.CI ? [['junit', { outputFile: 'test-results/junit.xml' }]] : []),
    ],

    // Shared settings for all projects
    use: {
        // Base URL to use in actions like `await page.goto('/')`
        baseURL: process.env.BASE_URL || 'http://localhost:3000',

        // Collect trace when retrying the failed test
        trace: 'on-first-retry',

        // Screenshot on failure
        screenshot: 'only-on-failure',

        // Video on failure
        video: 'retain-on-failure',

        // Maximum time each action (click, fill, etc.) can take
        actionTimeout: 10000,

        // Navigation timeout
        navigationTimeout: 30000,
    },

    // Configure projects for major browsers
    projects: [
        {
            name: 'chromium',
            use: { ...devices['Desktop Chrome'] },
        },

        {
            name: 'firefox',
            use: { ...devices['Desktop Firefox'] },
        },

        {
            name: 'webkit',
            use: { ...devices['Desktop Safari'] },
        },

        // Mobile browsers
        {
            name: 'Mobile Chrome',
            use: { ...devices['Pixel 5'] },
        },
        {
            name: 'Mobile Safari',
            use: { ...devices['iPhone 13'] },
        },

        // Uncomment for branded browsers
        // {
        //     name: 'Microsoft Edge',
        //     use: { ...devices['Desktop Edge'], channel: 'msedge' },
        // },
        // {
        //     name: 'Google Chrome',
        //     use: { ...devices['Desktop Chrome'], channel: 'chrome' },
        // },
    ],

    // Run local dev server before starting tests
    webServer: {
        command: 'npm run dev',
        url: 'http://localhost:3000',
        reuseExistingServer: !process.env.CI,
        timeout: 120000,
    },
});
