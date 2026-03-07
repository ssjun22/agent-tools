# Project Context Strategy

## Overview

여러 독립 프로젝트를 오가며 작업할 때, 매번 프로젝트 맥락을 설명하지 않아도 AI가 빠르게 컨텍스트를 파악할 수 있도록 하는 전략.

## Problem

- 관리 중인 프로젝트가 많아 매 세션마다 맥락을 다시 설명해야 한다
- 세션이 끊기면 현재 진행 상황을 AI가 모른다
- 각 프로젝트의 규칙, 진행 상황이 머릿속에만 있다

## Solution

각 프로젝트 레포의 `.claude/context/`에 컨텍스트 문서를 보관하고, 세션 시작 시 자동으로 주입한다. 컨텍스트 업데이트는 스킬로 명시적으로 호출한다.

## Core Principles

1. **직접 로드** — `project.md`와 `status.md`를 세션 시작 시 직접 로드
2. **정적/동적 분리** — `project.md`(정적)와 `status.md`(동적)를 분리
3. **명시적 업데이트** — 자동 갱신 대신 `/project-context-manager` 스킬로 직접 호출
4. **CLAUDE.md와 역할 구분** — CLAUDE.md는 "규칙", context/는 "상태 정보"

## File Structure

### 전략 파일 (agent-tools)

```
strategies/project-context/
├── README.md                         # 이 파일
├── settings.json                     # hooks 등록 설정 (설치 시 참조)
├── rules/
│   └── project-context.md            # AI 동작 규칙 (CLAUDE.md에 추가)
├── hooks/
│   └── load-context                  # SessionStart: project.md + status.md 주입
└── skills/
    ├── project-context-init/
    │   └── SKILL.md                  # context/ 초기화 스킬
    └── project-context-manager/
        ├── SKILL.md                  # context/ 업데이트 스킬
        └── references/
            ├── project-template.md   # project.md 포맷 명세
            └── status-template.md    # status.md 포맷 명세
```

### 각 프로젝트 레포

```
.claude/
├── CLAUDE.md                         # 프로젝트 규칙/컨벤션 (기존)
└── context/
    ├── project.md                    # 정적: 프로젝트 개요, 도메인, 아키텍처 결정
    └── status.md                     # 동적: 작업 상태 목록
```

## Context Files

### `project.md` — 정적 정보

`/project-context-manager` 로 수동 업데이트.

- 프로젝트 목적 및 배경
- 현재 상태 (단계, 규모, 환경)
- 도메인 용어 및 엔티티 관계
- 아키텍처 결정 이유

### `status.md` — 동적 정보

`/project-context-manager` 로 수동 업데이트.

- 진행 중 / 진행 예정 / 진행 완료 목록

## Hooks

| Hook 파일 | 이벤트 | 동작 |
|-----------|--------|------|
| `load-context` | SessionStart | `context/project.md` + `context/status.md` 읽어서 AI에게 주입 |
| `save-context` | SessionEnd | 세션 중 발생한 변경사항이 draft로 저장됐는지 더블체크. 누락된 항목은 `context/drafts/`에 생성하도록 AI에게 지시 |

## Skills

| 스킬 | 용도 |
|------|------|
| `/project-context-init` | 새 프로젝트에 context/ 구조 초기화 |
| `/project-context-manager` | project.md / status.md 업데이트 |

## Installation

```bash
# 1. hooks 복사
cp strategies/project-context/hooks/load-context .claude/hooks/
cp strategies/project-context/hooks/save-context .claude/hooks/
chmod +x .claude/hooks/load-context .claude/hooks/save-context

# 2. rules 추가
cat strategies/project-context/rules/project-context.md >> .claude/CLAUDE.md

# 3. context/ 초기화 (스킬로 실행)
# /project-context-init

# 4. settings.local.json 등록
cp strategies/project-context/settings.json .claude/settings.local.json

# 5. skills 심볼릭 링크 (agent-tools-linker 사용)
python3 agent-tools/.claude/skills/agent-tools-linker/scripts/link.py strategy project-context --repo <alias>
```

## Relation to Other Strategies

| 전략 | 역할 | 차이점 |
|------|------|--------|
| `handoff-strategy` | 세션 간 작업 인수인계 | 작업 단위, 태스크 중심 |
| `project-context` | 프로젝트 맥락 유지 | 프로젝트 단위, 상태 중심 |
| `openspec-sdd` | 스펙 기반 개발 | 스펙 문서 관리 |

세 전략은 함께 사용할 수 있으며 역할이 겹치지 않는다.
