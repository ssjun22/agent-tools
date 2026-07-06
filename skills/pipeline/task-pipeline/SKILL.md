---
name: task-pipeline
description: "요구사항이 정해진 코드 변경 작업을 위한 6단계 파이프라인(clarify → explore → plan → generate → refactor → evaluate). 코드 변경은 태스크 내 TDD(red-green)로 진행. /task-pipeline <설명>으로 호출. 탐색·측정·variant 공존 작업(A/B 테스트, spike, 벤치마크 등)에는 적합하지 않음."
argument-hint: "[작업 설명 (자유 텍스트, 빈 인자 허용)]"
disable-model-invocation: true
---

# task-pipeline — 코드 변경 작업의 6단계 파이프라인

> 이 문서는 메인 세션의 실행 절차서(runbook)다 — 서브에이전트의 내부 동작은 각 에이전트 정의(`.md`)가, 데이터 규약은 `references/`가 원천이며 여기 재서술하지 않는다.

작업을 일관된 6단계 흐름으로 처리한다. clarify는 사용자와의 라이브 인터뷰가 필요하므로 *메인이 인라인으로 직접 수행*하고, 나머지 단계는 별도 서브에이전트가 담당한다. 메인은 *오케스트레이터 + clarify 인터뷰 + 게이트 confirm*을 책임진다. 산출물은 디스크에 영속화되어 단계 간 인계가 명시적으로 일어난다.

## 흐름

```
[1] clarify → [2] explore → [3] plan → (브랜치 생성) → [4] generate → [5] refactor → [6] evaluate
→ (done 시) 컨텍스트 문서 업데이트 → (선택) tutor

종료 상태: done · handoff · cancelled · failed
```

## 사용자 개입 게이트

게이트 발화는 모두 `AskUserQuestion`으로 다지선다 — 자유 텍스트로 묻지 않는다. header는 짧게(12자 이내), 첫 옵션이 권장이면 라벨에 `(권장)`.

| # | 지점 | 시점 | 무엇을 묻나 | header | options |
|---|-----|----|------------|---|---|
| ① | clarify Lock confirm | clarify 종료 직후 | 정리한 이해/통과 기준이 맞는지 | `Lock 확인` | `확인` / `수정 필요` |
| ② | plan 확정 | plan 종료 직후 | 태스크·통과 기준·Max Rounds OK 여부 + 브랜치명 | `Plan 확인` | `확인` / `Max Rounds 변경` / `브랜치명 변경` / `수정 필요` |
| ③ | 결과 검수 | evaluate Verdict=PASS 후 | 결과가 의도에 부합하는지 | `결과 검수` | `확인 (사이클 종료)` / `보완 필요 (사이클 종료, 새 /task-pipeline 권장)` |
| ④ | Max Rounds 분기 | Max Rounds 모두 FAIL일 때 | 재시도 / plan 수정 / 중단 / handoff | `분기 결정` | `재시도 (라운드 리셋)` / `plan 수정` / `중단` / `handoff 문서` |
| ⑤ | 문서 업데이트 승인 | ③ 검수 OK 후, archive 전 | 컨텍스트 문서 변경 제안 중 무엇을 적용할지 | `문서 승인` | `전체 적용` / `일부만 적용 (선택)` / `적용 안 함` |

**②가 자유→정형의 분기점.** 이전에는 사용자에게 자유 질문 가능 (explore 후 *러너 부재 분기*도 이 구간). 이후에는 위 게이트 + 예외 confirm(*generate plan-외 결정·TDD blocked 발생*, *evaluate 의도 누락 FAIL 단독·이탈 발견*)에서만 묻는다. clarify를 거쳐도 작업이 하나의 방향으로 좁혀지지 않으면 ②에서 사이클을 정리하고 다른 흐름으로 진행한다.

**③ NG = 사이클 종료.** 결과를 받아들이지 않으면 사이클을 끝내고, 후속 작업은 새 `/task-pipeline` 호출로 시작한다 (자가 평가 retry 루프 금지 — 같은 실수를 반복하기 쉬워 라운드만 소진).

## 단계 계약 (한눈에)

| Step | 실행자 | 산출물 | 게이트 |
|---|---|---|---|
| 1 clarify | 메인 인라인 | `01-clarify.md` | ① Lock |
| 2 explore | @explorer | `02-explore.md` | (러너 부재 분기) |
| 3 plan | @planner | `03-plan.md` · `tasks.json` | ② Plan |
| 4 generate | @generator ×N (태스크당) | `04-generate-<Tx>.md` | — |
| 5 refactor | @refactorer | `05-refactor.md` | — |
| 6 evaluate | @evaluator | `06-evaluate.md` | ③ 검수 · ④ 분기 |
| 종료 | @context-doc-updater · @tutor | `07-context-update.md` | ⑤ 문서 승인 |

## 사이클 진입 동작 (메인)

`/task-pipeline <설명>` 호출 직후 메인이 수행:

```
bash .claude/skills/task-pipeline/scripts/state.sh init "<사용자 요청 요약>"
→ OK <cycle_dir>   (이 경로를 이후 모든 헬퍼 호출에 사용)
```

디렉토리 생성·템플릿 cp·placeholder 치환이 한 번에 일어난다 — 치환 누락이 구조적으로 불가능.

`.gitignore`에 `.claude/task-pipeline/` 누락 시 사용자에게 추가 권장 (자동 수정 안 함).

**결정론 헬퍼 (4파일 — 변이 대상별 소유권 분리)**: 기계적 작업은 메인이 손으로 하지 않고 아래 스크립트로 실행한다. 경로는 전 레포 공통 `.claude/skills/task-pipeline/scripts/` 기준. **메인은 git 변이 명령과 상태 JSON 편집을 직접 수행하지 않는다** — 아래 표의 스크립트 경유가 유일 경로이며, 이 문서에는 다단계 bash 블록을 두지 않는다 (즉흥 조합의 퇴로 차단).

| 스크립트 | 변이 대상 | 커맨드 |
|---|---|---|
| `state.sh` | 상태 JSON·라이프사이클 | init · tasks-init · task-update · step-start/finish · set-branch · round-start/finish/reset · archive |
| `git-ops.sh` | git (유일한 git 쓰기 지점) | preflight · commit-group · clean-task · commit-refactor |
| `artifact.sh` | 산출물 frontmatter | stamp |
| `inspect.sh` | **없음 (read-only 보장)** | doctor · read-signal · status · tasks · stats |

출력 규약: 모든 커맨드의 **마지막 줄 = 단일 기계 토큰**(`OK ...` 또는 실패 토큰), exit 0=정상 / 1=검증 실패 / 2=사용법 오류. 메인은 토큰으로만 분기한다.

**resume**: 사이클 도중 세션이 끊겼다 재개되면, 상태의 원천은 컨텍스트가 아니라 디스크다 — 먼저 `inspect.sh status`로 활성 사이클을 찾아 current_step별로 재진입한다. 절차는 아래 [Resume — 세션 재개 프로토콜](#resume--세션-재개-프로토콜).

각 단계 진입 시 1줄 헤더로 위치를 알린다:

```
▶ Step 1/6 · clarify
▶ Step 6/6 · evaluate (round 2/3)
✓ Done
```

## Resume — 세션 재개 프로토콜

사이클 도중 세션이 끊겼다 재개되면 **상태의 원천은 컨텍스트가 아니라 디스크**(progress.json·tasks.json·산출물 frontmatter)다. 판별은 `inspect.sh`(read-only: `status`·`tasks`·`read-signal`·`doctor`)로만, 복구는 `state.sh`/`git-ops.sh`/`artifact.sh` 커맨드로만 한다 — 이 문서 밖의 raw git/jq 절차를 새로 만들지 않는다. 확신이 안 서면 먼저 `inspect.sh doctor <cycle_dir>`로 무결성부터 본다.

**진입** — `inspect.sh status` (인자 없으면 `.claude/task-pipeline` 기준)로 활성 사이클을 찾는다:

- `NO_ACTIVE` → 활성 사이클 없음. 신규 요청이면 평소대로 `state.sh init`으로 시작.
- `OK 1` → `cycle=` 경로가 `<cycle_dir>`. 출력의 `current_step`으로 아래 표에 진입.
- `OK <n≥2>` → 활성 사이클 복수. 각 블록(`cycle=`/`current_step=`)을 사용자에게 보여주고 어느 것을 재개할지(또는 stale 정리) 물은 뒤 진행.

게이트(①②③④⑤)의 통과 여부는 디스크에 남지 않는다 — 재개 지점이 게이트 직전/직후로 판별되면 **게이트를 다시 제시**하는 게 안전하다(재확인은 무해). 아래 (c)의 반쪽 상태 복구 커맨드는 전부 멱등이라 재실행해도 안전하다.

| current_step | (a) 디스크에서 읽기 | (b) 재개 지점 | (c) 반쪽 상태 — 판별 → 복구 |
|---|---|---|---|
| `clarify` | `read-signal 01-clarify.md` | 파일 없음/`NO_FRONTMATTER` → clarify 라이브 재수행. `completed` → ① Lock 게이트부터 | 본문 O·frontmatter X(stamp 전 중단): `read-signal`=`NO_FRONTMATTER` → `artifact.sh stamp 01-clarify.md --stage clarify --status completed` 후 ① |
| `explore` | `read-signal 02-explore.md` | 없음 → explorer 재호출. `completed` → 러너 부재 분기 확인 후 plan | 본문 O·stamp X → `artifact.sh stamp 02-explore.md --stage explore --status <Status>` (explorer는 무상태 → 재호출도 안전) |
| `plan` | `read-signal 03-plan.md` + `inspect.sh tasks <dir>` + `status`의 `branch`/`base_commit` | 03 없음/`NO_FRONTMATTER` → planner 재호출. 03 `completed`·tasks 비어있음 → `state.sh tasks-init`. tasks 있음·`branch=-` → ② 게이트 → `git-ops.sh preflight`. `branch`·`base_commit` 채워짐 → `state.sh step-start generate`로 generate 진입 | **preflight 중간사**(checkout 됨·set-branch 전 중단 — git은 브랜치 위, progress는 `branch=null`): `git-ops.sh preflight <branch> <dir>` 재실행 — 그 브랜치가 현재 브랜치이고 미기록이면 스크립트가 base=HEAD로 잡아 조정, `OK <base>`(멱등). tasks-init은 원자적이라 반쪽 없음 |
| `generate` | `inspect.sh tasks <dir>`(태스크별 status·commit) + 이번 round 각 `read-signal 04-generate-<Tx>[-R<N>].md` + `status`의 `current_round` | 태스크별로 — tasks.json `done`+commit有 → 건너뜀. 산출물 `completed`인데 tasks.json `pending`/`commit=-` → 그 group `git-ops.sh commit-group` (재)실행. 산출물 `blocked`/`failed` → `git-ops.sh clean-task` 후 generator 재호출. 산출물 없음 → generator 재호출. 전 group 처리 후 refactor | **커밋됨·tasks.json 미갱신**: `inspect.sh tasks`가 `status=pending`·`commit=-`인데 `read-signal`은 `status=completed` → `git-ops.sh commit-group <dir> <group>` 재실행. 변경이 이미 HEAD에 있으면 스크립트가 새 커밋 없이 기존 커밋으로 tasks.json을 조정, `OK <hash> ...`(멱등) — raw git 불필요 |
| `refactor` | `read-signal 05-refactor[-N].md` | 없음/`NO_FRONTMATTER`/`failed` → refactorer 재호출. `completed`(적용 또는 skip) → evaluate | 리팩토링 커밋은 tasks.json 비참여·`base_commit..HEAD` diff에 포함되어 무해 → 별도 판별 불필요. refactorer 재호출이 멱등(손볼 것 없으면 `## Result: skipped`) |
| `evaluate` | `status`의 `current_round`(N) + `read-signal 06-evaluate[-N].md`(`verdict`) | 06 없음 → (`current_round`가 N이면 round-start 이미 됨) evaluator 재호출; N이 아니면 `state.sh round-start <N>` 후 evaluator. verdict 확인 후 `state.sh round-finish <N> <PASS\|FAIL>`(멱등) → verdict·round<Max로 [Step 6 분기] | **평가됨·round 미기록**(06에 `verdict=` 있음): `state.sh round-finish <dir> <N> <verdict>`는 멱등이라 그냥 실행. `round-start`만 중복 append 주의 — `current_round`가 이미 N이면 재실행 금지 |

**종료 상태(`done`/`handoff`/`cancelled`/`failed`)로 표시되는데 아직 `archived/`가 아님**(archive의 mv 미완): `state.sh archive <dir> <current_step>` 재실행 — doctor 재검증 후 mv까지 멱등하게 마무리한다.

## sub-agent 호출 공통 규약

메인이 sub-agent를 호출할 때 prompt에 다음을 *명시 주입*한다 — 산출물 입출력 경로의 placeholder가 채워지지 않으면 sub-agent가 작업 불가.

- 입력 산출물 경로(들) — sub-agent는 `Read`로 직접 읽음
- 출력 산출물 경로 — sub-agent는 `Write`로 작성
- 그 외 단계별 추가 컨텍스트 (라운드 번호, 재처리 태스크 목록 등)

sub-agent 종료 직후 메인은 산출물 frontmatter `status` 한 필드를 읽어 흐름 분기:

| status | 메인의 행동 |
|---|---|
| `completed` | 다음 단계로 (해당 지점에 게이트가 정의돼 있으면 — 게이트 표 참조 — 사용자 confirm 후) |
| `cancelled` | 사이클 종료, archived/로 이동 |
| `blocked` | 사용자에 blocker 제시 → 재시도/중단 |
| `failed` | retry 없이 즉시 사용자 알림, `current_step=failed` 종료 |

예외 — 산출물을 디스크에 쓰지 않는 sub-agent는 응답 첫 줄 `Status:`로 같은 신호를 보낸다: explorer는 항상(메인이 응답을 받아 frontmatter를 얹어 Write — Step 2 참조), planner는 시스템 에러 시(`Status: failed — <사유>` 한 줄만 응답, 산출물 없음).

**tool_result 화면 미표시**: sub-agent 응답은 tool_result로만 들어와 화면에 표시되지 않는다 — 사용자에게 보여야 하는 본문(게이트 confirm 대상 포함)은 메인이 그대로 출력한 뒤 진행한다.

**시각 기록 주체 (2체제)**: Bash를 가진 generator·refactorer·evaluator는 자기 산출물 frontmatter의 `started_at`/`finished_at`을 `date -u`로 **직접 기록**한다. 메인이 소유하는 산출물(clarify 본문, explore 응답, planner의 `<ISO8601>` placeholder)은 메인이 손으로 적지 않고 `artifact.sh stamp <file> [--stage s --status st]`로 처리한다 (frontmatter 생성/치환은 스크립트 소유). 시각 미치환·역전 leak의 원인이 두 경로 모두에서 제거된다.

**progress.json 전이**: 단계 진입 시 `state.sh step-start <cycle_dir> <step>`, 종료 시 `state.sh step-finish <cycle_dir> <step> <state>` — 수기 편집하지 않는다. evaluate 라운드는 `round-start`/`round-finish <round> <PASS|FAIL>`.

단계와 무관하게 사용자가 *"취소 / 멈춰 / 그만"* 등 명시 발화를 하면 사이클을 종료한다 (`state.sh archive <cycle_dir> cancelled`).

frontmatter 규약 상세는 `references/state-files.md`.

## Step 1 · clarify (메인 인라인 — sub-agent 아님)

**[수행]** 메인이 사용자와 라이브 멀티턴 인터뷰로 explore/plan이 의지할 *확정된 이해*를 만든다 (sub-agent는 화면에 질문이 닿지 않아 불가 → 메인 인라인). 기법·종료 조건·산출물 형식의 원천은 `references/clarify-format.md` — 메인이 Read해 적용한다 (컨텍스트 문서 참조 ⓪ · One question at a time · Understanding Lock[종료 조건 4가지: 목적/통과 기준/제외 범위/테스트 수준·대상] · Socratic Challenge 1회). 메인은 ②(plan 확정) 이전에는 자유 질문 가능.

확정된 정리를 메인이 `.claude/task-pipeline/<ts>/01-clarify.md`에 **본문만** Write — 본문은 clarify-format.md의 산출물 형식(요약/통과 기준/제외 범위/테스트 범위/미확정 사항(조건부)/참조 컨텍스트 문서(조건부)). frontmatter는 손으로 적지 않고 `artifact.sh stamp <파일> --stage clarify --status completed --started <인터뷰 시작 ISO8601>`로 부여한다 (finished는 stamp 시점 자동).

**[분기]** ① Lock 확인 게이트 — 작성 후 메인이:

```
산출물 본문(요약(의도 포함) → 통과 기준 → 제외 범위 → 테스트 범위 → 미확정 사항(있으면) → 참조 컨텍스트 문서(있으면))을 이 순서로 전체 출력한 뒤 AskUserQuestion으로 confirm.
```

- `수정 필요` → 메인이 어느 부분을 고칠지 자유 질문으로 받아 산출물 갱신 후 다시 confirm.
- 인터뷰 중 "취소/그만/잘못 호출" → `status: cancelled` + `## Cancellation`(발화 인용+시점), 사이클 종료. 정보 부족(사용자 잘 모름·타인 결정 필요) → `status: blocked` + `## Blocker` 후 재시도/중단 질문.

> 부적합 감지: variant 공존(A/B)·탐색측정(spike·벤치마크·데이터 분석)·git 영구화가 부자연스러운 신호면 부적합을 지적하고 취소/다른 흐름 제안 — 상세는 clarify-format.md.

## Step 2 · explore (@explorer)

**[호출]** explorer는 디스크에 쓰지 않고 텍스트로 4섹션 마크다운을 반환(형식은 explorer.md) — 메인이 응답에 frontmatter를 얹어 Write. prompt 템플릿:

```
clarify 산출물 경로: .claude/task-pipeline/<ts>/01-clarify.md
clarify 산출물 본문: <메인이 위 파일 내용을 인라인으로 주입>
작업 루트: <pwd>

4섹션 마크다운 형식으로 응답 (형식 정의는 explorer.md 출력 규격을 따름).
디스크에 쓰지 말고 단일 메시지로 반환.
```

**[후처리]** 메인이 explorer 응답 **본문**(첫 줄 `Status:` 제외)을 `.claude/task-pipeline/<ts>/02-explore.md`에 Write한 뒤, frontmatter를 stamp로 부여한다:

```
bash .claude/skills/task-pipeline/scripts/artifact.sh stamp \
  .claude/task-pipeline/<ts>/02-explore.md \
  --stage explore --status <explorer 첫 줄 Status 값> --started <호출 시각 ISO8601>
```

**[분기]** `blocked`/`cancelled`면 본문은 4섹션 대신 `## Blocker`/`## Cancellation`만 온다 (status 분기 자체는 공통 status 표).

- 미확정 사항 회신의 [신규 의문]·[조건 보고: 성립/판정불가] 항목이 있으면 plan 진입 전에 메인이 *자유 질문*으로 처리.
- **러너 부재 분기**: `## 테스트 환경`이 러너 부재(X) + 테스트 면제 아님이면, plan 진입 전 AskUserQuestion — `러너 셋업 태스크 추가` / `이번 사이클 TDD 면제`. 결과를 planner prompt에 명시 주입.

> 러너 도입을 자동화하지 않는 이유: 의존성 추가는 프로젝트 차원 결정.

## Step 3 · plan (@planner)

**[호출]** prompt 템플릿:

```
clarify 산출물: .claude/task-pipeline/<ts>/01-clarify.md
explore 산출물: .claude/task-pipeline/<ts>/02-explore.md
산출물 경로: .claude/task-pipeline/<ts>/03-plan.md
사용자 요청 원문: <원문>
(러너 부재 분기 결과 — 해당 시): 러너 셋업 태스크 추가 / 이번 사이클 TDD 면제
```

> planner 산출물은 6섹션(개요/인터페이스 계약/실행 계획/테스트 실행/통과 기준/범위 밖·위험) + **`## 태스크 데이터`의 ```json tasks 블록**(groups·tasks 기계용 — 산문 실행 계획과 동일 내용) — 내부 구성은 planner.md. 메인이 쓰는 계약: **개요의 유형 값**=브랜치 prefix, **json tasks 블록**=tasks.json·커밋 구성 원천 (메인이 산문을 번역하지 않는다). planner는 Bash 없음 → frontmatter 시각은 `<ISO8601>` placeholder로 남고, 메인이 plan 종료 직후 `artifact.sh stamp <plan 경로> --started <호출 시각>`으로 치환.

**[후처리]** 종료 후 메인이:

1. `tasks.json` 초기화 — `state.sh tasks-init <cycle_dir>` (plan의 ```json tasks 블록으로 생성 — 스키마·stage 내 비겹침 검증은 스크립트 소유). 토큰 분기: `OK <n>` → 진행 / `NO_BLOCK`·`SCHEMA_VIOLATION`·`OVERLAP` → planner 결함이므로 결함 내용 주입해 재호출 (게이트 ② **전**에 잡혀 사용자는 결함 plan을 안 봄).
2. 브랜치명 제안 — clarify 요약의 '작업' 행에서 slug 추출(영문 kebab-case, 최대 30자), plan **개요의 유형** 값 prefix와 결합. 패턴: `<type>/<slug>` (예: `feat/home-screen-scaffold`, `refactor/components-extract`). plan 개요에 유형이 없거나 모호하면 `feat`로 기본 적용.
3. ② Plan 확인 게이트 — planner 산출물은 디스크에만 있으므로, 메인이 plan 본문(개요 → 인터페이스 계약 → 실행 계획 → 테스트 실행 → 통과 기준 → 범위 밖·위험 순서 전체)과 제안 브랜치명을 화면에 먼저 출력한 뒤 AskUserQuestion으로 confirm한다. 사용자가 `브랜치명 변경`을 선택하면 메인이 자유 텍스트로 입력 받아 검증(`^[a-z0-9][a-z0-9/_-]{0,63}$`) 후 그 값을 사용한다.
4. confirm 후 `git-ops.sh preflight <branch> <cycle_dir>` 실행 — 브랜치 생성 + `base_commit` 기록을 한 호출로 (브랜치명 검증·git 검사는 스크립트 소유).

   토큰 분기: `NOT_GIT` → 비-git 디렉토리라 진행 안 함, `current_step=failed` 종료. `DIRTY` → 브랜치 만들지 않고 commit/stash/중단 요청. `BAD_NAME`·`BRANCH_EXISTS` → 다른 브랜치명 요청. `OK <base_hash>` → 완료. base는 progress.json `base_commit`에 저장돼 이후 evaluate에 주입된다 (세션 컨텍스트 비의존 — resume 후에도 유효). preflight 멱등 재개는 Resume 절.

**[분기]** 이 Step의 분기는 후처리에 인라인 — ② Plan 게이트(3)와 git preflight 토큰(4). preflight `NOT_GIT`만 종료 분기(`current_step=failed`), 나머지는 게이트·요청 반복으로 흡수.

## Step 4 · generate (@generator)

**[호출]** 호출 단위 = 태스크 1개, 커밋 단위 = group 1개 (분리). 메인이 stage별로 순회하며 태스크당 generator를 호출하고, stage 종료 후 커밋·갱신을 직렬 후처리한다. 순회:

```
for stage in plan.stages:
    targets = stage의 모든 태스크 ID (같은 stage면 group 무관 동시 호출)
    for t in targets:
        invoke @generator(target_task=t)  ← multiple tool calls 한 메시지로
    wait_all()
    후처리(메인, 직렬): git-ops.sh clean-task(실패 태스크) → git-ops.sh commit-group(group별 — tasks.json 갱신 내장)
    if any failed/blocked: break
```

> stage=스케줄링 축(같은 stage 동시·다른 stage 순차), group=커밋 묶음(group ⊂ stage) — 정의는 state-files.md tasks.json 절. 커밋을 메인이 직렬 처리하는 이유: 동시 인스턴스가 git index 공유 → 동시 커밋 race·교차오염.

prompt 템플릿 (인스턴스당):

```
clarify 산출물: .claude/task-pipeline/<ts>/01-clarify.md
explore 산출물: .claude/task-pipeline/<ts>/02-explore.md
plan 산출물: .claude/task-pipeline/<ts>/03-plan.md
산출물 경로: .claude/task-pipeline/<ts>/04-generate-<Tx>.md  (round ≥2이면 04-generate-<Tx>-R<N>.md)
tasks.json 경로: .claude/task-pipeline/<ts>/tasks.json  (Read 전용 — 갱신은 메인이 일괄 처리)
현재 라운드: <N>
target_task: "Tx"   ← 이 인스턴스가 처리할 단일 태스크 ID
role: <plan 태스크의 role 값>   ← role별 추가 컨텍스트가 정의돼 있으면 메인이 함께 주입
이전 evaluate 산출물: .claude/task-pipeline/<ts>/06-evaluate.md 또는 06-evaluate-<N-1>.md   ← round ≥2일 때만 주입 (retry 사유 흡수용)
작업 루트: <pwd>
```

retry(round ≥2)에서는 메인이 *재처리 태스크 목록*을 stage 순으로 재구성해 동일 흐름으로 호출.

> generator 계약: 태스크당 코드 변경만(태스크 내 TDD·커밋 안 함, `## TDD 증거` 기록) — 내부 동작은 generator.md. 커밋 구성은 plan·tasks.json이 원천, 커밋은 메인이 group 단위로 생성. 메인은 산출물 `status`(아래 [분기])와 plan `touched_files` 범위(같은 stage 비겹침 = 동시 편집 안전)로만 generator를 접한다.

**[후처리]** 각 인스턴스 종료 후, 메인은 frontmatter status 분기 판단 *전에* 다음을 **직렬로** 수행한다 (동시 갱신 lost-update·git 경합 방지 — generator가 시각 자가 기록하므로 메인 치환 단계 없음):

1. **실패 태스크 정리**: `blocked`/`failed` 인스턴스마다 `git-ops.sh clean-task <cycle_dir> <task_id>` — **커밋 전에**, 잔존물이 다음 단계에 안 섞이도록 (completed 지정 거부 등 안전장치는 스크립트 소유).
2. **group별 커밋**: group마다 `git-ops.sh commit-group <cycle_dir> <group_id>` — completed 태스크만 골라 1커밋 + tasks.json 기록까지 **원자적**. 선별·subject·add·해시 기록은 스크립트가 하고, **메인은 어떤 값도 옮겨 적지 않는다**.
   - retry(round ≥2): `commit-group <cycle_dir> <group_id> --retry <round> -m "<실패 사유 요약>"` → `fix(<group>): ...` 새 커밋. 사유 요약만 메인이 이전 evaluate에서 취해 전달.
   - 토큰: `OK <hash> <태스크 ID들>` → 진행 / `NO_COMPLETED`(전원 실패) / `COMMIT_FAILED`(실제 커밋 실패 — 원인 확인 후 재시도). 재실행 멱등(반쪽 상태 흡수)은 Resume 절.

**[분기]** 후처리 후 frontmatter status로 분기 (generator의 `blocked`에는 TDD 진행 불가[RED 미형성·GREEN 미달]도 포함):

- `completed` → 다음 (모든 동시 인스턴스 완료 대기 후 다음 stage 또는 refactor로 진입)
- `blocked` (plan-외 결정 필요 또는 touched_files 위반) → 메인이 사용자에 결정 묻고 plan을 갱신할지 ④로 분기할지 결정
- `failed` → 같은 stage의 다른 인스턴스 완료를 기다린 뒤 즉시 종료

stage 내 일부 태스크가 fail/blocked, 나머지 completed인 경우: 완료된 태스크의 group 커밋은 그대로 유지하고, 실패 태스크만 다음 round에서 재처리한다(그 group에 fix 커밋이 추가됨).

## Step 5 · refactor (@refactorer)

**[호출]** prompt 템플릿:

```
plan 산출물: .claude/task-pipeline/<ts>/03-plan.md
tasks.json 경로: .claude/task-pipeline/<ts>/tasks.json  (Read 전용 — 이번 round `done` 태스크 touched_files 합집합이 리팩토링 범위)
사이클 디렉토리: .claude/task-pipeline/<ts>  (commit-refactor 호출 인자용)
산출물 경로: .claude/task-pipeline/<ts>/05-refactor.md  (round ≥2이면 05-refactor-<N>.md)
현재 라운드: <N>
작업 루트: <pwd>
```

> refactorer 계약: 이번 round `done` 태스크 touched_files 범위 안 동작 보존 리팩토링(5축·기준선 GREEN 확인) — 내부 동작·범위 규칙은 refactorer.md. 커밋은 raw git이 아니라 **`git-ops.sh commit-refactor`** 경유(파이프라인 경로 거부·amend 불가를 스크립트가 강제 — git 쓰기의 유일 경로 불변식 유지). 손볼 게 없으면 `## Result: skipped`. 산출물 `## 이월 후보`는 done 종료 시 메인이 표시(종료 처리).

**[후처리]** 없음 — refactorer가 스스로 커밋한다. 메인은 산출물 status만 확인.

**[분기]** `completed`(리팩토링 적용 또는 skip) → evaluate 진입. `failed`(도구·환경 에러)는 공통 status 표대로.

## Step 6 · evaluate (@evaluator)

**[호출]** prompt 템플릿:

```
plan 산출물: .claude/task-pipeline/<ts>/03-plan.md
tasks.json 경로: .claude/task-pipeline/<ts>/tasks.json
generate 산출물 패턴: .claude/task-pipeline/<ts>/04-generate-*.md  (round 1) / .claude/task-pipeline/<ts>/04-generate-*-R<N>.md  (round ≥2) — 이번 round에 처리된 모든 태스크의 산출물을 ls로 식별 후 모두 Read
refactor 산출물: .claude/task-pipeline/<ts>/05-refactor.md  (round ≥2이면 05-refactor-<N>.md)
산출물 경로: .claude/task-pipeline/<ts>/06-evaluate.md  (round ≥2이면 06-evaluate-<N>.md)
현재 라운드: <N>
Max Rounds: <plan에서 ② confirm된 값>
base 커밋: <progress.json의 base_commit 값 — preflight가 기록, 2-B diff 기준>
작업 루트: <pwd>
```

호출 직전 `state.sh round-start <cycle_dir> <N>`, Verdict 확인 후 `state.sh round-finish <cycle_dir> <N> <PASS|FAIL>`로 라운드를 기록한다.

> evaluator 계약: plan 부합(주축)+verify(보조) 두 축 AND 결합으로 `Verdict`·실패 유형 산출 — 판정 기법은 evaluate-report.md/evaluator.md.

**[후처리]** 없음 — evaluator가 산출물을 자가 Write(시각 자가 기록). 메인은 `Verdict`·실패 유형만 읽는다.

**[분기]** 종료 후 메인이 본문 `Verdict` + 실패 유형을 읽어 분기한다. **핵심 원칙: 자동 재시도는 객관 신호(구조·verify)에만. 주관 판단(의도 누락)·이탈은 사람이 결정한다** (③의 "자가 평가 retry 루프 금지" 원칙과 동일).

- `Verdict: PASS` → ③ 결과 검수 게이트. evaluate 산출물은 디스크에만 있으므로, 메인이 결과 요약(Verdict·plan 부합/verify 두 축 결과·핵심 변경)을 화면에 먼저 출력한 뒤 AskUserQuestion으로 검수받는다. evaluate 산출물에 '사람 검수 대기' 목록이 있으면 ③에서 항목별로 함께 표시한다 (plan이 verify 사각으로 등재한 '사람 확인 필요' 항목 — 사람만 판정 가능)
- `Verdict: FAIL` → 본문의 실패 유형에 따라:
  - **구조 누락 / verify FAIL** (객관): 영향 태스크를 tasks.json에서 `failed`로 변경. 추정 불가면 사용자에 자유 질문. round +1 후 **자동으로 generator → refactorer → evaluator 순 재호출**
  - **의도 누락(주관)이 *유일한* FAIL 사유**: 자동 재시도하지 않는다. AskUserQuestion으로 해당 의도 항목을 보여주고 분기 (예외 confirm) — `재시도 / 수용(③로) / 종료`. 재시도 선택 시에만 영향 태스크 `failed` → round +1 재호출
  - 객관 FAIL과 의도 누락 FAIL이 *함께* 있으면: 객관이 재시도를 트리거하므로 자동 재시도하고, 그 round에 의도 항목은 같이 재검증된다 (별도로 사람에게 묻지 않음)
  - **이탈** (plan에 없는 변경): 이탈 내역을 사용자에 그대로 보여주고 `plan 수정 / generator 재실행 / 허용(plan에 사후 추가)` 자유 질문 → 선택에 따라 분기
  - round가 Max Rounds 초과면 ④ 분기

plan에 verify 명령이 없으면 verify 축은 `N/A`로 두고 plan 부합 축만으로 Verdict 결정.

frontmatter `status: failed` (verify 명령 자체 실행 불가)면 retry 없이 사용자 알림 + 종료.

## ④ 분기 처리 상세

Max Rounds 모두 FAIL이면 AskUserQuestion으로 4지선다 — 선택지 라벨은 게이트 표 ④ 참조. 아래 표는 각 선택의 **메인 행동**(유일 원천):

| 선택 | 메인의 행동 |
|---|---|
| 재시도 (라운드 리셋) | `state.sh round-reset <cycle_dir>` (commit 필드는 유지 — 과거 커밋은 git history에 남음). generate부터 다시 |
| plan 수정 | `state.sh step-start <cycle_dir> plan`, planner 재호출 (사용자에게 어떤 부분 수정할지 자유 질문 후 prompt에 주입) |
| 중단 | `state.sh archive <cycle_dir> cancelled` |
| handoff 문서 | @handoff-creator 호출(있으면) 또는 메인이 직접 `.claude/task-pipeline/<ts>/handoff.md` 작성, `current_step=handoff` |

## 종료 직전 · 컨텍스트 문서 업데이트 (@context-doc-updater) — done 한정

③ 결과 검수 OK로 `current_step=done`이 확정되면, tutor 제안·archive **전에** 메인이 수행한다 (`cancelled`/`failed`/`handoff` 종료에서는 skip — 완료된 작업의 학습만 문서화):

1. @context-doc-updater를 `mode: propose`로 호출. prompt에 주입:
   - `targets`: `docs/` 내 문서들 — clarify `## 참조 컨텍스트 문서`에 기록된 문서 우선. `docs/` 부재 시 targets 생략 (에이전트가 후보 발굴, 새 문서 생성 제안 가능)
   - `session_context`: 이번 사이클 요약 — clarify 요지, plan 설계, generate/evaluate에서 드러난 결정·학습
2. 제안이 있으면 **⑤ 문서 업데이트 승인 게이트** — 받은 제안 본문을 출력한 뒤 AskUserQuestion으로 적용 범위를 confirm받는다 (선택지는 게이트 표 ⑤)
3. 승인분만 `mode: apply`로 재호출해 적용 — `일부만 적용`이면 사용자가 고른 제안 번호만 전달한다(제안마다 번호가 매겨져 있음). 적용된 문서 변경은 메인이 사이클 브랜치에 커밋 — `docs: 컨텍스트 문서 갱신 (task-pipeline)`
4. 메인이 `.claude/task-pipeline/<ts>/07-context-update.md`에 기록: 제안 요약 · 사용자 결정 · 적용 파일 목록. *"변경 제안 없음"* 응답이면 그 사실만 한 줄 기록하고 게이트는 생략

## 종료 직전 · tutor (@tutor) — 선택 호출

`current_step`이 종료 상태(`done` / `cancelled` / `failed` / `handoff`) 중 하나로 결정되면 (done이면 컨텍스트 문서 업데이트까지 마친 뒤), archive 직전에 메인이 한 번 tutor 호출을 제안한다.

> `AskUserQuestion` — header=`설명 듣기`, options=[`네, 설명 들을게요`, `아니요, 종료`]

**[호출]** Yes 선택 시 메인이 @tutor를 호출. prompt 템플릿:

```
사이클 디렉토리: .claude/task-pipeline/<ts>/
종료 경로: done | failed | handoff | cancelled
작업 루트: <pwd>
```

**[후처리]** tutor는 산출물·`git log`/`git diff`를 근거로 설명을 채팅으로만 반환(디스크 산출물 없음) — 내부 동작은 tutor.md. 메인은 받은 본문을 그대로 출력한다(공통 규약).

설명 후 사용자가 추가 질문하면 자연스럽게 Q&A 흐름으로 이어지고, 다른 주제로 이동하면 자연 종료된다 (별도 종료 키워드 없음). Q&A가 끝나면 메인이 archive 진행. No 선택 시 곧장 archive.

## 종료 처리

archive는 `state.sh archive <cycle_dir> <done|handoff|cancelled|failed>` 한 호출 — **doctor 검증이 내장**되어 있어 통과해야만 current_step 기록·mv가 일어난다 (깨진 상태가 archived/에 굳는 경로가 구조적으로 없음). `DOCTOR_FAILED` 시 doctor 출력의 문제를 메인이 해소(주로 시각 보정·enum 위반)한 뒤 재실행한다.

종료 상태별 (tutor 호출 여부와 무관):

- `done` (③ 검수 OK): archive **전**, refactor 산출물(들)에 `## 이월 후보`가 있으면 메인이 사용자에게 그대로 표시한다 (다음 세션 인지용 — 착수 트리거·누적 매체는 미설계). archive 후 메인이 "현재 브랜치: <branch>. PR/머지는 별도로 진행하세요" 안내
- `cancelled` / `failed` / `handoff`: 동일하게 archive, 브랜치는 그대로 둠

push와 PR 생성은 자동화하지 않는다.
