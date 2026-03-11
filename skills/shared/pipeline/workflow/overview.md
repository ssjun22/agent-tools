# Workflow Overview

## 구조도

```
┌─────────────────────────────────────────────────────────┐
│                     /workflow (스킬)                      │
│              체크리스트 관리 + 다음 단계 안내              │
│              CLEAR/BLOCKED 신호 기반 자동 진행            │
└─────────────────────┬───────────────────────────────────┘
                      │
    ┌─────────────────▼─────────────────┐
    │  1. 작업사항 확인 (메인 AI)        │ ── 자동 진행
    │  2. 작업 선택 (사용자)             │ ── 항상 멈춤
    └─────────────────┬─────────────────┘
                      │
    ┌─────────────────▼─────────────────┐
    │  3. @interviewer                     │ ── 항상 멈춤
    │  ┌───────────────────────────┐    │
    │  │ Phase 1: 리서치            │    │
    │  │  docs/context/, openspec/,│    │
    │  │  코드베이스 조사           │    │
    │  ├───────────────────────────┤    │
    │  │ Phase 2: 브리핑 제시       │    │
    │  ├───────────────────────────┤    │
    │  │ Phase 3: /brainstorming   │◄───┼─── Skill 호출
    │  ├───────────────────────────┤    │
    │  │ Phase 4: Devil's Advocate │    │
    │  ├───────────────────────────┤    │
    │  │ Phase 5: 결과 정리         │    │
    │  └───────────────────────────┘    │
    └─────────────────┬─────────────────┘
                      │
    ┌─────────────────▼─────────────────┐
    │  4. @spec-writer                  │ ── 조건부 멈춤
    │     interviewer 결과 → OpenSpec   │
    │     /opsx:new → /opsx:ff 호출     │
    └─────────────────┬─────────────────┘
                      │
    ┌─────────────────▼─────────────────┐
    │  5. @designer (frontend만)          │ ── 조건부 멈춤
    │     /ui-ux-pro-max 호출           │
    │     design-system/MASTER.md 생성  │
    └─────────────────┬─────────────────┘
                      │
    ┌─────────────────▼─────────────────┐
    │  6. @spec-builder                     │ ── 조건부 멈춤
    │     스펙 기반 코드 작성 전담        │
    └─────────────────┬─────────────────┘
                      │
    ┌─────────────────▼─────────────────┐
    │  7. @spec-checker                   │ ── 조건부 멈춤
    │     스펙 대비 매칭 전담             │
    └──────┬──────────────────┬─────────┘
           │                  │
         FAIL               PASS
           │                  │
           ▼                  │
    ┌──────────────┐          │
    │  8. 이슈 수정 │ ── 항상 멈춤
    │  메인 대화    │
    │  또는         │
    │  @spec-builder   │
    └──────┬───────┘
           │
           └──► 7번 재실행
                              │
    ┌─────────────────────────▼─────────┐
    │  9. @code-reviewer                   │ ── 조건부 멈춤
    │     코드 품질/보안/패턴 검사        │
    └──────┬──────────────────┬─────────┘
           │                  │
        BLOCKED             CLEAR
           │                  │
           ├─ CRITICAL ──► 4번(@spec-writer) 또는 6번(@spec-builder)
           ├─ HIGH ──► 6번(@spec-builder)
           ├─ MEDIUM ──► 메인 대화에서 수정 후 9번 재실행
           │                  │
    ┌──────┴──────────────────▼─────────┐
    │  10. @docs-updater                  │ ── 조건부 멈춤
    │     status.md, project.md 갱신     │
    │     drafts 반영 + openspec archive │
    └─────────────────┬─────────────────┘
                      │
    ┌─────────────────▼─────────────────┐
    │  11. @committer                    │ ── 조건부 멈춤
    │  ┌───────────────────────────┐    │
    │  │ /git-commit-helper        │◄───┼─── Skill 호출
    │  └───────────────────────────┘    │
    └───────────────────────────────────┘
```

## 자동 진행 규칙

각 에이전트는 output 마지막에 `Status: CLEAR` 또는 `Status: BLOCKED`를 반환한다.

### 항상 멈추는 스텝

| 스텝 | 이유 |
|------|------|
| 2. 작업 선택 | 사용자가 직접 결정 |
| 3. @interviewer | 요구사항 확정은 사용자 확인 필요 |
| 8. 이슈 수정 | FAIL에서만 진입, 수정 방향 결정 필요 |

### 조건부 멈추는 스텝

| 스텝 | BLOCKED 조건 | CLEAR 시 자동 진행 |
|------|-------------|-------------------|
| 1. 작업사항 확인 | — | → 2번 (목록 + "새 작업 시작" 선택지 제시) |
| 4. @spec-writer | spec seed 필요, 기존 spec 충돌, artifact 생성 실패 | → 5번 (frontend 작업) 또는 6번 (그 외) |
| 5. @designer | — | → 6번 |
| 6. @spec-builder | 테스트 실패, tasks 없음, 설계 모순 | → 7번 |
| 7. @spec-checker | CRITICAL 이슈 발견 | → 9번 |
| 9. @code-reviewer | CRITICAL/HIGH/MEDIUM 이슈 발견 | → 10번 |
| 10. @docs-updater | Breaking Changes 등 큰 변경 | → 11번 |
| 11. @committer | 민감 파일 감지, 커밋 분리 필요 | → 완료 |

## 단계별 설명

### 1. 작업사항 확인 — 메인 AI
docs/context/status.md를 읽고 진행 중/예정 항목을 요약한다.

### 2. 작업 선택 — 사용자
사용자가 작업을 지정한다.

### 3. `@interviewer` — 리서치 + 브레인스토밍
- docs/context/, openspec/, 코드베이스를 조사하여 브리핑 반환
- Skill 도구로 `/brainstorming`을 호출하여 요구사항 정리
- AskUserQuestion으로 사용자에게 직접 질문
- Devil's Advocate: 브레인스토밍 결과에 의도적 반론 제기

### 4. `@spec-writer` — OpenSpec artifact 생성
- @interviewer의 Phase 5 출력을 prompt에 원문 포함하여 호출
- 내부에서 `/opsx:new` → `/opsx:ff` 스킬을 호출하여 change + artifact 생성

### 5. `@designer` — UI/UX 설계 (frontend 작업일 때만)
- `/ui-ux-pro-max` 스킬로 design-system/MASTER.md 생성
- frontend 작업이 아니면 건너뛴다

### 6. `@spec-builder` — 스펙 기반 코드 작성
- openspec change의 tasks artifact를 순서대로 구현
- 코드 작성 + 테스트 작성
- tasks 없으면 종료하고 4번 안내

### 7. `@spec-checker` — 스펙 대비 매칭
- spec 대비 완전성/정확성/일관성 검증
- PASS → 9번 / FAIL → 8번 (이슈 수정)

### 8. 이슈 수정
- FAIL에서만 진입
- 메인 대화에서 직접 수정하거나 @spec-builder로 재작업
- 수정 후 7번(@spec-checker) 재실행

### 9. `@code-reviewer` — 코드 품질 검사
- 보안, 코드 품질, 패턴 일관성 검사
- 읽기 전용 — 파일 수정 없음
- CLEAR → 10번
- BLOCKED (CRITICAL) → 4번(@spec-writer) 또는 6번(@spec-builder)
- BLOCKED (HIGH) → 6번(@spec-builder)
- BLOCKED (MEDIUM) → 메인 대화에서 수정 후 9번 재실행

### 10. `@docs-updater` — 문서 갱신
- docs/context/status.md, project.md 갱신 + drafts 반영 + openspec archive
- 변경 제안 보여주고 승인 후 반영

### 11. `@committer` — 커밋
- Skill 도구로 `/git-commit-helper`를 호출하여 커밋 수행

## 파일 구조

```
.claude/
├── skills/
│   └── workflow/SKILL.md        ← /workflow (플로우 가이드)
└── agents/
    ├── interviewer.md            ← @interviewer (리서치 + 브레인스토밍)
    ├── spec-writer.md           ← @spec-writer (OpenSpec artifact 생성)
    ├── designer.md              ← @designer (UI/UX 설계)
    ├── spec-builder.md          ← @spec-builder (스펙 기반 코드 작성)
    ├── spec-checker.md          ← @spec-checker (스펙 대비 매칭)
    ├── code-reviewer.md          ← @code-reviewer (코드 품질 검사)
    ├── review-fixer.md           ← @review-fixer (독립 호출용, 워크플로우 외)
    ├── docs-updater.md           ← @docs-updater (문서 갱신)
    └── committer.md             ← @committer (커밋)

docs/
└── context/                     ← 프로젝트 컨텍스트 (git 관리)
    ├── index.md
    ├── project.md
    ├── status.md
    ├── refs/
    └── drafts/
```

## 스킬 의존성

| 에이전트 | 호출하는 스킬/도구 |
|----------|-------------------|
| `@interviewer` | `/brainstorming`, AskUserQuestion |
| `@spec-writer` | `/opsx:new`, `/opsx:ff` |
| `@designer` | `/ui-ux-pro-max` |
| `@committer` | `/git-commit-helper` |
| `@docs-updater` | `openspec archive` (CLI) |
