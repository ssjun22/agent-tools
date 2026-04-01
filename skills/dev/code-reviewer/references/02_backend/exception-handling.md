---
title: Proper Exception Handling
impact: HIGH
impactDescription: provides clear error messages with correct status codes
tags: fastapi, error-handling, http, api-design
---

## Proper Exception Handling

적절한 HTTP 상태 코드와 함께 HTTPException을 사용합니다.

**Incorrect (일반 Exception raise):**

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: str, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise Exception("User not found")  # 500 에러로 처리됨
    return user

@app.post("/users")
async def create_user(data: dict):
    if not data.get("email"):
        raise ValueError("Email is required")  # 500 에러
    return {"email": data["email"]}
```

**Correct (HTTPException with status codes):**

```python
from fastapi import FastAPI, HTTPException, status
from typing import Optional

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: str, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return user

@app.delete("/users/{user_id}")
async def delete_user(user_id: str, current_user: User):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can delete users"
        )
    # 삭제 로직
    return {"message": "User deleted"}

@app.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    # 생성 로직
    return new_user
```

**Note:** 적절한 HTTP 상태 코드는 API 클라이언트가 에러를 올바르게 처리하도록 도와줍니다.
