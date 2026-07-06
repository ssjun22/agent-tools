#!/usr/bin/env bash
# git-ops.sh — git 저장소·워킹트리에 쓰는 코드가 존재하는 *유일한* 파일.
# 불변식: 파이프라인의 어떤 컴포넌트도 (메인·refactorer 포함) raw git 변이 명령을
# 직접 실행하지 않는다. 전부 이 스크립트 경유.
#
# usage:
#   git-ops.sh preflight <branch> <cycle_dir>
#   git-ops.sh commit-group <cycle_dir> <group_id> [--retry <round> -m "<사유 요약>"]
#   git-ops.sh clean-task <cycle_dir> <task_id>
#   git-ops.sh commit-refactor <cycle_dir> -m "<summary>" -- <files...>
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
. "$SCRIPT_DIR/lib.sh"

BRANCH_RE='^[a-z0-9][a-z0-9/_-]{0,63}$'

# ── preflight ────────────────────────────────────────────────────────────────
# 브랜치명 검증 → git 3검사 → 브랜치 생성 → base 커밋을 progress.json에 기록.
# base가 세션 컨텍스트가 아닌 디스크에 남으므로 resume 후에도 evaluate 주입이 가능.
cmd_preflight() {
  [ $# -eq 2 ] || die "usage: git-ops.sh preflight <branch> <cycle_dir>"
  local b="$1" dir="$2"; require_cycle_dir "$dir"
  echo "$b" | grep -Eq "$BRANCH_RE" || fail "BAD_NAME"
  git rev-parse --is-inside-work-tree >/dev/null 2>&1 || fail "NOT_GIT"
  [ -z "$(git status --porcelain -- ':!.claude/task-pipeline')" ] || fail "DIRTY"
  if git show-ref --verify --quiet "refs/heads/$b"; then
    # 브랜치가 이미 있음 — resume 중 preflight 중간사(checkout 후 set-branch 전 중단)인지 판별.
    # 지금 그 브랜치 위에 있고 progress.json에 미기록(또는 동일 기록)이면 우리 것 → base=HEAD로 조정(멱등).
    need_jq
    local cur rec
    cur="$(git rev-parse --abbrev-ref HEAD)"
    rec="$(jq -r '.branch // ""' "$(progress_json "$dir")")"
    if [ "$cur" = "$b" ] && { [ -z "$rec" ] || [ "$rec" = "$b" ]; }; then
      local base0; base0="$(git rev-parse HEAD)"
      bash "$SCRIPT_DIR/state.sh" set-branch "$dir" "$b" "$base0" >/dev/null
      echo "OK $base0"
      return 0
    fi
    fail "BRANCH_EXISTS"
  fi
  git checkout -q -b "$b"
  local base; base="$(git rev-parse HEAD)"
  bash "$SCRIPT_DIR/state.sh" set-branch "$dir" "$b" "$base" >/dev/null
  echo "OK $base"
}

# ── 내부: 태스크의 이번 round generate 산출물 경로 ────────────────────────────
gen_artifact() { # gen_artifact <cycle_dir> <task_id> <round>
  local dir="$1" id="$2" round="$3"
  if [ "$round" -ge 2 ]; then
    echo "$dir/04-generate-$id-R$round.md"
  else
    echo "$dir/04-generate-$id.md"
  fi
}

# ── commit-group ─────────────────────────────────────────────────────────────
# group의 completed 태스크만 골라 1커밋. 판정은 generate 산출물 frontmatter에서
# 직접 읽는다 (메인의 옮겨 적기 없음). 커밋 후 tasks.json 기록까지 원자적
# (기록은 state.sh task-update 내부 호출 — 파일 소유권 유지).
cmd_commit_group() {
  [ $# -ge 2 ] || die "usage: git-ops.sh commit-group <cycle_dir> <group_id> [--retry <round> -m \"<사유>\"]"
  need_jq
  local dir="$1" group="$2"; shift 2
  require_cycle_dir "$dir"
  local round=1 summary=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --retry) round="$2"; shift 2 ;;
      -m)      summary="$2"; shift 2 ;;
      *) die "알 수 없는 옵션: $1" ;;
    esac
  done
  if [ "$round" -ge 2 ] && [ -z "$summary" ]; then
    die "--retry에는 -m \"<evaluate 실패 사유 요약>\"이 필요"
  fi
  local tj; tj="$(tasks_json "$dir")"
  [ -f "$tj" ] || die "tasks.json 없음: $tj"

  # group 메타 (subject의 type·제목 원천 — planner JSON 블록에서 tasks-init이 적재)
  local gmeta title type
  gmeta="$(jq -r --arg g "$group" '.groups[]? | select(.id==$g) | "\(.type // "")\t\(.title // "")"' "$tj")"
  [ -n "$gmeta" ] || fail "NO_GROUP $group"
  type="${gmeta%%$'\t'*}"; title="${gmeta#*$'\t'}"

  # 대상 판정: 산출물 frontmatter status == completed
  local ids=() files=() id st art
  while IFS= read -r id; do
    art="$(gen_artifact "$dir" "$id" "$round")"
    [ -f "$art" ] || continue                      # 이번 round 미처리 태스크
    st="$(fm_field "$art" status)"
    [ "$st" = "completed" ] || continue
    ids+=("$id")
    while IFS= read -r f; do files+=("$f"); done \
      < <(jq -r --arg id "$id" '.tasks[] | select(.id==$id) | .touched_files[]' "$tj")
  done < <(jq -r --arg g "$group" '.tasks[] | select(.group==$g) | .id' "$tj")
  [ "${#ids[@]}" -gt 0 ] || fail "NO_COMPLETED $group"

  if has_pipeline_path "${files[@]}"; then
    fail "REFUSED_PIPELINE_PATH"
  fi

  # subject: round 1은 plan group 메타, retry는 fix + 사유
  local subject
  if [ "$round" -ge 2 ]; then
    subject="fix($group): $summary"
  else
    subject="${type:-feat}($group): $title"
  fi
  # 본문 bullet: 태스크 제목
  local body=""
  for id in "${ids[@]}"; do
    body="$body- $id $(jq -r --arg id "$id" '.tasks[]|select(.id==$id)|.title' "$tj")"$'\n'
  done

  git add -- "${files[@]}"
  local hash
  if git diff --cached --quiet -- "${files[@]}"; then
    # 스테이징할 변경이 없음 = 이 group의 변경이 이미 HEAD에 커밋된 상태
    # (resume 후 고아 커밋 — commit 성공 뒤 tasks.json 기록 전 중단 — 또는 순수 재실행).
    # 새 커밋을 만들지 않고, 순차 소유 불변식상 그 group의 커밋인 HEAD로 tasks.json을 조정한다(멱등).
    hash="$(git rev-parse HEAD)"
  else
    if ! git commit -q -m "$subject" -m "$body"; then
      git reset -q -- "${files[@]}" || true         # 더러운 index를 다음 커밋에 안 물림
      fail "COMMIT_FAILED"
    fi
    hash="$(git rev-parse HEAD)"
  fi
  local now; now="$(iso_now)"
  for id in "${ids[@]}"; do
    bash "$SCRIPT_DIR/state.sh" task-update "$dir" "$id" \
      --status done --commit "$hash" --finished "$now" >/dev/null
  done
  echo "OK $hash $(IFS=,; echo "${ids[*]}")"
}

# ── clean-task ───────────────────────────────────────────────────────────────
# blocked/failed 태스크의 미커밋 잔존물 정리. 경로는 tasks.json에서 직접 읽고,
# completed 태스크·이미 staged된 파일은 거부 — 멀쩡한 변경 파괴를 enum으로 차단.
cmd_clean_task() {
  [ $# -eq 2 ] || die "usage: git-ops.sh clean-task <cycle_dir> <task_id>"
  need_jq
  local dir="$1" id="$2"; require_cycle_dir "$dir"
  local tj; tj="$(tasks_json "$dir")"
  [ "$(jq -r --arg id "$id" '[.tasks[]|select(.id==$id)]|length' "$tj")" != "0" ] || fail "NO_TASK $id"

  # 이 태스크의 최신 round 산출물에서 status 판정
  local art="" f n
  for f in "$dir/04-generate-$id"-R*.md "$dir/04-generate-$id.md"; do
    [ -f "$f" ] || continue
    if [ -z "$art" ]; then art="$f"
    else
      # -R<N> 최대값 선택 (plain은 round 1)
      n1="$(echo "$art" | sed -n 's/.*-R\([0-9]*\)\.md/\1/p')"; n1="${n1:-1}"
      n2="$(echo "$f"   | sed -n 's/.*-R\([0-9]*\)\.md/\1/p')"; n2="${n2:-1}"
      [ "$n2" -gt "$n1" ] && art="$f"
    fi
  done
  [ -n "$art" ] || fail "NO_ARTIFACT $id"
  local st; st="$(fm_field "$art" status)"
  case "$st" in
    blocked|failed) : ;;
    completed) fail "REFUSED_COMPLETED $id" ;;
    *) fail "BAD_ARTIFACT_STATUS $st" ;;
  esac

  local files=()
  while IFS= read -r f; do files+=("$f"); done \
    < <(jq -r --arg id "$id" '.tasks[]|select(.id==$id)|.touched_files[]' "$tj")

  # 순서 위반 감지: 이미 staged면 커밋 절차가 시작된 것 — 정리 거부
  local staged; staged="$(git diff --cached --name-only)"
  for f in "${files[@]}"; do
    if echo "$staged" | grep -Fxq "$f"; then fail "REFUSED_STAGED $f"; fi
  done

  n=0
  for f in "${files[@]}"; do
    if git ls-files --error-unmatch -- "$f" >/dev/null 2>&1; then
      git checkout -q -- "$f"; n=$((n+1))          # tracked → 원복
    elif [ -e "$f" ]; then
      rm -f -- "$f"; n=$((n+1))                    # 신규 untracked → 제거
    fi
  done
  echo "OK $n"
}

# ── commit-refactor ──────────────────────────────────────────────────────────
# refactorer 전용. raw git 대신 이걸 호출 — 파이프라인 경로 거부·명시적 add·
# amend 불가(항상 새 커밋)·subject 접두를 스크립트가 강제.
cmd_commit_refactor() {
  [ $# -ge 4 ] || die "usage: git-ops.sh commit-refactor <cycle_dir> -m \"<summary>\" -- <files...>"
  local dir="$1"; shift
  require_cycle_dir "$dir"
  local summary="" files=()
  while [ $# -gt 0 ]; do
    case "$1" in
      -m) summary="$2"; shift 2 ;;
      --) shift; files=("$@"); break ;;
      *) die "알 수 없는 옵션: $1" ;;
    esac
  done
  [ -n "$summary" ]        || die "-m \"<summary>\" 필요"
  [ "${#files[@]}" -gt 0 ] || die "-- <files...> 필요"
  if has_pipeline_path "${files[@]}"; then
    fail "REFUSED_PIPELINE_PATH"
  fi
  git add -- "${files[@]}"
  if ! git commit -q -m "refactor: $summary"; then
    git reset -q -- "${files[@]}" || true
    fail "COMMIT_FAILED"
  fi
  echo "OK $(git rev-parse HEAD)"
}

# ── dispatch ─────────────────────────────────────────────────────────────────
cmd="${1:-}"; [ $# -gt 0 ] && shift || true
case "$cmd" in
  preflight)       cmd_preflight "$@" ;;
  commit-group)    cmd_commit_group "$@" ;;
  clean-task)      cmd_clean_task "$@" ;;
  commit-refactor) cmd_commit_refactor "$@" ;;
  *) sed -n '2,11p' "$0" >&2; exit 2 ;;
esac
