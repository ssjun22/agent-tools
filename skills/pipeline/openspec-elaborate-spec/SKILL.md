---
name: opsx:elaborate-spec
description: 'Elaborate an existing OpenSpec main spec for a specific domain. Use when a seeded spec exists but requirement/scenario detail is insufficient.'
compatibility: Requires codebase access.
---

# /opsx:elaborate-spec — Elaborate Existing Main Spec

## Overview

기존 `openspec/specs/<domain>/spec.md`를 대상으로, 현재 코드 동작 기준으로 requirement/scenario를 더 구체화/상세화한다.
이 스킬은 신규 기능 제안이 아니라, 이미 존재하는 main spec의 명확성/완성도/테스트 가능성을 높이기 위한 문서 작업이다.

## Input

- 대상 도메인 이름 (kebab-case)
- 선택: 구체화 범위
  - `full` (기본)
  - `requirements-only`
  - `scenarios-only`
  - 특정 requirement 이름

## Workflow

### 1. 대상 spec 확인

- `openspec/specs/<domain>/spec.md` 존재 여부를 확인한다.
- 파일이 없으면 중단하고 `/opsx:seed`를 안내한다.

### 2. 구체화 범위 합의

사용자에게 범위를 명시적으로 확인한다.

> "기존 스펙을 유지한 채 현재 코드 기준으로 어느 범위까지 구체화할까요? (full / requirements-only / scenarios-only / 특정 requirement)"

### 3. 코드 근거 수집

도메인 관련 구현 파일을 읽고 관찰 가능한 동작 근거를 수집한다.

- API 엔드포인트/입출력 계약
- 핵심 비즈니스 분기/예외 처리
- 데이터 모델/제약조건
- 상태 전이/재사용/캐시 규칙

### 4. 상세화 초안 작성

기존 spec을 baseline으로 유지한 채 상세화 초안을 만든다.

- 기존 requirement를 불필요하게 삭제하지 않는다.
- 모호한 requirement는 더 구체적인 requirement/scenario로 분해한다.
- scenario를 WHEN/THEN 형식의 테스트 가능한 문장으로 구체화한다.
- happy path + 에러/엣지 케이스를 균형 있게 포함한다.
- 코드에 없는 신규 기능/이상 동작을 추가하지 않는다.

### 5. 사용자 확인

상세화 초안을 먼저 보여주고 승인받는다.

- **Approve** — 파일 반영
- **Needs changes** — 피드백 반영 후 재확인

사용자 승인 없이 파일을 반영하지 않는다.

### 6. main spec 반영

승인 후 `openspec/specs/<domain>/spec.md`에 상세화 내용을 반영한다.

### 7. 완료 요약

- 구체화된 requirement/scenario 개수와 핵심 변경점을 요약한다.
- 다음 단계를 안내한다.
  - 정합성 확인: `/opsx:audit-spec`
  - 동작 변경 필요: `/opsx:new <change-name>`

## Guardrails

- 코드 변경 금지 (문서 작업만 수행)
- 현재 코드 동작 기반으로만 상세화
- 승인 없이 파일 반영 금지
- 한 번에 하나의 도메인만 처리
- 동작 변경이 필요한 경우 `/opsx:new`로 전환

## Related Commands

| Command | Role |
|---------|------|
| `/opsx:seed` | 기존 코드에서 초기 main spec 생성 |
| `/opsx:elaborate-spec` | 특정 main spec 구체화/상세화 |
| `/opsx:audit-spec` | main spec-코드 정합성 감사 |
| `/opsx:new` | 동작 변경이 필요한 change 생성 |
