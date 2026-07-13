# 상태 파일 — 중앙 저장소 명세

사이클의 모든 기록은 repo 밖 **중앙 저장소**에 산다(repo와 생명주기 분리, 자기완결). `state.json`·`journal.md`·`handoff.md`·`verify/`·git 변이는 `scripts/core.sh` 경유가 유일(raw 편집·raw git 금지). `brief.md`·`plan.md`는 ① 동결 전까지 main·planner가 직접 쓰고, 동결 후엔 수정 금지 — lock이 sha256을 기록해 래퍼가 매 verify·commit 전 대조한다(`FROZEN_DRIFT`).

```
${TASK_PIPELINE_STORE:-~/.task-pipeline}/<repo-slug>/<cycle-id>/
├── state.json     # 판정·라이프사이클 (진단 정보 금지)
├── journal.md     # 서사·발견·이월·문답 (append 전용·수정 금지)
├── brief.md       # 착수 합의문 (templates/brief.md 6섹션) — ①에서 동결
├── plan.md        # 걸음 목록 + json steps 기계 정본 (templates/plan.md) — ①에서 동결
├── handoff.md     # 이월 그릇 — ③에서 add, close 후에도 소진 표시만 가변 (유일 예외)
└── verify/        # 검증 raw + meta (불변)
    ├── final-<ts>.log final-<ts>.meta.json   # 최종 검증
    └── step-S-1-<ts>.log …                   # 걸음 확인
```

- **repo-slug**: git remote 기반 `<host>__<owner>__<repo>`(예 `github.com__acme__widget`), remote 없으면 `<basename>__<경로해시6>`.
- **cycle-id**: `YYYYMMDDTHHMMSSZ` UTC. 동일 초 충돌 시 `-2`,`-3` 접미.
- 모든 기록에 repo-id + base_commit이 박혀 자기완결(어느 repo·어느 시점 기준인지 기록만으로 복원).

## state.json — 판정·라이프사이클만
단계 전이·verdict·커밋·게이트·lock 블록만. **진단 정보(왜·어떻게)는 넣지 않는다** — 그건 journal·verify 지층.

```json
{
  "cycle_id": "20260706T143052Z",
  "repo": { "slug": "github.com__acme__widget", "root": "/abs/repo", "base_commit": "<hash>" },
  "request": "<사용자 요청 원문>",
  "created_at": "<ISO8601Z>",
  "phase": "converge|criteria|plan|locked|loop|refactor|review|closed",
  "final": null,                    // done|handoff|cancelled|failed (close 시)
  "lock": {                         // ① 동결 시 채워짐 (그 전엔 null)
    "at": "...", "verify_cmd": "<최종 검증 명령>", "max_rounds": 3,
    "review_checklist": [{"item": "<판정 문장>", "how": "<확인 방법: 어디를 열어 무엇을 본다>"}],
    "branch": "feat/<slug>", "base_commit": "<hash>",
    "brief_sha": "<sha256>", "plan_sha": "<sha256>"
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

## journal.md — append 전용
`core.sh log`만 append(수정 금지, close 후 불가). 엔트리:

```
### <ISO8601Z> · <actor> · <tag>
<본문 — brief/plan ID(G-/C-/S-/W-)를 인라인 참조>
```

- actor: `main · explorer · planner · generator:S-n · refactorer`
- tag: `발견`(generator 간 상속 통로) · `이월` · `blocked` · `문답` · `결정`

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
- **brief.md**: `templates/brief.md` 6섹션(요청 원문/성공/보존/비목표/전제/미해결). 수렴 중 증분, ①에서 전체 동결. 루프 중 전제 오류 발견 시 brief 수정이 아니라 journal + blocked.
- **plan.md**: `templates/plan.md`. frontmatter(cycle·repo·base_commit·type·slug) + 산문 + **` ```json steps ` 블록(기계 정본)**. 래퍼·generator 배정은 블록만 읽는다(`core.sh commit`이 `files`·title·type을, `verify --step`이 `check`를 여기서 읽음). 걸음당 `check`/`human_check` ≥1은 ① lock에서 래퍼가 검증(`STEP_NO_CHECK`).

## 전이 규칙
전이는 전부 `core.sh` 경유(수기 JSON 편집·raw git 금지). **verify·commit은 ① lock 후 · close 전에만 동작**(가드 토큰: `NOT_LOCKED`/`CLOSED`), 동결 후 brief·plan 드리프트는 `FROZEN_DRIFT`로 거부. 커밋은 `core.sh commit`(걸음: subject `<type>: <title>` + trailer `TP-Step`/`TP-Cycle`, 또는 `--refactor`; 무변경 시 `NO_CHANGES` — HEAD가 같은 걸음의 커밋일 때만 멱등 인정). 종료는 `core.sh close <dir> <final>`(done은 `loop.last_verify.token==PASS` 필수 — 아니면 `NOT_PASS` 거부. 이동 없음 — 무기한 보존, `status`가 `final!=null`로 필터). resume은 `core.sh status`로 활성 사이클을 찾아 state.json + journal 재개.
