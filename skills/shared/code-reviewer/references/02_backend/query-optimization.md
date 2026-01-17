---
title: Database Query Optimization
impact: HIGH
impactDescription: eliminates N+1 queries and improves performance
tags: database, performance, sqlalchemy, optimization
---

## Database Query Optimization

N+1 쿼리 문제를 방지하고 필요한 데이터를 한 번에 가져옵니다.

**Incorrect (N+1 쿼리 문제):**

```python
from fastapi import FastAPI
from sqlalchemy.orm import Session

app = FastAPI()

@app.get("/posts")
async def get_posts_with_authors(db: Session):
    posts = db.query(Post).all()  # 1번 쿼리

    result = []
    for post in posts:
        # 각 post마다 1번씩 쿼리 (N번)
        author = db.query(User).filter(User.id == post.author_id).first()
        result.append({
            "title": post.title,
            "author_name": author.name
        })

    return result  # 총 1 + N번의 쿼리
```

**Correct (Join 또는 eager loading 사용):**

```python
from fastapi import FastAPI
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

app = FastAPI()

@app.get("/posts")
async def get_posts_with_authors(db: Session):
    # selectinload로 관련 데이터를 한 번에 가져옴
    stmt = select(Post).options(selectinload(Post.author))
    result = await db.execute(stmt)
    posts = result.scalars().all()

    return [
        {
            "title": post.title,
            "author_name": post.author.name
        }
        for post in posts
    ]  # 단 2번의 쿼리 (posts 1번, authors 1번)

# 또는 JOIN 사용
@app.get("/posts/with-join")
async def get_posts_with_join(db: Session):
    stmt = (
        select(Post.title, User.name)
        .join(User, Post.author_id == User.id)
    )
    result = await db.execute(stmt)
    return [
        {"title": title, "author_name": name}
        for title, name in result
    ]  # 단 1번의 JOIN 쿼리
```

**Note:** SQLAlchemy의 `selectinload()`, `joinedload()` 등을 활용하면 N+1 문제를 쉽게 해결할 수 있습니다.
