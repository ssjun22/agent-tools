---
status: 🏗 Draft
created: {{DATE}}
updated: {{DATE}}
related_docs: []
tags: [spec]
---

# {{TITLE}}

## Context

> [!info] Why This Feature?
> {{설명: 이 기능이 왜 필요한지, 어떤 문제를 해결하는지 작성}}

### Background
{{배경 정보}}

### Related Documents
{{관련 문서 링크}}

---

## Requirements

### Functional Requirements
- [ ] {{기능적 요구사항 1}}
- [ ] {{기능적 요구사항 2}}
- [ ] {{기능적 요구사항 3}}

### Non-Functional Requirements
- [ ] {{비기능적 요구사항 1}}
- [ ] {{비기능적 요구사항 2}}

### Out of Scope
- {{범위 밖의 항목 1}}
- {{범위 밖의 항목 2}}

---

## Technical Design

### Data Models

#### Entities
{{주요 엔티티 정의}}

```typescript
// Example
interface {{EntityName}} {
  id: string;
  // ... fields
}
```

#### Relationships
{{엔티티 간 관계 설명}}

### API Specification

#### Endpoints
{{API 엔드포인트 목록}}

| Method | Endpoint | Description |
|--------|----------|-------------|
| {{METHOD}} | {{/path}} | {{설명}} |

#### Request/Response Examples
{{요청/응답 예시}}

### Business Logic Flow

```mermaid
sequenceDiagram
    participant User
    participant System
    participant Database

    User->>System: {{액션}}
    System->>Database: {{쿼리}}
    Database-->>System: {{결과}}
    System-->>User: {{응답}}
```

### State Transitions

```mermaid
stateDiagram-v2
    [*] --> {{InitialState}}
    {{InitialState}} --> {{NextState}}: {{조건}}
    {{NextState}} --> [*]
```

### Edge Cases & Error Handling

> [!warning] Edge Cases
> {{예외 상황 1}}
> {{예외 상황 2}}

| Scenario | Expected Behavior |
|----------|-------------------|
| {{시나리오}} | {{예상 동작}} |

---

## Acceptance Criteria

### Success Metrics
- [ ] {{성공 기준 1}}
- [ ] {{성공 기준 2}}
- [ ] {{성공 기준 3}}

### Test Scenarios
1. **{{시나리오 이름}}**
   - Given: {{전제 조건}}
   - When: {{실행 액션}}
   - Then: {{기대 결과}}

---

## Implementation Notes

> [!tip] Developer Notes
> {{구현 시 유의사항}}

### Dependencies
- {{의존성 1}}
- {{의존성 2}}

### Migration Strategy
{{기존 시스템이 있는 경우, 마이그레이션 전략}}

---

## Timeline & Milestones

- [ ] Phase 1: {{단계 설명}}
- [ ] Phase 2: {{단계 설명}}
- [ ] Phase 3: {{단계 설명}}

---

## Review History

| Date | Reviewer | Status | Comments |
|------|----------|--------|----------|
| {{DATE}} | {{NAME}} | Draft | Initial draft |
