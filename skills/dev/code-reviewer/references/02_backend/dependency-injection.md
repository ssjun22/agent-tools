---
title: Dependency Injection Pattern
impact: MEDIUM
impactDescription: improves testability and maintainability
tags: fastapi, dependency-injection, testing, architecture
---

## Dependency Injection Pattern

FastAPI의 `Depends()`를 사용하여 의존성을 주입하고 테스트 가능성을 높입니다.

**Incorrect (함수 내부에서 직접 의존성 생성):**

```python
from fastapi import FastAPI
from database import SessionLocal

app = FastAPI()

@app.get("/users")
async def get_users():
    db = SessionLocal()  # 의존성을 직접 생성
    try:
        users = db.query(User).all()
        return users
    finally:
        db.close()

@app.get("/posts")
async def get_posts():
    db = SessionLocal()  # 중복된 코드
    try:
        posts = db.query(Post).all()
        return posts
    finally:
        db.close()
```

**Correct (Depends()로 의존성 주입):**

```python
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db

app = FastAPI()

async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

@app.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()

@app.get("/posts")
async def get_posts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post))
    return result.scalars().all()

# 테스트에서 쉽게 mock 가능
@app.get("/test")
async def test_endpoint(db: AsyncSession = Depends(get_db)):
    # db는 테스트 시 mock으로 교체 가능
    return {"db": str(db)}
```

**Note:** Dependency Injection은 단위 테스트 작성을 크게 단순화합니다.
