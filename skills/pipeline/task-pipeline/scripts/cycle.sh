#!/usr/bin/env bash
# task-pipeline 결정론적 헬퍼.
#
# 메인이 손으로 하던 기계적 작업 중, 데이터상 leak이 입증됐거나(시각 미치환·역전)
# JSON 수기 편집이 위험한 부분만 스크립트로 내린다. 정책(게이트·분기·설계)은 메인이 한다.
#
#   cycle.sh doctor <cycle_dir>
#       사이클 산출물을 read-only로 검증. placeholder 잔존 / tasks.json 스키마 /
#       스테이지 frontmatter status·시각 단조성을 점검. 문제 있으면 exit 1.
#       archive 직전에 돌려 깨진 상태가 보존되는 걸 막는다.
#
#   cycle.sh task-update <tasks_json> <task_id> [--status S] [--commit H] [--started ISO] [--finished ISO]
#       tasks.json의 한 태스크를 jq로 안전하게 변이(임시파일+mv 원자적). 수기 JSON 편집을 대체.
#
# 플랫폼: macOS(BSD) 전제 — date -u, jq(/usr/local/bin/jq) 사용. GNU 전용 플래그 안 씀.
set -euo pipefail

# tasks.json 태스크 status enum (state-files.md)
TASK_STATUS_ENUM="pending in_progress done failed skipped"
# 스테이지 산출물 frontmatter status enum
STAGE_STATUS_ENUM="completed blocked cancelled failed"

die()  { echo "error: $*" >&2; exit 2; }
need_jq() { command -v jq >/dev/null 2>&1 || die "jq 없음 — task-pipeline 헬퍼에 필요"; }

in_enum() { # in_enum <value> <space-separated-enum>
  local v="$1" e
  for e in $2; do [ "$v" = "$e" ] && return 0; done
  return 1
}

# 파일 상단 frontmatter에서 `key:` 첫 값을 뽑는다 (없으면 빈 문자열)
fm_field() { # fm_field <file> <key>
  awk -v k="$2" '
    NR==1 && $0!="---" { exit }      # frontmatter 없음
    NR>1 && $0=="---"  { exit }      # frontmatter 끝
    { sub(/\r$/,"") }
    $0 ~ "^"k":" { sub("^"k":[ \t]*",""); print; exit }
  ' "$1"
}

# ── doctor ───────────────────────────────────────────────────────────────────
doctor() {
  [ $# -eq 1 ] || die "usage: cycle.sh doctor <cycle_dir>"
  local dir="$1"
  [ -d "$dir" ] || die "디렉토리 없음: $dir"
  need_jq
  local issues=0
  note() { echo "  ✗ $*"; issues=$((issues+1)); }

  echo "doctor: $dir"

  # 1) placeholder 잔존 (시각 미치환·init 미치환의 직접 신호)
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
    # 각 태스크: id 존재 + status enum
    local n bad_status missing_id
    n="$(jq '.tasks | length' "$tj")"
    [ "$n" = "0" ] && echo "  · tasks 비어 있음 (plan 전이면 정상)"
    missing_id="$(jq -r '[.tasks[] | select((.id // "") == "")] | length' "$tj")"
    [ "$missing_id" != "0" ] && note "tasks.json: id 없는 태스크 ${missing_id}개"
    bad_status="$(jq -r --arg e "$TASK_STATUS_ENUM" '
      ($e | split(" ")) as $enum
      | [.tasks[] | select((.status // "") as $s | ($enum | index($s)) | not) | .id] | join(", ")
    ' "$tj")"
    [ -n "$bad_status" ] && note "tasks.json: status enum 위반 — $bad_status"
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
    # 07-context-update 등 일부는 frontmatter status가 없을 수 있음 — 있을 때만 enum 검사
    if [ -n "$st" ] && ! in_enum "$st" "$STAGE_STATUS_ENUM"; then
      note "$base: frontmatter status enum 위반 — '$st'"
    fi
    s_at="$(fm_field "$f" started_at)"
    f_at="$(fm_field "$f" finished_at)"
    # 둘 다 실제 값(placeholder 아님)일 때만 단조성 — placeholder는 위 1)에서 이미 잡음
    if [ -n "$s_at" ] && [ -n "$f_at" ] && \
       [ "${s_at#*<}" = "$s_at" ] && [ "${f_at#*<}" = "$f_at" ]; then
      # ISO8601 UTC(Z) 동일 포맷이면 문자열 비교가 시간 비교와 일치
      if [[ "$s_at" > "$f_at" ]]; then
        note "$base: 시각 역전 (started_at $s_at > finished_at $f_at)"
      fi
    fi
  done

  if [ "$issues" -eq 0 ]; then
    echo "✓ 이상 없음"
    return 0
  fi
  echo "✗ 문제 ${issues}건 — archive 전에 메인이 해소할 것"
  return 1
}

# ── task-update ──────────────────────────────────────────────────────────────
task_update() {
  [ $# -ge 2 ] || die "usage: cycle.sh task-update <tasks_json> <task_id> [--status S] [--commit H] [--started ISO] [--finished ISO]"
  need_jq
  local tj="$1" id="$2"; shift 2
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
    die "status enum 위반: '$status' (허용: $TASK_STATUS_ENUM)"
  fi
  if [ "$(jq --arg id "$id" '[.tasks[]|select(.id==$id)]|length' "$tj")" = "0" ]; then
    die "태스크 없음: $id"
  fi

  local tmp; tmp="$(mktemp)"
  jq \
    --arg id "$id" --arg status "$status" --arg commit "$commit" \
    --arg started "$started" --arg finished "$finished" '
    .tasks |= map(
      if .id == $id then
          (if $status   != "" then .status      = $status   else . end)
        | (if $commit   != "" then .commit      = $commit   else . end)
        | (if $started  != "" then .started_at  = $started  else . end)
        | (if $finished != "" then .finished_at = $finished else . end)
      else . end)
  ' "$tj" > "$tmp" && mv "$tmp" "$tj"
  echo "task-update: $id ←$([ -n "$status" ] && echo " status=$status")$([ -n "$commit" ] && echo " commit=$commit")$([ -n "$started" ] && echo " started=$started")$([ -n "$finished" ] && echo " finished=$finished")"
}

# ── dispatch ─────────────────────────────────────────────────────────────────
cmd="${1:-}"; [ $# -gt 0 ] && shift || true
case "$cmd" in
  doctor)      doctor "$@" ;;
  task-update) task_update "$@" ;;
  *) cat >&2 <<'EOF'
task-pipeline 헬퍼
usage:
  cycle.sh doctor <cycle_dir>
  cycle.sh task-update <tasks_json> <task_id> [--status S] [--commit H] [--started ISO] [--finished ISO]
EOF
     exit 2 ;;
esac
