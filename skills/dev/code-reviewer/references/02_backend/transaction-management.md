---
title: Transaction Management
impact: HIGH
impactDescription: ensures data consistency and handles rollbacks properly
tags: database, transaction, sqlalchemy, data-integrity
---

## Transaction Management

명시적인 트랜잭션 관리로 데이터 일관성을 보장합니다.

**Incorrect (명시적 트랜잭션 없음):**

```python
from fastapi import FastAPI
from sqlalchemy.orm import Session

app = FastAPI()

@app.post("/transfer")
async def transfer_money(from_id: str, to_id: str, amount: float, db: Session):
    from_account = db.query(Account).filter(Account.id == from_id).first()
    to_account = db.query(Account).filter(Account.id == to_id).first()

    # 오류 발생 시 from_account만 업데이트되고 to_account는 안될 수 있음
    from_account.balance -= amount
    db.commit()

    # 여기서 오류 발생하면 데이터 불일치
    to_account.balance += amount
    db.commit()

    return {"message": "Transfer completed"}
```

**Correct (Context manager로 트랜잭션 관리):**

```python
from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

app = FastAPI()

@app.post("/transfer")
async def transfer_money(
    from_id: str,
    to_id: str,
    amount: float,
    db: AsyncSession
):
    try:
        async with db.begin():  # 트랜잭션 시작
            from_account = await db.get(Account, from_id)
            to_account = await db.get(Account, to_id)

            if not from_account or not to_account:
                raise HTTPException(status_code=404, detail="Account not found")

            if from_account.balance < amount:
                raise HTTPException(status_code=400, detail="Insufficient funds")

            # 모두 성공하거나 모두 롤백됨
            from_account.balance -= amount
            to_account.balance += amount

            await db.flush()  # DB에 반영
            # context manager 종료 시 자동 commit

        return {"message": "Transfer completed"}

    except Exception as e:
        # 자동으로 rollback됨
        raise HTTPException(status_code=500, detail=str(e))
```

**Note:** `async with db.begin()`을 사용하면 에러 발생 시 자동으로 rollback됩니다.
