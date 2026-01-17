---
title: Magic Numbers and Strings
impact: LOW
impactDescription: improves code clarity and maintainability
tags: clean-code, constants, magic-numbers
---

## Magic Numbers and Strings

하드코딩된 값 대신 명명된 상수를 사용합니다.

**Incorrect (하드코딩된 값):**

```typescript
function calculatePrice(quantity: number, price: number) {
  if (quantity > 100) {
    return quantity * price * 0.9
  } else if (quantity > 50) {
    return quantity * price * 0.95
  }
  return quantity * price
}

function isValidAge(age: number) {
  return age >= 18 && age <= 120
}

if (user.role === 'admin') {
  // ...
}
```

**Correct (명명된 상수):**

```typescript
const BULK_ORDER_THRESHOLD = 100
const WHOLESALE_DISCOUNT = 0.9

const MEDIUM_ORDER_THRESHOLD = 50
const MEDIUM_DISCOUNT = 0.95

function calculatePrice(quantity: number, price: number) {
  if (quantity > BULK_ORDER_THRESHOLD) {
    return quantity * price * WHOLESALE_DISCOUNT
  } else if (quantity > MEDIUM_ORDER_THRESHOLD) {
    return quantity * price * MEDIUM_DISCOUNT
  }
  return quantity * price
}

const MIN_LEGAL_AGE = 18
const MAX_REASONABLE_AGE = 120

function isValidAge(age: number) {
  return age >= MIN_LEGAL_AGE && age <= MAX_REASONABLE_AGE
}

const USER_ROLES = {
  ADMIN: 'admin',
  USER: 'user',
  GUEST: 'guest'
} as const

if (user.role === USER_ROLES.ADMIN) {
  // ...
}
```

**Note:** 상수 이름은 값의 의미를 명확히 전달해야 합니다.
