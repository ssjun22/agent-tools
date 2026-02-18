# Handoff Rules

AI 에이전트가 세션 간 컨텍스트를 유지하기 위한 handoff 관리 규칙.

## Automation via Hooks

handoff는 Claude Code hooks를 통해 자동으로 관리됩니다:

- **sessionStart**: 세션 시작 → 최신 handoff 자동 로드
- **sessionEnd**: 세션 종료 → handoff 자동 업데이트
- **preCompact**: 컨텍스트 압축 전 → handoff 자동 업데이트

## Reading Handoffs (Session Start)

**Trigger**: session-start hook 실행 시

**Process**:
1. `.claude/handoffs/index.md` 확인
2. 가장 최근 handoff 파일 찾기 (날짜순, Status "In Progress" 우선)
3. handoff 파일 읽기
4. 사용자에게 3-5줄 요약 제공

**Summary Format**:
```
[Handoff 로드됨]

이전 세션 컨텍스트:
- 작업: {Task Name}
- 진행률: {Progress}
- 마지막 작업: {Last completed}
- 다음 단계: {Next steps}

어떤 작업을 이어가시겠습니까?
```

**Edge Cases**:
- handoff 없음 → "새 작업 시작"
- 여러 In Progress → 사용자에게 선택 요청

## Writing Handoffs

**Triggers**:
- 컨텍스트 압축 전 (preCompact hook) - 주요 트리거
- 세션 종료 시 (sessionEnd hook)
- 주요 작업 완료 시 (AI 판단)

**File Naming**: `{YYYY-MM-DD}-{task-name}.md`

**Examples**:
- `2024-01-30-auth-refactor.md`
- `2024-02-01-api-optimization.md`

**Content Structure**:

```markdown
# Handoff: {Task Name}

**Date**: YYYY-MM-DD
**Session**: N
**Status**: In Progress | Completed | Blocked

## Context
{1-3 sentences: 왜 이 작업을 하는가?}

## What Was Done
- Item 1
- Item 2

## Current Status
{진행률 및 현재 상태}

## Issues/Blockers
{알려진 문제 (없으면 생략)}

## Next Steps
1. Step 1
2. Step 2

## Decisions Made
- Decision 1: {이유}

## Notes
{추가 고려사항 (선택적)}
```

**Key Principles**:
- **간결함**: ~2000 토큰 이하
- **핵심 집중**: 코드 변경 X, 결정 사항과 컨텍스트 O
- **미래 지향**: 다음 세션을 위한 정보

## Index Management

**File**: `.claude/handoffs/index.md`

**Format**:
```markdown
# Handoff Index

| 파일명 | 작업명 | 날짜 | 상태 | 설명 |
|--------|--------|------|------|------|
| 2024-02-01-api-optimization.md | API Optimization | 2024-02-01 | In Progress | REST API performance |
| 2024-01-30-auth-refactor.md | Auth Refactor | 2024-01-30 | Completed | JWT implementation |
```

**Update Rules**:
- 새 handoff 생성 시 → index에 추가 (최신이 상단)
- 상태 변경 시 → index의 Status 컬럼 업데이트

## What to Include

✅ **Include**:
- 중요한 결정 사항과 이유
- 알려진 문제/블로커
- 다음 작업 단계
- 코드에 없는 컨텍스트

❌ **Exclude**:
- Git commit 메시지의 세부 코드 변경
- 파일명/라인 번호 (빠르게 outdated)
- 당연한 정보 ("테스트를 실행했다")
- 개인적 감정/의견

## Quick Reference

### Session Start
```
AI Action:
1. Read .claude/handoffs/index.md
2. Find latest handoff (In Progress 우선)
3. Summarize to user (3-5 lines)
```

### Session End / PreCompact
```
AI Action:
1. Determine handoff file (existing or new)
2. Update content (What Was Done, Status, Next Steps)
3. Update index.md
4. Keep under ~2000 tokens
```

### File Structure
```
.claude/handoffs/
├── index.md
├── 2024-01-30-auth-refactor.md
└── 2024-01-31-api-optimization.md
```

---

**Note**: hooks가 자동으로 실행되므로, AI는 hook의 지시에 따라 handoff를 읽고 쓰기만 하면 됩니다.
