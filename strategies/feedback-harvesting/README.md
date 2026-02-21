# Feedback Harvesting

## Overview

Claude Code 세션에서 발생하는 사용자 피드백을 자동으로 감지하고, 대상 파일(스킬/에이전트/규칙)에 대한 구체적 수정 초안을 생성하는 점진적 최적화 전략.

정적 도구를 "사용할수록 나아지는 시스템"으로 전환하기 위한 메타 레이어.

## Purpose

Claude Code 사용 중 반복되는 문제:
- 스킬이 의도한 대로 동작하지 않음
- 규칙이 누락되어 같은 피드백을 반복함
- 에이전트 정의가 실제 사용 패턴과 맞지 않음

이 전략은 피드백 → 감지 → 수정 초안 → 승인 반영의 루프를 구축하여, 도구가 세션을 거듭하며 점진적으로 개선되도록 한다.

## When to Use

This strategy is applicable when:

- Claude Code로 스킬/에이전트를 사용하며 작업하는 프로젝트
- 사용자가 반복적으로 동일한 피드백을 주는 상황
- 스킬/규칙을 점진적으로 개선하고 싶을 때

## Data Flow

```
피드백 메시지 발생
      |
feedback-harvesting.md 규칙이 감지
      |
feedback-harvester 서브 에이전트 (백그라운드)
      |
대상 파일 탐색 -> 읽기 -> 수정 초안 생성
      |
.claude/evolution/pending-{timestamp}.md 저장
      |
[다음 세션 시작]
      |
check-harvest-updates.sh -> 개수 알림
      |
사용자 승인 -> 반영 -> .claude/evolution/archived/ 이동
```

## Core Principles

### 1. 승인 기반 반영

자동 반영 없음. 모든 수정은 사용자 승인 후에만 적용된다.

### 2. 최소 수술 (Surgical Changes)

피드백이 직접적으로 가리키는 범위만 수정 초안에 포함. 관련 없는 "개선"을 제안하지 않는다.

### 3. 점진적 진화

한 번에 완벽해지는 게 아니라, 세션을 거듭하며 조금씩 나아진다.

## Strategy Components

- **README.md** (this file): 전략 개요 및 사용 가이드
- **rules/**: 피드백 감지 트리거 규칙
- **agents/**: feedback-harvester 서브 에이전트 정의
- **hooks/**: SessionStart 알림 hook 스크립트

## Usage Examples

### Example 1: 스킬 동작 피드백

**Context**: brainstorming 스킬 사용 중 AskUserQuestion tool을 쓰지 않는 문제

**Application**:
1. 사용자: "왜 AskUserQuestion tool을 쓰지 않았어?"
2. Claude가 피드백으로 감지 -> feedback-harvester 백그라운드 실행
3. `.claude/evolution/pending-20260221-143022.md` 생성
4. 다음 세션 시작 시: "반영 대기 중인 피드백이 1개 있습니다."
5. `/apply-harvest-updates` 실행 -> 수정안 확인 -> 승인

**Result**: brainstorming SKILL.md에 AskUserQuestion 사용 규칙 추가

### Example 2: 규칙 누락 피드백

**Context**: Claude가 파일 생성 시 기존 파일 확인을 하지 않는 문제

**Application**:
1. 사용자: "새 파일 만들기 전에 기존 파일 먼저 확인해야 해"
2. feedback-harvester가 rule 대상으로 분류
3. pending 파일에 `.claude/rules/` 또는 `CLAUDE.md` 수정 초안 생성

**Result**: 규칙 파일에 "파일 생성 전 기존 파일 확인" 규칙 추가

## Integration Guide

### 프로젝트에 적용하기

1. 아래 파일들을 프로젝트의 `.claude/`에 배치:
   - `rules/feedback-harvesting.md` -> `.claude/rules/`
   - `agents/feedback-harvester.md` -> `.claude/agents/`
   - `hooks/check-harvest-updates.sh` -> `.claude/hooks/`

2. `.claude/evolution/` 디렉토리 생성:
   ```
   .claude/evolution/
   └── archived/
   ```

3. `settings.local.json`에 SessionStart hook 등록:
   ```json
   {
     "SessionStart": [
       {
         "matcher": "*",
         "hooks": [
           {
             "type": "command",
             "command": "bash .claude/hooks/check-harvest-updates.sh"
           }
         ]
       }
     ]
   }
   ```

## Feedback Targets

| 대상 | 탐색 경로 | 설명 |
|------|----------|------|
| skill | `.claude/skills/<name>/` | 스킬 폴더 전체 (SKILL.md, references/, assets/) |
| agent | `.claude/agents/<name>.md` | 에이전트 정의 파일 |
| rule | `.claude/CLAUDE.md` 또는 `.claude/rules/<name>.md` | 규칙 파일 |

## Decision Log

| 결정 | 선택 | 대안 | 이유 |
|------|------|------|------|
| 트리거 방식 | CLAUDE.md 규칙 | Hook, 슬래시 커맨드 | Hook 오버헤드 없이 Claude가 직접 판단 |
| 실행 방식 | 백그라운드 서브 에이전트 | Stop hook, 스킬 | 사용자 흐름 방해 없음 |
| 피드백 소스 | 사용자 메시지 기반 | 전체 트랜스크립트 | 컨텍스트 경량화 |
| 파일 구조 | 세션별 타임스탬프 파일 | 단일 파일, 대상별 파일 | 충돌 없음, 관리 단순 |
| 반영 완료 처리 | archived/ 이동 | 삭제, 상태 표시 | 히스토리 보존 |
| 대상 파일 탐색 | Glob 탐색 | 경로 매핑, 컨텍스트 추론 | 프로젝트 구조 무관하게 동작 |
| SessionStart | 알림만 | 자동 리뷰, 강제 적용 | 세션 시작 방해 최소화 |
| 트리거 규칙 위치 | `.claude/rules/` 별도 파일 | CLAUDE.md 직접 추가 | CLAUDE.md 비대화 방지 |

## Version History

- **v0.1.0** - 초기 전략 설계 (2026-02-21)

---

**Last Updated**: 2026-02-21
**AI Platforms**: Claude Code
