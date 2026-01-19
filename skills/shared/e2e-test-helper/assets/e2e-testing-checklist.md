# E2E Testing Checklist

Comprehensive checklist for planning, writing, and maintaining E2E tests.

## Planning Phase

### What to Test

- [ ] **Critical User Journeys**
  - [ ] User registration/signup
  - [ ] Login/logout flows
  - [ ] Password reset
  - [ ] Main conversion flows (checkout, subscription, etc.)
  - [ ] Data creation workflows
  - [ ] Data editing/deletion workflows

- [ ] **Complex Interactions**
  - [ ] Multi-step forms
  - [ ] Drag-and-drop functionality
  - [ ] File uploads
  - [ ] Rich text editors
  - [ ] Real-time features (chat, notifications)
  - [ ] Search and filtering

- [ ] **Cross-Browser Requirements**
  - [ ] Chrome/Chromium
  - [ ] Firefox
  - [ ] Safari (if applicable)
  - [ ] Edge

- [ ] **Responsive Design**
  - [ ] Desktop viewports
  - [ ] Tablet viewports
  - [ ] Mobile viewports

- [ ] **Authentication & Authorization**
  - [ ] Public/unauthenticated flows
  - [ ] Authenticated user flows
  - [ ] Role-based access (admin, user, etc.)
  - [ ] Permission boundaries

### What NOT to Test

- [ ] Confirm you're NOT testing:
  - [ ] Unit-level logic (use unit tests)
  - [ ] API contracts (use integration tests)
  - [ ] Every edge case (too slow)
  - [ ] Internal implementation details
  - [ ] Third-party library functionality

## Setup Phase

### Tool Selection

- [ ] Choose testing framework
  - [ ] Playwright (multi-browser, free parallel)
  - [ ] Cypress (developer UX, component testing)

- [ ] Install and configure
  - [ ] Framework installed
  - [ ] Configuration file created
  - [ ] TypeScript support enabled (if applicable)
  - [ ] CI/CD integration planned

### Project Structure

- [ ] Organize test files
  - [ ] `e2e/` or `cypress/e2e/` directory created
  - [ ] Test files named descriptively (*.spec.ts, *.cy.ts)
  - [ ] Page Objects directory created (if using POM)
  - [ ] Fixtures directory for test data
  - [ ] Support/helper files organized

### Environment Setup

- [ ] Configure test environment
  - [ ] Base URL configured
  - [ ] Environment variables defined
  - [ ] Test database/backend setup
  - [ ] Mock data strategy defined

## Writing Tests

### Test Structure

- [ ] Follow AAA pattern
  - [ ] **Arrange**: Setup test data and state
  - [ ] **Act**: Perform user actions
  - [ ] **Assert**: Verify expected outcomes

- [ ] Test isolation
  - [ ] Each test runs independently
  - [ ] No shared state between tests
  - [ ] Proper setup in beforeEach/before
  - [ ] Cleanup in afterEach/after

### Selectors

- [ ] Use stable selectors
  - [ ] `data-testid` or `data-cy` attributes added
  - [ ] Semantic selectors (role, label, text) used
  - [ ] Avoid CSS classes and nth-child
  - [ ] Avoid XPath when possible

### Waiting Strategies

- [ ] Implement proper waits
  - [ ] No fixed timeouts (waitForTimeout, wait(3000))
  - [ ] Use condition-based waits
  - [ ] Wait for network requests to complete
  - [ ] Wait for elements to be visible/enabled
  - [ ] Handle loading states

### Page Objects (if using)

- [ ] Create Page Objects
  - [ ] One Page Object per page/component
  - [ ] Encapsulate selectors
  - [ ] Provide action methods
  - [ ] Include assertion helpers
  - [ ] Follow naming conventions

### Network Handling

- [ ] Mock external dependencies
  - [ ] Intercept API calls
  - [ ] Mock third-party services
  - [ ] Provide stable test data
  - [ ] Handle authentication tokens

### Assertions

- [ ] Meaningful assertions
  - [ ] Assert on user-visible behavior
  - [ ] Check URLs for navigation
  - [ ] Verify UI elements are visible
  - [ ] Validate form submissions
  - [ ] Check error messages

## Test Quality

### Reliability

- [ ] Tests are deterministic
  - [ ] No flaky tests
  - [ ] Consistent pass/fail results
  - [ ] Run successfully 10+ times locally

- [ ] Handle timing issues
  - [ ] Auto-waiting enabled
  - [ ] Proper wait strategies
  - [ ] Animations disabled or handled
  - [ ] Network delays accounted for

### Maintainability

- [ ] Tests are readable
  - [ ] Descriptive test names
  - [ ] Clear test structure
  - [ ] Comments for complex logic
  - [ ] Consistent code style

- [ ] Tests are maintainable
  - [ ] Page Objects reduce duplication
  - [ ] Helper functions for common tasks
  - [ ] Configuration centralized
  - [ ] Fixtures for test data

### Performance

- [ ] Tests run efficiently
  - [ ] Parallel execution enabled
  - [ ] Unnecessary waits removed
  - [ ] Test data reused when possible
  - [ ] Heavy tests tagged/grouped

## CI/CD Integration

### Configuration

- [ ] CI/CD pipeline setup
  - [ ] Test command in package.json
  - [ ] CI configuration file created
  - [ ] Environment variables configured
  - [ ] Test artifacts saved (screenshots, videos)

### Execution

- [ ] Tests run on CI
  - [ ] Triggered on pull requests
  - [ ] Run on main branch commits
  - [ ] Parallel execution configured
  - [ ] Retry strategy configured

### Reporting

- [ ] Test results visible
  - [ ] HTML report generated
  - [ ] JUnit/XML report for CI
  - [ ] Screenshots on failure
  - [ ] Videos on failure
  - [ ] Test duration tracked

## Maintenance

### Regular Review

- [ ] Review test suite monthly
  - [ ] Remove obsolete tests
  - [ ] Update for feature changes
  - [ ] Refactor duplicated code
  - [ ] Improve flaky tests

### Monitoring

- [ ] Track test health
  - [ ] Monitor flakiness rate
  - [ ] Track test duration
  - [ ] Review failure patterns
  - [ ] Update as application evolves

### Documentation

- [ ] Document testing approach
  - [ ] README with setup instructions
  - [ ] How to run tests locally
  - [ ] How to debug failures
  - [ ] Page Object conventions
  - [ ] Test data strategy

## Best Practices Checklist

### General

- [ ] Test user behavior, not implementation
- [ ] Keep tests independent and isolated
- [ ] Use data-testid for stable selectors
- [ ] Mock external dependencies
- [ ] Clean up test data after each test

### Playwright Specific

- [ ] Use auto-waiting features
- [ ] Enable fullyParallel execution
- [ ] Configure trace on first retry
- [ ] Use test.step() for better reporting
- [ ] Leverage built-in fixtures

### Cypress Specific

- [ ] Use cy.intercept() for network control
- [ ] Create custom commands for common actions
- [ ] Use cy.session() for authentication
- [ ] Leverage time-travel debugging
- [ ] Use aliases with .as()

## Common Pitfalls to Avoid

- [ ] ❌ NOT using fixed timeouts (wait(3000))
- [ ] ❌ NOT selecting by CSS classes
- [ ] ❌ NOT sharing state between tests
- [ ] ❌ NOT testing implementation details
- [ ] ❌ NOT over-testing with E2E (use unit tests)
- [ ] ❌ NOT having coupled tests (test order matters)
- [ ] ❌ NOT using brittle selectors
- [ ] ❌ NOT forgetting to clean up test data

## Accessibility Testing

- [ ] Add accessibility checks
  - [ ] Install axe-core integration
  - [ ] Add a11y tests for key pages
  - [ ] Test keyboard navigation
  - [ ] Verify screen reader labels
  - [ ] Check color contrast

## Visual Regression

- [ ] Setup visual testing (optional)
  - [ ] Configure screenshot comparison
  - [ ] Baseline screenshots captured
  - [ ] Threshold configured appropriately
  - [ ] Visual tests in CI

## Security Testing

- [ ] Basic security checks
  - [ ] Test authentication boundaries
  - [ ] Verify authorization rules
  - [ ] Check for XSS vulnerabilities
  - [ ] Test CSRF protection
  - [ ] Validate input sanitization

## Pre-Deployment Checklist

Before deploying test suite:

- [ ] All tests pass locally
- [ ] Tests pass on CI
- [ ] No flaky tests in last 10 runs
- [ ] Code review completed
- [ ] Documentation updated
- [ ] Team trained on new tests
- [ ] Monitoring/alerts configured

## Post-Deployment Monitoring

After deployment:

- [ ] Monitor test pass rate
- [ ] Check test execution time
- [ ] Review failure patterns
- [ ] Collect team feedback
- [ ] Iterate and improve
