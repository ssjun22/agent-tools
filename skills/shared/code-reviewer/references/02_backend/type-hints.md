---
title: Type Hints Usage
impact: MEDIUM
impactDescription: enables static type checking and improves code clarity
tags: python, type-hints, mypy, type-safety
---

## Type Hints Usage

모든 함수에 타입 힌트를 추가하여 코드 명확성과 타입 안전성을 높입니다.

**Incorrect (타입 힌트 누락):**

```python
from fastapi import FastAPI

app = FastAPI()

def process_data(data):
    return [item * 2 for item in data]

def get_user_name(user):
    return user.get("name", "Unknown")

@app.post("/calculate")
async def calculate(numbers):
    total = sum(numbers)
    average = total / len(numbers)
    return {"total": total, "average": average}
```

**Correct (타입 힌트 추가):**

```python
from fastapi import FastAPI
from typing import List, Dict, Any, Optional

app = FastAPI()

def process_data(data: List[int]) -> List[int]:
    return [item * 2 for item in data]

def get_user_name(user: Dict[str, Any]) -> str:
    return user.get("name", "Unknown")

@app.post("/calculate")
async def calculate(numbers: List[float]) -> Dict[str, float]:
    total: float = sum(numbers)
    average: float = total / len(numbers)
    return {"total": total, "average": average}

# Optional 사용
def find_user(user_id: str) -> Optional[Dict[str, Any]]:
    # user를 찾지 못할 수 있음
    user = db.get(user_id)
    return user if user else None
```

**Note:** `mypy`로 정적 타입 검사를 수행하면 런타임 전에 타입 에러를 발견할 수 있습니다.
