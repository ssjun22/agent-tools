---
title: Avoiding Flaky Tests
impact: HIGH
impactDescription: ensures test reliability and CI stability
tags: testing, flaky, reliability
---

## Avoiding Flaky Tests

랜덤 값이나 시간 의존성을 제거하여 결정론적 테스트를 작성합니다.

**Incorrect (불안정한 테스트):**

```typescript
test('creates order with timestamp', () => {
  const order = createOrder()

  // 실행 타이밍에 따라 실패할 수 있음
  expect(order.createdAt).toBe(new Date())
})

test('generates random ID', () => {
  const id1 = generateId()
  const id2 = generateId()

  // 극히 드물게 중복될 수 있음
  expect(id1).not.toBe(id2)
})

test('waits for async operation', async () => {
  startOperation()
  await sleep(100)  // 충분한 시간인지 불확실

  expect(isComplete()).toBe(true)
})
```

**Correct (결정론적 테스트):**

```typescript
test('creates order with timestamp', () => {
  const mockDate = new Date('2024-01-01')
  jest.useFakeTimers().setSystemTime(mockDate)

  const order = createOrder()

  expect(order.createdAt).toEqual(mockDate)

  jest.useRealTimers()
})

test('generates unique IDs', () => {
  const mockIdGenerator = jest.fn()
    .mockReturnValueOnce('id-1')
    .mockReturnValueOnce('id-2')

  const service = new OrderService(mockIdGenerator)

  const id1 = service.generateId()
  const id2 = service.generateId()

  expect(id1).toBe('id-1')
  expect(id2).toBe('id-2')
  expect(mockIdGenerator).toHaveBeenCalledTimes(2)
})

test('waits for async operation completion', async () => {
  const operation = startOperation()

  // 명시적으로 완료 대기
  await operation.complete()

  expect(operation.isComplete()).toBe(true)
})
```

**Note:** 시간이나 랜덤 값은 항상 mock하거나 주입 가능하도록 설계합니다.
