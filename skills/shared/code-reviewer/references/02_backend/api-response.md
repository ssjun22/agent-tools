---
title: API Response Structure
impact: MEDIUM
impactDescription: provides consistent API responses
tags: api-design, fastapi, response, consistency
---

## API Response Structure

일관된 응답 구조로 API 사용성을 높입니다.

**Incorrect (일관성 없는 응답 구조):**

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    user = find_user(user_id)
    if user:
        return user  # 성공 시 user 객체 반환
    return {"error": "Not found"}  # 실패 시 다른 구조

@app.get("/posts")
async def get_posts():
    posts = fetch_posts()
    return posts  # 리스트 직접 반환

@app.post("/users")
async def create_user(data: dict):
    new_user = create(data)
    return {"success": True, "user": new_user}  # 또 다른 구조
```

**Correct (표준화된 응답 모델):**

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, List

app = FastAPI()

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None

class User(BaseModel):
    id: str
    name: str
    email: str

@app.get("/users/{user_id}", response_model=APIResponse[User])
async def get_user(user_id: str):
    user = find_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return APIResponse(
        success=True,
        data=user,
        message="User retrieved successfully"
    )

@app.get("/posts", response_model=APIResponse[List[Post]])
async def get_posts():
    posts = fetch_posts()
    return APIResponse(
        success=True,
        data=posts,
        message=f"Retrieved {len(posts)} posts"
    )

@app.post("/users", response_model=APIResponse[User], status_code=201)
async def create_user(user_data: UserCreate):
    new_user = create(user_data)
    return APIResponse(
        success=True,
        data=new_user,
        message="User created successfully"
    )
```

**Note:** Generic을 사용하면 타입 안전성을 유지하면서 일관된 응답 구조를 만들 수 있습니다.
