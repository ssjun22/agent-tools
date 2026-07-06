#!/usr/bin/env bash
# task-pipeline 공통 헬퍼 — source 전용, 직접 실행 금지.
# 부수효과 없는 함수만 둔다. 파일·git을 변이하는 로직은 각 소유 스크립트에.
[ -n "${TP_LIB_LOADED:-}" ] && return 0
TP_LIB_LOADED=1

# ── enum (원천: references/state-files.md) ──────────────────────────────────
TASK_STATUS_ENUM="pending in_progress done failed skipped"
STAGE_STATUS_ENUM="completed blocked cancelled failed"
STEP_NAME_ENUM="clarify explore plan generate refactor evaluate"
FINAL_STEP_ENUM="done handoff cancelled failed"

# ── 출력 규약 ────────────────────────────────────────────────────────────────
# 마지막 줄 = 단일 기계 토큰. exit 0=정상 / 1=검증 실패 / 2=사용법 오류.
die()  { echo "error: $*" >&2; exit 2; }   # 사용법 오류 (호출부 잘못)
fail() { echo "$*"; exit 1; }              # 검증 실패 (토큰으로 종료)

need_jq() { command -v jq >/dev/null 2>&1 || die "jq 없음 — task-pipeline 헬퍼에 필요"; }
iso_now() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

in_enum() { # in_enum <value> <space-separated-enum>
  local v="$1" e
  for e in $2; do [ "$v" = "$e" ] && return 0; done
  return 1
}

# 파일 상단 frontmatter에서 `key:` 첫 값을 뽑는다 (없으면 빈 문자열)
fm_field() { # fm_field <file> <key>
  awk -v k="$2" '
    NR==1 && $0!="---" { exit }
    NR>1 && $0=="---"  { exit }
    { sub(/\r$/,"") }
    $0 ~ "^"k":" { sub("^"k":[ \t]*",""); print; exit }
  ' "$1"
}

# jq 원자 변이 (임시파일 + mv)
jq_inplace() { # jq_inplace <file> <jq-args...>
  local f="$1"; shift
  local tmp; tmp="$(mktemp)"
  jq "$@" "$f" > "$tmp" && mv "$tmp" "$f"
}

# .claude/task-pipeline/ 하위 경로가 섞여 있으면 1 (git 대상 방어)
has_pipeline_path() { # has_pipeline_path <files...>
  local p
  for p in "$@"; do
    case "$p" in .claude/task-pipeline/*|*/.claude/task-pipeline/*) return 0 ;; esac
  done
  return 1
}

# cycle_dir 존재 + 내부 JSON 경로 헬퍼
require_cycle_dir() { # require_cycle_dir <dir>
  [ -d "$1" ] || die "사이클 디렉토리 없음: $1"
}
tasks_json()    { echo "$1/tasks.json"; }
progress_json() { echo "$1/progress.json"; }
