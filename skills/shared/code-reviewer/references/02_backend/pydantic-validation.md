---
title: Pydantic Model Validation
impact: HIGH
impactDescription: automatic validation and type checking
tags: pydantic, validation, type-safety, fastapi
---

## Pydantic Model Validation

Pydantic BaseModel을 사용하여 자동 검증 및 타입 체킹을 수행합니다.

**Incorrect (수동 입력 검증):**

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.post("/users")
async def create_user(data: dict):
    if "email" not in data:
        raise HTTPException(status_code=400, detail="Email is required")
    if not isinstance(data["email"], str):
        raise HTTPException(status_code=400, detail="Email must be a string")
    if "@" not in data["email"]:
        raise HTTPException(status_code=400, detail="Invalid email format")

    if "age" in data:
        if not isinstance(data["age"], int):
            raise HTTPException(status_code=400, detail="Age must be an integer")
        if data["age"] < 0:
            raise HTTPException(status_code=400, detail="Age must be positive")

    # 검증 후 사용
    return {"email": data["email"], "age": data.get("age")}
```

**Correct (Pydantic BaseModel 활용):**

```python
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, Field

app = FastAPI()

class UserCreate(BaseModel):
    email: EmailStr
    age: int | None = Field(None, ge=0, description="User age must be non-negative")
    name: str = Field(..., min_length=1, max_length=100)

@app.post("/users")
async def create_user(user: UserCreate):
    # 자동으로 검증됨
    return user.model_dump()
```

**Note:** Pydantic은 검증 실패 시 자동으로 422 에러를 반환하며, 상세한 에러 메시지를 제공합니다.
