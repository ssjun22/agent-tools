---
title: Test Isolation
impact: HIGH
impactDescription: prevents test interference and flakiness
tags: testing, isolation, independence
---

## Test Isolation

각 테스트는 독립적으로 실행 가능해야 하며, 다른 테스트의 상태에 영향을 받지 않아야 합니다.

**Incorrect (테스트 간 상태 공유):**

```typescript
describe('UserService', () => {
  let users: User[] = []

  test('creates user', () => {
    const user = { id: 1, name: 'John' }
    users.push(user)
    expect(users).toHaveLength(1)
  })

  test('finds user', () => {
    // 이전 테스트에 의존
    const found = users.find(u => u.id === 1)
    expect(found).toBeDefined()
  })

  test('deletes user', () => {
    // 이전 테스트들에 의존
    users = users.filter(u => u.id !== 1)
    expect(users).toHaveLength(0)
  })
})
```

**Correct (독립적인 테스트):**

```typescript
describe('UserService', () => {
  let userService: UserService
  let db: TestDatabase

  beforeEach(async () => {
    db = await createTestDatabase()
    userService = new UserService(db)
  })

  afterEach(async () => {
    await db.cleanup()
  })

  test('creates user', async () => {
    const user = await userService.create({ name: 'John' })
    expect(user.name).toBe('John')

    const found = await userService.findById(user.id)
    expect(found).toBeDefined()
  })

  test('finds user by id', async () => {
    const created = await userService.create({ name: 'Jane' })

    const found = await userService.findById(created.id)
    expect(found?.name).toBe('Jane')
  })

  test('deletes user', async () => {
    const user = await userService.create({ name: 'Bob' })

    await userService.delete(user.id)

    const found = await userService.findById(user.id)
    expect(found).toBeNull()
  })
})
```

**Note:** `beforeEach`와 `afterEach`로 각 테스트의 환경을 초기화합니다.
