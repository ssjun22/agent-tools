---
title: Mock vs Real Dependencies
impact: MEDIUM
impactDescription: balances test speed and reliability
tags: testing, mocking, integration
---

## Mock vs Real Dependencies

외부 의존성(API, DB)만 mock하고, 내부 로직은 실제로 테스트합니다.

**Incorrect (모든 것을 mock):**

```typescript
test('processOrder', async () => {
  const mockValidator = jest.fn().mockReturnValue(true)
  const mockCalculator = jest.fn().mockReturnValue(100)
  const mockSaver = jest.fn().mockResolvedValue({ id: 1 })

  const service = new OrderService(mockValidator, mockCalculator, mockSaver)
  await service.processOrder({})

  expect(mockValidator).toHaveBeenCalled()
  expect(mockCalculator).toHaveBeenCalled()
  expect(mockSaver).toHaveBeenCalled()
  // 실제 로직은 테스트되지 않음
})
```

**Correct (외부 의존성만 mock):**

```typescript
test('processOrder calculates total and saves to database', async () => {
  // Arrange
  const mockDb = {
    save: jest.fn().mockResolvedValue({ id: 1 })
  }

  const service = new OrderService(mockDb)
  const order = {
    items: [
      { price: 10, quantity: 2 },
      { price: 20, quantity: 1 }
    ]
  }

  // Act
  const result = await service.processOrder(order)

  // Assert
  // 실제 계산 로직 검증
  expect(result.total).toBe(40)
  expect(result.tax).toBe(4)
  expect(result.grandTotal).toBe(44)

  // DB 호출만 mock
  expect(mockDb.save).toHaveBeenCalledWith(
    expect.objectContaining({ grandTotal: 44 })
  )
})
```

**Note:** 너무 많은 mock은 테스트의 가치를 떨어뜨립니다.
