#!/usr/bin/env bash
# task-pipeline 공통 헬퍼 — source 전용, 직접 실행 금지.
# 부수효과 없는 함수만 둔다. 파일·git을 변이하는 로직은 각 소유 스크립트에.
[ -n "${TP_LIB_LOADED:-}" ] && return 0
TP_LIB_LOADED=1

# ── 출력 규약 ────────────────────────────────────────────────────────────────
# 마지막 줄 = 단일 기계 토큰. exit 2=사용법 오류(die) / 1=전제 미충족·거부(fail)
# / 0=정상 완료. verify는 PASS·FAIL·ERROR·LIMIT 모두 토큰으로 알리고 exit 0 —
# 호출부는 exit code가 아니라 마지막 줄 토큰을 읽는다.
die()  { echo "error: $*" >&2; exit 2; }   # 사용법 오류 (호출부 잘못)
fail() { echo "$*"; exit 1; }              # 전제 미충족·거부 (토큰으로 종료)

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

# cycle_dir 존재 확인
require_cycle_dir() { # require_cycle_dir <dir>
  [ -d "$1" ] || die "사이클 디렉토리 없음: $1"
}
