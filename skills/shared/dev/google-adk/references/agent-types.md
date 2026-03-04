# Google ADK 에이전트 타입

## 개요

ADK는 네 가지 기본 에이전트 타입을 제공한다. 각 타입은 특정 오케스트레이션 패턴에 최적화되어 있다.

---

## LlmAgent

LLM을 기반으로 자율적으로 판단하고 툴을 호출하는 범용 에이전트.

```python
from google.adk.agents import LlmAgent
from google.adk.tools import google_search

agent = LlmAgent(
    name="research_agent",
    model="gemini-2.5-flash",
    instruction="사용자의 질문에 대해 검색을 수행하고 정확한 답변을 제공하라.",
    tools=[google_search],
    output_key="research_result",
)
```

> Skeleton 코드: `assets/single_agent.py`

### 주요 파라미터

| 파라미터 | 설명 |
|---------|------|
| `name` | 에이전트 식별자 (멀티 에이전트 시 고유해야 함) |
| `model` | 사용할 Gemini 모델 ID |
| `description` | 에이전트의 목적을 간결하게 설명. 멀티 에이전트에서 라우터가 위임 결정 시 참조 |
| `instruction` | 에이전트의 상세한 행동 지침. 작업 방식, 제약, 출력 형식 등을 정의 |
| `tools` | 에이전트가 호출할 수 있는 툴 목록 |
| `output_key` | 최종 응답을 세션 state에 저장할 키 이름 |
| `output_schema` | 응답을 강제할 Pydantic 모델 (tools와 함께 사용 불가) |
| `planner` | Thinking mode 등 추론 방식 제어 (`BuiltInPlanner` 사용) |
| `sub_agents` | 하위 에이전트 목록 (에이전트가 다른 에이전트를 호출할 때) |

### description vs instruction

```python
agent = LlmAgent(
    name="search_agent",
    # description: 멀티 에이전트 라우팅 시 다른 에이전트가 참조하는 한 줄 요약
    description="웹 검색을 수행하고 관련 정보를 반환하는 에이전트",
    # instruction: 에이전트가 실제로 따르는 상세 행동 지침
    instruction="""
    사용자의 질문에 대해 웹 검색을 수행하라.
    검색 결과를 요약하여 핵심 정보만 추출하라.
    출처 URL을 반드시 포함하라.
    """,
)
```

### 프롬프트 파일 분리 패턴

instruction이 길어질 경우 역할별로 파일로 분리하여 관리할 수 있다.

```
agents/my_agent/
├── agent.py
└── prompt_parts/
    ├── 1_role.md           # 에이전트 역할 정의
    ├── 2_io.md             # 입출력 형식
    ├── 3_requirements.md   # 검사/판단 기준 목록 (검사 항목이 많을 때 constraints와 분리)
    ├── 4_constraints.md    # 판단 행동 제약 (근거 없이 오류 판정 금지 등)
    └── 5_examples.md       # Few-shot 예시
```

검사 항목이 단순하거나 적은 경우 `3_requirements.md`를 생략하고 `3_constraints.md`에 통합할 수 있다.

```python
# agent.py
from pathlib import Path

def _load_prompt(filename: str) -> str:
    path = Path(__file__).parent / "prompt_parts" / filename
    return path.read_text(encoding="utf-8")

def get_instruction() -> str:
    parts = ["1_role.md", "2_io.md", "3_requirements.md", "4_constraints.md", "5_examples.md"]
    return "\n\n".join(_load_prompt(p) for p in parts)

agent = LlmAgent(
    name="my_agent",
    model="gemini-2.5-flash",
    instruction=get_instruction(),
)
```

> **참고**: 파일 분리는 ADK 공식 권장 패턴은 아니지만, instruction이 복잡할 때 유지보수성을 높여준다.

---

## SequentialAgent

하위 에이전트(또는 툴)를 **순서대로** 실행하는 파이프라인 에이전트.

```python
from google.adk.agents import SequentialAgent

pipeline = SequentialAgent(
    name="data_pipeline",
    sub_agents=[fetch_agent, process_agent, summarize_agent],
)
```

> Skeleton 코드: `assets/sequential_pipeline.py`

- 각 에이전트의 `output_key`로 저장된 결과가 다음 에이전트의 입력으로 전달됨
- 중간 에이전트가 실패하면 파이프라인 전체가 중단됨

---

## ParallelAgent

하위 에이전트들을 **동시에** 실행하고 모든 결과를 수집하는 에이전트.

```python
from google.adk.agents import ParallelAgent

parallel = ParallelAgent(
    name="multi_search",
    sub_agents=[news_agent, wiki_agent, web_agent],
)
```

> Skeleton 코드: `assets/parallel_pipeline.py`

- 독립적인 작업을 병렬로 처리할 때 사용
- 모든 하위 에이전트가 완료된 후 다음 단계로 진행

---

## LoopAgent

조건이 충족될 때까지 하위 에이전트를 **반복** 실행하는 에이전트.

```python
from google.adk.agents import LoopAgent

loop = LoopAgent(
    name="retry_loop",
    sub_agents=[attempt_agent],
    max_iterations=5,
)
```

- `max_iterations`로 최대 반복 횟수 제한
- 하위 에이전트가 `escalate=True`를 반환하면 루프 종료
