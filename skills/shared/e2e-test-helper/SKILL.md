---
name: e2e-test-helper
description: Implement reliable E2E tests with Playwright or Cypress. Use when writing end-to-end tests, debugging flaky tests, setting up test automation, or testing critical user flows. Triggers on E2E, Playwright, Cypress, test automation, user journey testing, or flaky test debugging.
---

# E2E Test Helper

Build reliable, fast, and maintainable end-to-end test suites that provide confidence to ship code quickly and catch regressions before users do.

## When to Use This Skill

- Implementing end-to-end test automation
- Debugging flaky or unreliable tests
- Testing critical user workflows
- Setting up CI/CD test pipelines
- Testing across multiple browsers
- Validating accessibility requirements
- Establishing E2E testing standards

## Quick Reference

**Recommended Tools**:
- **Playwright**: Multi-browser support, modern APIs, auto-waiting, parallel execution
- **Cypress**: Developer-friendly UX, time-travel debugging, easier learning curve

**Key Commands**:
```bash
# Playwright
npx playwright test              # Run all tests
npx playwright test --debug      # Debug mode
npx playwright codegen <url>     # Record tests

# Cypress
npx cypress open                 # Open interactive UI
npx cypress run                  # Run headless
```

**File Naming Conventions**:
- Playwright: `*.spec.ts`, `*.e2e.ts`
- Cypress: `*.cy.ts`

**Stable Selectors**:
```typescript
// ✓ Good - use data-testid or semantic roles
getByTestId('submit-button')
getByRole('button', { name: 'Submit' })
getByLabel('Email address')

// ✗ Bad - brittle CSS selectors
get('.btn.btn-primary.submit')
get('div:nth-child(2) > button')
```

## Core Concepts

### Testing Pyramid

```
        /\
       /E2E\         ← Few, focused on critical paths
      /─────\
     /Integr\        ← More, test component interactions
    /────────\
   /Unit Tests\      ← Many, fast, isolated
  /────────────\
```

### What to Test with E2E

**Test with E2E** ✓:
- Critical user journeys (login, checkout, signup)
- Complex interactions (drag-and-drop, multi-step forms)
- Cross-browser compatibility
- Real API integration
- Authentication flows

**Don't Test with E2E** ✗:
- Unit-level logic → use unit tests
- API contracts → use integration tests
- Edge cases → too slow, use unit tests
- Internal implementation details

### Test Philosophy

**Principles**:
1. **Test user behavior, not implementation** - Focus on what users see and do
2. **Keep tests independent** - Each test should run in isolation
3. **Make tests deterministic** - No random failures
4. **Optimize for speed** - Mock external services when appropriate
5. **Use stable selectors** - `data-testid`, roles, labels (not CSS classes)

## E2E Testing Workflow

### Step 1: Choose Your Testing Tool

**Decision Guide**:

Choose **Playwright** if you need:
- Multi-browser testing (Chrome, Firefox, Safari, Edge)
- Parallel test execution out of the box
- Modern async/await APIs
- Built-in auto-waiting
- Mobile browser emulation

Choose **Cypress** if you prefer:
- Superior developer experience
- Time-travel debugging with visual replay
- Easier learning curve
- Real-time reloading
- Focus on Chrome/Edge (Firefox experimental)

See `references/tool-comparison.md` for detailed feature comparison.

### Step 2: Set Up Test Environment

**Playwright Setup**:
```bash
npm init playwright@latest
```

**Cypress Setup**:
```bash
npm install cypress --save-dev
npx cypress open
```

For detailed configuration templates, see:
- `assets/playwright.config.template.ts`
- `assets/cypress.config.template.ts`

Configuration details in:
- `references/playwright-patterns.md`
- `references/cypress-patterns.md`

### Step 3: Implement Page Objects

Use the **Page Object Model (POM)** pattern to encapsulate page logic and reduce duplication.

**Basic Pattern**:
```typescript
// pages/LoginPage.ts
export class LoginPage {
    readonly page: Page;
    readonly emailInput: Locator;
    readonly passwordInput: Locator;
    readonly loginButton: Locator;

    constructor(page: Page) {
        this.page = page;
        this.emailInput = page.getByLabel('Email');
        this.passwordInput = page.getByLabel('Password');
        this.loginButton = page.getByRole('button', { name: 'Login' });
    }

    async goto() {
        await this.page.goto('/login');
    }

    async login(email: string, password: string) {
        await this.emailInput.fill(email);
        await this.passwordInput.fill(password);
        await this.loginButton.click();
    }
}
```

For complete Page Object examples, see:
- `assets/page-object.template.ts`
- `references/playwright-patterns.md` (Pattern 1)
- `references/cypress-patterns.md` (Pattern 1)

### Step 4: Write Test Cases

**Follow the AAA Pattern**:
- **Arrange**: Set up test data and initial state
- **Act**: Perform user actions
- **Assert**: Verify expected outcomes

**Example**:
```typescript
test('successful login redirects to dashboard', async ({ page }) => {
    // Arrange
    const loginPage = new LoginPage(page);
    await loginPage.goto();

    // Act
    await loginPage.login('user@example.com', 'password123');

    // Assert
    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});
```

**Key Principles**:
- One behavior per test
- Descriptive test names
- Use auto-waiting (avoid `waitForTimeout`)
- Test user-visible behavior

For common test patterns, see:
- `references/playwright-patterns.md` (Patterns 2-4)
- `references/cypress-patterns.md` (Pattern 2)

### Step 5: Handle Flaky Tests

**Common Causes and Solutions**:

1. **Fixed Timeouts** ✗
   ```typescript
   // ✗ Bad
   await page.waitForTimeout(3000);

   // ✓ Good
   await expect(page.getByText('Welcome')).toBeVisible();
   ```

2. **Network Dependencies**
   - Mock external APIs
   - Use network interception
   - See `references/playwright-patterns.md` (Pattern 4)

3. **Animation/Transitions**
   - Wait for specific conditions, not arbitrary delays
   - Use `waitForLoadState('networkidle')`

4. **Test Isolation**
   - Clean up test data
   - Don't share state between tests
   - Use fixtures for test data

For comprehensive debugging strategies, see `references/debugging-flaky-tests.md`.

## Common Mistakes to Avoid

- ❌ **Flaky Tests**: Use proper waits, not fixed timeouts
- ❌ **Slow Tests**: Mock external APIs, use parallel execution
- ❌ **Over-Testing**: Don't test every edge case with E2E
- ❌ **Coupled Tests**: Tests should not depend on each other
- ❌ **Brittle Selectors**: Avoid CSS classes, use `data-testid` or semantic roles
- ❌ **No Cleanup**: Always clean up test data after each test
- ❌ **Testing Implementation**: Test user behavior, not internals

## Best Practices

1. **Use Data Attributes**: `data-testid` or `data-cy` for stable selectors
2. **Avoid Brittle Selectors**: Don't rely on CSS classes or DOM structure
3. **Test User Behavior**: Click, type, see - not implementation details
4. **Keep Tests Independent**: Each test should run in isolation
5. **Clean Up Test Data**: Create and destroy test data in each test
6. **Use Page Objects**: Encapsulate page logic to reduce duplication
7. **Meaningful Assertions**: Check actual user-visible behavior
8. **Optimize for Speed**: Mock when possible, enable parallel execution

## Advanced Patterns

For advanced testing patterns, see `references/advanced-testing.md`:

- **Visual Regression Testing**: Screenshot comparison across test runs
- **Parallel Testing with Sharding**: Distribute tests across multiple workers
- **Accessibility Testing**: Automated a11y validation with axe-core

## Resources

### references/

- **playwright-patterns.md**: Complete Playwright patterns with detailed code examples
  - Page Object Model, Fixtures, Waiting Strategies, Network Mocking
- **cypress-patterns.md**: Complete Cypress patterns with detailed code examples
  - Custom Commands, Intercept, Configuration
- **advanced-testing.md**: Advanced testing patterns
  - Visual Regression, Parallel Testing, Accessibility Testing
- **debugging-flaky-tests.md**: Comprehensive debugging strategies and tools
- **tool-comparison.md**: Playwright vs Cypress detailed feature comparison

### assets/

- **playwright.config.template.ts**: Production-ready Playwright configuration
- **cypress.config.template.ts**: Production-ready Cypress configuration
- **page-object.template.ts**: Page Object Model template
- **e2e-testing-checklist.md**: Comprehensive E2E testing checklist
