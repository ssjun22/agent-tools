# Handoff Index

마지막 업데이트: {YYYY-MM-DD HH:MM}

이 파일은 모든 handoff 파일의 중앙 인덱스입니다. 새로운 handoff 파일을 생성할 때 이 테이블에 추가하세요.

## Active Handoffs

현재 진행 중인 작업들:

| 파일명 | 작업명 | 날짜 | 상태 | 설명 |
|--------|--------|------|------|------|
| *항목이 추가됩니다* | | | In Progress | |

## Completed Handoffs

완료된 작업들:

| 파일명 | 작업명 | 날짜 | 상태 | 설명 |
|--------|--------|------|------|------|
| *항목이 추가됩니다* | | | Completed | |

## Blocked Handoffs

블로커로 인해 중단된 작업들:

| 파일명 | 작업명 | 날짜 | 상태 | 설명 |
|--------|--------|------|------|------|
| *항목이 추가됩니다* | | | Blocked | |

---

## 사용 가이드

### 새 Handoff 추가

1. handoff 파일 생성: `{YYYY-MM-DD}-{task-name}.md`
2. 파일 작성 (templates/handoff-template.md 참조)
3. 이 index.md의 적절한 섹션에 행 추가
4. Git에 커밋

### 상태 변경

handoff의 상태가 변경되면:
1. 해당 handoff 파일의 Status 업데이트
2. 이 index.md에서 해당 행을 적절한 섹션으로 이동

### 예시

```markdown
| 파일명 | 작업명 | 날짜 | 상태 | 설명 |
|--------|--------|------|------|------|
| 2024-01-30-auth-refactor.md | Auth Refactor | 2024-01-30 | In Progress | JWT authentication implementation |
```
