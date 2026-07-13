#!/usr/bin/env bash
# handoff 목록과 활성본을 출력한다. 활성본은 ●로 표시하고 맨 아래 "활성:"에 경로를 모은다.
# 여러 handoff가 동시에 active일 수 있다.
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
DIR="${ROOT}/.claude/handoffs"
[ -d "$DIR" ] || { echo "handoff 디렉터리 없음: $DIR"; exit 0; }

actives=()
found=""
for f in "$DIR"/*.md; do
  [ -e "$f" ] || continue
  found=1
  st="$(sed -n 's/^status: *//p' "$f" | head -1)"
  nm="$(sed -n 's/^name: *//p' "$f" | head -1)"
  base="$(basename "$f")"
  if [ "$st" = "active" ]; then
    actives+=("$f")
    printf '● %-22s %-9s %s\n' "$base" "$st" "$nm"
  else
    printf '  %-22s %-9s %s\n' "$base" "${st:-?}" "$nm"
  fi
done

[ -n "$found" ] || { echo "handoff 없음: $DIR"; exit 0; }

echo
count=${#actives[@]}
if [ "$count" -eq 0 ]; then
  echo "활성 handoff 없음"
else
  echo "활성 ${count}개:"
  for a in "${actives[@]}"; do echo "  $a"; done
fi
