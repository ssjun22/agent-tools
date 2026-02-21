#!/bin/bash
EVOLUTION_DIR="$CLAUDE_PROJECT_DIR/.claude/evolution"
PENDING_FILES=$(ls "$EVOLUTION_DIR"/pending-*.md 2>/dev/null)

if [ -z "$PENDING_FILES" ]; then
  exit 0
fi

COUNT=$(echo "$PENDING_FILES" | wc -l | tr -d ' ')
echo "📋 반영 대기 중인 피드백이 ${COUNT}개 있습니다."
echo "확인하려면 /apply-harvest-updates 를 실행하세요."
