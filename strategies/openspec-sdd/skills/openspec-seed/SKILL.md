---
name: opsx:seed
description: 'Seed OpenSpec specs from existing code. Use when the codebase has implemented features but no corresponding specs exist.'
compatibility: Requires openspec CLI.
---

# /opsx:seed — Seed Specs from Code

## Overview

기존 코드에서 OpenSpec spec을 생성하는 agent-driven 스킬. 코드를 읽고 분석하여 `openspec/specs/`에 spec 파일을 직접 생성한다.

**핵심 원칙:** 현재 동작만 문서화한다. 개선 제안은 `/opsx:new`로 별도 처리한다.

**Tip:** 코드 구조가 복잡하거나 어디서부터 시작할지 불명확하면 `/opsx:explore`로 먼저 탐색한 후 seed를 진행할 수 있다.

## Input

도메인 이름(kebab-case)과 코드 경로를 선택적으로 지정. 생략 시 사용자에게 질문.

유효한 입력 예시:
- `user-auth, server/api/v1/endpoints/auth.py`
- `single-image-eval, llm/agents/single_image_eval_agent/`
- `payments` (코드 경로는 코드베이스에서 탐색)

## Workflow

### 1. 대상 정보 수집

명확한 입력이 없으면 기존 spec 목록을 확인한 후 사용자에게 직접 질문:

> "어떤 코드/기능의 spec을 생성할까요? 도메인 이름(kebab-case)과 관련 코드 경로를 알려주세요."

입력으로부터 결정할 항목:
- **Domain name** (kebab-case → `openspec/specs/<domain>/`)
- **Code paths** (미제공 시 코드베이스에서 관련 파일 탐색)

도메인 이름과 최소 하나의 코드 경로가 확인될 때까지 진행하지 않는다.

### 2. 기존 spec 확인

`openspec/specs/<domain>/spec.md`가 이미 존재하면 사용자에게 명시적으로 확인:
- **Overwrite** — 새로 분석하여 덮어쓰기
- **Cancel** — 중단, `/opsx:new`로 수정 권장

분기 기준:
- 현재 코드에서 관찰되는 동작 범위 안에서 requirement/scenario를 세분화·명확화하려면 `/opsx:elaborate-spec`를 안내한다.
- 새로운 동작 추가, 기존 결과 변경, 정책 변경이 필요하면 `/opsx:new`로 전환한다.

Cancel 선택 시 아래 출력 후 중단:

```
## Spec Already Exists

openspec/specs/<domain>/spec.md already exists with N requirements.

To elaborate this spec (without changing behavior scope), use /opsx:elaborate-spec <domain>.
To modify this spec, use /opsx:new <change-name> to create a change
with delta specs (MODIFIED/ADDED/REMOVED).
```

### 3. 코드베이스 분석

관련 코드 파일을 읽고 다음을 추출:

- **API endpoints**: 라우트 정의, HTTP 메서드, 요청/응답 스키마, 에러 응답
- **Business logic**: 핵심 함수 동작, 분기 조건, 데이터 변환
- **Data models**: 스키마 정의, 관계, 제약조건
- **Integration points**: 외부 서비스 호출, 이벤트 핸들러, 미들웨어

구현 세부사항이 아닌 **관찰 가능한 동작**에 집중한다.

### 4. Spec 작성

OpenSpec 형식으로 spec을 작성:

```markdown
# {Domain} Specification

## Purpose
{1-2 sentences describing what this domain does}

## Requirements

### Requirement: {Behavior Name}
The system SHALL {what the system does}.

#### Scenario: {Scenario Name}
- **WHEN** {condition/trigger}
- **THEN** {observable outcome}

#### Scenario: {Edge Case Name}
- **WHEN** {edge condition}
- **THEN** {how system handles it}
```

**작성 규칙:**
- 하나의 requirement = 하나의 구별되는 시스템 동작 (함수나 파일 단위가 아님)
- 하나의 scenario = 하나의 구체적이고 테스트 가능한 예시
- SHALL/MUST로 규범적 요구사항 기술
- WHEN/THEN 형식으로 시나리오 기술
- 모든 requirement에 최소 하나의 scenario 필수
- happy path + 최소 하나의 에러/엣지 케이스 포함
- 코드가 **실제로 하는 것**을 기술 (해야 하는 것이 아님)
- 동작이 불명확하면 `(inferred)`로 표시

### 5. 사용자 확인

전체 spec 초안을 표시한 후 사용자에게 명시적으로 확인:

> "이 spec이 현재 코드의 동작을 정확히 반영하고 있나요?"
- **Yes, create the spec** — 파일 생성 진행
- **Needs changes** — 수정 사항 반영 후 재확인

사용자 확인 없이 파일을 생성하지 않는다.

### 6. Spec 파일 생성

`openspec/specs/<domain>/spec.md` 생성. 디렉토리가 없으면 함께 생성.

### 7. 완료 요약 출력

```
## Spec Seeded: <domain>

**Created:** openspec/specs/<domain>/spec.md
**Requirements:** N
**Scenarios:** M

This spec documents current code behavior. Next steps:
- To verify code matches: /opsx:verify
- To modify behavior: /opsx:new <change-name>
- To seed another domain: /opsx:seed
```

## Guardrails

**CRITICAL**
- MUST NOT modify, patch, or suggest changes to code — this is a read-only analysis. 코드-스펙 불일치를 발견하면 `/opsx:verify` 사용을 안내한다
- MUST NOT create or overwrite spec files without explicit user approval — Step 5를 절대 생략하지 않는다
- If user requests both spec creation and code modification, STOP after showing the spec draft and request approval before proceeding. Code changes belong in `/opsx:new`, not `/opsx:seed`
- MUST process one domain at a time — 여러 도메인을 요청받은 경우 각 도메인마다 Step 1~7을 완전히 수행한 후 다음 도메인으로 넘어간다

**General**
- change 폴더를 생성하지 않는다 — `openspec/specs/`에 직접 작성
- 이상적인 동작을 기술하지 않는다 — 코드의 현재 동작만 문서화
- spec에 구현 세부사항을 포함하지 않는다 — 관찰 가능한 동작에 집중
- 동작이 모호하면 `(inferred)`로 표시하고 불확실성을 기록
- 새 기능의 spec을 작성하려면 `/opsx:seed`가 아닌 `/opsx:new`를 사용한다

## Related Commands

| Command | Role |
|---------|------|
| `/opsx:seed` | 기존 코드에서 초기 spec 생성 (this skill) |
| `/opsx:elaborate-spec` | 기존 main spec의 requirement/scenario 구체화/상세화 |
| `/opsx:new` | 변경사항 생성 (spec/code 수정) |
| `/opsx:verify` | 코드-스펙 일치 검증 |
| `/opsx:archive` | 변경 완료 + main spec 병합 |
