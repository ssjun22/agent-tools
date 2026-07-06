# task-pipeline evaluate — 정형 리포트 + retry 흐름

evaluate는 plan을 기준으로 산출물이 그대로 만들어졌는지 검증하는 객관 reviewer다. 두 축으로 평가하고 **AND 결합** — 둘 다 PASS여야 최종 PASS.

| 축 | 역할 | 비중 |
|---|---|---|
| **A. plan 부합 검증** | plan에 명시된 것이 실제 산출물에 그대로 반영됐는지 | 주축 |
| **B. verify 명령** | plan이 정의한 자동 검증 스크립트 실행 (exit code) | 보조 |

plan에 verify 명령이 없으면 verify 축은 `N/A`로 두고 plan 부합 축만으로 Verdict 결정.

## A. plan 부합 검증

### A-1. 구조 사실 비교 (객관)

| 항목 | 비교 대상 |
|---|---|
| 태스크 완료 | `tasks.json`의 모든 태스크 `done` 여부 |
| 변경 파일 범위 | (plan 명시 파일 + refactor `## 변경 파일`) 합집합 vs 실제 git diff — 아래 이탈 판정 |
| 계약 일치 | plan에 명시된 인터페이스/시그니처/스키마/의존성 |
| TDD 증거 | 각 코드 태스크의 generate 산출물에 `## TDD 증거`(RED·GREEN 실행 기록 또는 명시된 면제) 존재 |

**변경 파일 범위 이탈 판정**: 비교 기준은 *plan 명시 파일 + refactor 산출물 `## 변경 파일`의 합집합*이다. refactor가 만든 새 파일은 `(new — 원천)`, 범위 밖 파일은 `(파급 — 원인)` 표기가 있어야 허용 범위로 인정한다. 표기 없는 plan-외 변경(새 의존성 추가 등)은 기본 **이탈 FAIL** — 메인의 retry 분기에서 사용자에 처리 방향을 묻는다. (근거: refactor는 plan touched_files 밖(공통 모듈·파급)을 정당하게 만들 수 있는 유일한 단계 — 이 합산 계약 없이는 정당한 추출이 라운드마다 이탈 FAIL을 생산한다.)

### A-2. 의도 부합 LLM 판단 (가드 3종 강제)

plan `## 통과 기준` 동작 계층의 원문 항목(*"재시도 시 idempotency 보장"*, *"에러 로그에 trace_id 포함"* 등 — 구체화·"사람 확인 필요" 표기는 판단 보조)이 코드에 반영됐는지 판단한다. 가드 없이 자유 판단하면 셀프 평가 함정(표면 매칭·모호함 후하게 해석·confirmation bias)에 빠지므로 다음 3단계를 **모두** 거친다.

**1단계 — Blind reading**
plan을 열기 전, 코드와 git diff부터 보고 *"이 코드가 무엇을 하는가"*를 항목별로 요약한다. plan을 먼저 읽으면 키워드에 끌려가 confirmation bias가 발생한다.

**2단계 — 체크리스트 분해**
plan `## 통과 기준` 동작 계층의 원문 항목을 *검증 가능한 N개 항목*으로 분해한다. **'사람 확인 필요' 표기 항목**은 판정 N/A — '사람 검수 대기'로 집계, Verdict 불산입(③ 인계). **표기 없이** 검증 불가로 드러난 항목(*"UX가 부드럽게 동작"* 등)은 원문 인용 + **검증 불가 → FAIL**(엄격 원칙).

**3단계 — 항목별 매핑 + 증거 강제**
각 항목마다 다음 형식으로 적는다. *"충족됨"* 단답 금지.

```
항목 ①: <plan에서 인용한 요구사항>
- 코드 위치: file.ts:42-50
- 매핑 근거: <어떤 동작이 어떻게 충족하는지>
- 판정: PASS | FAIL
```

**모호함 처리**: 판정 근거가 불충분하면 FAIL로 기울인다. *"적절히 처리됨"*, *"맥락상 충족"* 같은 얼버무림은 자동 FAIL.

## B. verify 명령

plan의 verify 스크립트를 그대로 실행하고 exit code로 PASS/FAIL. 명령별 출력 요약(주요 에러만)을 리포트에 첨부.

plan에 verify가 없거나 *"verify 불가"*로 명시되어 있으면 `N/A`. AND 결합에서 verify 축은 평가에서 제외하고 plan 부합 축만으로 Verdict 결정.

## 라운드 리포트 형식

각 라운드 종료시 다음 마크다운을 그대로 출력하고 컨텍스트에 누적한다.

```markdown
## Round N
- plan 부합 검증: PASS | FAIL
- verify 명령: PASS | FAIL | N/A
- 최종 Verdict: PASS | FAIL
- 종료 조건: PASS / 다음 라운드로 / 핸들오버

### A. plan 부합 검증

#### A-1. 구조 사실 비교
- 태스크 완료: ✓ T1, T2, T3 모두 done
- 변경 파일 범위: ✗ plan에 없는 file C.ts 수정 (이탈)
- 계약 일치: ✓ API 시그니처 plan과 동일

#### A-2. 의도 부합 판단

**1단계 — 코드 요약 (Blind, plan 미참조)**
- A.ts: 사용자 입력 유효성 검사 후 ...
- B.ts: ...

**2단계 — plan 요구사항 분해**
- 항목 ①: "재시도 시 idempotency 보장"
- 항목 ②: "에러 로그에 trace_id 포함"
- 항목 ③: "UX가 부드럽게 동작" — '사람 확인 필요' 표기 有 → N/A(검수 대기) / 표기 無 → 검증 불가 FAIL

**3단계 — 항목별 매핑**
- 항목 ① — A.ts:34-48에서 idempotency_key 기반 dedup. 근거: ... — **PASS**
- 항목 ② — B.ts:120 로그 호출에 trace_id 미포함 — **FAIL**
- 항목 ③ — (표기 無 가정) 검증 불가 → **FAIL**

#### 사람 검수 대기 (Verdict 불산입)
- plan이 '사람 확인 필요'로 표기한 항목만 집계. 예: "로딩이 자연스럽게 보임" — Verdict 불산입, ③ 검수에서 사람이 확인

### B. verify 명령
- `pnpm test` — PASS
- `pnpm typecheck` — PASS

### 다음 라운드 지시 (FAIL인 경우만)
- 실패 유형: 구조 누락 / verify / 의도 누락 / 이탈
- 구조 누락: 항목 ② (영향 태스크 T2)
- verify: `pnpm test` FAIL (영향 태스크 T2)
- 의도 누락: "재시도 시 idempotency 보장" 미충족 — 메인이 사용자에 재시도 여부 질문
- 이탈: file C.ts 수정 — 메인이 사용자에 처리 방향 질문
- tasks.json 상태 변경: T2 → failed (구조 누락·단서 명확한 verify만. 의도 누락·이탈은 사람 확인 후 결정)
```

## FAIL 유형과 메인의 분기

핵심 구분은 **객관 신호 vs 주관 판단**이다. 객관 FAIL(구조·verify)은 외부 사실이라 자동 재시도해도 수렴하지만, 주관 FAIL(의도 부합)을 자동 루프로 돌리면 같은 시스템이 *스스로* 재시도를 결정하게 되어 같은 실수 반복·라운드 소진(스킬 ③의 "자가 평가 retry 루프 금지" 원칙). 그래서 **자동 재시도는 객관 신호에만, 주관 FAIL은 사람이 결정**한다.

| 유형 | 정의 | 메인의 행동 |
|---|---|---|
| **구조 누락** (객관) | 태스크 미완료·TDD 증거 부재 / plan에 명시된 파일 부재 / 시그니처·스키마 불일치 | 영향 태스크 `failed` 표시 → **자동** generator 재실행 |
| **verify** (객관) | verify 명령 exit code 실패 | 영향 태스크 명시돼 있으면 `failed` → **자동** 재실행. 추정 불가면 사용자 질문 |
| **의도 누락** (주관) | 의도 부합 LLM 판단 항목 FAIL | 자동 재시도하지 않음 — 항목을 사용자에 보여주고 `재시도 / 수용(③로) / 종료` 질문 후 분기. 사용자가 재시도를 택하면 영향 태스크 `failed` → 재실행 |
| **이탈** | plan에 없는 변경이 산출물에 있음 | 이탈 내역을 사용자에 보여주고 `plan 수정 / 재실행 / 허용` 질문 후 분기 |

여러 유형이 동시에 발생하면 리포트에 모두 기록한다. **객관 FAIL이 하나라도 있으면 그게 재시도를 트리거하고**(자동 재실행), 그 라운드에 의도 누락은 같이 재검증된다. 의도 누락이 *유일한* FAIL 사유일 때만 사람에게 묻는다.

### 영향 태스크 식별 불확실할 때

verify FAIL 또는 의도 부합 FAIL이 어느 태스크 탓인지 명확한 단서가 없으면 추측하지 않는다. 추측으로 잘못 표시하면 retry가 멀쩡한 부분을 회귀시키거나 같은 실패를 반복한다.

- 사용자에 묻기 — *"검증 출력만으로는 영향 태스크를 특정하기 어렵습니다. 어느 태스크가 원인일 것 같으신가요?"*
- 모든 태스크를 `failed`로 보수적 처리 (generate 전체 재실행 — 안전하지만 비효율)

## 케이스 예시

### Case A. Round 2에 PASS (객관 FAIL → 자동 재시도)

Round 1에서 `pnpm test` FAIL(또는 구조 누락) → 객관 신호이므로 영향 태스크 T2 `failed` → generator가 T2만 자동 재처리 → Round 2:

```markdown
## Round 2
- plan 부합 검증: PASS
- verify 명령: PASS
- 최종 Verdict: PASS
- 종료 조건: PASS
```

→ ③ 진입.

### Case B. Max Rounds 도달 → 핸들오버 분기

3 라운드(또는 plan에서 정한 N) 모두 FAIL. 누적 리포트 + 최종 tasks.json + 분기 옵션 제시:

```
evaluate가 3 라운드 모두 FAIL했습니다.
- Round 1: ...
- Round 2: ...
- Round 3: ...

tasks.json 최종: T1=done, T2=failed, T3=done

어떻게 진행할까요?
1. 재시도 (라운드 카운트 리셋, generate부터)
2. plan 수정 (plan.md 재작성, ② confirm 다시)
3. 중단 (cancelled로 종료)
4. handoff 문서 만들기 (.claude/task-pipeline/<ts>/handoff.md 작성)
```

사용자 선택 → progress.json `current_step` 갱신:
- 1 → `current_step = "generate"`, evaluate.rounds 비우기
- 2 → `current_step = "plan"`
- 3 → `current_step = "cancelled"`
- 4 → handoff-creator 호출 후 `current_step = "handoff"`

### Case C. verify 명령 없는 작업 (문서·리팩토링 등)

plan에 verify가 없거나 *"verify 불가"*로 명시된 경우 verify 축은 N/A로 빠지고 plan 부합 축만으로 Verdict 결정.

```markdown
## Round 1
- plan 부합 검증: PASS
- verify 명령: N/A
- 최종 Verdict: PASS
- 종료 조건: PASS
```

plan 부합이 FAIL이면 동일하게 retry 분기(누락/이탈)로 진입한다.

## 시스템 에러 처리

테스트가 실행되지 않거나(node_modules 깨짐 등) 프레임워크 자체가 동작하지 않는 경우는 retry 라운드를 소진하지 않고 즉시 사용자에게 알린다. 환경 문제는 같은 작업을 반복해도 해결되지 않는다.

> 시스템 에러가 발생해 evaluate를 진행할 수 없습니다. 원인: [...]. 어떻게 진행할까요?

`current_step = "failed"`로 종료.
