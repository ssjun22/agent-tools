#!/usr/bin/env bash
# state.sh — progress.json · tasks.json · 사이클 라이프사이클의 유일한 변이 지점.
# git과 코드 파일은 절대 건드리지 않는다 (git은 git-ops.sh 관할).
#
# usage:
#   state.sh init "<request>"
#   state.sh tasks-init <cycle_dir>
#   state.sh task-update <cycle_dir> <task_id> [--status S] [--commit H] [--started ISO] [--finished ISO]
#   state.sh step-start <cycle_dir> <step>
#   state.sh step-finish <cycle_dir> <step> <state>
#   state.sh set-branch <cycle_dir> <branch> <base_hash>
#   state.sh round-start <cycle_dir> <round>
#   state.sh round-finish <cycle_dir> <round> <result>
#   state.sh round-reset <cycle_dir>
#   state.sh archive <cycle_dir> <final_step>
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
. "$SCRIPT_DIR/lib.sh"
TPL_DIR="$SCRIPT_DIR/../templates"

# ── init ─────────────────────────────────────────────────────────────────────
cmd_init() {
  [ $# -eq 1 ] || die "usage: state.sh init \"<request>\""
  need_jq
  local req="$1"
  local ts; ts="$(date -u +"%Y-%m-%dT%H-%M-%S")"
  local dir=".claude/task-pipeline/$ts"
  [ -e "$dir" ] && fail "EXISTS $dir"
  [ -f "$TPL_DIR/progress.template.json" ] || die "템플릿 없음: $TPL_DIR/progress.template.json"
  [ -f "$TPL_DIR/tasks.template.json" ]    || die "템플릿 없음: $TPL_DIR/tasks.template.json"
  mkdir -p "$dir"
  local now; now="$(iso_now)"
  # placeholder는 jq가 실제 값으로 덮어쓴다 — 치환 누락이 구조적으로 불가능
  jq --arg t "$now" --arg r "$req" \
     '.started_at=$t | .request=$r | .steps.clarify.started_at=$t' \
     "$TPL_DIR/progress.template.json" > "$dir/progress.json"
  cp "$TPL_DIR/tasks.template.json" "$dir/tasks.json"
  echo "OK $dir"
}

# ── tasks-init ───────────────────────────────────────────────────────────────
# 03-plan.md의 ```json tasks fenced 블록에서 tasks.json을 생성.
# 같은 stage 내 touched_files 비겹침을 여기서 기계 검증한다 (게이트 ② 전 실행 권장).
cmd_tasks_init() {
  [ $# -eq 1 ] || die "usage: state.sh tasks-init <cycle_dir>"
  need_jq
  local dir="$1"; require_cycle_dir "$dir"
  local plan="$dir/03-plan.md"
  [ -f "$plan" ] || die "plan 없음: $plan"

  local block
  block="$(awk '/^```json tasks[ \t]*$/{f=1;next} f&&/^```[ \t]*$/{exit} f{print}' "$plan")"
  [ -n "$block" ] || fail "NO_BLOCK"
  echo "$block" | jq empty 2>/dev/null || fail "SCHEMA_VIOLATION json-parse"

  # 구조 검증: groups[].id/title, tasks[] 필수 필드
  local viol
  viol="$(echo "$block" | jq -r '
    def miss(o; k): (o[k] // null) == null;
    [ (if (.groups|type) != "array" then "groups-not-array" else empty end),
      (if (.tasks|type)  != "array" then "tasks-not-array"  else empty end),
      (.groups // [] | .[] | select(miss(.;"id") or miss(.;"title")) | "group-missing-field"),
      (.tasks  // [] | .[] | select(
          miss(.;"id") or miss(.;"title") or miss(.;"group") or miss(.;"stage")
          or ((.touched_files|type) != "array") or ((.touched_files|length) == 0)
          or ((.depends_on|type)   != "array")
        ) | "task-missing-field:\(.id // "?")")
    ] | unique | join(" ")')"
  [ -z "$viol" ] || fail "SCHEMA_VIOLATION $viol"

  # 참조 무결성: 태스크의 group이 groups에 존재, depends_on 대상이 실존
  local badref
  badref="$(echo "$block" | jq -r '
    ([.groups[].id]) as $g | ([.tasks[].id]) as $ids |
    [ (.tasks[] | select((.group as $x | $g | index($x)) | not) | "unknown-group:\(.id)"),
      (.tasks[] | .id as $t | .depends_on[]? | select((. as $d | $ids | index($d)) | not) | "unknown-dep:\($t)->\(.)")
    ] | join(" ")')"
  [ -z "$badref" ] || fail "SCHEMA_VIOLATION $badref"

  # 같은 stage 내 touched_files 비겹침 (planner.md 제약을 코드로 강제)
  local overlap
  overlap="$(echo "$block" | jq -r '
    .tasks | group_by(.stage)[] |
    { stage: .[0].stage,
      dups: ([.[].touched_files[]] | group_by(.) | map(select(length>1) | .[0])) } |
    select((.dups|length) > 0) | "\(.stage) \(.dups|join(","))"' | head -n1)"
  [ -z "$overlap" ] || fail "OVERLAP $overlap"

  local tmp; tmp="$(mktemp)"
  echo "$block" | jq '{
    groups: .groups,
    tasks: [ .tasks[] | . + {status:"pending", commit:null, started_at:null, finished_at:null} ]
  }' > "$tmp" && mv "$tmp" "$(tasks_json "$dir")"
  echo "OK $(echo "$block" | jq '.tasks|length')"
}

# ── task-update (구 cycle.sh에서 이관 — 인자 1이 cycle_dir로 변경) ─────────────
cmd_task_update() {
  [ $# -ge 2 ] || die "usage: state.sh task-update <cycle_dir> <task_id> [--status S] [--commit H] [--started ISO] [--finished ISO]"
  need_jq
  local dir="$1" id="$2"; shift 2
  require_cycle_dir "$dir"
  local tj; tj="$(tasks_json "$dir")"
  local status="" commit="" started="" finished=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --status)   status="$2";   shift 2 ;;
      --commit)   commit="$2";   shift 2 ;;
      --started)  started="$2";  shift 2 ;;
      --finished) finished="$2"; shift 2 ;;
      *) die "알 수 없는 옵션: $1" ;;
    esac
  done
  [ -f "$tj" ] || die "tasks.json 없음: $tj"
  jq empty "$tj" 2>/dev/null || die "tasks.json JSON 파싱 실패: $tj"
  if [ -n "$status" ] && ! in_enum "$status" "$TASK_STATUS_ENUM"; then
    fail "BAD_STATUS $status"
  fi
  if [ "$(jq --arg id "$id" '[.tasks[]|select(.id==$id)]|length' "$tj")" = "0" ]; then
    fail "NO_TASK $id"
  fi
  jq_inplace "$tj" \
    --arg id "$id" --arg status "$status" --arg commit "$commit" \
    --arg started "$started" --arg finished "$finished" '
    .tasks |= map(
      if .id == $id then
          (if $status   != "" then .status      = $status   else . end)
        | (if $commit   != "" then .commit      = $commit   else . end)
        | (if $started  != "" then .started_at  = $started  else . end)
        | (if $finished != "" then .finished_at = $finished else . end)
      else . end)'
  echo "OK $id"
}

# ── step-start / step-finish ─────────────────────────────────────────────────
cmd_step_start() {
  [ $# -eq 2 ] || die "usage: state.sh step-start <cycle_dir> <step>"
  need_jq
  local dir="$1" step="$2"; require_cycle_dir "$dir"
  in_enum "$step" "$STEP_NAME_ENUM" || fail "BAD_STEP $step"
  jq_inplace "$(progress_json "$dir")" --arg s "$step" --arg t "$(iso_now)" '
    .current_step = $s
    | .steps[$s].state = "in_progress"
    | .steps[$s].started_at = (.steps[$s].started_at // $t)'
  echo "OK $step"
}

cmd_step_finish() {
  [ $# -eq 3 ] || die "usage: state.sh step-finish <cycle_dir> <step> <state>"
  need_jq
  local dir="$1" step="$2" state="$3"; require_cycle_dir "$dir"
  in_enum "$step"  "$STEP_NAME_ENUM"                     || fail "BAD_STEP $step"
  in_enum "$state" "completed failed skipped in_progress" || fail "BAD_STATE $state"
  jq_inplace "$(progress_json "$dir")" --arg s "$step" --arg st "$state" --arg t "$(iso_now)" '
    .steps[$s].state = $st
    | (if $st != "in_progress" then .steps[$s].finished_at = $t else . end)'
  echo "OK $step=$state"
}

# ── set-branch (git-ops.sh preflight가 내부 호출) ────────────────────────────
cmd_set_branch() {
  [ $# -eq 3 ] || die "usage: state.sh set-branch <cycle_dir> <branch> <base_hash>"
  need_jq
  local dir="$1"; require_cycle_dir "$dir"
  jq_inplace "$(progress_json "$dir")" --arg b "$2" --arg h "$3" \
    '.branch = $b | .base_commit = $h'
  echo "OK $2 $3"
}

# ── round-start / round-finish / round-reset ─────────────────────────────────
cmd_round_start() {
  [ $# -eq 2 ] || die "usage: state.sh round-start <cycle_dir> <round>"
  need_jq
  local dir="$1" r="$2"; require_cycle_dir "$dir"
  case "$r" in ''|*[!0-9]*) fail "BAD_ROUND $r" ;; esac
  jq_inplace "$(progress_json "$dir")" --argjson r "$r" --arg t "$(iso_now)" '
    .current_round = $r
    | .steps.evaluate.rounds += [{round: $r, started_at: $t}]'
  echo "OK $r"
}

cmd_round_finish() {
  [ $# -eq 3 ] || die "usage: state.sh round-finish <cycle_dir> <round> <PASS|FAIL>"
  need_jq
  local dir="$1" r="$2" res="$3"; require_cycle_dir "$dir"
  in_enum "$res" "PASS FAIL" || fail "BAD_RESULT $res"
  jq_inplace "$(progress_json "$dir")" --argjson r "$r" --arg res "$res" --arg t "$(iso_now)" '
    .steps.evaluate.rounds |= map(
      if .round == $r then . + {result: $res, finished_at: $t} else . end)'
  echo "OK $r=$res"
}

cmd_round_reset() {
  # ④ 분기 "재시도 (라운드 리셋)" 전용 — commit 필드는 보존 (git history 추적용)
  [ $# -eq 1 ] || die "usage: state.sh round-reset <cycle_dir>"
  need_jq
  local dir="$1"; require_cycle_dir "$dir"
  local n; n="$(jq '.tasks|length' "$(tasks_json "$dir")")"
  jq_inplace "$(tasks_json "$dir")" '
    .tasks |= map(. + {status:"pending", started_at:null, finished_at:null})'
  jq_inplace "$(progress_json "$dir")" '
    .current_round = 1
    | .current_step = "generate"
    | .steps.evaluate.rounds = []
    | .steps.generate.state = "pending" | .steps.generate.finished_at = null
    | .steps.refactor.state = "pending" | .steps.refactor.finished_at = null
    | .steps.evaluate.state = "pending" | .steps.evaluate.finished_at = null'
  echo "OK $n"
}

# ── archive (doctor 내장 — 통과해야만 mv) ────────────────────────────────────
cmd_archive() {
  [ $# -eq 2 ] || die "usage: state.sh archive <cycle_dir> <done|handoff|cancelled|failed>"
  need_jq
  local dir="$1" final="$2"; require_cycle_dir "$dir"
  in_enum "$final" "$FINAL_STEP_ENUM" || fail "BAD_FINAL $final"
  if ! bash "$SCRIPT_DIR/inspect.sh" doctor "$dir"; then
    fail "DOCTOR_FAILED"
  fi
  jq_inplace "$(progress_json "$dir")" --arg f "$final" --arg t "$(iso_now)" \
    '.current_step = $f | .finished_at = $t'
  local root archived
  root="$(dirname "$dir")"
  archived="$root/archived"
  mkdir -p "$archived"
  mv "$dir" "$archived/"
  echo "OK $archived/$(basename "$dir")"
}

# ── dispatch ─────────────────────────────────────────────────────────────────
cmd="${1:-}"; [ $# -gt 0 ] && shift || true
case "$cmd" in
  init)         cmd_init "$@" ;;
  tasks-init)   cmd_tasks_init "$@" ;;
  task-update)  cmd_task_update "$@" ;;
  step-start)   cmd_step_start "$@" ;;
  step-finish)  cmd_step_finish "$@" ;;
  set-branch)   cmd_set_branch "$@" ;;
  round-start)  cmd_round_start "$@" ;;
  round-finish) cmd_round_finish "$@" ;;
  round-reset)  cmd_round_reset "$@" ;;
  archive)      cmd_archive "$@" ;;
  *) sed -n '2,14p' "$0" >&2; exit 2 ;;
esac
