# Obsidian-Specific Syntax Guide

스펙 문서 작성 시 활용할 Obsidian 특화 문법 가이드입니다.

## 1. Wiki Links (위키링크)

Obsidian의 핵심 기능으로, 문서 간 연결을 생성합니다.

### Basic Link
```markdown
[[Document Name]]
```

### Link with Display Text
```markdown
[[Document Name|Display Text]]
```

### Link to Heading
```markdown
[[Document Name#Heading]]
```

### Link to Block
```markdown
[[Document Name#^block-id]]
```

### Example in Spec Document
```markdown
## Related Documents
- [[API Authentication Spec]]
- [[Database Schema|DB Schema]]
- [[User Flow#Registration Process]]
```

## 2. Callouts (콜아웃)

중요한 정보를 시각적으로 강조하는 블록입니다.

### Available Types

#### Info
```markdown
> [!info] Information Title
> 일반적인 정보나 참고사항
```

#### Warning
```markdown
> [!warning] Warning Title
> 주의해야 할 사항이나 잠재적 문제
```

#### Tip
```markdown
> [!tip] Tip Title
> 유용한 팁이나 모범 사례
```

#### Note
```markdown
> [!note] Note Title
> 추가 설명이나 참고 노트
```

#### Example
```markdown
> [!example] Example Title
> 구체적인 예시나 샘플
```

#### Question
```markdown
> [!question] Question Title
> 미해결 질문이나 논의 필요 사항
```

#### Success
```markdown
> [!success] Success Title
> 완료 사항이나 성공 기준
```

#### Danger
```markdown
> [!danger] Danger Title
> 심각한 경고나 중요한 제약사항
```

### Foldable Callouts
```markdown
> [!info]- Foldable Info (기본 접힘)
> 내용

> [!info]+ Foldable Info (기본 펼침)
> 내용
```

### Example in Spec Document
```markdown
## Edge Cases

> [!warning] Critical Edge Case
> 사용자가 동시에 두 개의 주문을 생성할 경우, 재고 잠금 메커니즘 필요

> [!tip] Implementation Tip
> Redis를 사용한 분산 락 패턴 권장

> [!question] Open Question
> 결제 실패 후 재고 복구 시점은 언제로 할 것인가?
```

## 3. Tags (태그)

문서를 분류하고 검색하기 위한 태그입니다.

### Inline Tags
```markdown
#spec #api #backend #v1
```

### Frontmatter Tags
```yaml
---
tags:
  - spec
  - api
  - backend
  - v1
---
```

### Nested Tags
```markdown
#project/backend/api
#status/draft
#priority/high
```

### Example in Spec Document
```yaml
---
tags:
  - spec
  - feature/authentication
  - project/ecommerce
  - status/draft
  - priority/critical
---
```

## 4. YAML Frontmatter

문서 메타데이터를 구조화하여 관리합니다.

### Standard Spec Metadata
```yaml
---
status: 🏗 Draft | ✅ Confirmed | 🚀 Implemented
created: 2026-01-23
updated: 2026-01-23
author: "Your Name"
reviewers:
  - "Reviewer 1"
  - "Reviewer 2"
related_docs:
  - "[[Related Spec 1]]"
  - "[[Related Spec 2]]"
tags:
  - spec
  - feature-name
priority: high | medium | low
version: "1.0.0"
---
```

### Custom Fields
```yaml
---
api_version: "v2"
estimated_effort: "3 weeks"
dependencies:
  - "Authentication Service"
  - "Payment Gateway"
blocking_issues:
  - "[[Issue-123]]"
---
```

## 5. Embedded Content (임베드)

다른 문서나 이미지를 현재 문서에 포함합니다.

### Embed Document
```markdown
![[Document Name]]
```

### Embed Specific Section
```markdown
![[Document Name#Section]]
```

### Embed Image
```markdown
![[image.png]]
![[image.png|300]]  # width 지정
```

### Example in Spec Document
```markdown
## API Schema

다음은 공통 인증 스키마입니다:
![[Common Authentication Schema#JWT Structure]]

## UI Mockup
![[login-mockup.png|600]]
```

## 6. Tables (테이블)

구조화된 정보를 표현합니다.

### Basic Table
```markdown
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes | Unique identifier |
| email | string | Yes | User email |
| name | string | No | Display name |
```

### Alignment
```markdown
| Left | Center | Right |
|:-----|:------:|------:|
| L1 | C1 | R1 |
| L2 | C2 | R2 |
```

## 7. Task Lists (체크리스트)

요구사항이나 완료 항목을 추적합니다.

### Basic Tasks
```markdown
- [ ] Uncompleted task
- [x] Completed task
```

### Nested Tasks
```markdown
- [ ] Phase 1: Design
  - [x] Create mockup
  - [x] Define API schema
  - [ ] Review with team
- [ ] Phase 2: Implementation
  - [ ] Backend API
  - [ ] Frontend integration
```

### Example in Spec Document
```markdown
## Requirements

### Functional Requirements
- [x] User can create account
- [x] User can login with email/password
- [ ] User can login with OAuth
- [ ] User can reset password
  - [ ] Email verification
  - [ ] Token expiration (24h)
  - [ ] Rate limiting
```

## 8. Code Blocks

코드 예시나 스키마를 표현합니다.

### With Syntax Highlighting
````markdown
```typescript
interface User {
  id: string;
  email: string;
  name?: string;
}
```
````

### With Title
````markdown
```typescript title="user.interface.ts"
interface User {
  id: string;
  email: string;
}
```
````

## 9. Dataview (선택사항)

Dataview 플러그인 사용 시 동적 쿼리가 가능합니다.

### List All Draft Specs
````markdown
```dataview
LIST
FROM #spec
WHERE status = "🏗 Draft"
SORT created DESC
```
````

### Table of Related Specs
````markdown
```dataview
TABLE status, priority, updated
FROM [[]]
WHERE contains(tags, "spec")
SORT priority ASC, updated DESC
```
````

## Best Practices for Spec Documents

### 1. Consistent Frontmatter
모든 스펙 문서에 동일한 메타데이터 구조 사용:
```yaml
---
status: 🏗 Draft
created: {{DATE}}
updated: {{DATE}}
related_docs: []
tags: [spec]
---
```

### 2. Use Callouts for Important Information
```markdown
> [!warning] Breaking Change
> 이 변경은 기존 API v1과 호환되지 않습니다.

> [!tip] Migration Path
> [[Migration Guide v1 to v2]] 참조
```

### 3. Link Related Documents
```markdown
## Context

이 스펙은 다음 문서들과 연관됩니다:
- [[User Authentication Flow]] - 인증 흐름 전체 개요
- [[Database Schema]] - 관련 데이터 모델
- [[API Versioning Strategy]] - API 버전 정책
```

### 4. Use Tables for Structured Data
```markdown
## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /api/v1/users | ❌ | Create user |
| GET | /api/v1/users/:id | ✅ | Get user details |
| PUT | /api/v1/users/:id | ✅ | Update user |
| DELETE | /api/v1/users/:id | ✅ | Delete user |
```

### 5. Track Progress with Tasks
```markdown
## Implementation Checklist

- [x] Backend
  - [x] Database migration
  - [x] API endpoints
  - [x] Unit tests
- [ ] Frontend
  - [x] UI components
  - [ ] Integration tests
  - [ ] E2E tests
- [ ] Documentation
  - [ ] API docs
  - [ ] User guide
```
