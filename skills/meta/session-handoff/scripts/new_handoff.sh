#!/usr/bin/env bash
# 기존 handoff를 .claude/handoffs/ 안에서 이관하고 새 뼈대를 생성한다.
set -euo pipefail
NAME="${1:?사용법: new_handoff.sh <작업명>}"
NOW="$(date '+%Y-%m-%d %H:%M')"
STAMP="$(date '+%Y-%m-%d-%H%M')"

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
DIR="${ROOT}/.claude/handoffs"
HANDOFF="${DIR}/HANDOFF.md"
mkdir -p "$DIR"

if [ -f "$HANDOFF" ]; then
  mv "$HANDOFF" "${DIR}/${STAMP}-이전본.md"
  echo "이전 handoff → ${DIR}/${STAMP}-이전본.md"
fi

cat > "$HANDOFF" << SKELETON
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
echo "${HANDOFF} 뼈대 생성 완료 — 작성 기준은 SKILL.md 참조"
