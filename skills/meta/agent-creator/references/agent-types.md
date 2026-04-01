# 에이전트 워크플로우 패턴 가이드

Anthropic의 [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) 분류를 기반으로, Claude Code 서브 에이전트가 내부적으로 따르는 워크플로우 패턴을 정의한다. 패턴에 따라 프롬프트 구조와 강조 요소가 달라진다.

## 핵심 원칙

> "성공은 가장 정교한 시스템을 만드는 것이 아니라, 필요에 맞는 적절한 시스템을 만드는 것이다."

단순한 패턴부터 시작하고, 복잡성은 결과가 개선될 때만 추가한다.

## 패턴 판별

brainstorming 결과를 기반으로 다음 질문을 순서대로 적용한다:

```
1. 작업 절차가 고정된 순서로 진행되는가?
   → Yes: Prompt Chaining
   → No: 2번으로

2. 입력 유형에 따라 처리 방식이 달라지는가?
   → Yes: Routing
   → No: 3번으로

3. 독립적인 하위 작업으로 분해 가능한가?
   → Yes: 하위 작업을 다른 에이전트에게 위임하는가?
     → Yes: Orchestrator-Workers
     → No: Parallelization
   → No: 4번으로

4. 산출물을 생성한 뒤 자체 평가/개선 루프가 필요한가?
   → Yes: Evaluator-Optimizer
   → No: 5번으로

5. 도구를 사용하며 자율적으로 목표를 달성하는가?
   → Yes: Autonomous Agent
   → No: 가장 단순한 패턴(Prompt Chaining)으로 시작
```

복합 패턴도 가능하다 — 예: Orchestrator가 내부적으로 Prompt Chaining을 따르는 worker를 호출.

## 패턴별 상세

### 1. Prompt Chaining (순차 실행)

**동작**: 작업을 고정된 순서의 단계로 분해, 각 단계 사이에 검증 게이트를 둔다.

**적합한 경우**: 절차가 예측 가능하고, 각 단계의 출력이 다음 단계의 입력이 되는 작업.

| 프롬프트 섹션 | 강조 요소 |
|--------------|-----------|
| Instructions | 단계별 절차를 명확한 순서로 정의. 각 단계의 입력/출력 명시. 단계 간 검증 조건(게이트) 포함 |
| Constraints | 단계 건너뛰기 금지. 게이트 실패 시 멈춤 규칙 |
| Output Format | 단계별 중간 산출물 + 최종 산출물 구조 |

**권장 tools**: 작업 도메인에 따라 결정 (패턴 자체는 도구에 무관)
**권장 model**: `sonnet` (개별 단계가 단순), `opus` (단계 내 판단이 복잡)

**추천 building-blocks:**
- 과잉 탐색 방지 (단계별로 집중)

---

### 2. Routing (입력 분류 → 분기 처리)

**동작**: 입력을 분류하고, 카테고리별로 다른 처리 로직을 적용한다.

**적합한 경우**: 입력 유형이 다양하고, 유형별로 최적 처리 방식이 다른 작업.

| 프롬프트 섹션 | 강조 요소 |
|--------------|-----------|
| Instructions | 분류 기준(카테고리 정의), 카테고리별 처리 로직, 애매한 입력의 분류 규칙 |
| Constraints | 미분류 입력 처리 방법 (기본 카테고리 또는 에러) |
| Output Format | 분류 결과 + 해당 카테고리의 처리 결과 |

**권장 tools**: Read, Glob, Grep (분류 판단을 위한 정보 수집)
**권장 model**: `sonnet` (분류 + 처리), `haiku` (단순 분류만)

**추천 building-blocks:**
- `investigate_before_answering` — 분류 전 충분한 정보 확인

---

### 3. Parallelization (병렬 실행)

**동작**: 독립적인 하위 작업을 병렬로 실행하고 결과를 종합한다. 두 가지 변형이 있다:
- **Sectioning**: 작업을 독립 하위 작업으로 분해하여 병렬 실행
- **Voting**: 같은 작업을 여러 관점으로 반복 실행하여 신뢰도 확보

**적합한 경우**: 하위 작업 간 의존성이 없고, 속도 또는 다양한 관점이 중요한 작업.

| 프롬프트 섹션 | 강조 요소 |
|--------------|-----------|
| Instructions | 독립 분석 차원 정의. 각 차원의 평가 기준. 결과 종합 방법 |
| Constraints | 차원 간 중복 판단 방지. 종합 시 충돌 해결 규칙 |
| Output Format | 차원별 결과 + 종합 결론 |

**권장 tools**: Read, Glob, Grep (병렬 분석)
**권장 model**: `sonnet` (각 병렬 작업이 적당한 복잡도)

**추천 building-blocks:**
- `use_parallel_tool_calls` — 병렬 도구 호출 극대화

---

### 4. Orchestrator-Workers (동적 위임)

**동작**: 중앙 에이전트가 작업을 동적으로 분해하고, worker 에이전트에게 위임한 뒤, 결과를 종합한다. Parallelization과 달리 하위 작업이 사전에 정해지지 않는다.

**적합한 경우**: 하위 작업을 미리 예측할 수 없는 복잡한 작업. 여러 파일/모듈에 걸친 변경.

| 프롬프트 섹션 | 강조 요소 |
|--------------|-----------|
| Instructions | 작업 분해 기준. worker 에이전트 호출 방법. 결과 종합 및 충돌 해결 방법. 에러/실패 처리 |
| Constraints | orchestrator가 직접 구현하지 않음. 위임 범위 제한 |
| Output Format | 종합 보고서 또는 통합된 결과물 |

**권장 tools**: Agent, Read, Bash
**권장 model**: `opus` (복잡한 분해 판단), `sonnet` (단순 조율)

**추천 building-blocks:**
- `use_parallel_tool_calls` — worker 병렬 실행
- 과잉 탐색 방지 (분해 후 위임, 직접 수행 않음)

---

### 5. Evaluator-Optimizer (생성 + 평가 루프)

**동작**: 산출물을 생성하고, 평가 기준에 따라 자체 평가한 뒤, 기준 미달이면 개선을 반복한다.

**적합한 경우**: 명확한 평가 기준이 있고, 반복을 통해 품질이 실질적으로 향상되는 작업.

| 프롬프트 섹션 | 강조 요소 |
|--------------|-----------|
| Instructions | 생성 기준 + 평가 기준을 분리하여 정의. 반복 조건 (언제 개선하고, 언제 멈추는가). 최대 반복 횟수 |
| Constraints | 무한 루프 방지 (최대 반복 제한). 과잉 최적화 방지 |
| Output Format | 최종 산출물 + 평가 결과 (통과/미달 여부) |

**권장 tools**: 도메인에 따라 결정 (생성: Write/Edit, 평가: Read/Bash)
**권장 model**: `opus` (평가 품질이 중요), `sonnet` (생성이 단순)

**추천 building-blocks:**
- `default_to_action` — 생성 단계에서 구현 우선
- `investigate_before_answering` — 평가 단계에서 확인 후 판단

---

### 6. Autonomous Agent (자율 실행)

**동작**: 도구를 사용하며 환경 피드백에 따라 자율적으로 목표를 달성한다. 고정된 절차 없이 상황에 맞게 다음 행동을 결정한다.

**적합한 경우**: 실행 경로를 미리 예측할 수 없는 열린 문제. 도구 기반 탐색과 실행이 필요한 작업.

| 프롬프트 섹션 | 강조 요소 |
|--------------|-----------|
| Instructions | 목표 정의 (절차가 아닌 목표). 사용 가능한 도구와 각 도구의 용도. 의사결정 기준. 사용자 확인이 필요한 체크포인트 |
| Constraints | 정지 조건 (목표 달성 / 최대 시도 / 교착 상태). 위험한 행동 전 확인 규칙 |
| Output Format | 실행 결과 요약 + 수행한 작업 목록 |

**권장 tools**: Read, Edit, Write, Glob, Grep, Bash (폭넓은 도구 접근)
**권장 model**: `opus` (복잡한 판단), `sonnet` (일반적 자율 작업)

**추천 building-blocks:**
- `default_to_action` — 능동적 실행
- `investigate_before_answering` — 추측 방지
- `use_parallel_tool_calls` — 효율적 도구 사용
- 과잉 엔지니어링 방지

## 패턴 선택 요약

| 패턴 | 핵심 질문 | 복잡도 |
|------|-----------|--------|
| Prompt Chaining | 절차가 고정되어 있는가? | 낮음 |
| Routing | 입력 유형별 처리가 다른가? | 낮음 |
| Parallelization | 독립 하위 작업으로 분해 가능한가? | 중간 |
| Orchestrator-Workers | 하위 작업을 동적으로 위임하는가? | 높음 |
| Evaluator-Optimizer | 생성 후 자체 평가 루프가 필요한가? | 중간 |
| Autonomous Agent | 열린 문제를 자율적으로 해결하는가? | 높음 |

단순한 패턴으로 충분하면 복잡한 패턴을 사용하지 않는다.
