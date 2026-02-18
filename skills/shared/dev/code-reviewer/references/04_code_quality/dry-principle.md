---
title: DRY (Don't Repeat Yourself)
impact: HIGH
impactDescription: reduces code duplication and maintenance cost
tags: clean-code, dry, refactoring
---

## DRY (Don't Repeat Yourself)

중복된 코드를 재사용 가능한 추상화로 대체합니다.

**Incorrect (중복된 코드):**

```typescript
function getUserProfile(userId: string) {
  const user = await fetch(`/api/users/${userId}`)
  if (!user.ok) {
    throw new Error('Failed to fetch user')
  }
  return await user.json()
}

function getPostData(postId: string) {
  const post = await fetch(`/api/posts/${postId}`)
  if (!post.ok) {
    throw new Error('Failed to fetch post')
  }
  return await post.json()
}

function getCommentData(commentId: string) {
  const comment = await fetch(`/api/comments/${commentId}`)
  if (!comment.ok) {
    throw new Error('Failed to fetch comment')
  }
  return await comment.json()
}
```

**Correct (재사용 가능한 추상화):**

```typescript
async function fetchResource<T>(endpoint: string): Promise<T> {
  const response = await fetch(endpoint)

  if (!response.ok) {
    throw new Error(`Failed to fetch ${endpoint}`)
  }

  return await response.json()
}

function getUserProfile(userId: string) {
  return fetchResource<User>(`/api/users/${userId}`)
}

function getPostData(postId: string) {
  return fetchResource<Post>(`/api/posts/${postId}`)
}

function getCommentData(commentId: string) {
  return fetchResource<Comment>(`/api/comments/${commentId}`)
}
```

**Note:** 중복을 제거하되, 우연한 중복(accidental duplication)과 진짜 중복을 구분해야 합니다.
