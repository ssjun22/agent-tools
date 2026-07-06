#!/usr/bin/env bash
# inspect.sh — read-only 보장. 이 파일의 어떤 커맨드도 파일·git·상태를 변이하지 않는다.
# 확신이 없을 때 "일단 inspect부터"가 항상 안전한 이유가 이 보장이다.
#
# usage:
#   inspect.sh doctor <cycle_dir>          사이클 상태 검증 (archive 전 필수 — state.sh archive가 내부 호출)
#   inspect.sh read-signal <file>          산출물의 기계 신호(key=value)를 표준 출력으로
#   inspect.sh status [<pipeline_root>]    활성 사이클 요약 (resume 진입점)
#   inspect.sh tasks <cycle_dir>           tasks.json 태스크별 상태 덤프 (resume 판별용)
#   inspect.sh stats [<archived_root>]     archived/ 집계 (Round1 PASS율 등)
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
. "$SCRIPT_DIR/lib.sh"

# ── doctor (구 cycle.sh에서 이관 + commit 실존 검증 추가) ─────────────────────
cmd_doctor() {
  [ $# -eq 1 ] || die "usage: inspect.sh doctor <cycle_dir>"
  local dir="$1"
  [ -d "$dir" ] || die "디렉토리 없음: $dir"
  need_jq
  local issues=0
  note() { echo "  ✗ $*"; issues=$((issues+1)); }

  echo "doctor: $dir"

  # 1) placeholder 잔존
  local hits
  hits="$(grep -rlE '<ISO8601>|__ISO8601__|__USER_REQUEST__' "$dir" 2>/dev/null || true)"
  if [ -n "$hits" ]; then
    while IFS= read -r f; do note "placeholder 미치환: ${f#$dir/}"; done <<< "$hits"
  fi

  # 2) tasks.json 구조
  local tj="$dir/tasks.json"
  if [ ! -f "$tj" ]; then
    note "tasks.json 없음"
  elif ! jq empty "$tj" 2>/dev/null; then
    note "tasks.json JSON 파싱 실패"
  else
    local n bad_status missing_id badgroup
    n="$(jq '.tasks | length' "$tj")"
    [ "$n" = "0" ] && echo "  · tasks 비어 있음 (plan 전이면 정상)"
    missing_id="$(jq -r '[.tasks[] | select((.id // "") == "")] | length' "$tj")"
    [ "$missing_id" != "0" ] && note "tasks.json: id 없는 태스크 ${missing_id}개"
    bad_status="$(jq -r --arg e "$TASK_STATUS_ENUM" '
      ($e | split(" ")) as $enum
      | [.tasks[] | select((.status // "") as $s | ($enum | index($s)) | not) | .id] | join(", ")
    ' "$tj")"
    [ -n "$bad_status" ] && note "tasks.json: status enum 위반 — $bad_status"
    badgroup="$(jq -r '
      ([.groups[]?.id]) as $g
      | [.tasks[] | select((.group as $x | $g | index($x)) | not) | .id] | join(", ")' "$tj")"
    [ -n "$badgroup" ] && note "tasks.json: groups에 없는 group 참조 — $badgroup"

    # commit 해시 실존 검증 (git repo 안일 때만) — 기록과 실제 히스토리의 괴리 탐지
    if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
      local h
      while IFS= read -r h; do
        [ -n "$h" ] || continue
        git cat-file -e "$h^{commit}" 2>/dev/null || note "tasks.json: 실존하지 않는 commit — $h"
      done < <(jq -r '.tasks[] | .commit // empty' "$tj" | sort -u)
    fi
  fi

  # 3) progress.json 파싱
  local pj="$dir/progress.json"
  if [ -f "$pj" ] && ! jq empty "$pj" 2>/dev/null; then
    note "progress.json JSON 파싱 실패"
  fi

  # 4) 스테이지 산출물 frontmatter: status enum + 시각 단조성
  local f base st s_at f_at
  for f in "$dir"/[0-9][0-9]-*.md; do
    [ -e "$f" ] || continue
    base="${f##*/}"
    st="$(fm_field "$f" status)"
    if [ -n "$st" ] && ! in_enum "$st" "$STAGE_STATUS_ENUM"; then
      note "$base: frontmatter status enum 위반 — '$st'"
    fi
    s_at="$(fm_field "$f" started_at)"
    f_at="$(fm_field "$f" finished_at)"
    if [ -n "$s_at" ] && [ -n "$f_at" ] && \
       [ "${s_at#*<}" = "$s_at" ] && [ "${f_at#*<}" = "$f_at" ]; then
      if [[ "$s_at" > "$f_at" ]]; then
        note "$base: 시각 역전 (started_at $s_at > finished_at $f_at)"
      fi
    fi
  done

  if [ "$issues" -eq 0 ]; then
    echo "OK"
    return 0
  fi
  echo "ISSUES $issues"
  return 1
}

# ── read-signal ──────────────────────────────────────────────────────────────
# 산출물의 분기 신호를 key=value 라인으로 — 메인은 이 출력만 읽고 분기표를 따른다.
cmd_read_signal() {
  [ $# -eq 1 ] || die "usage: inspect.sh read-signal <file>"
  local f="$1"
  [ -f "$f" ] || die "파일 없음: $f"
  [ "$(head -n1 "$f")" = "---" ] || fail "NO_FRONTMATTER"
  local k v
  for k in stage round target_task status; do
    v="$(fm_field "$f" "$k")"
    [ -n "$v" ] && echo "$k=$v"
  done
  # evaluate 산출물의 Verdict (본문 마지막 `## Verdict:` 라인 — 없으면 생략)
  v="$(grep -E '^## Verdict:' "$f" 2>/dev/null | tail -n1 | sed 's/^## Verdict:[ \t]*//' || true)"
  [ -n "$v" ] && echo "verdict=$v"
  echo "OK"
}

# ── status (resume 진입점) ───────────────────────────────────────────────────
cmd_status() {
  local root="${1:-.claude/task-pipeline}"
  need_jq
  [ -d "$root" ] || fail "NO_ACTIVE"
  local d found=0
  for d in "$root"/*/; do
    d="${d%/}"
    [ "$(basename "$d")" = "archived" ] && continue
    [ -f "$d/progress.json" ] || continue
    found=$((found+1))
    jq -r --arg d "$d" '
      "cycle=\($d)",
      "current_step=\(.current_step)",
      "current_round=\(.current_round // "-")",
      "branch=\(.branch // "-")",
      "base_commit=\(.base_commit // "-")"' "$d/progress.json"
    if [ -f "$d/tasks.json" ]; then
      jq -r '"tasks=" + ([.tasks[].status] | group_by(.) | map("\(.[0]):\(length)") | join(","))' "$d/tasks.json"
    fi
    echo "---"
  done
  [ "$found" -gt 0 ] || fail "NO_ACTIVE"
  echo "OK $found"
}

# ── stats (자기 측정 — archived/ 집계) ───────────────────────────────────────
cmd_stats() {
  local root="${1:-.claude/task-pipeline/archived}"
  need_jq
  [ -d "$root" ] || fail "NO_ARCHIVE"
  local d total=0 r1_pass=0 r1_total=0 rounds_sum=0 rounds_n=0
  local finals=""    # macOS bash 3.2 호환 — 연관 배열 대신 라인 누적 후 uniq -c
  for d in "$root"/*/; do
    d="${d%/}"
    [ -f "$d/progress.json" ] || continue
    total=$((total+1))
    local fs r1 nr
    fs="$(jq -r '.current_step // "?"' "$d/progress.json")"
    finals="$finals$fs"$'\n'
    nr="$(jq -r '.steps.evaluate.rounds | length' "$d/progress.json")"
    if [ "$nr" -gt 0 ]; then
      rounds_sum=$((rounds_sum+nr)); rounds_n=$((rounds_n+1))
      r1="$(jq -r '.steps.evaluate.rounds[0].result // "?"' "$d/progress.json")"
      r1_total=$((r1_total+1))
      [ "$r1" = "PASS" ] && r1_pass=$((r1_pass+1))
    fi
  done
  [ "$total" -gt 0 ] || fail "NO_ARCHIVE"
  echo "cycles=$total"
  printf '%s' "$finals" | sort | uniq -c | awk '{print "final."$2"="$1}'
  if [ "$r1_total" -gt 0 ]; then
    echo "round1_pass_rate=$r1_pass/$r1_total"
  fi
  if [ "$rounds_n" -gt 0 ]; then
    echo "avg_rounds=$(awk -v s="$rounds_sum" -v n="$rounds_n" 'BEGIN{printf "%.1f", s/n}')"
  fi
  echo "OK"
}

# ── tasks (per-task 덤프 — resume 판별용) ─────────────────────────────────────
# tasks.json 한 태스크당 한 줄로 id·status·commit·group·stage를 뱉는다.
# status의 집계(tasks=pending:2,done:1)로는 '어느' 태스크가 미갱신인지 못 가리므로,
# generate 재개 시 산출물 frontmatter(read-signal)와 대조할 원천을 여기서 제공한다.
cmd_tasks() {
  [ $# -eq 1 ] || die "usage: inspect.sh tasks <cycle_dir>"
  local dir="$1"; require_cycle_dir "$dir"
  need_jq
  local tj; tj="$(tasks_json "$dir")"
  [ -f "$tj" ] || fail "NO_TASKS"
  jq empty "$tj" 2>/dev/null || fail "BAD_JSON"
  jq -r '.tasks[] | "task=\(.id) status=\(.status) commit=\(.commit // "-") group=\(.group) stage=\(.stage)"' "$tj"
  echo "OK $(jq '.tasks | length' "$tj")"
}

# ── dispatch ─────────────────────────────────────────────────────────────────
cmd="${1:-}"; [ $# -gt 0 ] && shift || true
case "$cmd" in
  doctor)      cmd_doctor "$@" ;;
  read-signal) cmd_read_signal "$@" ;;
  status)      cmd_status "$@" ;;
  tasks)       cmd_tasks "$@" ;;
  stats)       cmd_stats "$@" ;;
  *) sed -n '2,10p' "$0" >&2; exit 2 ;;
esac
