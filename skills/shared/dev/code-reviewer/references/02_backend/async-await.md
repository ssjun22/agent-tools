---
---
title: Async/Await for I/O Operations
impact: HIGH
impactDescription: prevents blocking and improves concurrency
tags: async, fastapi, performance, concurrency
---

## Async/Await for I/O Operations

I/O 작업(데이터베이스 쿼리, API 호출 등)에는 반드시 async/await를 사용하여 블로킹을 방지합니다.

**Incorrect (블로킹 동기 코드):**

```python
from fastapi import FastAPI
import requests

app = FastAPI()

@app.get("/users/{user_id}")
def get_user(user_id: str):
    # 블로킹 I/O - 다른 요청이 대기해야 함
    response = requests.get(f"https://api.example.com/users/{user_id}")
    return response.json()

@app.get("/posts")
def get_posts():
    db = get_db_connection()
    # 블로킹 쿼리
    result = db.execute("SELECT * FROM posts")
    return result.fetchall()
```

**Correct (async/await로 비블로킹 처리):**

```python
from fastapi import FastAPI
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/users/{user_id}")
        return response.json()

@app.get("/posts")
async def get_posts(db: AsyncSession):
    result = await db.execute("SELECT * FROM posts")
    return result.fetchall()
```

**Note:** FastAPI는 async 엔드포인트에서 더 높은 처리량을 제공합니다.
