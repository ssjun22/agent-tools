# task-pipeline — 상태 파일 명세

`/task-pipeline` 사이클이 만드는 두 종류의 상태:

1. **사이클 디렉토리** — 단계별 산출물(.md) + 진행 상태 JSON 2개
2. **산출물 frontmatter** — 각 .md 상단에 메인 흐름 분기 신호로 사용

## 사이클 디렉토리

활성 사이클은 `.claude/task-pipeline/<ts>/`. 사이클 종료 시 `.claude/task-pipeline/archived/<ts>/`로 이동.

`<ts>` = ISO8601 변형 — 콜론을 하이픈으로 (파일시스템 호환). 예: `2026-05-07T14-30-22`.

디렉토리 생성·템플릿 cp·placeholder 치환은 `scripts/state.sh init "<request>"`가 한 번에 수행한다 (메인이 손으로 만들지 않는다).

`.claude/task-pipeline/`는 사용자가 `.gitignore`에 추가하기를 권장 (스킬은 자동으로 변경하지 않는다 — 메인이 첫 사이클에서 누락 확인 후 안내).

같은 사이클 내 동일 디렉토리 재사용. 다중 동시 사이클은 `<ts>`가 초 단위로 다르므로 충돌하지 않음 (1초 안에 두 번 호출하는 극단 케이스는 의도적으로 다루지 않음).

## 디렉토리 내부 구조

```
.claude/task-pipeline/2026-05-07T14-30-22/
├── progress.json
├── tasks.json
├── 01-clarify.md
├── 02-explore.md
├── 03-plan.md
├── 04-generate-T1.md       # round 1 — 태스크별 산출물 (04-generate-<Tx>.md)
├── 04-generate-T2.md
├── 05-refactor.md          # round 1
├── 06-evaluate.md          # round 1
├── 04-generate-T2-R2.md    # round 2 retry 시 추가 (round 1 파일은 그대로 유지)
├── 05-refactor-2.md
├── 06-evaluate-2.md
├── 07-context-update.md    # done 종료 시 컨텍스트 문서 업데이트 기록 (메인이 작성 — 제안·승인·적용)
└── handoff.md              # ④ 분기에서 handoff 선택 시
```

규칙:

- generate는 *태스크별* 산출물 — round 1은 `04-generate-<Tx>.md`, round N≥2는 `04-generate-<Tx>-R<N>.md`
- refactor·evaluate는 round 1 접미사 없음(`05-refactor.md`), round N≥2는 `-N` 접미사(`05-refactor-2.md`)
- 1라운드에 끝나는 일반 케이스는 접미사 없는 깔끔한 트리

## progress.json

6단계 + 라운드 상태를 추적한다. 초기 생성은 `templates/progress.template.json`을 cp하는 방식으로 한다 — 스키마 드리프트 방지.

```json
{
  "started_at": "2026-05-07T14:30:22Z",
  "request": "사용자가 /task-pipeline 인자로 넘긴 요약",
  "branch": "feat/<slug>",
  "base_commit": "<preflight가 기록한 브랜치 생성 직후 HEAD>",
  "current_step": "clarify | explore | plan | generate | refactor | evaluate | done | handoff | cancelled | failed",
  "max_rounds": 3,
  "current_round": 1,
  "steps": {
    "clarify":  { "state": "completed",   "started_at": "...", "finished_at": "..." },
    "explore":  { "state": "completed",   "started_at": "...", "finished_at": "..." },
    "plan":     { "state": "completed",   "started_at": "...", "finished_at": "..." },
    "generate": { "state": "in_progress", "started_at": "..." },
    "refactor": { "state": "pending" },
    "evaluate": {
      "state": "pending",
      "rounds": [
        { "round": 1, "result": "FAIL", "started_at": "...", "finished_at": "..." }
      ]
    }
  }
}
```

`state` 값: `pending` / `in_progress` / `completed` / `failed` / `skipped`

`current_step`은 마지막 활성 단계 또는 종료 상태(`done` / `handoff` / `cancelled` / `failed`).

`branch`·`base_commit`은 `git-ops.sh preflight`가 브랜치 생성 직후 기록한다 (`<type>/<slug>` — type은 plan 개요의 유형 값). base_commit은 evaluate 2-B diff 기준으로 매 라운드 주입된다. base가 디스크에 남으므로 resume 후에도 유효하다 — `preflight`는 멱등이라, 브랜치는 만들어졌는데 기록 전 중단된 경우(현재 그 브랜치 위·progress 미기록) 재실행하면 base=HEAD로 조정한다.

## tasks.json

plan 태스크의 진행 상태 + 커밋 해시 매핑. 초기 생성은 `state.sh tasks-init <cycle_dir>` — plan 산출물의 ```json tasks 블록(groups+tasks)을 추출·검증(스키마 + 같은 stage 내 touched_files 비겹침)해 생성한다. 메인이 산문 plan을 번역해 push하지 않는다.

최상위 `groups` 배열이 group 메타(커밋 subject의 제목·type 원천)를 담는다 — `git-ops.sh commit-group`이 여기서 subject를 조립한다:

```json
{
  "groups": [
    { "id": "A", "title": "의존성 설치", "type": "chore" },
    { "id": "B", "title": "스키마 정의", "type": "feat" }
  ],
  "tasks": [
    {
      "id": "T1",
      "title": "의존성 설치",
      "group": "A",
      "stage": 1,
      "touched_files": ["package.json", "pnpm-lock.yaml"],
      "depends_on": [],
      "status": "done",
      "commit": "a1b2c3d",
      "started_at": "...",
      "finished_at": "..."
    },
    {
      "id": "T2",
      "title": "스키마 정의",
      "group": "B",
      "stage": 2,
      "touched_files": ["src/lib/db/schema.ts"],
      "depends_on": ["T1"],
      "status": "in_progress",
      "commit": null,
      "started_at": "...",
      "finished_at": null
    }
  ]
}
```

`status` 값: `pending` / `in_progress` / `done` / `failed` / `skipped`

`group`: **커밋 묶음 단위** — planner가 부여한 논리 그룹 ID(`A`, `B`, ...). 같은 group의 태스크들은 메인이 *한 커밋으로 묶는다*. group ⊂ stage (한 group은 한 stage 안에 속한다). 같은 group 안의 `touched_files`는 절대 겹치지 않는다. group의 제목·type은 plan(`03-plan.md`)이 source of truth.

`stage`: **스케줄링 단위** — 실행 단계 번호(1, 2, ...). 같은 stage의 태스크는 group 무관 메인이 generator를 *동시 호출*하고, 다른 stage는 순차. 즉 `stage`는 *언제 도느냐*(병렬·의존), `group`은 *어떻게 묶어 커밋하느냐*를 가른다.

`touched_files`: 이 태스크가 *write할* 파일 경로. read 전용 파일은 적지 않는다. generator는 이 목록 외 파일에 write 시도 시 `blocked`로 종료.

`depends_on`: 이 태스크가 의존하는 선행 태스크 id 배열. 그래프 검증·재시도 영향 분석에 사용.

`commit`: 이 태스크가 포함된 **group 커밋의 해시**(메인이 group 단위로 커밋 후 채운다 — 같은 group의 태스크들은 같은 해시를 가리킨다). retry로 그 태스크의 fix 새 커밋이 추가되면 *그 태스크의* commit만 fix 해시로 갱신(같은 group의 다른 태스크는 원래 group 커밋 해시 유지). 이전 커밋 히스토리는 git이 추적. generator는 커밋하지 않으므로 이 필드를 채우지 않는다.

설명·verify 명령은 `03-plan.md`(메인 컨텍스트)가 source of truth — tasks.json에 중복 저장하지 않는다.

## 산출물 frontmatter 규약

모든 단계 산출물(.md)은 상단에 다음 frontmatter를 *반드시* 가진다. 메인은 sub-agent 종료 직후 *frontmatter status 한 필드만* 읽어 흐름을 분기한다.

```yaml
---
stage: clarify | explore | plan | generate | refactor | evaluate
round: 1                          # round-aware 단계만 (generate/refactor/evaluate). 1차에서는 생략 가능
status: completed | cancelled | blocked | failed
started_at: 2026-05-07T14:30:22Z
finished_at: 2026-05-07T14:35:11Z
---
```

### status 값의 의미와 메인의 분기

| status | 의미 | 메인의 처리 |
|---|---|---|
| `completed` | 단계 본업 정상 완료 | 다음 단계로 진행 (해당 지점에 게이트가 정의돼 있으면 사용자 confirm 후) |
| `cancelled` | 사용자가 인터뷰 도중 "취소/그만/잘못 호출" 발화 | 사이클 종료, `current_step = cancelled`, archived/로 이동 |
| `blocked` | 외부 결정·정보가 필요해 단계 진행 불가 | 사용자에게 blocker 제시 → 재시도/중단 선택 |
| `failed` | 도구·환경 에러 (sub-agent 본업 자체 실패) | retry 소진 없이 즉시 사용자 알림, `current_step = failed` 종료 |

> **`status` ≠ 단계 결과의 좋고 나쁨.**
> evaluator는 plan 부합 또는 verify가 FAIL이어도 *본업(검증 보고)은 정상 완료*했으므로 `status: completed` + 본문 `Verdict: FAIL`. 메인은 frontmatter status로 sub-agent 작업 자체의 성공 여부를, 본문 Verdict로 검증 결과를 따로 본다.

### 본문 추가 섹션 매핑

상태에 따라 본문에 정해진 헤더가 함께 들어간다 (sub-agent 정의에 강제됨):

- `cancelled` → `## Cancellation` (사용자 발화 인용 + 시점)
- `blocked` → `## Blocker` (막힌 지점 + 필요한 결정)
- `failed` → `## 시스템 에러` (에러 내용 + 영향 범위)

## 상태 전이 규칙

### progress.json

- 단계 진입: 해당 step.state를 `in_progress`로, started_at 기록
- sub-agent 종료 후: 산출물 frontmatter status를 보고 단계 state 결정
  - `completed` → `completed` + finished_at
  - `failed` → `failed` + finished_at, `current_step = failed`
  - `cancelled` → `current_step = cancelled`
  - `blocked` → state는 `in_progress` 유지하고 메인이 사용자에 처리 요청
- evaluate 라운드 진입: rounds 배열에 `{round, started_at}` 추가
- evaluate 라운드 종료: 산출물 본문 Verdict를 result로 기록 + finished_at
- 사이클 종료: current_step을 종료 상태로 갱신 후 archived/로 이동

### tasks.json

> status 전이·commit 해시·시각 기록은 `git-ops.sh commit-group`이 커밋과 원자적으로 수행한다 (내부에서 `state.sh task-update` 호출 — 판정 원천은 generate 산출물 frontmatter status). 그 외 개별 갱신도 항상 `state.sh task-update` 경유 — 수기 JSON 편집 금지. Write가 스크립트 직렬 실행이므로 동시 lost-update가 없다.
>
> `commit-group`은 멱등이다 — 커밋은 성공했으나 tasks.json 기록 전 세션이 끊긴 반쪽 상태에서 재실행하면, 스테이징할 변경이 없음을 감지해 새 커밋을 만들지 않고 기존 HEAD 커밋으로 tasks.json을 조정한다. 덕분에 resume 시 판별은 `inspect.sh tasks`(태스크별 status·commit)로, 복구는 `commit-group` 재실행으로 닫힌다 — resume 프로토콜은 SKILL.md 참조.

- 태스크 완료 (메인이 frontmatter에서 도출해 적용): `pending → done`. 메인이 group 커밋 해시·finished_at을 채움
- evaluate 라운드 FAIL시 영향 태스크 (메인): `done → failed` (영향 태스크 추정 가능 시에만)
- 다음 라운드 generate 재진입: `failed → done`. 메인이 그 group의 fix 커밋 해시로 해당 태스크 commit 갱신
- ④ 분기 "재시도 (라운드 리셋)" 선택 시 (메인): 모든 태스크 `done|failed → pending`, started_at/finished_at null로 리셋. commit 필드는 유지 — 과거 커밋은 git history에 그대로 남고 추적용으로 보존

## 사이클 종료 처리

`current_step`이 다음 중 하나가 되면 메인이 `<ts>` 디렉토리를 통째로 `archived/`로 이동:

- `done`
- `handoff`
- `cancelled`
- `failed`

이동은 `state.sh archive <cycle_dir> <final_step>` — doctor 검증이 내장되어 통과해야만 mv된다 (`inspect.sh doctor` 단독 실행은 read-only 점검용).

archived/는 사용자가 직접 정리. 스킬은 자동 정리하지 않는다. `inspect.sh stats`가 archived/를 집계해 Round 1 PASS율·종료 상태 분포를 보고한다.
