---
title: Async Test Handling
impact: HIGH
impactDescription: prevents timing issues and flaky tests
tags: testing, async, promises
---

## Async Test Handling

비동기 코드를 테스트할 때는 async/await를 명시적으로 사용합니다.

**Incorrect (setTimeout으로 대기):**

```typescript
test('fetches user data', (done) => {
  fetchUser('123')

  setTimeout(() => {
    const user = getCache('123')
    expect(user.name).toBe('John')
    done()
  }, 1000)  // 임의의 대기 시간
})
```

**Correct (async/await로 명시적 대기):**

```typescript
test('fetches user data', async () => {
  const userPromise = fetchUser('123')

  await expect(userPromise).resolves.toEqual({
    id: '123',
    name: 'John'
  })

  const cached = getCache('123')
  expect(cached.name).toBe('John')
})

test('handles fetch error', async () => {
  mockFetch.mockRejectedValueOnce(new Error('Network error'))

  await expect(fetchUser('123')).rejects.toThrow('Network error')
})
```

**Note:** `async/await`를 사용하면 타이밍 문제가 사라집니다.
