#!/bin/bash
# 사용법: ./validate-codex.sh <skill-dir-path> [rounds]

set -e

SKILL_DIR="${1:?'스킬 디렉토리 경로를 지정해주세요'}"
ROUNDS="${2:-3}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=config.sh
source "$SCRIPT_DIR/config.sh"
AGENTS_DIR="$SCRIPT_DIR/agents"

# 작업 디렉토리 초기화
rm -rf "$WORK_DIR"
cp -r "$SKILL_DIR" "$WORK_DIR"
echo "" > "$LOG"

echo "🚀 Skill Validator 시작 (${ROUNDS}라운드)"
echo "   검증 대상: $SKILL_DIR"
echo "   작업 경로: $WORK_DIR"
echo ""

cd "$SCRIPT_DIR"

for i in $(seq 1 "$ROUNDS"); do
    echo "-----------------------------------"
    echo "🔄 [Round $i/$ROUNDS] Critic 실행 중..."

    CRITIC_PROMPT="$(envsubst '$WORK_DIR $LOG' < "$AGENTS_DIR/critic.md")"
    codex "$CRITIC_PROMPT"

    echo "🛠️  [Round $i/$ROUNDS] Improver 실행 중..."

    IMPROVE_PROMPT="$(envsubst '$WORK_DIR $LOG' < "$AGENTS_DIR/improve.md")"
    codex "$IMPROVE_PROMPT"

    echo "✅ Round $i 완료"
done

echo "🎉 완료!"
echo "   개선된 스킬 디렉토리: $WORK_DIR"
echo "   비평 로그:            $LOG"
echo ""
echo "원본에 반영하려면:"
echo "   diff -r $SKILL_DIR $WORK_DIR"
echo "   cp -r $WORK_DIR/* $SKILL_DIR/"