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
#   - close done은 최종 검증 PASS를 요구한다 (NOT_PASS 거부).
#   - handoff.md는 close 후 유일 가변 파일 — 연산은 consume(상태 전이) 하나, 래퍼 경유.
#   - transcript.md는 clarify 원문 정본 — append 전용, lock 후 불변.
#   - score·guard의 의견은 격리 lane(claude -p, 도구 없음)이 내되, 통과/차단 규칙은 코드가 소유.
#
# 저장소: ${TASK_PIPELINE_STORE:-~/.task-pipeline}/<repo-slug>/<cycle-id>/
#   state.json · journal.md · brief.md · plan.md · transcript.md · handoff.md · verify/ · score/ · guard/
#
# usage:
#   core.sh new "<request>"                          → OK <cycle_dir>
#   core.sh status [<cycle_dir>]                     → 활성 사이클 요약 + 미소진 handoff
#   core.sh log <cycle_dir> --actor <a> --tag <t> -m "<msg>"
#   core.sh interview-log <cycle_dir> --q "<질문>" --a "<답변>"   → OK R<n>
#   core.sh interview-log <cycle_dir> --refined "<결정>" --from <code|user> --round <N>
#   core.sh score <cycle_dir>  → 스냅샷 + CONVERGED|FLOOR_PASS|BELOW_FLOOR|EARLY|SNAPSHOT_UNAVAILABLE
#   core.sh guard <cycle_dir>  → 판정 뷰 + PASS|BLOCK|UNAVAILABLE
#   core.sh step phase   <cycle_dir> <phase>
#   core.sh step lock    <cycle_dir> --verify "<cmd>" --max <N> [--branch <name>] [--check "<항목> :: <확인 방법>"]...
#   core.sh verify       <cycle_dir> [--step <S-n>]  → PASS|FAIL|ERROR|LIMIT
#   core.sh commit       <cycle_dir> <S-n>           → OK <hash> <S-n>
#   core.sh commit       <cycle_dir> --refactor -m "<summary>" -- <files...>
#   core.sh report       <cycle_dir>                 → 완료 보고 뷰 (저장 없음, 매번 조합)
#   core.sh handoff add     <cycle_dir> -m "<제목>" --refs "<출처>" [--why "<배경>"]
#   core.sh handoff list    <cycle_dir>
#   core.sh handoff consume <cycle_dir> <H-n> --by <cycle-id>
#   core.sh close        <cycle_dir> <done|handoff|cancelled|failed>
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
. "$SCRIPT_DIR/lib.sh"

STORE="${TASK_PIPELINE_STORE:-$HOME/.task-pipeline}"

# ── clarify 상수 ─────────────────────────────────────────────────────────────
CLARIFY_MODEL="${TP_CLARIFY_MODEL:-haiku}"  # 채점기·guard lane 모델
SCORE_FLOOR=4        # 전 축 최저선 (1~5 척도)
SCORE_MIN_ROUNDS=3   # 이 라운드까지는 채점하지 않음 (조기 채점 방지)

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
require_unlocked() { # <state.json> — clarify 구간: close 전 · ① lock 전에만
  require_active "$1"
  [ "$(jq -r '.lock // "null"' "$1")" = "null" ] || fail "LOCKED"
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
  # 스킬 판본 스탬프 — 스킬 파일이 사는 git 저장소의 HEAD (심링크 물리 해석, 보통 agent-tools)
  local sroot scommit sdirty
  sroot="$(cd "$SCRIPT_DIR/.." && pwd -P)"
  scommit="$(git -C "$sroot" rev-parse HEAD 2>/dev/null || echo "")"
  if [ -n "$scommit" ]; then
    [ -n "$(git -C "$sroot" status --porcelain -- . 2>/dev/null)" ] && sdirty=true || sdirty=false
  else
    sdirty=null
  fi
  local repo_store="$STORE/$slug"
  mkdir -p "$repo_store"
  # cycle-id 충돌 회피 (-2, -3 …)
  dir="$repo_store/$cid"; n=2
  while [ -e "$dir" ]; do dir="$repo_store/${cid}-$n"; n=$((n+1)); done
  mkdir -p "$dir/verify"
  jq -n --arg cid "$(basename "$dir")" --arg slug "$slug" --arg root "$root" \
        --arg base "$base" --arg req "$req" --arg now "$now" \
        --arg scommit "$scommit" --argjson sdirty "$sdirty" '{
    cycle_id:$cid, schema_version:1,
    skill:{commit:(if $scommit=="" then null else $scommit end), dirty:$sdirty},
    repo:{slug:$slug, root:$root, base_commit:$base},
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

# ── clarify: interview-log · score · guard ───────────────────────────────────
# transcript.md = 인터뷰 원문 정본 (append 전용). 채점·guard는 격리 lane(claude -p,
# 도구 없음)이 의견을 내고, 통과/차단 규칙은 아래 코드가 소유한다. raw는 score/·guard/에
# 캡처(verify/ 패턴), state.json에는 판정만 남긴다.

_transcript() { echo "$1/transcript.md"; }

_round_max() { # <transcript> — 최대 라운드 번호 (없으면 0)
  awk '/^## R[0-9]+ /{ n=substr($2,2)+0; if(n>m)m=n } END{ print m+0 }' "$1"
}

# 격리 lane 1회 호출 — 프롬프트(stdin) → claude -p(도구 없음) → .result의 JSON 추출.
# 성공: <out_json>에 파싱된 JSON 저장 후 0. 실패: 비0 (raw는 <raw_log>에 캡처됨).
_lane_run() { # <raw_log> <out_json>  (프롬프트는 stdin)
  local raw="$1" out="$2" rc=0
  claude -p --model "$CLARIFY_MODEL" --tools "" --output-format json >"$raw" 2>&1 || rc=$?
  [ "$rc" -eq 0 ] || return 1
  jq -r '.result // empty' "$raw" 2>/dev/null | grep -v '^```' | jq -ce . > "$out" 2>/dev/null || return 1
}

cmd_interview_log() {
  [ $# -ge 1 ] || die "usage: core.sh interview-log <cycle_dir> --q \"<질문>\" --a \"<답변>\" | --refined \"<결정>\" --from <code|user> --round <N>"
  need_jq
  local dir="$1"; shift; require_cycle_dir "$dir"
  require_unlocked "$(state_json "$dir")"
  local q="" a="" refined="" from="" round=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --q)       q="$2";       shift 2 ;;
      --a)       a="$2";       shift 2 ;;
      --refined) refined="$2"; shift 2 ;;
      --from)    from="$2";    shift 2 ;;
      --round)   round="$2";   shift 2 ;;
      *) die "알 수 없는 옵션: $1" ;;
    esac
  done
  local tf; tf="$(_transcript "$dir")"
  [ -f "$tf" ] || printf '# Transcript — %s\n' "$(basename "$dir")" > "$tf"
  if [ -n "$refined" ]; then
    [ -z "$q$a" ] || die "--refined는 --q/--a와 함께 쓸 수 없음"
    in_enum "$from" "code user" || die "--from은 code|user"
    case "$round" in ''|*[!0-9]*) die "--round <N> 필요" ;; esac
    local max; max="$(_round_max "$tf")"
    [ "$round" -ge 1 ] && [ "$round" -le "$max" ] || fail "BAD_ROUND R$round (최대 R$max)"
    printf -- '- [refined][from-%s][R%s] %s\n' "$from" "$round" "$refined" >> "$tf"
    echo "OK refined R$round"
  else
    [ -n "$q" ] && [ -n "$a" ] || die "--q/--a 모두 필요 (또는 --refined)"
    local n; n=$(( $(_round_max "$tf") + 1 ))
    printf '\n## R%s · %s\n**Q:** %s\n**A:** %s\n' "$n" "$(iso_now)" "$q" "$a" >> "$tf"
    echo "OK R$n"
  fi
}

# 채점 — rubric 4축 스냅샷 + floor·streak 판정. 마지막 줄 토큰:
#   CONVERGED(floor+2연속 → guard로) | FLOOR_PASS(streak 1) | BELOW_FLOOR | EARLY | SNAPSHOT_UNAVAILABLE
cmd_score() {
  [ $# -eq 1 ] || die "usage: core.sh score <cycle_dir>"
  need_jq
  local dir="$1"; require_cycle_dir "$dir"
  local sj; sj="$(state_json "$dir")"
  require_unlocked "$sj"
  local tf; tf="$(_transcript "$dir")"
  [ -s "$tf" ] || fail "NO_TRANSCRIPT"
  local rounds; rounds="$(_round_max "$tf")"
  [ "$rounds" -gt "$SCORE_MIN_ROUNDS" ] || { echo "EARLY"; return 0; }
  command -v claude >/dev/null 2>&1 || { echo "SNAPSHOT_UNAVAILABLE"; return 0; }
  mkdir -p "$dir/score"
  local label="R${rounds}-$(date -u +%Y%m%dT%H%M%SZ)"
  local raw="$dir/score/$label.log" res="$dir/score/$label.json"
  if ! { cat "$SCRIPT_DIR/prompts/rubric.md"; echo; echo "---"; echo; cat "$tf"; } \
       | _lane_run "$raw" "$res"; then
    echo "── 채점기 장애 (raw: $raw) ──" >&2
    echo "SNAPSHOT_UNAVAILABLE"; return 0
  fi
  if ! jq -e '[.problem.score,.goal.score,.preserve.score,.nongoal.score]
              | all(type=="number" and .>=1 and .<=5)' "$res" >/dev/null 2>&1; then
    echo "── 채점 형식 불일치 (raw: $raw) ──" >&2
    echo "SNAPSHOT_UNAVAILABLE"; return 0
  fi
  # floor·streak 판정 (판정은 코드). streak = 연속 '라운드' — 같은 라운드 재채점은 가산 없음.
  local pass streak last_round
  pass="$(jq -r --argjson f "$SCORE_FLOOR" \
    '[.problem.score,.goal.score,.preserve.score,.nongoal.score] | min >= $f' "$res")"
  streak="$(jq -r '.clarify.streak // 0' "$sj")"
  last_round="$(jq -r '.clarify.last_score.round // 0' "$sj")"
  if [ "$pass" != "true" ]; then streak=0
  elif [ "$rounds" -gt "$last_round" ]; then streak=$((streak+1))
  elif [ "$streak" -eq 0 ]; then streak=1
  fi
  jq_inplace "$sj" --argjson r "$rounds" --argjson st "$streak" --argjson fl "$pass" \
    --arg t "$(iso_now)" \
    --argjson sc "$(jq -c '{problem:.problem.score,goal:.goal.score,preserve:.preserve.score,nongoal:.nongoal.score}' "$res")" '
    .clarify = ((.clarify // {}) + {streak:$st, last_score:{at:$t, round:$r, floor:$fl, scores:$sc}})'
  # 스냅샷 뷰 — 약한 축 = 최저점 (동률이면 problem→goal→preserve→nongoal 순)
  echo "## 채점 스냅샷 — R$rounds"
  jq -r '[["problem",.problem],["goal",.goal],["preserve",.preserve],["nongoal",.nongoal]] as $axes
    | ($axes | min_by(.[1].score)) as $weak
    | ($axes | map("\(.[0])\t\(.[1].score)\t\(.[1].justification // "")") | join("\n"))
      + "\n약한 축: \($weak[0]) (\($weak[1].score)) — \($weak[1].justification // "")"' "$res"
  echo "floor $SCORE_FLOOR · streak $streak"
  if [ "$pass" = "true" ] && [ "$streak" -ge 2 ]; then echo "CONVERGED"
  elif [ "$pass" = "true" ]; then echo "FLOOR_PASS"
  else echo "BELOW_FLOOR"; fi
}

# Acceptance Guard — ① 발견자 2 독립 병렬 → ② closer 종합 → ③ 코드 규칙.
# 코드 규칙: closer not_ready OR (closer 종합 gaps의 high ≥ 1) → BLOCK, 그 외 PASS.
# BLOCK이면 streak 리셋(라운드 되돌림)은 여기서 수행. 마지막 줄 토큰: PASS|BLOCK|UNAVAILABLE
cmd_guard() {
  [ $# -eq 1 ] || die "usage: core.sh guard <cycle_dir>"
  need_jq
  local dir="$1"; require_cycle_dir "$dir"
  local sj; sj="$(state_json "$dir")"
  require_unlocked "$sj"
  local tf; tf="$(_transcript "$dir")"
  [ -s "$tf" ] || fail "NO_TRANSCRIPT"
  command -v claude >/dev/null 2>&1 || { echo "UNAVAILABLE"; return 0; }
  mkdir -p "$dir/guard"
  local ts; ts="$(date -u +%Y%m%dT%H%M%SZ)"
  # ① 발견자 2 독립 병렬 — 같은 transcript, 서로의 출력을 보지 못한다
  local cj="$dir/guard/$ts-contrarian.json" gj="$dir/guard/$ts-gap_hunter.json"
  local p1 p2 ok=0
  { cat "$SCRIPT_DIR/prompts/guard-contrarian.md"; echo; echo "---"; echo; cat "$tf"; } \
    | _lane_run "$dir/guard/$ts-contrarian.log" "$cj" &
  p1=$!
  { cat "$SCRIPT_DIR/prompts/guard-gap-hunter.md"; echo; echo "---"; echo; cat "$tf"; } \
    | _lane_run "$dir/guard/$ts-gap_hunter.log" "$gj" &
  p2=$!
  wait "$p1" || ok=1
  wait "$p2" || ok=1
  if [ "$ok" -ne 0 ] \
     || ! jq -e '.findings|type=="array"' "$cj" >/dev/null 2>&1 \
     || ! jq -e '.findings|type=="array"' "$gj" >/dev/null 2>&1; then
    echo "── 발견자 lane 장애 (raw: $dir/guard/$ts-*.log) ──" >&2
    echo "UNAVAILABLE"; return 0
  fi
  # ② closer 종합 — [발견 결과 + transcript]
  local oj="$dir/guard/$ts-closer.json"
  if ! { cat "$SCRIPT_DIR/prompts/guard-closer.md"; echo; echo "## FINDER FINDINGS"; \
         cat "$cj"; cat "$gj"; echo; echo "## TRANSCRIPT"; cat "$tf"; } \
       | _lane_run "$dir/guard/$ts-closer.log" "$oj" \
     || ! jq -e '.verdict=="ready" or .verdict=="not_ready"' "$oj" >/dev/null 2>&1; then
    echo "── closer lane 장애 (raw: $dir/guard/$ts-closer.log) ──" >&2
    echo "UNAVAILABLE"; return 0
  fi
  # ③ 코드 규칙 — 판정은 코드가 소유 (closer 종합본의 severity를 읽는다)
  local verdict high token
  verdict="$(jq -r '.verdict' "$oj")"
  high="$(jq '[.gaps[]? | select(.severity=="high")] | length' "$oj")"
  if [ "$verdict" != "ready" ] || [ "$high" -ge 1 ]; then token="BLOCK"; else token="PASS"; fi
  jq_inplace "$sj" --arg t "$(iso_now)" --arg tok "$token" --argjson h "$high" '
    .clarify = ((.clarify // {}) + {last_guard:{at:$t, token:$tok, high:$h}})
    | if $tok == "BLOCK" then .clarify.streak = 0 else . end'
  # 판정 뷰 — BLOCK이면 gaps를 Q-로 라우팅할 재료
  jq -r '"## guard — closer \(.verdict) · high \([.gaps[]?|select(.severity=="high")]|length)"
    + "\n근거: \(.reason // "-")"
    + (if .blocking_question then "\n차단 질문: \(.blocking_question)" else "" end)
    + (if (.gaps|length) > 0
       then "\n" + (.gaps | map("  [\(.severity)] (\(.source // "?")) \(.finding)"
                               + (if .question then " → \(.question)" else "" end)) | join("\n"))
       else "\n  gap 없음" end)' "$oj"
  echo "$token"
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
  # 체크리스트 항목은 "판정 문장 :: 확인 방법(어디를 열어 무엇을 본다)" — 구분자 없으면 how는 빈값
  local checks_json="[]" c item how
  for c in "${checks[@]:-}"; do
    [ -n "$c" ] || continue
    case "$c" in
      *" :: "*) item="${c%% :: *}"; how="${c#* :: }" ;;
      *)        item="$c"; how="" ;;
    esac
    checks_json="$(jq -n --argjson a "$checks_json" --arg i "$item" --arg h "$how" '$a + [{item:$i, how:$h}]')"
  done
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
  if [ "${#found[@]}" -eq 0 ]; then echo "NO_ACTIVE"; else
    echo "OK ${#found[@]}"
    for d in "${found[@]}"; do _status_one "$d"; done
  fi
  _status_handoff "$repo_store"
}

# 미소진 handoff 요약 — 전 사이클(닫힌 것 포함)의 '대기' 항목을 노출
_status_handoff() { # <repo_store>
  local store="$1" d hf cid out=""
  for d in "$store"/*/; do
    hf="${d}handoff.md"; [ -f "$hf" ] || continue
    cid="$(basename "${d%/}")"
    local block
    block="$(awk -v c="$cid" '
      function flush(){ if(id!="" && st ~ /^대기/) printf "  %s  %-5s %s\n", c, id, ti }
      /^## H-/ { flush(); id=$2; ti=$0; sub(/^## H-[0-9]+[ \t]+·[ \t]+/,"",ti); st="?" }
      /^- 상태:/ { if(st=="?"){ s=$0; sub(/^- 상태:[ \t]*/,"",s); st=s } }
      END{ flush() }
    ' "$hf")"
    [ -n "$block" ] || continue
    [ -n "$out" ] && out+=$'\n'
    out+="$block"
  done
  [ -n "$out" ] || return 0
  printf 'HANDOFF %d\n%s\n' "$(printf '%s\n' "$out" | grep -c .)" "$out"
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
  # done = 기계 검증 통과가 데이터로 보장된 상태 — 최종 검증 PASS 없이는 거부
  if [ "$final" = "done" ]; then
    [ "$(jq -r '.loop.last_verify.token // ""' "$sj")" = "PASS" ] || fail "NOT_PASS"
  fi
  jq_inplace "$sj" --arg f "$final" --arg t "$(iso_now)" '
    .final=$f | .phase="closed" | .closed_at=$t
    | .gates += [{gate:"③", at:$t, verdict:$f}]'
  echo "OK $final"
}

# ── report (완료 보고 뷰) ─────────────────────────────────────────────────────
# 저장하지 않는다 — state.json·verify meta·동결 checklist·handoff 상태를 매번 조합.
# ③ 검수 재료(close 전)와 사후 감사(close 후)를 같은 명령이 겸한다.
# 유도 규칙: checklist 항목 중 handoff(관련: checklist:N)로 빠지지 않은 것 = 검수에서 확인.
cmd_report() {
  [ $# -eq 1 ] || die "usage: core.sh report <cycle_dir>"
  need_jq
  local dir="$1"; require_cycle_dir "$dir"
  local sj; sj="$(state_json "$dir")"
  jq -r '"# 완료 보고 — \(.cycle_id) · \(.final // ("진행중: " + .phase))\n요청: \(.request)\n브랜치: \(.lock.branch // "-") · base \(.repo.base_commit[0:7])"' "$sj"
  echo; echo "## 기계 검증"
  jq -r '"최종: \(.loop.last_verify.token // "미실행") (\(.loop.last_verify.at // "-") · round \(.loop.round)/\(.loop.max_rounds // "-"))\n  cmd: \(.lock.verify_cmd // "-")"' "$sj"
  local m
  for m in "$dir"/verify/final-*.meta.json; do [ -f "$m" ] || continue
    jq -r '"  \(.token)  \(.at)  exit \(.exit)  HEAD \(.head[0:7])  → verify/\(.label).log"' "$m"
  done
  echo; echo "## 걸음 (커밋 · 걸음 확인)"
  local sid h last tok
  for sid in $(jq -r '(.loop.steps // {}) | keys[]' "$sj" | sort -V); do
    h="$(jq -r --arg s "$sid" '.loop.steps[$s].commit[0:7]' "$sj")"
    last="$(ls "$dir"/verify/step-"$sid"-*.meta.json 2>/dev/null | sort | tail -1)"
    tok="확인 수단: 검수"; [ -n "$last" ] && tok="걸음 확인 $(jq -r .token "$last")"
    printf '  %-5s 커밋 %s · %s\n' "$sid" "$h" "$tok"
  done
  echo; echo "## 사람 검수 체크리스트 (handoff 미편입 = 검수에서 확인)"
  local n item how hid st i=0
  n="$(jq -r '(.lock.review_checklist // []) | length' "$sj")"
  while [ "$i" -lt "$n" ]; do
    item="$(jq -r --argjson i "$i" '.lock.review_checklist[$i] | if type=="string" then . else .item end' "$sj")"
    how="$(jq -r --argjson i "$i" '.lock.review_checklist[$i] | if type=="string" then "" else (.how // "") end' "$sj")"
    hid=""
    [ -f "$dir/handoff.md" ] && hid="$(awk -v pat="checklist:$((i+1))" \
      '/^## H-/{id=$2} /^- 관련:/ && index($0,pat){print id; exit}' "$dir/handoff.md")"
    if [ -n "$hid" ]; then
      st="$(awk -v id="$hid" '/^## H-/{insec=($2==id)} insec&&/^- 상태:/{sub(/^- 상태:[ \t]*/,"");print;exit}' "$dir/handoff.md")"
      printf '  [이월→%s] %s\n            └ %s\n' "$hid" "$item" "$st"
    else
      printf '  [검수 확인] %s\n' "$item"
    fi
    [ -n "$how" ] && printf '            확인: %s\n' "$how"
    i=$((i+1))
  done
  if [ -f "$dir/handoff.md" ]; then
    echo; echo "## 이월 그릇 (handoff.md)"
    _handoff_list "$dir"
  fi
}

# ── handoff (이월 그릇) ───────────────────────────────────────────────────────
# add는 활성 사이클에서만(③ 검수 시점, close 전). consume은 close 후에도 허용 —
# 닫힌 사이클에서 변이 가능한 유일한 파일·유일한 연산(상태 전이)이다.
cmd_handoff() {
  local sub="${1:-}"; [ $# -gt 0 ] && shift || true
  case "$sub" in
    add)     _handoff_add "$@" ;;
    list)    _handoff_list "$@" ;;
    consume) _handoff_consume "$@" ;;
    *) die "usage: core.sh handoff <add|list|consume> <cycle_dir> ..." ;;
  esac
}

_handoff_add() { # <cycle_dir> -m "<제목>" --refs "<출처>" [--why "<배경>"]
  need_jq
  local dir="$1"; shift; require_cycle_dir "$dir"
  require_active "$(state_json "$dir")"
  local title="" why="" refs=""
  while [ $# -gt 0 ]; do
    case "$1" in
      -m)     title="$2"; shift 2 ;;
      --why)  why="$2";   shift 2 ;;
      --refs) refs="$2";  shift 2 ;;
      *) die "알 수 없는 옵션: $1" ;;
    esac
  done
  [ -n "$title" ] || die "-m \"<제목>\" 필요"
  # 출처 참조 필수 — checklist:N(검수 항목 유래)·brief ID·경로. report 유도가 여기에 의존한다.
  [ -n "$refs" ] || die "--refs \"<출처>\" 필요 (예: checklist:4 · Q-1 · 경로)"
  local hf="$dir/handoff.md"
  [ -f "$hf" ] || printf '# Handoff — %s\n' "$(basename "$dir")" > "$hf"
  local n
  n="$(awk '/^## H-[0-9]+ /{sub(/^## H-/,""); sub(/ .*/,""); if($0+0>m)m=$0+0} END{print m+0}' "$hf")"
  local hid="H-$((n+1))"
  {
    printf '\n## %s · %s\n' "$hid" "$title"
    printf -- '- 상태: 대기\n'
    [ -n "$why" ] && printf -- '- 배경: %s\n' "$why"
    printf -- '- 관련: %s\n' "$refs"
    printf -- '- 기록: %s\n' "$(iso_now)"
  } >> "$hf"
  echo "OK $hid"
}

_handoff_list() { # <cycle_dir>
  local dir="$1"; require_cycle_dir "$dir"
  [ -f "$dir/handoff.md" ] || { echo "NO_HANDOFF"; return 0; }
  awk '
    function flush(){ if(id!="") printf "%-5s %-28s %s\n", id, st, ti }
    /^## H-/ { flush(); id=$2; ti=$0; sub(/^## H-[0-9]+[ \t]+·[ \t]+/,"",ti); st="?" }
    /^- 상태:/ { if(st=="?"){ s=$0; sub(/^- 상태:[ \t]*/,"",s); st=s } }
    END{ flush() }
  ' "$dir/handoff.md"
}

_handoff_consume() { # <cycle_dir> <H-n> --by <cycle-id>
  local dir="$1" hid="${2:-}"; shift 2 || die "usage: core.sh handoff consume <cycle_dir> <H-n> --by <cycle-id>"
  require_cycle_dir "$dir"
  echo "$hid" | grep -Eq '^H-[0-9]+$' || fail "BAD_HANDOFF $hid"
  local by=""
  while [ $# -gt 0 ]; do
    case "$1" in --by) by="$2"; shift 2 ;; *) die "알 수 없는 옵션: $1" ;; esac
  done
  [ -n "$by" ] || die "--by <채택 사이클 id> 필요"
  [ -d "$(dirname "$dir")/$by" ] || fail "NO_SUCH_CYCLE $by"
  local hf="$dir/handoff.md"
  [ -f "$hf" ] || fail "NO_HANDOFF"
  grep -q "^## $hid " "$hf" || fail "NO_ENTRY $hid"
  local st
  st="$(awk -v id="$hid" '/^## H-/{insec=($2==id)} insec && /^- 상태:/{sub(/^- 상태:[ \t]*/,""); print; exit}' "$hf")"
  case "$st" in 대기*) ;; *) fail "ALREADY_CONSUMED $hid ($st)" ;; esac
  local tmp; tmp="$(mktemp)"
  awk -v id="$hid" -v by="$by" -v ts="$(iso_now)" '
    /^## H-/ { insec=($2==id) }
    insec && /^- 상태: 대기/ { print "- 상태: 소진 → " by " (" ts ")"; insec=0; next }
    { print }
  ' "$hf" > "$tmp" && mv "$tmp" "$hf"
  echo "OK $hid → $by"
}

# ── dispatch ─────────────────────────────────────────────────────────────────
cmd="${1:-}"; [ $# -gt 0 ] && shift || true
case "$cmd" in
  new)    cmd_new "$@" ;;
  status) cmd_status "$@" ;;
  log)    cmd_log "$@" ;;
  interview-log) cmd_interview_log "$@" ;;
  score)  cmd_score "$@" ;;
  guard)  cmd_guard "$@" ;;
  step)   cmd_step "$@" ;;
  verify) cmd_verify "$@" ;;
  commit) cmd_commit "$@" ;;
  report) cmd_report "$@" ;;
  handoff) cmd_handoff "$@" ;;
  close)  cmd_close "$@" ;;
  *) sed -n '2,37p' "$0" >&2; exit 2 ;;
esac
