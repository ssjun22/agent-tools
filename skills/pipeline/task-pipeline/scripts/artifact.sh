#!/usr/bin/env bash
# artifact.sh — 산출물(.md) frontmatter의 유일한 스탬핑 지점.
# 메인이 소유하는 산출물(clarify·explore·plan placeholder)의 시각·status 기록을
# 손 편집 대신 여기로 — 시각 미치환·역전 leak의 원인 제거.
#
# usage:
#   artifact.sh stamp <file> --stage <s> --status <st> [--round N] [--started ISO] [--finished ISO]
#
# 동작:
#   파일에 frontmatter 없음  → 옵션으로 frontmatter를 생성해 앞에 붙임 (explore 응답 본문 등)
#   frontmatter 있음         → <ISO8601> placeholder를 실제 시각으로 치환하고
#                              --status가 주어지면 status도 갱신 (planner 산출물 등)
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
. "$SCRIPT_DIR/lib.sh"

cmd_stamp() {
  [ $# -ge 1 ] || die "usage: artifact.sh stamp <file> --stage <s> --status <st> [--round N] [--started ISO] [--finished ISO]"
  local file="$1"; shift
  [ -f "$file" ] || die "파일 없음: $file"
  local stage="" status="" round="" started="" finished=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --stage)    stage="$2";    shift 2 ;;
      --status)   status="$2";   shift 2 ;;
      --round)    round="$2";    shift 2 ;;
      --started)  started="$2";  shift 2 ;;
      --finished) finished="$2"; shift 2 ;;
      *) die "알 수 없는 옵션: $1" ;;
    esac
  done
  local now; now="$(iso_now)"
  started="${started:-$now}"
  finished="${finished:-$now}"
  if [ -n "$status" ] && ! in_enum "$status" "$STAGE_STATUS_ENUM"; then
    fail "BAD_STATUS $status"
  fi

  local tmp; tmp="$(mktemp)"
  if [ "$(head -n1 "$file")" = "---" ]; then
    # 기존 frontmatter: placeholder 치환 + status 갱신 (본문의 <ISO8601>은 건드리지 않음)
    awk -v started="$started" -v finished="$finished" -v status="$status" '
      BEGIN { infm=0; done=0 }
      NR==1 && $0=="---" { infm=1; print; next }
      infm && !done && $0=="---" { done=1; print; next }
      infm && !done {
        if ($0 ~ /^started_at:/)  { sub(/<ISO8601>/, started) }
        if ($0 ~ /^finished_at:/) { sub(/<ISO8601>/, finished) }
        if (status != "" && $0 ~ /^status:/) { $0 = "status: " status }
        print; next
      }
      { print }
    ' "$file" > "$tmp" && mv "$tmp" "$file"
    echo "OK stamped"
  else
    # frontmatter 없음: 생성해 prepend (stage·status 필수)
    [ -n "$stage" ]  || die "frontmatter 생성에는 --stage 필요"
    [ -n "$status" ] || die "frontmatter 생성에는 --status 필요"
    {
      echo "---"
      echo "stage: $stage"
      [ -n "$round" ] && echo "round: $round"
      echo "status: $status"
      echo "started_at: $started"
      echo "finished_at: $finished"
      echo "---"
      echo ""
      cat "$file"
    } > "$tmp" && mv "$tmp" "$file"
    echo "OK created"
  fi
}

cmd="${1:-}"; [ $# -gt 0 ] && shift || true
case "$cmd" in
  stamp) cmd_stamp "$@" ;;
  *) sed -n '2,12p' "$0" >&2; exit 2 ;;
esac
