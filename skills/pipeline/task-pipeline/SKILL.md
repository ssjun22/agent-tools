---
name: task-pipeline
description: "요구가 정해진 코드 변경 작업을 위한 하네스 — 수렴(clarify⇄explore) → 기준 설계 → plan → ① 착수 게이트(동결) → 변경⇄검증 루프 → refactor(선택) → ③ 검수 → 기록. 기록은 repo 밖 중앙 저장소에, 판정은 core.sh 래퍼가 소유. /task-pipeline <설명>으로 호출. 탐색·측정·variant 공존 작업(A/B·spike·벤치마크)에는 부적합."
argument-hint: "[작업 설명 (자유 텍스트, 빈 인자 허용)]"
disable-model-invocation: true
---

# task-pipeline — 코드 변경 하네스

> 메인 세션은 **지휘자**다: 사용자 창구(수렴 대화·게이트·blocked 알림)이며 코드를 만들지 않는다. 단계 방법론은 `references/`, 데이터 규약은 `references/state-files.md`, 결정론 작업은 `scripts/core.sh`가 원천 — 여기 재서술하지 않는다.

## 발동
`/task-pipeline <설명>` → 메인이 `bash .claude/skills/task-pipeline/scripts/core.sh new "<요약>"`으로 사이클을 연다(중앙 저장소에 `<cycle_dir>` 반환). 이후 모든 커맨드에 이 경로를 넘긴다. `status`의 `HANDOFF`(미소진 이월)를 확인해 관련 항목을 수렴에서 제시(채택 시 `handoff consume --by`). 수렴부터 시작.

## 개요
환원 불가능한 골격은 **기준 → [변경⇄검증] → 기록**. 나머지 단계는 과제의 불확실성이 정당화하는 만큼만 존재한다. 사람 판정 지점은 **① 착수**(방향 승인 + 통째로 동결)와 **③ 검수**(의도 부합) 둘 뿐(②는 없음). 전체 절차는 `references/stages.md`.

## 라우팅
| 단계 | 실행 | 커맨드 / 산출 |
|---|---|---|
| 수렴 clarify⇄explore | 메인(clarify 라이브) · @explorer(스캔 보조) | `core.sh interview-log <dir> …`(transcript) · `score <dir> [--greenfield]` · `guard <dir>` → 종료 시 `brief.md` 1회 생성 + `brief-check <dir>`(전사 대조) |
| 기준 설계 + plan | @planner | `plan.md`(`json steps`) |
| ① 착수 게이트 | 메인 + 사용자 | `clarify-status <dir>`(뷰 고지 재료) → `core.sh step lock <dir> --verify … --max … [--check …]` (동결 + 브랜치 생성 + clarify 스냅샷) |
| 루프 (걸음별) | @generator ×1/걸음 | `core.sh verify <dir> --step S-n` · `core.sh commit <dir> S-n` |
| 웨이브 경계 | 메인 | `core.sh verify <dir>` (최종, FAIL 시 라운드 소모, 상한 시 `LIMIT`) |
| refactor (선택) | @refactorer | `core.sh commit <dir> --refactor -m … -- …` |
| ③ 검수 게이트 | 메인 + 사용자 | 최종 점검 절차(`gate-views.md`): 요약 → 체크리스트 문답(증거 첨부) → 이월 → `core.sh report <dir>` 전문 출력 → 종합 판정 · 이월분 `handoff add` |
| 기록·종료 | 메인 | `core.sh close <dir> <done\|handoff\|cancelled\|failed>` (done은 PASS 필수) |

- 사람 접점 발화(수렴 확인·게이트·blocked·handoff)는 `references/gate-views.md` 규격 — 메인이 뷰를 즉석 생성(화면 라벨·스켈레톤 준수), `AskUserQuestion` 다지선다.
- `blocked`(작업자 선언)·`LIMIT`(래퍼 자동) = 게이트 아닌 예외 경로 → 사람 호출.
- 위임 판별식: 입력이 경로 · 출력이 파일·커밋·토큰 · 중간에 사용자 불필요 — 셋 다 예면 위임.
- 서브에이전트 응답도 Bash stdout도 tool_result라 화면에 안 보인다 — 사용자에게 보일 본문(게이트 대상, 특히 `report` 뷰 전문 포함)은 메인이 응답에 그대로 옮겨 출력한 뒤 진행.
- resume: `core.sh status`로 활성 사이클(final==null)을 찾아 state.json + journal 읽고 재개. `HANDOFF`(미소진 이월)도 함께 확인.

## 금지
- **동결 수정** — ① 이후 brief·plan을 고치지 않는다. 전제 오류는 journal 기록 + blocked.
- **재확인 없는 진행** — 사람 확인은 제시한 판본에 귀속. 확인 후 brief·plan이 바뀌면 변경점 재제시 + 재판정이 먼저다. 수정 지시를 승인으로 치환 금지.
- **자가 판정** — 판정은 `core.sh verify`(기계)와 게이트(사람). 자가 평가 retry 루프 금지.
- **raw git / 수기 상태 편집** — git 쓰기·state.json 변이는 `core.sh` 경유가 유일.
- **요약 인계** — 컨텍스트는 항상 경로로 넘긴다.

## 참조
`references/`: `stages.md`(단계 절차·crew·병렬) · `clarify-method.md` · `plan-rules.md` · `state-files.md`(데이터 규약) · `gate-views.md`(사람 접점 발화 규격) · `terms.md`(용어). 템플릿: `templates/{brief,plan}.md`. 채점·guard·대조 프롬프트: `scripts/prompts/`(rubric·guard 3종·brief-check — core.sh 전용, 메인이 읽지 않는다).
