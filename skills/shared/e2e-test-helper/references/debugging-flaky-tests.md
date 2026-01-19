# Debugging Failing Tests

## Playwright Debugging

```typescript
// 1. Run in headed mode
npx playwright test --headed

// 2. Run in debug mode
npx playwright test --debug

// 3. Use trace viewer
await page.screenshot({ path: 'screenshot.png' });
await page.video()?.saveAs('video.webm');

// 4. Add test.step for better reporting
test('checkout flow', async ({ page }) => {
    await test.step('Add item to cart', async () => {
        await page.goto('/products');
        await page.getByRole('button', { name: 'Add to Cart' }).click();
    });

    await test.step('Proceed to checkout', async () => {
        await page.goto('/cart');
        await page.getByRole('button', { name: 'Checkout' }).click();
    });
});

// 5. Inspect page state
await page.pause();  // Pauses execution, opens inspector
```

## Common Pitfalls

- **Flaky Tests**: Use proper waits, not fixed timeouts
- **Slow Tests**: Mock external APIs, use parallel execution
- **Over-Testing**: Don't test every edge case with E2E
- **Coupled Tests**: Tests should not depend on each other
- **Poor Selectors**: Avoid CSS classes and nth-child
- **No Cleanup**: Clean up test data after each test
- **Testing Implementation**: Test user behavior, not internals
