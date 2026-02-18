import { defineConfig } from 'cypress';

/**
 * Cypress Configuration Template
 *
 * Production-ready configuration for Cypress E2E tests.
 * Customize baseUrl, viewport, and timeout values based on your needs.
 */

export default defineConfig({
    e2e: {
        // Base URL for cy.visit() and cy.request()
        baseUrl: process.env.CYPRESS_BASE_URL || 'http://localhost:3000',

        // Viewport size
        viewportWidth: 1280,
        viewportHeight: 720,

        // Video recording (disable for faster local runs)
        video: process.env.CI ? true : false,
        videosFolder: 'cypress/videos',

        // Screenshot on failure
        screenshotOnRunFailure: true,
        screenshotsFolder: 'cypress/screenshots',

        // Spec file pattern
        specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',

        // Support file
        supportFile: 'cypress/support/e2e.ts',

        // Fixture folder
        fixturesFolder: 'cypress/fixtures',

        // Test isolation (recommended)
        testIsolation: true,

        // Timeouts
        defaultCommandTimeout: 10000,  // Time to wait for commands
        requestTimeout: 10000,          // Time to wait for cy.request()
        responseTimeout: 30000,         // Time to wait for response
        pageLoadTimeout: 60000,         // Time to wait for page load

        // Retry failed tests
        retries: {
            runMode: 2,     // Retry twice in CI
            openMode: 0,    // No retry in interactive mode
        },

        // Environment variables
        env: {
            apiUrl: process.env.API_URL || 'http://localhost:4000/api',
        },

        setupNodeEvents(on, config) {
            // Implement node event listeners here
            // Examples:
            // - Code coverage
            // - Database seeding
            // - Custom tasks

            // on('task', {
            //     'db:seed': () => {
            //         // Seed database
            //         return null;
            //     },
            //     'db:clear': () => {
            //         // Clear database
            //         return null;
            //     },
            // });

            return config;
        },
    },

    // Component testing configuration (optional)
    component: {
        devServer: {
            framework: 'react',  // or 'vue', 'angular', etc.
            bundler: 'vite',     // or 'webpack'
        },
        specPattern: 'src/**/*.cy.{js,jsx,ts,tsx}',
    },
});
