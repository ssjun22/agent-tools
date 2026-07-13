#!/usr/bin/env bash
# 새 handoff를 {YYYY-MM-DD-HHMM}.md에 status: active로 생성한다.
# 활성 여부는 파일명이 아니라 frontmatter의 status 필드로 관리한다.
# 여러 handoff가 동시에 active일 수 있다 — 다른 활성본은 건드리지 않는다.
# 기존 handoff의 status 정리는 그 handoff를 다루는 세션이 set_status.sh로 처리한다.
set -euo pipefail
NAME="${1:?사용법: new_handoff.sh <작업명>}"
NOW="$(date '+%Y-%m-%d %H:%M')"
STAMP="$(date '+%Y-%m-%d-%H%M')"

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
DIR="${ROOT}/.claude/handoffs"
mkdir -p "$DIR"

# 같은 분에 이미 파일이 있으면 접미사로 충돌 회피
HANDOFF="${DIR}/${STAMP}.md"
n=2
while [ -e "$HANDOFF" ]; do
  HANDOFF="${DIR}/${STAMP}-${n}.md"
  n=$((n+1))
done

cat > "$HANDOFF" << SKELETON
---
status: active
name: ${NAME}
created: ${NOW}
---

# Handoff: ${NAME} (${NOW})

## 목표

## 현재 상황

## 다음 액션
1.

## 열린 질문

## 누락
_이 문서를 읽고 작업을 이어가는 중에, 여기 있었어야 했는데
없어서 재발굴한 정보를 발견 즉시 한 줄씩 적을 것. 다음
handoff의 작성 기준을 개선하는 재료가 된다._

SKELETON
echo "${HANDOFF} 뼈대 생성 완료 (status: active) — 작성 기준은 SKILL.md 참조"
