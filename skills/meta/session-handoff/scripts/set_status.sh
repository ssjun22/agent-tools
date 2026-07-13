#!/usr/bin/env bash
# 특정 handoff의 frontmatter status를 변경한다.
# 활성 다중 허용 — 각 handoff의 status는 그 handoff를 다루는 세션이 직접 처리한다.
# (예: 이어받은 작업을 마치거나 폐기할 때 archived로)
set -euo pipefail
ARG="${1:?사용법: set_status.sh <파일경로|스탬프> <status>}"
STATUS="${2:?사용법: set_status.sh <파일경로|스탬프> <status>}"

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
DIR="${ROOT}/.claude/handoffs"

# 인자가 실제 파일이면 그대로, 아니면 스탬프로 간주해 DIR에서 찾는다
if [ -f "$ARG" ]; then
  F="$ARG"
elif [ -f "${DIR}/${ARG}" ]; then
  F="${DIR}/${ARG}"
elif [ -f "${DIR}/${ARG}.md" ]; then
  F="${DIR}/${ARG}.md"
else
  echo "handoff 못 찾음: $ARG" >&2
  exit 1
fi

if grep -q '^status: ' "$F"; then
  sed -i '' "s/^status: .*/status: ${STATUS}/" "$F"
else
  echo "frontmatter에 status 줄이 없음: $F" >&2
  exit 1
fi
echo "$F → status: ${STATUS}"
