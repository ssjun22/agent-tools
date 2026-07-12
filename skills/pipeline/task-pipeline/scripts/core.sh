#!/usr/bin/env bash
# core.sh — task-pipeline 하네스의 결정론 래퍼 (유일한 상태·git·검증 변이 지점).
#
# 불변식:
#   - 판정·라이프사이클은 state.json에만 (진단 정보 금지 — 그건 journal/verify 지층).
#   - journal.md는 append 전용 (수정 금지, close 후 불가).
#   - git 쓰기는 commit 서브커맨드 경유 (raw git 변이 금지).
#   - verify는 전체 출력을 tee + meta 기록, 에이전트에는 실패만 보인다.
#   - verify·commit은 ① lock 후 · close 전에만 (라이프사이클 가드).
#   - lock이 brief·plan sha256을 동결 — 이후 드리프트는 FROZEN_DRIFT 거부.
#   - 라운드 = 최종 검증 FAIL 누적. PASS·ERROR는 상한을 소모하지 않는다.
#
# 저장소: ${TASK_PIPELINE_STORE:-~/.task-pipeline}/<repo-slug>/<cycle-id>/
#   state.json · journal.md · brief.md · plan.md · verify/
#
# usage:
#   core.sh new "<request>"                          → OK <cycle_dir>
#   core.sh status [<cycle_dir>]                     → 활성 사이클 요약 / 특정 사이클 상태
#   core.sh log <cycle_dir> --actor <a> --tag <t> -m "<msg>"
#   core.sh step phase   <cycle_dir> <phase>
#   core.sh step lock    <cycle_dir> --verify "<cmd>" --max <N> [--branch <name>] [--check "<항목>"]...
#   core.sh verify       <cycle_dir> [--step <S-n>]  → PASS|FAIL|ERROR|LIMIT
#   core.sh commit       <cycle_dir> <S-n>           → OK <hash> <S-n>
#   core.sh commit       <cycle_dir> --refactor -m "<summary>" -- <files...>
#   core.sh close        <cycle_dir> <done|handoff|cancelled|failed>
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
. "$SCRIPT_DIR/lib.sh"

STORE="${TASK_PIPELINE_STORE:-$HOME/.task-pipeline}"

# ── 새 모델 enum ──────────────────────────────────────────────────────────────
PHASE_ENUM="converge criteria plan locked loop refactor review closed"
FINAL_ENUM="done handoff cancelled failed"
ACTOR_RE='^(main|explorer|planner|refactorer|generator(:S-[0-9]+)?)$'
TAG_ENUM="발견 이월 blocked 문답 결정"
STEP_RE='^S-[0-9]+$'
BRANCH_RE='^[a-z0-9][a-z0-9/_-]{0,63}$'

state_json() { echo "$1/state.json"; }

# ── 라이프사이클 가드 ────────────────────────────────────────────────────
require_active() { # <state.json> — close 전에만
  [ "$(jq -r '.final // "null"' "$1")" = "null" ] || fail "CLOSED"
}
require_locked() { # <state.json> — ① lock 후 · close 전에만
  require_active "$1"
  [ "$(jq -r '.lock // "null"' "$1")" != "null" ] || fail "NOT_LOCKED"
}

# ── 동결 무결 ────────────────────────────────────────────────────────
_sha256() { { shasum -a 256 "$1" 2>/dev/null || sha256sum "$1"; } | cut -d' ' -f1; }

require_frozen() { # <cycle_dir> <state.json> — lock 시점 sha와 대조
  local bh ph
  bh="$(jq -r '.lock.brief_sha // ""' "$2")"
  ph="$(jq -r '.lock.plan_sha // ""' "$2")"
  [ -z "$bh" ] || [ "$(_sha256 "$1/brief.md")" = "$bh" ] || fail "FROZEN_DRIFT brief.md"
  [ -z "$ph" ] || [ "$(_sha256 "$1/plan.md")" = "$ph" ] || fail "FROZEN_DRIFT plan.md"
}

# plan.md의 ```json steps 블록 원문
_plan_steps_block() { # <cycle_dir>
  awk '/^```json steps[ \t]*$/{f=1;next} f&&/^```[ \t]*$/{exit} f{print}' "$1/plan.md"
}

# ── repo 식별 ────────────────────────────────────────────────────────────
_hash6() { printf '%s' "$1" | { shasum 2>/dev/null || sha1sum; } | cut -c1-6; }

repo_slug() {
  local url host rest root base
  if url="$(git config --get remote.origin.url 2>/dev/null)" && [ -n "$url" ]; then
    url="${url%.git}"
    url="${url#*://}"        # scheme 제거
    url="${url#*@}"          # user@ 제거
    url="${url/:/\/}"        # git@host:owner → host/owner
    host="${url%%/*}"; rest="${url#*/}"
    echo "${host}__${rest//\//__}"
  else
    root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
    base="$(basename "$root")"
    echo "${base}__$(_hash6 "$root")"
  fi
}

# ── new ───────────────────────────────────────────────────────────────────────
cmd_new() {
  [ $# -eq 1 ] || die "usage: core.sh new \"<request>\""
  need_jq
  local req="$1"
  git rev-parse --is-inside-work-tree >/dev/null 2>&1 || fail "NOT_GIT"
  local root slug base now cid dir n
  root="$(git rev-parse --show-toplevel)"
  slug="$(repo_slug)"
  base="$(git rev-parse HEAD 2>/dev/null || echo "")"
  now="$(iso_now)"
  cid="$(date -u +%Y%m%dT%H%M%SZ)"
  local repo_store="$STORE/$slug"
  mkdir -p "$repo_store"
  # cycle-id 충돌 회피 (-2, -3 …)
  dir="$repo_store/$cid"; n=2
  while [ -e "$dir" ]; do dir="$repo_store/${cid}-$n"; n=$((n+1)); done
  mkdir -p "$dir/verify"
  jq -n --arg cid "$(basename "$dir")" --arg slug "$slug" --arg root "$root" \
        --arg base "$base" --arg req "$req" --arg now "$now" '{
    cycle_id:$cid, repo:{slug:$slug, root:$root, base_commit:$base},
    request:$req, created_at:$now,
    phase:"converge", final:null,
    lock:null,
    loop:{round:0, max_rounds:null, steps:{}},
    gates:[]
  }' > "$(state_json "$dir")"
  printf '# Journal — %s\n' "$(basename "$dir")" > "$dir/journal.md"
  : > "$dir/brief.md"
  : > "$dir/plan.md"
  echo "OK $dir"
}

# ── log (append 전용) ──────────────────────────────────────────────────────
cmd_log() {
  [ $# -ge 1 ] || die "usage: core.sh log <cycle_dir> --actor <a> --tag <t> -m \"<msg>\""
  need_jq
  local dir="$1"; shift; require_cycle_dir "$dir"
  require_active "$(state_json "$dir")"
  local actor="" tag="" msg=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --actor) actor="$2"; shift 2 ;;
      --tag)   tag="$2";   shift 2 ;;
      -m)      msg="$2";   shift 2 ;;
      *) die "알 수 없는 옵션: $1" ;;
    esac
  done
  [ -n "$actor" ] && [ -n "$tag" ] && [ -n "$msg" ] || die "--actor/--tag/-m 모두 필요"
  echo "$actor" | grep -Eq "$ACTOR_RE" || fail "BAD_ACTOR $actor"
  in_enum "$tag" "$TAG_ENUM" || fail "BAD_TAG $tag"
  local j="$dir/journal.md"
  [ -f "$j" ] || fail "NO_JOURNAL"
  printf '\n### %s · %s · %s\n%s\n' "$(iso_now)" "$actor" "$tag" "$msg" >> "$j"
  echo "OK"
}

# ── step ──────────────────────────────────────────────────────────────────────
cmd_step() {
  local sub="${1:-}"; [ $# -gt 0 ] && shift || true
  case "$sub" in
    phase) _step_phase "$@" ;;
    lock)  _step_lock "$@" ;;
    *) die "usage: core.sh step <phase|lock> <cycle_dir> ..." ;;
  esac
}

_step_phase() {
  [ $# -eq 2 ] || die "usage: core.sh step phase <cycle_dir> <phase>"
  need_jq
  local dir="$1" phase="$2"; require_cycle_dir "$dir"
  require_active "$(state_json "$dir")"
  in_enum "$phase" "$PHASE_ENUM" || fail "BAD_PHASE $phase"
  jq_inplace "$(state_json "$dir")" --arg p "$phase" '.phase=$p'
  echo "OK $phase"
}

# ① 착수 게이트: brief·plan·검증 구성을 통째로 동결 + 사이클 브랜치 생성.
_step_lock() {
  [ $# -ge 1 ] || die "usage: core.sh step lock <cycle_dir> --verify \"<cmd>\" --max <N> [--branch <n>] [--check \"<항목>\"]..."
  need_jq
  local dir="$1"; shift; require_cycle_dir "$dir"
  local sj; sj="$(state_json "$dir")"
  require_active "$sj"
  [ "$(jq -r '.lock // "null"' "$sj")" = "null" ] || fail "ALREADY_LOCKED"
  local verify="" max="" branch=""; local checks=()
  while [ $# -gt 0 ]; do
    case "$1" in
      --verify) verify="$2"; shift 2 ;;
      --max)    max="$2";    shift 2 ;;
      --branch) branch="$2"; shift 2 ;;
      --check)  checks+=("$2"); shift 2 ;;
      *) die "알 수 없는 옵션: $1" ;;
    esac
  done
  [ -n "$verify" ] || fail "NO_VERIFY"
  case "$max" in ''|*[!0-9]*) fail "BAD_MAX $max" ;; esac
  local plan="$dir/plan.md"
  [ -s "$plan" ] || fail "NO_PLAN"
  [ -s "$dir/brief.md" ] || fail "NO_BRIEF"
  # 동결 자격: json steps가 파싱되고, 걸음마다 check 또는 human_check ≥1
  local block; block="$(_plan_steps_block "$dir")"
  [ -n "$block" ] || fail "NO_STEPS"
  echo "$block" | jq -e '.steps | length > 0' >/dev/null 2>&1 || fail "NO_STEPS"
  local nocheck
  nocheck="$(echo "$block" | jq -r \
    '[.steps[]? | select(((.check // "") == "") and ((.human_check // "") == "")) | .id] | join(",")')"
  [ -z "$nocheck" ] || fail "STEP_NO_CHECK $nocheck"
  # 브랜치명: --branch 우선, 없으면 plan frontmatter의 type/slug에서 파생
  if [ -z "$branch" ]; then
    local ty sl
    ty="$(fm_field "$plan" type)"; sl="$(fm_field "$plan" slug)"
    [ -n "$ty" ] && [ -n "$sl" ] || fail "NO_BRANCH_META"
    branch="$ty/$sl"
  fi
  echo "$branch" | grep -Eq "$BRANCH_RE" || fail "BAD_NAME $branch"
  # 브랜치 생성은 repo 루트에서 (저장소는 repo 밖이라 경로 오염 없음)
  local root; root="$(jq -r '.repo.root' "$sj")"
  local base
  base="$(git -C "$root" rev-parse HEAD)"
  [ -z "$(git -C "$root" status --porcelain)" ] || fail "DIRTY"
  if git -C "$root" show-ref --verify --quiet "refs/heads/$branch"; then
    local cur; cur="$(git -C "$root" rev-parse --abbrev-ref HEAD)"
    [ "$cur" = "$branch" ] || fail "BRANCH_EXISTS $branch"   # 이미 그 브랜치 위면 멱등 허용
  else
    git -C "$root" checkout -q -b "$branch"
  fi
  # 동결: lock 블록(brief·plan sha 포함) + phase=locked + 게이트 ① 기록
  local checks_json; checks_json="$(printf '%s\n' "${checks[@]:-}" | jq -R . | jq -s 'map(select(length>0))')"
  local bsha psha
  bsha="$(_sha256 "$dir/brief.md")"; psha="$(_sha256 "$plan")"
  jq_inplace "$sj" --arg v "$verify" --argjson m "$max" --arg b "$branch" \
     --arg base "$base" --arg t "$(iso_now)" --argjson ck "$checks_json" \
     --arg bs "$bsha" --arg ps "$psha" '
    .lock = {at:$t, verify_cmd:$v, max_rounds:$m, review_checklist:$ck, branch:$b,
             base_commit:$base, brief_sha:$bs, plan_sha:$ps}
    | .loop.max_rounds = $m
    | .phase = "locked"
    | .gates += [{gate:"①", at:$t, verdict:"lock"}]'
  echo "OK $branch $base"
}

# ── verify ───────────────────────────────────────────────────────────────
# --step 없음 = 최종 검증 (라운드 카운트, lock.verify_cmd) / --step S-n = 걸음 확인 (라운드 미카운트, plan step check)
cmd_verify() {
  [ $# -ge 1 ] || die "usage: core.sh verify <cycle_dir> [--step <S-n>]"
  need_jq
  local dir="$1"; shift; require_cycle_dir "$dir"
  local step=""
  while [ $# -gt 0 ]; do
    case "$1" in --step) step="$2"; shift 2 ;; *) die "알 수 없는 옵션: $1" ;; esac
  done
  local sj; sj="$(state_json "$dir")"
  require_locked "$sj"
  require_frozen "$dir" "$sj"
  local root; root="$(jq -r '.repo.root' "$sj")"
  local cmd label out meta

  if [ -n "$step" ]; then
    echo "$step" | grep -Eq "$STEP_RE" || fail "BAD_STEP $step"
    cmd="$(_plan_step_field "$dir" "$step" check)"
    [ -n "$cmd" ] && [ "$cmd" != "null" ] || fail "NO_CHECK $step"
    label="step-$step-$(date -u +%Y%m%dT%H%M%SZ)"
  else
    cmd="$(jq -r '.lock.verify_cmd // ""' "$sj")"
    [ -n "$cmd" ] || fail "NOT_LOCKED"
    local round max
    round="$(jq -r '.loop.round' "$sj")"
    max="$(jq -r '.loop.max_rounds // 0' "$sj")"
    if [ "$round" -ge "$max" ]; then
      # 상한 소진 — 사람 개입 이벤트. 무실행이되 흔적은 state에 남긴다.
      jq_inplace "$sj" --arg t "$(iso_now)" \
        '.loop.last_verify = {token:"LIMIT", at:$t, round:.loop.round}'
      echo "LIMIT"; return 0
    fi
    label="final-$(date -u +%Y%m%dT%H%M%SZ)"
  fi

  out="$dir/verify/$label.log"
  meta="$dir/verify/$label.meta.json"
  local head_at; head_at="$(git -C "$root" rev-parse HEAD 2>/dev/null || echo "")"
  local rc=0
  ( cd "$root" && bash -c "$cmd" ) >"$out" 2>&1 || rc=$?
  local token
  if [ "$rc" -eq 0 ]; then token="PASS"
  elif [ "$rc" -eq 127 ]; then token="ERROR"
  else token="FAIL"; fi
  jq -n --arg at "$(iso_now)" --arg cmd "$cmd" --argjson exit "$rc" \
        --arg head "$head_at" --arg tok "$token" --arg label "$label" \
        '{at:$at, cmd:$cmd, exit:$exit, head:$head, token:$tok, label:$label}' > "$meta"
  # 최종 검증이면 verdict를 state에 기록 — FAIL만 라운드 소모 (회로 차단기)
  if [ -z "$step" ]; then
    [ "$token" != "FAIL" ] || round=$((round+1))
    jq_inplace "$sj" --arg tok "$token" --arg t "$(iso_now)" --argjson r "$round" \
      '.loop.round = $r | .loop.last_verify = {token:$tok, at:$t, round:$r}'
  fi
  # 에이전트에는 실패만 상세 노출
  if [ "$token" != "PASS" ]; then
    echo "── verify $token (raw: $out) ──" >&2
    tail -n 40 "$out" >&2 || true
  fi
  echo "$token"
}

# plan.md의 ```json steps 블록에서 특정 걸음의 필드를 뽑는다
_plan_step_field() { # <cycle_dir> <S-n> <field>
  local dir="$1" sn="$2" field="$3"
  local block
  block="$(_plan_steps_block "$dir")"
  [ -n "$block" ] || return 0
  echo "$block" | jq -r --arg id "$sn" --arg f "$field" \
    '.steps[]? | select(.id==$id) | .[$f] // ""' 2>/dev/null
}

# ── commit ───────────────────────────────────────────────────────────────
# subject `<type>: <걸음 제목>`, trailer `TP-Step`/`TP-Cycle` — plan json steps에서 기계 조립.
cmd_commit() {
  [ $# -ge 1 ] || die "usage: core.sh commit <cycle_dir> <S-n> | commit <cycle_dir> --refactor -m \"<summary>\" -- <files...>"
  need_jq
  local dir="$1"; shift; require_cycle_dir "$dir"
  local sj; sj="$(state_json "$dir")"
  require_locked "$sj"
  require_frozen "$dir" "$sj"
  if [ "${1:-}" = "--refactor" ]; then shift; _commit_refactor "$dir" "$@"; return; fi
  local sn="${1:-}"; echo "$sn" | grep -Eq "$STEP_RE" || fail "BAD_STEP $sn"
  local cid root; cid="$(jq -r '.cycle_id' "$sj")"; root="$(jq -r '.repo.root' "$sj")"
  local block
  block="$(_plan_steps_block "$dir")"
  [ -n "$block" ] || fail "NO_STEPS"
  local meta
  meta="$(echo "$block" | jq -r --arg id "$sn" '.steps[]? | select(.id==$id) | "\(.title)\t\(.type // "")"')"
  [ -n "$meta" ] || fail "NO_STEP $sn"
  local title type; title="${meta%%$'\t'*}"; type="${meta#*$'\t'}"
  # 사이클 유형 상속: step.type 생략 시 plan frontmatter type
  [ -n "$type" ] || type="$(fm_field "$dir/plan.md" type)"
  [ -n "$type" ] || type="feat"
  local files=()
  while IFS= read -r f; do [ -n "$f" ] && files+=("$f"); done \
    < <(echo "$block" | jq -r --arg id "$sn" '.steps[]? | select(.id==$id) | .files[]?')
  [ "${#files[@]}" -gt 0 ] || fail "NO_FILES $sn"

  git -C "$root" add -- "${files[@]}"
  local hash
  if git -C "$root" diff --cached --quiet -- "${files[@]}"; then
    # 무변경 — HEAD가 바로 이 걸음의 커밋일 때만 멱등 인정, 아니면 가짜 출처 방지
    local head_step
    head_step="$(git -C "$root" log -1 --format='%(trailers:key=TP-Step,valueonly)' | head -n1)"
    [ "$head_step" = "$sn" ] || fail "NO_CHANGES $sn"
    hash="$(git -C "$root" rev-parse HEAD)"
  else
    local subject="$type: $title"
    if ! git -C "$root" commit -q -m "$subject" -m "TP-Step: $sn"$'\n'"TP-Cycle: $cid"; then
      git -C "$root" reset -q -- "${files[@]}" || true
      fail "COMMIT_FAILED"
    fi
    hash="$(git -C "$root" rev-parse HEAD)"
  fi
  jq_inplace "$sj" --arg s "$sn" --arg h "$hash" --arg t "$(iso_now)" '
    .loop.steps[$s] = ((.loop.steps[$s] // {}) + {commit:$h, committed_at:$t})'
  echo "OK $hash $sn"
}

# ── status ────────────────────────────────────────────────────────────────────
cmd_status() {
  need_jq
  if [ $# -ge 1 ]; then
    local dir="$1"; require_cycle_dir "$dir"
    _status_one "$dir"; return 0
  fi
  # 인자 없음 → cwd의 repo-slug 활성 사이클 (final==null)
  git rev-parse --is-inside-work-tree >/dev/null 2>&1 || fail "NOT_GIT"
  local repo_store="$STORE/$(repo_slug)"
  [ -d "$repo_store" ] || { echo "NO_ACTIVE"; return 0; }
  local found=() d
  for d in "$repo_store"/*/; do
    [ -f "$d/state.json" ] || continue
    [ "$(jq -r '.final // "null"' "$d/state.json")" = "null" ] || continue
    found+=("${d%/}")
  done
  if [ "${#found[@]}" -eq 0 ]; then echo "NO_ACTIVE"; return 0; fi
  echo "OK ${#found[@]}"
  for d in "${found[@]}"; do _status_one "$d"; done
}

_status_one() {
  local sj; sj="$(state_json "$1")"
  jq -r '"cycle=\(.cycle_id) phase=\(.phase) round=\(.loop.round)/\(.loop.max_rounds // "-") "
    + "branch=\(.lock.branch // "-") lock=\(if .lock then "yes" else "no" end) final=\(.final // "-")"' "$sj"
}

# refactorer 전용 커밋 — subject `refactor: <summary>`, trailer TP-Cycle만 (걸음 무관).
_commit_refactor() {
  local dir="$1"; shift
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
  local sj; sj="$(state_json "$dir")"
  local root cid; root="$(jq -r '.repo.root' "$sj")"; cid="$(jq -r '.cycle_id' "$sj")"
  git -C "$root" add -- "${files[@]}"
  local hash
  if git -C "$root" diff --cached --quiet -- "${files[@]}"; then
    # 무변경 — HEAD가 이 사이클의 동일 refactor 커밋일 때만 멱등 인정
    local head_sub head_cid
    head_sub="$(git -C "$root" log -1 --format=%s)"
    head_cid="$(git -C "$root" log -1 --format='%(trailers:key=TP-Cycle,valueonly)' | head -n1)"
    { [ "$head_sub" = "refactor: $summary" ] && [ "$head_cid" = "$cid" ]; } || fail "NO_CHANGES refactor"
    hash="$(git -C "$root" rev-parse HEAD)"
  else
    if ! git -C "$root" commit -q -m "refactor: $summary" -m "TP-Cycle: $cid"; then
      git -C "$root" reset -q -- "${files[@]}" || true; fail "COMMIT_FAILED"
    fi
    hash="$(git -C "$root" rev-parse HEAD)"
  fi
  jq_inplace "$sj" --arg h "$hash" --arg t "$(iso_now)" '.loop.refactor = {commit:$h, at:$t}'
  echo "OK $hash refactor"
}

# ── close (기록·종료) ─────────────────────────────────────────────────────────
# final 설정 + phase=closed. 이동 없음(중앙 저장소 무기한 보존, status가 final!=null로 필터).
cmd_close() {
  [ $# -eq 2 ] || die "usage: core.sh close <cycle_dir> <done|handoff|cancelled|failed>"
  need_jq
  local dir="$1" final="$2"; require_cycle_dir "$dir"
  in_enum "$final" "$FINAL_ENUM" || fail "BAD_FINAL $final"
  local sj; sj="$(state_json "$dir")"
  [ "$(jq -r '.final // "null"' "$sj")" = "null" ] || fail "ALREADY_CLOSED"
  jq_inplace "$sj" --arg f "$final" --arg t "$(iso_now)" '
    .final=$f | .phase="closed" | .closed_at=$t
    | .gates += [{gate:"③", at:$t, verdict:$f}]'
  echo "OK $final"
}

# ── dispatch ─────────────────────────────────────────────────────────────────
cmd="${1:-}"; [ $# -gt 0 ] && shift || true
case "$cmd" in
  new)    cmd_new "$@" ;;
  status) cmd_status "$@" ;;
  log)    cmd_log "$@" ;;
  step)   cmd_step "$@" ;;
  verify) cmd_verify "$@" ;;
  commit) cmd_commit "$@" ;;
  close)  cmd_close "$@" ;;
  *) sed -n '2,25p' "$0" >&2; exit 2 ;;
esac
