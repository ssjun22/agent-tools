---
title: Test Data Builders
impact: LOW
impactDescription: reduces duplication in test setup
tags: testing, builders, fixtures
---

## Test Data Builders

반복되는 테스트 데이터 생성을 Builder 패턴으로 추상화합니다.

**Incorrect (중복된 데이터 생성):**

```typescript
test('validates adult user', () => {
  const user = {
    id: '1',
    name: 'John',
    email: 'john@test.com',
    age: 25,
    address: '123 St',
    phone: '555-0000',
    verified: true
  }
  expect(isAdult(user)).toBe(true)
})

test('calculates discount for premium user', () => {
  const user = {
    id: '2',
    name: 'Jane',
    email: 'jane@test.com',
    age: 30,
    address: '456 Ave',
    phone: '555-1111',
    verified: true,
    premium: true
  }
  expect(calculateDiscount(user)).toBe(0.2)
})
```

**Correct (Test Data Builder 활용):**

```typescript
class UserBuilder {
  private user: Partial<User> = {
    id: '1',
    name: 'Test User',
    email: 'test@test.com',
    age: 25,
    verified: true
  }

  withAge(age: number) {
    this.user.age = age
    return this
  }

  asPremium() {
    this.user.premium = true
    return this
  }

  withEmail(email: string) {
    this.user.email = email
    return this
  }

  build(): User {
    return this.user as User
  }
}

test('validates adult user', () => {
  const user = new UserBuilder().withAge(25).build()
  expect(isAdult(user)).toBe(true)
})

test('calculates discount for premium user', () => {
  const user = new UserBuilder().asPremium().build()
  expect(calculateDiscount(user)).toBe(0.2)
})

test('rejects underage user', () => {
  const user = new UserBuilder().withAge(15).build()
  expect(isAdult(user)).toBe(false)
})
```

**Note:** Builder는 테스트에서만 사용하고, 프로덕션 코드에서는 사용하지 않습니다.
