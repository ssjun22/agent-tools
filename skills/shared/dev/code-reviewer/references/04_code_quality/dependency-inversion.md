---
title: Dependency Inversion
impact: MEDIUM
impactDescription: reduces coupling and improves testability
tags: solid, dip, dependency-injection
---

## Dependency Inversion

고수준 모듈은 저수준 모듈에 의존하지 않고, 둘 다 추상화에 의존해야 합니다.

**Incorrect (구체 클래스에 직접 의존):**

```typescript
class MySQLDatabase {
  query(sql: string) {
    // MySQL specific implementation
  }
}

class UserService {
  private db = new MySQLDatabase()  // 직접 의존

  getUser(id: string) {
    return this.db.query(`SELECT * FROM users WHERE id = ${id}`)
  }
}
```

**Correct (추상화에 의존):**

```typescript
interface Database {
  query(sql: string): Promise<any>
}

class MySQLDatabase implements Database {
  async query(sql: string) {
    // MySQL implementation
  }
}

class PostgreSQLDatabase implements Database {
  async query(sql: string) {
    // PostgreSQL implementation
  }
}

class UserService {
  constructor(private db: Database) {}  // 추상화에 의존

  async getUser(id: string) {
    return await this.db.query(`SELECT * FROM users WHERE id = ?`)
  }
}

// 사용
const userService = new UserService(new MySQLDatabase())
// 또는
const userService = new UserService(new PostgreSQLDatabase())
```

**Note:** 의존성 주입을 통해 테스트가 쉬워지고 유연성이 증가합니다.
