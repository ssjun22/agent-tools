/**
 * Page Object Model Template
 *
 * Use this template to create Page Object classes for your application.
 * Page Objects encapsulate page logic and selectors, making tests more maintainable.
 */

// ============================================================================
// PLAYWRIGHT PAGE OBJECT TEMPLATE
// ============================================================================

import { Page, Locator } from '@playwright/test';

export class PlaywrightPageTemplate {
    readonly page: Page;

    // Locators - define all page elements here
    readonly emailInput: Locator;
    readonly passwordInput: Locator;
    readonly submitButton: Locator;
    readonly errorMessage: Locator;
    readonly successMessage: Locator;

    constructor(page: Page) {
        this.page = page;

        // Initialize locators using stable selectors
        this.emailInput = page.getByLabel('Email');
        this.passwordInput = page.getByLabel('Password');
        this.submitButton = page.getByRole('button', { name: 'Submit' });
        this.errorMessage = page.getByRole('alert');
        this.successMessage = page.getByTestId('success-message');
    }

    // Navigation methods
    async goto() {
        await this.page.goto('/page-path');
        await this.page.waitForLoadState('domcontentloaded');
    }

    // Action methods - encapsulate user interactions
    async fillEmail(email: string) {
        await this.emailInput.fill(email);
    }

    async fillPassword(password: string) {
        await this.passwordInput.fill(password);
    }

    async submit() {
        await this.submitButton.click();
    }

    // Composite actions - common user workflows
    async submitForm(email: string, password: string) {
        await this.fillEmail(email);
        await this.fillPassword(password);
        await this.submit();
    }

    // Getter methods - retrieve page data
    async getErrorMessage(): Promise<string> {
        return await this.errorMessage.textContent() ?? '';
    }

    async getSuccessMessage(): Promise<string> {
        return await this.successMessage.textContent() ?? '';
    }

    // Assertion helpers - common assertions
    async expectToBeVisible() {
        await expect(this.page).toHaveURL(/\/page-path/);
    }

    async expectErrorMessage(message: string) {
        await expect(this.errorMessage).toContainText(message);
    }

    async expectSuccessMessage(message: string) {
        await expect(this.successMessage).toContainText(message);
    }
}

// ============================================================================
// CYPRESS PAGE OBJECT TEMPLATE
// ============================================================================

export class CypressPageTemplate {
    // Selector methods - return Cypress chainables
    getEmailInput() {
        return cy.getByLabel('Email');
        // or cy.get('[data-testid="email"]')
    }

    getPasswordInput() {
        return cy.getByLabel('Password');
        // or cy.get('[data-testid="password"]')
    }

    getSubmitButton() {
        return cy.getByRole('button', { name: 'Submit' });
        // or cy.get('[data-testid="submit-button"]')
    }

    getErrorMessage() {
        return cy.get('[role="alert"]');
        // or cy.get('[data-testid="error-message"]')
    }

    getSuccessMessage() {
        return cy.get('[data-testid="success-message"]');
    }

    // Navigation methods
    visit() {
        cy.visit('/page-path');
    }

    // Action methods
    fillEmail(email: string) {
        this.getEmailInput().type(email);
    }

    fillPassword(password: string) {
        this.getPasswordInput().type(password);
    }

    submit() {
        this.getSubmitButton().click();
    }

    // Composite actions
    submitForm(email: string, password: string) {
        this.fillEmail(email);
        this.fillPassword(password);
        this.submit();
    }

    // Assertion helpers
    assertUrl(expectedUrl: string) {
        cy.url().should('include', expectedUrl);
    }

    assertErrorMessage(message: string) {
        this.getErrorMessage().should('contain', message);
    }

    assertSuccessMessage(message: string) {
        this.getSuccessMessage().should('contain', message);
    }
}

// ============================================================================
// USAGE EXAMPLES
// ============================================================================

/*
// PLAYWRIGHT USAGE
import { test, expect } from '@playwright/test';
import { PlaywrightPageTemplate } from './pages/PageTemplate';

test('successful form submission', async ({ page }) => {
    const formPage = new PlaywrightPageTemplate(page);

    await formPage.goto();
    await formPage.submitForm('user@example.com', 'password123');
    await formPage.expectSuccessMessage('Form submitted successfully');
});

test('form validation error', async ({ page }) => {
    const formPage = new PlaywrightPageTemplate(page);

    await formPage.goto();
    await formPage.submitForm('invalid-email', 'short');
    await formPage.expectErrorMessage('Please enter a valid email');
});

// CYPRESS USAGE
import { CypressPageTemplate } from '../pages/PageTemplate';

describe('Form Tests', () => {
    const formPage = new CypressPageTemplate();

    beforeEach(() => {
        formPage.visit();
    });

    it('successful form submission', () => {
        formPage.submitForm('user@example.com', 'password123');
        formPage.assertSuccessMessage('Form submitted successfully');
    });

    it('form validation error', () => {
        formPage.submitForm('invalid-email', 'short');
        formPage.assertErrorMessage('Please enter a valid email');
    });
});
*/

// ============================================================================
// BEST PRACTICES
// ============================================================================

/*
1. Use Stable Selectors:
   - Prefer: data-testid, role, label
   - Avoid: CSS classes, nth-child

2. Encapsulate Logic:
   - Keep selectors in Page Object
   - Don't expose implementation details
   - Provide high-level methods

3. Single Responsibility:
   - One Page Object per page/component
   - Keep methods focused and simple

4. Return Types:
   - Playwright: Return Locators or Promises
   - Cypress: Return Chainables

5. Naming Conventions:
   - get* for element selectors
   - fill*, click*, select* for actions
   - assert*, expect* for validations

6. Reusability:
   - Extract common patterns
   - Create composite actions
   - Use inheritance for shared logic
*/
