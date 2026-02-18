---
---
title: AAA Pattern (Arrange-Act-Assert)
impact: MEDIUM
impactDescription: improves test readability and structure
tags: testing, aaa, structure, readability
---

## AAA Pattern (Arrange-Act-Assert)

테스트는 Arrange, Act, Assert 세 부분으로 명확히 구분합니다.

**Incorrect (구조 없이 섞인 테스트):**

```typescript
test('user creation', async () => {
  const user = await createUser({ name: 'John', email: 'john@test.com' })
  const db = getTestDb()
  expect(user.name).toBe('John')
  const saved = await db.users.findOne({ email: 'john@test.com' })
  expect(saved).toBeDefined()
  expect(user.email).toBe('john@test.com')
})
```

**Correct (명확한 AAA 구조):**

```typescript
test('user creation', async () => {
  // Arrange
  const userData = { name: 'John', email: 'john@test.com' }
  const db = getTestDb()

  // Act
  const user = await createUser(userData)

  // Assert
  expect(user.name).toBe('John')
  expect(user.email).toBe('john@test.com')

  const saved = await db.users.findOne({ email: 'john@test.com' })
  expect(saved).toBeDefined()
  expect(saved.name).toBe('John')
})
```

**Note:** 주석으로 세 부분을 명시하면 테스트 의도가 명확해집니다.
