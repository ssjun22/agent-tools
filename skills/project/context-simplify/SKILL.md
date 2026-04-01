---
name: context-simplify
description: Simplify docs/context/ files (project.md + status.md) to reduce session context injection size. Use this skill when the load-context hook fires a bloat warning, or when the user says "context 정리", "context 간소화", "컨텍스트 줄여줘", or asks to reduce context size. This skill analyzes the current state, proposes a simplification plan, and executes only after user approval.
---

# Context Simplify

Reduce the token footprint of `docs/context/project.md` and `docs/context/status.md` — the two files injected into every session via the `load-context` hook.

This skill does NOT touch `docs/context/refs/` files (they are already lazy-loaded by path only).

## Prerequisites

- `docs/context/` structure initialized by `project-context-init`
- Expected files: `project.md`, `status.md`, `refs/` directory

## Workflow

### Phase 1: Analyze

1. Read `docs/context/project.md` and `docs/context/status.md`
2. List existing `docs/context/refs/` files
3. Measure:
   - Total line count (both files combined)
   - Per-section line count (split by `## ` headings)

Present the measurements to the user:

```
현재 상태:
- project.md: {N}줄
- status.md: {N}줄
- 합계: {N}줄 (임계치: 150줄)
- refs/ 파일: {list}
```

### Phase 2: Apply Rules

Evaluate each rule in order. Skip rules whose conditions are not met.

#### R1: Completed History Trim

- **Target**: `status.md` — the section under `### 진행 완료` or `### 최근 완료`
- **Condition**: More than 3 completed items
- **Action**: Keep only the 3 most recent items. Add a note: `> 전체 완료 이력은 git log 참조`
- **Why**: Completed work history accumulates every session. Git log is the authoritative source — duplicating it in context wastes tokens.

#### R2: Breaking Changes Split

- **Target**: `project.md` — `## Breaking Changes` section
- **Condition**: More than 5 table rows
- **Action**: Move the entire table to `docs/context/refs/breaking-changes.md`. Remove the section from `project.md`.
- **Why**: Breaking changes are historical records needed only when investigating API compatibility — not every session.

#### R3: Architecture Decisions Split

- **Target**: `project.md` — `## 아키텍처 결정` section
- **Condition**: More than 5 table rows
- **Action**:
  1. Move the full table to `docs/context/refs/architecture-decisions.md`
  2. Replace the section in `project.md` with a summary table of the top 5 most impactful decisions (use your judgment based on how frequently they affect day-to-day work)
  3. Add a pointer: `> 전체 아키텍처 결정 목록: docs/context/refs/architecture-decisions.md`
- **Why**: Most architecture decisions are "set and forget" — only the active/impactful ones need to be in every session's context.

#### R4: Requirements Table Merge

- **Target**: `project.md` — `## 전체 요구사항` section
- **Condition**: All items in the table have status "완료" (completed)
- **Action**: Merge the information into the domain/role table (e.g., `### 에이전트별 역할` or equivalent), then remove the `## 전체 요구사항` section entirely.
- **Why**: A requirements table where everything is "완료" is pure redundancy — the same information exists in the role/component tables that describe the current system.

#### R5: Duplicate Table Detection

- **Target**: `project.md` — all markdown tables
- **Condition**: Two or more tables share the same data (same entities listed with overlapping columns)
- **Action**: Propose merging into a single table. Present both tables and the proposed merged version.
- **Why**: Tables sometimes grow independently during different sessions, leading to the same entities being described in multiple places.

### Phase 3: Propose Plan

Present the plan as a numbered list. For each applicable rule:

```
간소화 계획:

1. [R1] 완료 이력 축소: {N}건 → 3건 (예상 -{X}줄)
2. [R3] 아키텍처 결정 분리: refs/architecture-decisions.md 생성, 핵심 5개만 유지 (예상 -{X}줄)

예상 결과: {현재}줄 → {예상}줄

승인하시겠습니까?
```

If no rules apply, tell the user:

```
현재 적용 가능한 간소화 규칙이 없습니다. ({N}줄)
```

### Phase 4: Execute

Only after the user explicitly approves:

1. Create any new `refs/` files first (so no data is lost during edits)
2. Edit `project.md` — apply R2, R3, R4, R5 changes
3. Edit `status.md` — apply R1 changes
4. Report the result:

```
간소화 완료:
- before: {N}줄
- after: {N}줄 (절감: {N}줄, {P}%)
- 생성된 refs/ 파일: {list or "없음"}
```

## Important Constraints

- Never delete information without moving it to `refs/` or confirming it exists in git history
- Never modify `refs/` files (they are out of scope)
- If `refs/` directory doesn't exist, create it before moving files there
- Always show the plan before executing — this skill never auto-executes
- Preserve the section ordering of `project.md` — don't rearrange sections
