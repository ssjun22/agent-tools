# Handoff Strategy

## Overview

AI 에이전트 세션 간 컨텍스트 유지 및 협업을 위한 handoff 시스템. 매 세션마다 동일한 설명을 반복하지 않고, 압축된 핵심 정보로 빠르게 컨텍스트를 복원합니다.

## Purpose

**문제**: AI 에이전트 세션은 종료되면 컨텍스트가 소실되어, 다음 세션에서 동일한 설명을 반복해야 합니다.

**해결**: handoff.md 파일을 통해 세션 간 핵심 컨텍스트를 전달하여, 새로운 세션이 빠르게 작업을 이어받을 수 있도록 합니다.

## When to Use

이 전략은 다음과 같은 상황에서 적용됩니다:

- **장기 프로젝트**: 여러 세션에 걸쳐 작업이 진행되는 프로젝트
- **복잡한 컨텍스트**: 단순히 코드를 보는 것만으로는 파악하기 어려운 결정 사항이나 진행 상황
- **팀 협업**: 여러 개발자가 AI 에이전트와 협업하는 환경
- **중단된 작업**: 작업을 중단했다가 나중에 재개해야 하는 경우

## Core Principles

### 1. 간결성 (Conciseness)

handoff 파일은 간결하고 핵심적인 정보만 포함해야 합니다.
- 목표: ~2000 토큰 이하
- 불필요한 세부사항 제외
- 핵심 컨텍스트에 집중

### 2. 구조화 (Structure)

일관된 구조를 통해 AI가 빠르게 정보를 파악할 수 있도록 합니다.
- 표준화된 파일명: `{date}-{task-name}.md`
- 일관된 내용 구조: 문제 → 해결 → 할 일 → 고려사항
- 중앙 인덱스: `index.md`로 모든 handoff 추적

### 3. 자동화 (Automation)

hooks를 통해 handoff 관리를 완전 자동화합니다.
- **세션 시작** (sessionStart hook): 자동으로 최신 handoff 로드
- **세션 종료** (sessionEnd hook): 자동으로 handoff 업데이트
- **컨텍스트 압축 전** (preCompact hook): 압축 전 handoff 자동 업데이트

## Strategy Components

이 전략은 다음 구성요소를 포함합니다:

- **README.md** (이 파일): 전략 개요 및 사용 가이드
- **rules/**: AI 에이전트가 세션 시작 시 읽을 핵심 규칙
  - `handoff-rules.md`: 간결한 handoff 관리 규칙 (읽기/쓰기/구조)
- **hooks/**: 자동화 스크립트 (핵심)
  - `session-start`: 세션 시작 시 handoff 자동 로드
  - `session-end`: 세션 종료 시 handoff 자동 업데이트
  - `pre-compact`: 컨텍스트 압축 전 handoff 자동 업데이트
  - `settings.json`: Claude Code hooks 설정 파일
  - `INSTALL.md`: 상세 설치 가이드
- **assets/**: 템플릿 파일
  - `index-template.md`: index.md 템플릿
  - `handoff-template.md`: handoff 파일 템플릿

## File Structure

### 프로젝트 내 handoff 디렉토리 구조

```
.claude/handoffs/
├── index.md                          # 모든 handoff 파일의 인덱스 (장부)
├── 2024-01-30-auth-refactor.md      # 개별 handoff 파일
├── 2024-01-31-api-optimization.md
└── 2024-02-01-database-migration.md
```

### index.md 구조

```markdown
# Handoff Index

| 파일명 | 작업명 | 날짜 | 설명 |
|--------|--------|------|------|
| 2024-02-01-database-migration.md | Database Migration | 2024-02-01 | PostgreSQL to MongoDB migration |
| 2024-01-31-api-optimization.md | API Optimization | 2024-01-31 | REST API performance improvements |
| 2024-01-30-auth-refactor.md | Auth Refactor | 2024-01-30 | JWT authentication refactoring |
```

### handoff.md 파일 구조

```markdown
# Handoff: {Task Name}

**Date**: YYYY-MM-DD
**Session**: N
**Status**: [In Progress | Completed | Blocked]

## Context

[간략한 배경 설명 - 왜 이 작업을 하는가?]

## What Was Done

[이번 세션에서 완료한 작업]

- Item 1
- Item 2

## Current Status

[현재 상태 및 진행률]

## Issues/Blockers

[현재 알려진 문제나 블로커]

## Next Steps

[다음에 해야 할 작업]

1. Step 1
2. Step 2

## Decisions Made

[중요한 결정 사항 및 이유]

## Notes

[추가 고려사항 또는 참고 사항]
```

## Usage Examples

### Example 1: 세션 시작 시 (자동)

**Trigger**: Claude Code 세션 시작

**What Happens** (session-start hook):
1. Hook이 자동 실행
2. 최신 handoff 파일 식별
3. AI가 handoff를 읽고 요약 제공

**User Experience**:
```
[Handoff 로드됨]

이전 세션 컨텍스트:
- 작업: Auth Refactor
- 진행률: 60%
- 마지막 작업: JWT 토큰 검증 로직 구현
- 다음 단계: 리프레시 토큰 구현

어떤 작업을 이어가시겠습니까?
```

### Example 2: 컨텍스트 압축 전 (자동)

**Trigger**: Claude Code가 컨텍스트를 압축하려고 할 때

**What Happens** (preCompact hook):
1. Hook이 자동 실행
2. AI가 현재 세션 작업 분석
3. handoff 파일 자동 업데이트
4. 컨텍스트 압축 진행

**User Experience**:
```
=== Context Compaction: Updating Handoff ===

[AI가 자동으로 handoff 업데이트]

Handoff updated before compaction.
💡 This preserves context before compaction
```

### Example 3: 세션 종료 시 (자동)

**Trigger**: Claude Code 세션 종료

**What Happens** (session-end hook):
1. Hook이 자동 실행
2. AI가 현재 세션 작업 요약
3. handoff 파일 업데이트
4. index.md 갱신

**User Experience**:
```
Handoff updated for next session.
다음 세션에서 바로 이어서 작업할 수 있습니다.
```

## Integration Guide

### Quick Start (Claude Code - Recommended)

**완전 자동화 설정** - hooks를 통해 handoff 읽기/쓰기를 자동으로 처리:

```bash
# 1. 디렉토리 생성
mkdir -p .claude/hooks .claude/handoffs

# 2. hooks 복사
cp -r agent-tools/skills/shared/agent-strategy-manager/strategies/handoff-strategy/hooks/* .claude/hooks/

# 3. 실행 권한 부여
chmod +x .claude/hooks/*

# 4. index.md 초기화
cp agent-tools/.../assets/index-template.md .claude/handoffs/index.md

# 5. settings.json 복사 (또는 기존 settings.local.json에 hooks 추가)
cp agent-tools/.../hooks/settings.json .claude/settings.local.json
# 또는 수동으로 추가:
{
  "hooks": {
    "sessionStart": "bash .claude/hooks/session-start",
    "sessionEnd": "bash .claude/hooks/session-end",
    "preCompact": "bash .claude/hooks/pre-compact"
  }
}
```

✅ **완료!** 이제 handoff가 자동으로 작동합니다:
- 세션 시작 → 자동으로 최신 handoff 로드
- 세션 종료 → 자동으로 handoff 업데이트
- Git 커밋 → 자동으로 handoff 업데이트

### Detailed Installation

상세 설치 가이드는 [hooks/INSTALL.md](hooks/INSTALL.md)를 참조하세요.

### For Cursor/Codex

Cursor 및 기타 AI 도구는 hook 시스템이 다를 수 있습니다:

**Option 1: Manual hooks**
```bash
# hooks를 수동으로 실행
bash .claude/hooks/session-start
bash .claude/hooks/session-end
```

**Option 2: Platform-specific configuration**
- Cursor: `.cursorrules`에 handoff rules 추가
- 기타: 해당 플랫폼의 설정 파일 사용

### For Custom Agents

1. **handoff 구조 참조**: `rules/handoff-structure.md` 참조
2. **자동화 선택**: hooks, rules, 또는 둘 다 사용 가능
3. **템플릿 활용**: `assets/` 디렉토리의 템플릿 사용

## Key Guidelines

1. **간결함 유지**: 각 handoff 파일은 ~2000토큰 이하로 유지
2. **일관된 구조**: 템플릿을 따라 일관된 형식 유지
3. **정기적 업데이트**: 커밋 시, 주요 작업 완료 시 handoff 업데이트
4. **index.md 관리**: 새 handoff 파일 생성 시 index.md에 추가
5. **Git 커밋**: handoff 파일을 Git에 커밋하여 이력 관리

## References

### Hooks (자동화)

- **[hooks/settings.json](hooks/settings.json)** - Claude Code hooks 설정 파일
- **[hooks/INSTALL.md](hooks/INSTALL.md)** - 상세 설치 가이드
- [hooks/session-start](hooks/session-start) - 세션 시작 hook
- [hooks/session-end](hooks/session-end) - 세션 종료 hook
- [hooks/pre-compact](hooks/pre-compact) - 컨텍스트 압축 전 hook

### Rules (AI가 읽을 핵심 규칙)

- **[rules/handoff-rules.md](rules/handoff-rules.md)** - 간결한 handoff 관리 규칙 전체

### Templates

- [assets/index-template.md](assets/index-template.md) - index.md 템플릿
- [assets/handoff-template.md](assets/handoff-template.md) - handoff 파일 템플릿

## Version History

- **v1.0.0** - Initial handoff strategy creation (2024-01-30)

---

**Author**: AI Agent Strategy Manager
**Last Updated**: 2024-01-30
**AI Platforms**: Claude Code, Cursor, Codex, General AI Agents
