---
title: Meaningful Naming
impact: MEDIUM
impactDescription: improves code readability and understanding
tags: clean-code, naming, readability
---

## Meaningful Naming

변수, 함수, 클래스 이름은 의도를 명확히 드러내야 합니다.

**Incorrect (모호하고 축약된 이름):**

```typescript
function calc(d: number): number {
  const t = d * 24 * 60 * 60
  return t
}

const u = getUserData()
const tmp = processData(u)
const res = tmp.filter(x => x.s === 'active')
```

**Correct (명확하고 의도를 드러내는 이름):**

```typescript
function convertDaysToSeconds(days: number): number {
  const hoursPerDay = 24
  const minutesPerHour = 60
  const secondsPerMinute = 60

  return days * hoursPerDay * minutesPerHour * secondsPerMinute
}

const users = getUserData()
const processedUsers = processData(users)
const activeUsers = processedUsers.filter(user => user.status === 'active')
```

**Note:** 코드는 작성하는 시간보다 읽히는 시간이 훨씬 많습니다.
