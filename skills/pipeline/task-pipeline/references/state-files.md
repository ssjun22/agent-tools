# task-pipeline — 상태 파일 명세

`/task-pipeline` 사이클이 만드는 두 종류의 상태:

1. **사이클 디렉토리** — 단계별 산출물(.md) + 진행 상태 JSON 2개
2. **산출물 frontmatter** — 각 .md 상단에 메인 흐름 분기 신호로 사용

## 사이클 디렉토리

활성 사이클은 `.claude/task-pipeline/<ts>/`. 사이클 종료 시 `.claude/task-pipeline/archived/<ts>/`로 이동.

`<ts>` = ISO8601 변형 — 콜론을 하이픈으로 (파일시스템 호환). 예: `2026-05-07T14-30-22`.

```bash
TS=$(date -u +"%Y-%m-%dT%H-%M-%S")
TASK_PIPELINE_DIR=".claude/task-pipeline/$TS"
mkdir -p "$TASK_PIPELINE_DIR"
```

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
├── 04-generate.md          # round 1
├── 05-refactor.md          # round 1
├── 06-evaluate.md          # round 1
├── 04-generate-2.md        # round 2 retry 시 추가 (round 1 파일은 그대로 유지)
├── 05-refactor-2.md
├── 06-evaluate-2.md
└── handoff.md              # ④ 분기에서 handoff 선택 시
```

규칙:

- round 1은 접미사 없음 (`04-generate.md`)
- round N≥2는 `-N` 접미사 (`04-generate-2.md`)
- 1라운드에 끝나는 일반 케이스는 접미사 없는 깔끔한 트리

## progress.json

6단계 + 라운드 상태를 추적한다. 초기 생성은 `templates/progress.template.json`을 cp하는 방식으로 한다 — 스키마 드리프트 방지.

```json
{
  "started_at": "2026-05-07T14:30:22Z",
  "request": "사용자가 /task-pipeline 인자로 넘긴 요약",
  "branch": "task-pipeline/<slug>",
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

`branch`는 plan 확정 후 메인이 생성한 브랜치명.

## tasks.json

plan 태스크의 진행 상태 + 커밋 해시 매핑. 초기 생성은 `templates/tasks.template.json`을 cp하면 `{"tasks": []}` 빈 배열로 시작 — 메인이 plan 태스크별로 객체를 만들어 push (객체 스키마는 아래 본문).

```json
{
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
| `completed` | 단계 본업 정상 완료 | 다음 단계로 진행 (게이트 4지점이면 사용자 confirm 후) |
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

> status 전이는 generator가 산출물 `## tasks.json 갱신 요청`으로 *요청*하고, commit 해시·시각은 메인이 group 커밋 후 *채운다*. 실제 tasks.json Write는 항상 메인이 직렬로 일괄 처리한다 (동시 lost-update 방지).

- 태스크 완료 (generator 요청 → 메인 적용): `pending → done`. 메인이 group 커밋 해시·finished_at을 채움
- evaluate 라운드 FAIL시 영향 태스크 (메인): `done → failed` (영향 태스크 추정 가능 시에만)
- 다음 라운드 generate 재진입: `failed → done`. 메인이 그 group의 fix 커밋 해시로 해당 태스크 commit 갱신
- ④ 분기 "재시도 (라운드 리셋)" 선택 시 (메인): 모든 태스크 `done|failed → pending`, started_at/finished_at null로 리셋. commit 필드는 유지 — 과거 커밋은 git history에 그대로 남고 추적용으로 보존

## 사이클 종료 처리

`current_step`이 다음 중 하나가 되면 메인이 `<ts>` 디렉토리를 통째로 `archived/`로 이동:

- `done`
- `handoff`
- `cancelled`
- `failed`

```bash
mkdir -p .claude/task-pipeline/archived
mv .claude/task-pipeline/$TS .claude/task-pipeline/archived/
```

archived/는 사용자가 직접 정리. 스킬은 자동 정리하지 않는다.
