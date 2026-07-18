# 상태 파일 — 중앙 저장소 명세

사이클의 모든 기록은 repo 밖 **중앙 저장소**에 산다(repo와 생명주기 분리, 자기완결). `state.json`·`journal.md`·`transcript.md`·`handoff.md`·`verify/`·`score/`·`guard/`·git 변이는 `scripts/core.sh` 경유가 유일(raw 편집·raw git 금지). `brief.md`는 인터뷰 종료(restate 승인) 시 main이 1회 생성, `plan.md`는 ① 동결 전까지 planner가 직접 쓴다 — 동결 후엔 둘 다 수정 금지, lock이 sha256을 기록해 래퍼가 매 verify·commit 전 대조한다(`FROZEN_DRIFT`).

```
${TASK_PIPELINE_STORE:-~/.task-pipeline}/<repo-slug>/<cycle-id>/
├── state.json     # 판정·라이프사이클 (진단 정보 금지)
├── journal.md     # 서사·발견·이월·문답 (append 전용·수정 금지)
├── transcript.md  # clarify Q/A 원문 정본 — interview-log 경유 append 전용, lock 후 불변
├── brief.md       # 착수 합의문 (templates/brief.md 6섹션) — 인터뷰 종료 시 1회 생성, ①에서 동결
├── plan.md        # 걸음 목록 + json steps 기계 정본 (templates/plan.md) — ①에서 동결
├── handoff.md     # 이월 그릇 — ③에서 add, close 후에도 소진 표시만 가변 (유일 예외)
├── verify/        # 검증 raw + meta (불변)
│   ├── final-<ts>.log final-<ts>.meta.json   # 최종 검증
│   └── step-S-1-<ts>.log …                   # 걸음 확인
├── score/         # 채점 raw 캡처 — R<n>-<ts>.log(원문) · R<n>-<ts>.json(축별 파싱본)
├── guard/         # guard lane raw 캡처 — <ts>-{contrarian,gap_hunter,closer}.log/.json
└── brief-check/   # brief 대조 lane raw 캡처 — <ts>.log/.json
```

- **repo-slug**: git remote 기반 `<host>__<owner>__<repo>`(예 `github.com__acme__widget`), remote 없으면 `<basename>__<경로해시6>`.
- **cycle-id**: `YYYYMMDDTHHMMSSZ` UTC. 동일 초 충돌 시 `-2`,`-3` 접미.
- 모든 기록에 repo-id + base_commit이 박혀 자기완결(어느 repo·어느 시점 기준인지 기록만으로 복원).

## state.json — 판정·라이프사이클만
단계 전이·verdict·커밋·게이트·lock 블록만. **진단 정보(왜·어떻게)는 넣지 않는다** — 그건 journal·verify 지층.

```json
{
  "cycle_id": "20260706T143052Z",
  "schema_version": 1,
  "skill": { "commit": "<스킬 저장소 HEAD>", "dirty": false },
  "repo": { "slug": "github.com__acme__widget", "root": "/abs/repo", "base_commit": "<hash>" },
  "request": "<사용자 요청 원문>",
  "created_at": "<ISO8601Z>",
  "phase": "converge|criteria|plan|locked|loop|refactor|review|closed",
  "final": null,                    // done|handoff|cancelled|failed (close 시)
  "clarify": {                      // 채점 루프·guard·brief-check 판정만 (진단은 score/·guard/·brief-check/ 지층. 부재 = 채점 전)
    "streak": 0,                    // floor 연속 통과 '라운드' 수 — guard BLOCK·축 구성 변경 시 0으로 리셋
    "last_score": { "at": "...", "round": 4, "floor": true, "greenfield": false,
                    "scores": { "problem": 5, "goal": 5, "preserve": 5, "nongoal": 5 } },
    "last_guard": { "at": "...", "token": "PASS|BLOCK", "high": 0 },
    "last_brief_check": { "at": "...", "token": "PASS|FAIL", "high": 0, "mechanical": false,
                          "brief_sha": "<판정 시점 brief sha256 — lock이 판본 일치를 대조>" }
  },
  "lock": {                         // ① 동결 시 채워짐 (그 전엔 null)
    "at": "...", "verify_cmd": "<최종 검증 명령>", "max_rounds": 3,
    "review_checklist": [{"item": "<판정 문장>", "how": "<확인 방법: 어디를 열어 무엇을 본다>"}],
    "branch": "feat/<slug>", "base_commit": "<hash>",
    "brief_sha": "<sha256>", "plan_sha": "<sha256>",
    "clarify": {                    // lock 시점 clarify 최종 상태 스냅샷 — 기록+고지, 차단 아님
      "mode": "scored|override|adhoc",  // 유도는 코드 소유: scored=floor+streak≥2+guard PASS 완주 ·
                                        // override=채점 흔적 있으나 체인 미완(사용자 재량 종료) · adhoc=무채점
      "streak": 2, "score_round": 5, "greenfield": false,
      "guard": "PASS", "brief_check": "PASS", "brief_sha_match": true
    }
  },
  "loop": {
    "round": 0, "max_rounds": 3,
    "steps": { "S-1": { "commit": "<hash>", "committed_at": "<ISO8601Z>" } },
    "last_verify": { "token": "PASS|FAIL|ERROR|LIMIT", "at": "...", "round": 1 }
  },
  "gates": [ { "gate": "①", "at": "...", "verdict": "lock" } ]
}
```

`phase` enum: `converge · criteria · plan · locked · loop · refactor · review · closed`. `final` enum: `done · handoff · cancelled · failed`. `loop.round`는 최종 검증 **누적 FAIL 수**(PASS·ERROR 미소모).

**판본 스탬프** — `new`가 기록, 이후 불변. `skill.commit` = 스킬 파일이 사는 git 저장소의 HEAD(심링크는 물리 경로로 해석 — 보통 agent-tools, 해석 실패 시 null), `skill.dirty` = 스킬 서브트리 미커밋 변경 여부, `schema_version` = 이 파일의 스키마 기준점. **필드 부재 = 스탬프 이전 사이클**(legacy 코호트). 용도: 산출물을 스킬 판본별 코호트로 잘라 개선 전후를 비교.

## journal.md — append 전용
`core.sh log`만 append(수정 금지, close 후 불가). 엔트리:

```
### <ISO8601Z> · <actor> · <tag>
<본문 — brief/plan ID(G-/C-/S-/W-)를 인라인 참조>
```

- actor: `main · explorer · planner · generator:S-n · refactorer`
- tag: `발견`(generator 간 상속 통로) · `이월` · `blocked` · `문답`(③ 검수 전용 — clarify 결정은 transcript `[refined]`) · `결정`

## transcript.md — clarify 원문 정본
`core.sh interview-log`만 append(요약·삭제 금지, lock 후 `LOCKED` 거부). 라운드는 `## R<n> · <ts>` 아래 **Q:**/**A:** 원문, 확인된 결정은 `- [refined][from-code|from-user][R<n>] <결정>` 한 줄 — clarify 결정 기록의 단일 정본(journal `문답` 이중기록 폐지, `문답`은 ③ 검수 전용). 채점기의 무상태 재파생(매 라운드 전문 재채점)이 이 파일에 의존한다.

## score/ · guard/ · brief-check/ — 격리 lane 캡처
`core.sh score`·`guard`·`brief-check`가 격리 lane(`claude -p`, 도구 없음, 기본 haiku — `TP_CLARIFY_MODEL` 오버라이드)의 raw를 캡처한다(verify/ 패턴). state.json에는 판정만, 진단(justification·발견 내용)은 이 지층에.
- **score/**: `R<n>-<ts>.log`(raw) · `.json`(축별 파싱본). 토큰 `CONVERGED`(floor+2연속) `FLOOR_PASS` `BELOW_FLOOR` `EARLY`(R3까지 무채점) `SNAPSHOT_UNAVAILABLE`(장애 — 인터뷰는 계속). floor(전 축 4점)·streak 판정은 코드 소유. `--greenfield`(기존 동작 무접점 신규 작업)는 보존(preserve) 축을 축 집합에서 제외 — 축 구성이 직전 채점과 다르면 streak 리셋.
- **guard/**: `<ts>-{contrarian,gap_hunter,closer}.log/.json`. 발견자 2 독립 병렬 → closer 종합([발견+transcript]) → 코드 규칙 `closer not_ready OR 종합 gaps의 high≥1 → BLOCK`(+streak 리셋), 그 외 `PASS`, lane 장애 `UNAVAILABLE`. 프롬프트 원천: `scripts/prompts/`.
- **brief-check/**: `<ts>.log/.json`. brief 생성 직후 전사 대조 — 기계 태그 검사(코드: 확정 항목 `- G/C/N/A-n` 줄의 출처 태그 유무·R 범위) 위반이면 lane 없이 `FAIL`, 통과 시 대조 lane(누락·왜곡·무단추가·재등장, severity) 후 코드 규칙 `verdict fail OR high≥1 → FAIL`, 그 외 `PASS`, lane 장애 `UNAVAILABLE`(① 뷰에 고지 후 진행). FAIL이면 동결 전이므로 brief 수정 후 재실행. 판정 시점 brief sha를 함께 기록 — 판정 후 brief가 또 바뀌면 lock 스냅샷의 `brief_sha_match`가 false로 드러난다.

## clarify-status — 최종 상태 뷰 (저장 없음)
`core.sh clarify-status`가 `_clarify_snapshot_json`(lock 동결과 같은 코드 경로)으로 mode·streak·guard·brief-check·판본 일치를 요약하고 경고 줄(체인 미완·brief-check 미실행/FAIL/판본 불일치)을 산출한다. 마지막 줄 `CLEAN | WARN <n>`. ① 착수 뷰가 이 출력을 고지 재료로 쓴다 — lock은 같은 스냅샷을 `lock.clarify`에 동결한다(기록+고지, 차단 아님).

## verify/ — 검증 캡처
`core.sh verify`가 전체 출력을 tee(`<label>.log`) + meta(`<label>.meta.json`: `at·cmd·exit·head·token·label`) 기록. 토큰 `PASS/FAIL/ERROR/LIMIT`. 에이전트에는 실패만 상세 노출.
- 최종 검증(`verify <dir>`): `label = final-<ts>`, lock의 `verify_cmd` 실행. **FAIL일 때만 라운드++**. 상한 도달 시 `LIMIT`(무실행 — 단 `loop.last_verify`에 기록).
- 걸음 확인(`verify <dir> --step S-n`): `label = step-<S-n>-<ts>`, plan 걸음의 `check` 실행, 라운드 무카운트.

## handoff.md — 이월 그릇
③ 검수의 이월 판정분을 다음 사이클이 주울 수 있게 담는다. 변이는 `core.sh handoff`만.
- `add`(활성 중, close 전): `H-n` 항목 append — 제목 · 상태(대기) · 배경 · **관련(출처 참조 필수**: `checklist:N`·brief ID·경로**)** · 기록 시각.
- `consume <H-n> --by <채택 cycle-id>`: 상태를 `소진 → <cycle-id>`로 전이. **close 후에도 허용** — 닫힌 사이클에서 변이 가능한 유일한 파일·유일한 연산.
- `status`가 전 사이클의 `대기` 항목을 `HANDOFF`로 노출 → 발동·resume 시 수렴이 확인·제시하고, 채택 시 consume.

## 완료 보고 — `core.sh report` (저장 없음)
state.json(판정·커밋)·verify meta·동결 checklist·handoff 상태를 매번 조합하는 뷰. ③ 검수 재료(close 전)와 사후 감사(close 후)를 같은 명령이 겸해 "검수 때 본 것 ≠ 기록" 괴리가 없다. 유도 규칙: **checklist 항목 중 handoff(`checklist:N` 참조)로 빠지지 않은 것 = 검수에서 확인** — 이 유도는 handoff의 출처 참조 필수, ③ 문답의 journal 기록, close done의 PASS 가드가 받친다.

## brief.md / plan.md
- **brief.md**: `templates/brief.md` 6섹션(요청 원문/성공/보존/비목표/전제/미해결). 인터뷰 중 영속 정본은 transcript뿐 — brief는 인터뷰 종료(restate 승인) 시 1회 생성하며 확정 항목에 출처 태그 `[from-code|from-user][R<n>]`를 붙인다(항목 줄 형식 `- G-1 [from-user][R3] <내용>` — `brief-check` 기계 검사 대상). 생성 직후 `core.sh brief-check`로 transcript 대조 후 ①에서 전체 동결. 루프 중 전제 오류 발견 시 brief 수정이 아니라 journal + blocked.
- **plan.md**: `templates/plan.md`. frontmatter(cycle·repo·base_commit·type·slug) + 산문 + **` ```json steps ` 블록(기계 정본)**. 래퍼·generator 배정은 블록만 읽는다(`core.sh commit`이 `files`·title·type을, `verify --step`이 `check`를 여기서 읽음). 걸음당 `check`/`human_check` ≥1은 ① lock에서 래퍼가 검증(`STEP_NO_CHECK`).

## 전이 규칙
전이는 전부 `core.sh` 경유(수기 JSON 편집·raw git 금지). **verify·commit은 ① lock 후 · close 전에만**(가드 토큰: `NOT_LOCKED`/`CLOSED`), **interview-log·score·guard·brief-check는 lock 전에만**(`LOCKED`), 동결 후 brief·plan 드리프트는 `FROZEN_DRIFT`로 거부. 커밋은 `core.sh commit`(걸음: subject `<type>: <title>` + trailer `TP-Step`/`TP-Cycle`, 또는 `--refactor`; 무변경 시 `NO_CHANGES` — HEAD가 같은 걸음의 커밋일 때만 멱등 인정). 종료는 `core.sh close <dir> <final>`(done은 `loop.last_verify.token==PASS` 필수 — 아니면 `NOT_PASS` 거부. 이동 없음 — 무기한 보존, `status`가 `final!=null`로 필터). resume은 `core.sh status`로 활성 사이클을 찾아 state.json + journal 재개.
