# Handoff Plugin

## Overview

현재 세션을 유지하면서 파생된 작업을 새 세션으로 분리할 수 있도록 handoff 문서를 자동 생성하는 전략. 작업 중 추가 문제가 생겼을 때 현재 흐름을 끊지 않고 나중에 이어받을 수 있다.

## Purpose

작업 중 파생된 문제를 발견했을 때:
- 현재 세션의 집중을 방해받지 않고
- 나중에 새 세션에서 맥락 없이도 바로 작업을 시작할 수 있도록
- 인계 문서를 자동으로 생성한다

## When to Use

- 현재 작업 중 관련된 별도 문제가 생겼을 때
- 지금 당장 처리하기엔 범위가 크거나 방향이 다를 때
- 새 세션에서 이어받아야 할 작업이 생겼을 때

## Core Principles

### 1. 세션 독립성

handoff 문서는 새 세션의 AI가 첫 메시지만으로 작업을 시작할 수 있을 만큼 구체적이어야 한다.

### 2. 백그라운드 실행

handoff 문서 생성은 현재 세션의 흐름을 방해하지 않도록 백그라운드로 실행된다.

### 3. 명시적 저장 위치

`.claude/handoffs/`에 단순 파일 목록으로 보관. 완료 후 수동 정리.

## Plugin Components

- **README.md** (이 파일): 전략 개요
- **rules/handoff.md**: 자동 감지 트리거 + handoff 디렉토리 활용 규칙
- **agents/handoff-creator.md**: handoff 문서 생성 에이전트

## Usage Examples

### Example 1: 자동 감지

**Context**: 버그 수정 중 "이 부분은 나중에 별도 세션에서 리팩토링하자"고 언급

**Application**: rule이 표현을 감지 → `handoff-creator` 백그라운드 실행 → `.claude/handoffs/2026-03-02-리팩토링.md` 생성

**Result**: 현재 세션은 버그 수정에 집중, 나중에 새 세션에서 handoff 문서 참조하여 바로 작업 시작

### Example 2: 수동 호출

**Context**: 작업 중 "handoff 문서 만들어줘"라고 명시적으로 요청

**Application**: `handoff-creator` 에이전트 실행 → 현재 대화 맥락 분석 → 문서 생성

**Result**: 생성된 파일 경로가 현재 세션에 리포트됨

## Integration Guide

### For Claude Code

```bash
# 1. rules 복사
cp plugins/handoff/rules/handoff.md .claude/rules/

# 2. agents 복사
cp plugins/handoff/agents/handoff-creator.md .claude/agents/

# 또는 apply_to_repo 스크립트 사용
python3 agent-tools/.claude/skills/agent-plugin-manager/scripts/apply_to_repo.py handoff --repo <alias>
```

## File Structure (프로젝트 레포)

```
.claude/
├── agents/
│   └── handoff-creator.md
├── rules/
│   └── handoff.md
└── handoffs/              # 자동 생성됨
    └── YYYY-MM-DD-제목.md
```

## References

- `rules/handoff.md`: 자동 감지 트리거 및 동작 규칙
- `agents/handoff-creator.md`: 에이전트 정의 및 문서 포맷

## Version History

- **v1.0.0** - Initial plugin creation (2026-03-02)

---

**Last Updated**: 2026-03-02
**AI Platforms**: Claude Code
