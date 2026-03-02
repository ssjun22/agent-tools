# Project Context Rules

이 프로젝트의 컨텍스트는 `.claude/context/` 디렉토리에서 관리됩니다.
`.claude/context/` 디렉토리가 없으면 이 규칙을 무시합니다.

## 파일별 역할

| 파일 | 성격 | 갱신 주체 |
|------|------|-----------|
| `context/project.md` | 정적 — 프로젝트 개요, 도메인, 아키텍처 결정 | `/project-context-manager` |
| `context/status.md` | 동적 — 작업 상태 목록 | `/project-context-manager` |
| `context/drafts/` | 대화 중 감지된 변경사항 임시 저장 | 자동 생성 |

`context/`는 상태 정보, `CLAUDE.md`는 규칙/지침 — 역할을 혼용하지 않습니다.

## Draft 자동 생성

대화 중 다음 중 하나가 감지되면 `.claude/context/drafts/`에 draft 파일을 생성한다:

- 작업 상태가 변경되는 결정 ("이 작업 시작할게", "완료됐어")
- 프로젝트 목적·아키텍처·Breaking Changes에 영향을 주는 결정
- 사용자가 명시적으로 요청 ("draft로 저장해줘")

### 파일명

`YYYY-MM-DD-내용.md` — 내용은 변경사항을 한국어로 짧게 요약

### 포맷

```markdown
---
date: YYYY-MM-DD HH:mm
targets:
  - status.md
status: pending
---

## 변경 내용

{변경될 내용을 구체적으로 작성}

## 맥락

{왜 이 변경이 필요한지 한두 문장}
```
