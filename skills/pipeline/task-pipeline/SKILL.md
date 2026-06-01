---
name: task-pipeline
description: "요구사항이 정해진 코드 변경 작업을 위한 6단계 파이프라인(clarify → explore → plan → generate → refactor → evaluate). /task-pipeline <설명>으로 호출. 탐색·측정·variant 공존 작업(A/B 테스트, spike, 벤치마크 등)에는 적합하지 않음."
argument-hint: "[작업 설명 (자유 텍스트, 빈 인자 허용)]"
disable-model-invocation: true
---

# task-pipeline — 코드 변경 작업의 6단계 파이프라인

작업을 일관된 6단계 흐름으로 처리한다. clarify는 사용자와의 라이브 인터뷰가 필요하므로 *메인이 인라인으로 직접 수행*하고, 나머지 단계는 별도 서브에이전트가 담당한다. 메인은 *오케스트레이터 + clarify 인터뷰 + 게이트 4지점 confirm*을 책임진다. 산출물은 디스크에 영속화되어 단계 간 인계가 명시적으로 일어난다.

## 정체성

- 호출: `/task-pipeline <자유 텍스트>` (빈 인자 허용)
- 명시 호출 전용. 자동 키워드 트리거 없음
- 6단계: clarify → explore → plan → generate → refactor → evaluate
- clarify는 메인 인라인(사용자 인터뷰). explore~evaluate + tutor는 sub-agent로 위임. 메인은 흐름 통제·clarify 인터뷰·게이트 confirm·디스크 조작

## 적용 범위

**적합한 작업**
- 요구사항이 정해진 코드 변경 작업 (호출 시점에 명확하지 않아도 됨 — clarify가 정제함)
- 결과를 git commit으로 영구화하는 게 자연스러운 작업
- 예: 기능 구현(feat), 버그 수정(fix), 리팩토링(refactor), 마이그레이션, 문서/설정 변경(docs/chore/test)

**적합하지 않은 작업**
- explore 단계에서 결론나야 할 작업 — spike형 비교, 짧은 학습 실험
- variant들이 공존해야 하는 작업 — A/B 테스트
- 결과가 데이터·측정으로 결정되는 작업 — 성능 벤치마크, 데이터 분석

**진입 조건**

호출 시점의 명확도는 무관 — clarify 단계가 정제하므로 자유 텍스트 한 줄도 받는다. 진짜 조건은 *clarify를 거쳐 plan에서 하나의 방향으로 좁혀질 수 있는지*. 좁혀지지 않는 작업이면 ② plan 게이트에서 사이클을 정리하고 다른 흐름으로 진행하는 게 자연스럽다.

## 흐름

```
[1] clarify → [2] explore → [3] plan → (브랜치 생성) → [4] generate → [5] refactor → [6] evaluate → (선택) tutor

종료 상태: done · handoff · cancelled · failed
```

## 사용자 개입 4지점 (게이트)

| # | 지점 | 무엇을 묻나 | 시점 |
|---|-----|------------|----|
| ① | clarify Lock confirm | 정리한 이해/통과 기준이 맞는지 | clarify 종료 직후 |
| ② | plan 확정 | 태스크·통과 기준·Max Rounds OK 여부 + 브랜치명 | plan 종료 직후 |
| ③ | 결과 검수 | 결과가 의도에 부합하는지 | evaluate Verdict=PASS 후 |
| ④ | Max Rounds 분기 | 재시도 / plan 수정 / 중단 / handoff | Max Rounds 모두 FAIL일 때 |

**②가 자유→정형의 분기점.** 이전에는 사용자에게 자유 질문 가능. 이후에는 정해진 4지점 + 예외 confirm(*explore 모호 분기 발견*, *generate plan-외 결정 발생*, *evaluate 의도(2-D) FAIL 단독·이탈 발견*)에서만 묻는다.

**③ NG = 사이클 종료.** 결과를 받아들이지 않으면 사이클을 끝내고, 후속 작업은 새 `/task-pipeline` 호출로 시작한다 (자가 평가 retry 루프 금지 — 같은 실수를 반복하기 쉬워 라운드만 소진).

## 메인 게이트 발화는 모두 AskUserQuestion 도구 사용

자유 텍스트 묻기 대신 `AskUserQuestion`으로 다지선다. header는 짧게(12자 이내), 첫 옵션이 권장이면 라벨에 `(권장)`.

| # | header | options |
|---|---|---|
| ① | `Lock 확인` | `확인` / `수정 필요` |
| ② | `Plan 확인` | `확인` / `Max Rounds 변경` / `브랜치명 변경` / `수정 필요` |
| ③ | `결과 검수` | `확인 (사이클 종료)` / `보완 필요 (사이클 종료, 새 /task-pipeline 권장)` |
| ④ | `분기 결정` | `재시도 (라운드 리셋)` / `plan 수정` / `중단` / `handoff 문서` |

## 사이클 진입 동작 (메인)

`/task-pipeline <설명>` 호출 직후 메인이 수행:

```bash
TS=$(date -u +"%Y-%m-%dT%H-%M-%S")
TASK_PIPELINE_DIR=".claude/task-pipeline/$TS"
mkdir -p "$TASK_PIPELINE_DIR"
```

`progress.json` 초기화 — `templates/progress.template.json`을 `$TASK_PIPELINE_DIR/progress.json`으로 cp 후 placeholder(`__ISO8601__`, `__USER_REQUEST__`)만 치환한다.

`.gitignore`에 `.claude/task-pipeline/` 누락 시 사용자에게 추가 권장 (자동 수정 안 함).

각 단계 진입 시 1줄 헤더로 위치를 알린다:

```
▶ Step 1/6 · clarify
▶ Step 6/6 · evaluate (round 2/3)
✓ Done
```

## sub-agent 호출 공통 규약

메인이 sub-agent를 호출할 때 prompt에 다음을 *명시 주입*한다 — 산출물 입출력 경로의 placeholder가 채워지지 않으면 sub-agent가 작업 불가.

- 입력 산출물 경로(들) — sub-agent는 `Read`로 직접 읽음
- 출력 산출물 경로 — sub-agent는 `Write`로 작성
- 그 외 단계별 추가 컨텍스트 (라운드 번호, 재처리 태스크 목록 등)

sub-agent 종료 직후 메인은 산출물 frontmatter `status` 한 필드를 읽어 흐름 분기:

| status | 메인의 행동 |
|---|---|
| `completed` | 다음 단계로 (게이트 4지점이면 사용자 confirm 후) |
| `cancelled` | 사이클 종료, archived/로 이동 |
| `blocked` | 사용자에 blocker 제시 → 재시도/중단 |
| `failed` | retry 없이 즉시 사용자 알림, `current_step=failed` 종료 |

frontmatter 규약 상세는 `references/state-files.md`.

## Step 1 · clarify (메인 인라인 — sub-agent 아님)

목적: explore/plan이 의지할 *확정된 이해*를 만든다.

clarify는 사용자와 라이브 멀티턴 인터뷰가 필수다. sub-agent는 사용자에게 직접 질문할 수 없고(질문이 화면에 닿지 않음) 한 번 호출하면 이어 받기도 불가하므로, **메인이 인라인으로 직접 수행**한다. 메인은 게이트 외에도 ②(plan 확정) 이전에는 사용자에게 자유롭게 질문할 수 있다.

진행:

1. 메인이 `references/clarify-techniques.md`를 Read로 읽어 기법(One question at a time · Understanding Lock · Socratic Challenge)을 적용한다.
2. `AskUserQuestion`으로 *한 번에 한 질문*씩 인터뷰해 종료 조건 4가지(목적 · 통과 기준 · non-goals · 테스트 범위)를 채운다. 테스트 범위는 작업 성격을 보고 메인이 *제안→협의*로 확정한다 (clarify-techniques ④ 참고 — 강제 아님).
3. 네 항목이 채워지면 Socratic Challenge를 무조건 1회 수행한다 — 핵심 가정 2~3개를 식별해 `AskUserQuestion`으로 정면 도전, 빈틈이 드러나면 이해를 갱신(escalate는 가정당 1회, lock 갱신 1회까지).
4. 확정된 정리를 메인이 직접 `.claude/task-pipeline/<ts>/01-clarify.md`에 Write한다. 형식은 `references/clarify-techniques.md`의 산출물 형식(Understanding Summary / Assumptions / Challenge 통과 전제 / Open Questions / Verify 단서 / **테스트 범위**). frontmatter는 `stage: clarify`, `status: completed`, `started_at`/`finished_at`은 메인이 인터뷰 시작·종료 시각을 실제 ISO8601로 직접 기록한다(메인은 Bash로 시각 조회 가능 — placeholder 불필요).

사용자가 인터뷰 도중 "취소/그만/잘못 호출" 발화 시: 메인이 산출물 frontmatter `status: cancelled` + `## Cancellation`(발화 인용+시점)로 작성하고 사이클을 종료한다. 인터뷰 진행 불가능한 정보 부족(사용자가 잘 모름·타인 결정 필요)이면 `status: blocked` + `## Blocker`로 작성 후 사용자에 재시도/중단을 묻는다.

작성 후 메인이 ① Lock 확인 게이트:

```
산출물 본문(Understanding Summary, Assumptions, Challenge 통과 전제, Verify 단서, 테스트 범위)을 사용자에게 보여주고 AskUserQuestion으로 confirm.
```

사용자가 `수정 필요`를 선택하면 메인이 어느 부분을 고칠지 자유 질문으로 받아 산출물을 갱신한 뒤 다시 confirm한다.

## Step 2 · explore (@explorer)

기존 explorer는 *텍스트로 5섹션 마크다운을 반환*하는 형태이며 디스크에 직접 쓰지 않는다. 메인이 응답 텍스트를 받아 frontmatter를 얹어 직접 Write한다.

호출 prompt 템플릿:

```
clarify 산출물 경로: .claude/task-pipeline/<ts>/01-clarify.md
clarify 산출물 본문: <메인이 위 파일 내용을 인라인으로 주입>
작업 루트: <pwd>

5섹션 마크다운 형식으로 응답 (관련 파일/핵심 심볼/외부 의존성/변경 영향 범위/미해결 의문).
clarify가 테스트 작성을 합의했으면 "변경 영향 범위"에 기존 테스트 커버리지(러너·디렉토리·변경 대상 커버 유무·실행 명령)를 포함해 반환.
디스크에 쓰지 말고 단일 메시지로 반환.
```

explorer 응답 수신 후 메인이 다음 frontmatter를 얹어 `.claude/task-pipeline/<ts>/02-explore.md`에 Write:

```yaml
---
stage: explore
status: completed
started_at: <ISO8601>
finished_at: <ISO8601>
---
```

미해결 의문이 있으면 plan 진입 전에 메인이 *자유 질문*으로 처리.

## Step 3 · plan (@planner)

호출 prompt 템플릿:

```
clarify 산출물: .claude/task-pipeline/<ts>/01-clarify.md
explore 산출물: .claude/task-pipeline/<ts>/02-explore.md
산출물 경로: .claude/task-pipeline/<ts>/03-plan.md
사용자 요청 원문: <원문>
```

planner가 채택 설계 + 태스크 분해 + verify 명령 + Non-goals + 위험 + Max Rounds 권장값을 작성. 추가로 plan 본문 상단에 **작업 유형**(`feat` / `fix` / `refactor` / `chore` / `docs` / `test` 중 하나)을 한 줄로 명시한다 — 메인이 브랜치명 prefix로 사용한다. clarify `## 테스트 범위`도 함께 받아 `## 테스트 범위 반영`(작성O면 테스트 태스크 group `type:test`, 작성X면 면제 사유)으로 처리한다.

planner는 시각을 알 수 없으므로 frontmatter의 `started_at` / `finished_at`을 `<ISO8601>` placeholder로 둔다. 메인은 sub-agent 종료 직후 호출 시각·응답 시각을 실제 ISO8601로 산출물에서 치환한다 (explore 등 다른 sub-agent 단계와 동일 패턴).

종료 후 메인이:

1. `tasks.json` 초기화 — `templates/tasks.template.json`을 cp하면 `{"tasks": []}` 빈 배열로 시작한다. 메인이 plan의 각 태스크에 대해 `references/state-files.md`의 tasks 객체 스키마를 따라 새 객체를 만들어 배열에 push한다 (`id`/`title`/`group`/`stage`/`touched_files`/`depends_on`은 plan에서 채우고, `status`는 `pending`, `commit`/`started_at`/`finished_at`은 `null`).
2. 브랜치명 제안 — clarify Understanding Summary 첫 bullet에서 slug 추출(영문 kebab-case, 최대 30자), plan 본문 상단의 **작업 유형** prefix와 결합. 패턴: `<type>/<slug>` (예: `feat/home-screen-scaffold`, `refactor/components-extract`). plan에 작업 유형이 없거나 모호하면 `feat`로 기본 적용.
3. ② Plan 확인 게이트 — AskUserQuestion으로 plan 본문 + 제안 브랜치명을 함께 confirm. 이때 메인은 plan의 `## 테스트 범위 반영`을 사용자에게 함께 보여줘, clarify에서 합의한 테스트가 태스크로 반영됐는지(또는 면제 사유가 타당한지) **눈으로 확인**받는다 — planner의 테스트 누락을 막는 사람 백스톱. 사용자가 `브랜치명 변경`을 선택하면 메인이 자유 텍스트로 입력 받아 검증(`^[a-z0-9][a-z0-9/_-]{0,63}$`) 후 그 값을 사용한다.
4. confirm 후 브랜치 생성 전 git preflight를 수행.
   - `git rev-parse --is-inside-work-tree`가 실패하면 `current_step=failed`로 종료. task-pipeline는 태스크별 commit을 전제로 하므로 비-git 디렉토리에서는 진행하지 않는다.
   - `git status --porcelain -- ':!.claude/task-pipeline'`로 작업트리를 확인한다. 기존 변경이 있으면 브랜치를 만들지 않고 사용자에게 commit/stash/중단 중 하나를 요청한다.
   - `git show-ref --verify --quiet refs/heads/<branch>`로 같은 이름의 로컬 브랜치가 있는지 확인한다. 이미 있으면 사용자에게 다른 브랜치명 입력을 요청한다.
5. preflight 통과 후 `git checkout -b <branch>` 실행.

## Step 4 · generate (@generator)

**호출 단위는 *태스크 1개*, 커밋 단위는 *group 1개*다 — 둘은 분리돼 있다.** `stage`는 *언제 도느냐*(스케줄링: 같은 stage는 동시, 다른 stage는 순차), `group`은 *어떻게 묶어 커밋하느냐*(논리 단위, group ⊂ stage). 메인은 stage 순으로 순회하며 같은 stage 안의 모든 태스크에 generator를 *동시에 호출*하고(같은 메시지의 multiple tool calls), 같은 stage가 끝나면 **group 단위로 직렬 커밋**한 뒤 다음 stage로 진입한다. **커밋은 generator가 아니라 메인이 한다** — 동시 인스턴스가 하나의 git index를 공유해 동시 커밋은 race·교차오염을 일으키기 때문.

```
for stage in plan.stages:
    targets = stage의 모든 태스크 ID (같은 stage면 group 무관 동시 호출)
    for t in targets:
        invoke @generator(target_task=t)  ← multiple tool calls 한 메시지로
    wait_all()
    후처리(메인, 직렬): 시각 치환 → 실패 태스크 워킹트리 정리 → group별 커밋 → tasks.json 일괄 갱신
    if any failed/blocked: break
```

호출 prompt 템플릿 (인스턴스당):

```
clarify 산출물: .claude/task-pipeline/<ts>/01-clarify.md
explore 산출물: .claude/task-pipeline/<ts>/02-explore.md
plan 산출물: .claude/task-pipeline/<ts>/03-plan.md
산출물 경로: .claude/task-pipeline/<ts>/04-generate-<Tx>.md  (round ≥2이면 04-generate-<Tx>-R<N>.md)
tasks.json 경로: .claude/task-pipeline/<ts>/tasks.json  (Read 전용 — 갱신은 메인이 일괄 처리)
현재 라운드: <N>
target_task: "Tx"   ← 이 인스턴스가 처리할 단일 태스크 ID
이전 evaluate 산출물: .claude/task-pipeline/<ts>/06-evaluate.md 또는 06-evaluate-<N-1>.md   ← round ≥2일 때만 주입 (retry 사유 흡수용)
작업 루트: <pwd>
```

retry(round ≥2)에서는 메인이 *재처리 태스크 목록*을 stage 순으로 재구성해 동일 흐름으로 호출.

generator는 단일 태스크의 코드 변경만 하고 **커밋하지 않는다** — 산출물 `## 커밋 항목`에 명세(group·type·summary·touched_files)만 적는다. 커밋은 메인이 group 단위로 직렬 생성한다.

동시 호출 안전성: 같은 stage의 태스크들은 plan에서 `touched_files`가 겹치지 않음이 보장돼 동시 *파일 편집*은 안전하다(서로 다른 파일). git을 만지는 주체는 메인 하나뿐이므로 index.lock 경합·교차오염이 원천 차단된다. generator는 자신의 `touched_files` 외 파일에 write 시도 시 `blocked`로 종료.

각 인스턴스 종료 후, 메인은 산출물 frontmatter status를 분기 판단하기 *전에* 다음 후처리를 **직렬로** 수행한다 (동시 갱신 lost-update·git 경합 방지):

1. **시각 치환**: 각 산출물의 `started_at` / `finished_at` placeholder를 호출/응답 ISO8601로 치환.
2. **실패 태스크 워킹트리 정리**: `blocked` / `failed` 인스턴스(= `## 커밋 항목` 없음)의 미커밋 변경을 `git checkout -- <touched_files>`로 reset. 다음 단계(커밋·refactor)에 잔존물이 섞이지 않도록 **커밋 전에** 정리한다.
3. **group별 커밋**: 같은 stage에서 `completed`로 끝난 태스크들의 `## 커밋 항목`을 *group ID별로 묶어*, group마다 1커밋을 메인이 직렬 생성한다.
   - `git add -- <그 group 태스크들의 touched_files 전부>` 후 `git commit`.
   - 메시지 — round 1: subject `<type>(<group>): <plan의 group 제목>`, 본문은 각 태스크 summary를 bullet로. type·group 제목은 plan을 source of truth로 한다(섞이면 plan의 group type 우선).
   - retry(round ≥2): 해당 group에서 이번에 재처리된 태스크만 묶어 `fix(<group>): <retry 사유>` **새 커밋**(amend 없음).
   - group의 일부 태스크만 성공했으면 성공분만 묶어 커밋하고, 실패분은 다음 round fix 커밋으로.
   - 각 커밋 후 `git rev-parse HEAD`로 해시를 받아둔다.
4. **tasks.json 일괄 갱신**: 같은 stage 모든 인스턴스의 `## tasks.json 갱신 요청`을 모아, 메인이 *단일 프로세스*로 tasks.json을 Read → status 전이 + 3에서 받은 **group 커밋 해시**(같은 group 태스크는 같은 해시) + 시각을 한 번에 적용 → Write.

후처리 후 frontmatter status로 분기:

- `completed` → 다음 (모든 동시 인스턴스 완료 대기 후 다음 stage 또는 refactor로 진입)
- `blocked` (plan-외 결정 필요 또는 touched_files 위반) → 메인이 사용자에 결정 묻고 plan을 갱신할지 ④로 분기할지 결정
- `failed` → 같은 stage의 다른 인스턴스 완료를 기다린 뒤 즉시 종료

stage 내 일부 태스크가 fail/blocked, 나머지 completed인 경우: 완료된 태스크의 group 커밋은 그대로 유지하고, 실패 태스크만 다음 round에서 재처리한다(그 group에 fix 커밋이 추가됨).

## Step 5 · refactor (@refactorer)

호출 prompt 템플릿:

```
plan 산출물: .claude/task-pipeline/<ts>/03-plan.md
generate 산출물 패턴: .claude/task-pipeline/<ts>/04-generate-*.md  (round 1) / .claude/task-pipeline/<ts>/04-generate-*-R<N>.md  (round ≥2) — 이번 round에 처리된 모든 태스크의 산출물을 ls로 식별 후 모두 Read
산출물 경로: .claude/task-pipeline/<ts>/05-refactor.md  (round ≥2이면 05-refactor-<N>.md)
현재 라운드: <N>
작업 루트: <pwd>
```

refactorer가 *generate 변경 파일 범위 안에서만* 동작 보존 리팩토링. 손볼 게 없으면 `## Result: skipped`로 종료.

리팩토링 적용 시 커밋: `refactor: <summary>` (태스크 ID 없음 — 리팩토링은 태스크 단위가 아님). 의미상 분리해야 할 변경이 둘 이상이면 커밋도 분리.

## Step 6 · evaluate (@evaluator)

호출 prompt 템플릿:

```
clarify 산출물: .claude/task-pipeline/<ts>/01-clarify.md  (## 테스트 범위를 plan과 대조)
plan 산출물: .claude/task-pipeline/<ts>/03-plan.md
tasks.json 경로: .claude/task-pipeline/<ts>/tasks.json
generate 산출물 패턴: .claude/task-pipeline/<ts>/04-generate-*.md  (round 1) / .claude/task-pipeline/<ts>/04-generate-*-R<N>.md  (round ≥2) — 이번 round에 처리된 모든 태스크의 산출물을 ls로 식별 후 모두 Read
refactor 산출물: .claude/task-pipeline/<ts>/05-refactor.md  (round ≥2이면 05-refactor-<N>.md)
산출물 경로: .claude/task-pipeline/<ts>/06-evaluate.md  (round ≥2이면 06-evaluate-<N>.md)
현재 라운드: <N>
Max Rounds: <plan에서 ② confirm된 값>
작업 루트: <pwd>
```

evaluator는 **plan 부합 검증(주축) + verify 명령(보조)** 두 축으로 라운드 리포트를 작성한다. 두 축 모두 PASS여야 최종 PASS(AND 결합). 의도 부합 판단에는 가드 3종(증거 강제·체크리스트 분해·Blind reading)을 강제 적용한다. 형식은 `references/evaluate-report.md`.

종료 후 메인이 본문 `Verdict` + 실패 유형을 읽어 분기한다. **핵심 원칙: 자동 재시도는 객관 신호(구조·verify)에만. 주관 판단(2-D 의도)·이탈은 사람이 결정한다** (스킬 ③의 "자가 평가 retry 루프 금지"를 Step 6에도 일관 적용 — 같은 시스템이 스스로 재시도를 결정하면 같은 실수 반복·라운드 소진).

- `Verdict: PASS` → ③ 결과 검수 게이트
- `Verdict: FAIL` → 본문의 실패 유형에 따라:
  - **구조 누락 / verify FAIL** (객관): 영향 태스크를 tasks.json에서 `failed`로 변경. 추정 불가면 사용자에 자유 질문. round +1 후 **자동으로 generator → refactorer → evaluator 순 재호출**
  - **의도 누락 (2-D, 주관)이 *유일한* FAIL 사유**: 자동 재시도하지 않는다. AskUserQuestion으로 해당 의도 항목을 보여주고 분기 (예외 confirm) — `재시도 / 수용(③로) / 종료`. 재시도 선택 시에만 영향 태스크 `failed` → round +1 재호출
  - 객관 FAIL과 2-D FAIL이 *함께* 있으면: 객관이 재시도를 트리거하므로 자동 재시도하고, 그 round에 2-D는 같이 재검증된다 (별도로 사람에게 묻지 않음)
  - **이탈** (plan에 없는 변경): 이탈 내역을 사용자에 그대로 보여주고 `plan 수정 / generator 재실행 / 허용(plan에 사후 추가)` 자유 질문 → 선택에 따라 분기
  - **테스트 합의 누락** (clarify `작성: O`인데 plan에 테스트 태스크·verify 없음): 자동 재시도하지 않는다(재시도할 태스크가 없는 plan 결함). 사용자에 `plan 수정 / 면제로 수용 / 종료` 자유 질문 → 선택에 따라 분기
  - round가 Max Rounds 초과면 ④ 분기

plan에 verify 명령이 없으면 verify 축은 `N/A`로 두고 plan 부합 축만으로 Verdict 결정.

frontmatter `status: failed` (verify 명령 자체 실행 불가)면 retry 없이 사용자 알림 + 종료.

## 종료 직전 · tutor (@tutor) — 선택 호출

`current_step`이 종료 상태(`done` / `cancelled` / `failed` / `handoff`) 중 하나로 결정되면, archive 직전에 메인이 한 번 tutor 호출을 제안한다.

> `AskUserQuestion` — header=`설명 듣기`, options=[`네, 설명 들을게요`, `아니요, 종료`]

Yes 선택 시 메인이 @tutor를 호출. 호출 prompt 템플릿:

```
사이클 디렉토리: .claude/task-pipeline/<ts>/
종료 경로: done | failed | handoff | cancelled
작업 루트: <pwd>
```

tutor는 디렉토리 안의 산출물 중 필요한 것만 골라 Read하고, `git log` / `git diff`로 실제 커밋을 확인해 **핵심 코드 스니펫을 인용하면서** 일타강사 톤으로 풀어 설명한다 (채팅 메시지만, 디스크 산출물 없음). tutor 응답은 Agent 도구 특성상 tool_result로만 들어오므로, 메인은 받은 본문을 그대로 사용자에게 출력해야 화면에 표시된다.

설명 후 사용자가 추가 질문하면 자연스럽게 Q&A 흐름으로 이어지고, 다른 주제로 이동하면 자연 종료된다 (별도 종료 키워드 없음). Q&A가 끝나면 메인이 archive 진행. No 선택 시 곧장 archive.

## 종료 처리

archive 처리 (tutor 호출 여부와 무관):

- `done` (③ 검수 OK): `mv .claude/task-pipeline/$TS .claude/task-pipeline/archived/` + 메인이 "현재 브랜치: <branch>. PR/머지는 별도로 진행하세요" 안내
- `cancelled` / `failed` / `handoff`: 동일하게 archived/로 이동, 브랜치는 그대로 둠

push와 PR 생성은 자동화하지 않는다.

## ④ 분기 처리 상세

Max Rounds 모두 FAIL이면 AskUserQuestion으로 4지선다:

| 선택 | 메인의 행동 |
|---|---|
| 재시도 (라운드 리셋) | progress.json `current_round=1`, evaluate.rounds 비우기, **tasks.json 모든 태스크 status를 `pending`으로 리셋 (commit 필드는 유지 — 과거 커밋은 git history에 남음)**, generate부터 다시 |
| plan 수정 | `current_step=plan`, planner 재호출 (사용자에게 어떤 부분 수정할지 자유 질문 후 prompt에 주입) |
| 중단 | `current_step=cancelled`, archived/로 이동 |
| handoff 문서 | @handoff-creator 호출(있으면) 또는 메인이 직접 `.claude/task-pipeline/<ts>/handoff.md` 작성, `current_step=handoff` |

## 호출 시점 운영

- 단계 도중 sub-agent가 `status: failed` → 메인이 사용자 알림 + 즉시 종료 (`current_step=failed`)
- 사용자 *"취소 / 멈춰 / 그만"* 등 명시 발화 → `current_step=cancelled` + 종료
- sub-agent가 `status: blocked` → 메인이 본문의 Blocker 섹션을 사용자에 그대로 보여주고 재시도/중단 자유 질문
