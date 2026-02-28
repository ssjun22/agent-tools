# 멀티 에이전트 오케스트레이션

## 패턴 선택 가이드

```
작업들이 서로 의존하는가?
├── 예 → SequentialAgent (A 결과가 B의 입력)
└── 아니오 → 작업들이 독립적인가?
    ├── 예 → ParallelAgent (동시 실행으로 속도 향상)
    └── 결과에 따라 반복이 필요한가?
        └── 예 → LoopAgent (조건 충족까지 반복)
```

---

## 패턴 1: Sequential (파이프라인)

단계별로 처리해야 하는 데이터 파이프라인에 적합.

```python
from google.adk.agents import LlmAgent, SequentialAgent

fetch_agent = LlmAgent(
    name="fetch_agent",
    model="gemini-2.5-flash",
    instruction="주어진 URL에서 데이터를 수집하라.",
    output_key="raw_data",
)

analyze_agent = LlmAgent(
    name="analyze_agent",
    model="gemini-2.5-flash",
    instruction="세션 state의 raw_data를 분석하고 핵심 인사이트를 추출하라.",
    output_key="analysis_result",
)

pipeline = SequentialAgent(
    name="data_pipeline",
    sub_agents=[fetch_agent, analyze_agent],
)
```

> Skeleton 코드: `assets/sequential_pipeline.py`

### 에이전트 간 데이터 전달

`output_key`로 저장한 값은 세션 `state`를 통해 다음 에이전트에서 참조된다:

```python
# instruction에서 state 참조 방법
instruction = """
이전 단계에서 수집된 데이터를 분석하라.
데이터: {raw_data}
"""
```

---

## 패턴 2: Parallel (병렬 처리)

독립적인 여러 소스에서 동시에 데이터를 수집할 때 적합.

```python
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent

worker_a = LlmAgent(
    name="worker_a",
    model="gemini-2.5-flash",
    instruction="소스 A에서 정보를 수집하라.",
    output_key="result_a",
)

worker_b = LlmAgent(
    name="worker_b",
    model="gemini-2.5-flash",
    instruction="소스 B에서 정보를 수집하라.",
    output_key="result_b",
)

synthesize_agent = LlmAgent(
    name="synthesize_agent",
    model="gemini-2.5-flash",
    instruction="result_a와 result_b를 종합하여 최종 답변을 작성하라.",
    output_key="final_result",
)

# 병렬 수집 후 종합 순서 보장
root_agent = SequentialAgent(
    name="parallel_then_synthesize",
    sub_agents=[
        ParallelAgent(name="gather", sub_agents=[worker_a, worker_b]),
        synthesize_agent,
    ],
)
```

> Skeleton 코드: `assets/parallel_pipeline.py`

---

## 패턴 3: Loop (반복 처리)

검증 실패 시 재시도하거나, 조건 충족까지 반복할 때 적합.

```python
from google.adk.agents import LlmAgent, LoopAgent

attempt_agent = LlmAgent(
    name="attempt_agent",
    model="gemini-2.5-flash",
    instruction="""
    작업을 수행하고 결과를 검증하라.
    성공하면 'escalate'를 출력하여 루프를 종료하라.
    실패하면 원인을 분석하고 다시 시도하라.
    """,
    output_key="attempt_result",
)

loop = LoopAgent(
    name="retry_loop",
    sub_agents=[attempt_agent],
    max_iterations=3,
)
```

---

## 주의사항

- `output_key`는 파이프라인 내에서 **고유한 이름**을 사용하라 (덮어쓰기 방지)
- ParallelAgent의 하위 에이전트들은 **서로 독립적**이어야 한다 (상호 의존 금지)
- LoopAgent는 반드시 `max_iterations`를 설정하여 무한 루프를 방지하라
