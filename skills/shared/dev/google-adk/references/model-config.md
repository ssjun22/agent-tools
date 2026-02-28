# 모델 설정 (Model Configuration)

## 개요

ADK에서 LLM 동작을 제어하는 파라미터들을 `GenerateContentConfig`로 묶어 에이전트에 전달한다.
Thinking 제어는 `generate_content_config`가 아닌 `planner` 파라미터를 통해 설정한다.

---

## 기본 설정

```python
from google.adk.agents import LlmAgent
from google.genai import types

agent = LlmAgent(
    name="my_agent",
    model="gemini-2.5-flash",
    instruction="...",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.7,
        max_output_tokens=2048,
        top_p=0.9,
    ),
)
```

---

## 주요 파라미터

### temperature

창의성과 무작위성을 제어한다.

| 값 | 특성 | 적합한 상황 |
|----|------|------------|
| `0.0` | 결정론적, 일관성 높음 | 코드 생성, 데이터 추출, 분류 |
| `0.3~0.5` | 약간의 유연성 | 요약, Q&A, 분석 |
| `0.7~1.0` | 창의적, 다양한 응답 | 글쓰기, 브레인스토밍 |
| `1.0+` | 매우 창의적, 예측 불가 | 창작, 아이디어 발산 |

```python
# 정확한 데이터 추출용
config = types.GenerateContentConfig(temperature=0.0)

# 창의적 글쓰기용
config = types.GenerateContentConfig(temperature=0.9)
```

### max_output_tokens

모델이 생성할 최대 토큰 수. 비용과 응답 길이를 제어한다.

```python
config = types.GenerateContentConfig(
    max_output_tokens=1024,   # 짧은 응답
    # max_output_tokens=8192, # 긴 문서 생성
)
```

### top_p / top_k

토큰 샘플링 방식 제어. 일반적으로 `temperature`만 조정해도 충분하다.

```python
config = types.GenerateContentConfig(
    top_p=0.95,  # 확률 합이 95%인 토큰 후보군에서 샘플링
    top_k=40,    # 상위 40개 토큰에서 샘플링
)
```

---

## Thinking Mode (Extended Thinking)

복잡한 추론이 필요한 작업에서 모델이 답변 전에 내부적으로 사고하도록 한다.
ADK에서 thinking 제어는 `generate_content_config`가 아닌 **`planner` 파라미터**를 통해 설정하는 것이 권장 방식이다.

```python
from google.adk.agents import LlmAgent
from google.adk.planners import BuiltInPlanner
from google.genai import types

agent = LlmAgent(
    name="reasoning_agent",
    model="gemini-2.5-pro",
    instruction="복잡한 수학 문제를 단계별로 풀어라.",
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            thinking_budget=8192,
            include_thoughts=True,  # 응답에 thinking 과정 포함 여부
        )
    ),
    generate_content_config=types.GenerateContentConfig(
        temperature=1.0,  # thinking mode 사용 시 1.0 권장 (낮추면 루핑/성능 저하 가능)
    ),
)
```

### Thinking 비활성화

thinking이 기본 활성화된 모델에서 명시적으로 비활성화할 때:

```python
agent = LlmAgent(
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(thinking_budget=0)
    ),
    ...
)
```

### thinking_budget 가이드

| 값 | 설명 |
|----|------|
| `0` | Thinking 비활성화 |
| `-1` | 동적 사고 (모델이 복잡도에 따라 자동 조정) |
| `1024` | 간단한 추론 |
| `8192` | 복잡한 문제 해결 (권장) |
| `24576` | 매우 복잡한 다단계 추론 (최대값) |

> **주의**: Thinking mode는 추가 토큰을 소비하므로 비용이 증가한다. 단순한 작업에는 사용하지 않는다.
> **주의**: Thinking mode 사용 시 temperature는 `1.0`을 권장한다. 낮은 값은 루핑이나 성능 저하를 유발할 수 있다.

---

## 모델 선택 가이드

| 모델 | 특성 | 적합한 용도 |
|------|------|------------|
| `gemini-3.1-pro-preview` | 최신, 최고성능 | 고난이도 추론, Thinking mode |
| `gemini-3-flash-preview` | 최신, 빠름 | 대부분의 에이전트 작업 (최신 기능) |
| `gemini-2.5-pro` | 안정, 고성능 | Thinking mode, 복잡한 분석 |
| `gemini-2.5-flash` | 안정, 비용 효율적 | 대부분의 에이전트 작업 (권장) |
| `gemini-2.5-flash-lite` | 매우 빠름, 저비용 | 단순 분류, 라우팅 |

> **참고**: `gemini-3.*-preview`는 Preview 단계로 요금이 부과될 수 있으며 변경될 수 있다.
> `gemini-2.0-flash`, `gemini-2.0-flash-lite`는 deprecated 예정으로 사용하지 않는다.

---

## JSON 구조화 응답 (output_schema)

에이전트가 항상 특정 JSON 형식으로 응답하도록 강제할 때 사용한다.
`response_mime_type="application/json"`을 수동으로 설정하는 것보다 **`output_schema`에 Pydantic 모델을 전달하는 방식이 권장**된다.

```python
from pydantic import BaseModel
from google.adk.agents import LlmAgent

class AnalysisResult(BaseModel):
    summary: str
    score: float
    tags: list[str]

agent = LlmAgent(
    name="analysis_agent",
    model="gemini-2.5-flash",
    instruction="텍스트를 분석하고 지정된 JSON 형식으로 결과를 반환하라.",
    output_schema=AnalysisResult,  # 내부적으로 response_mime_type 자동 설정
    generate_content_config=types.GenerateContentConfig(
        temperature=0.0,
    ),
)
```

> **주의**: `output_schema`와 `tools`는 함께 사용할 수 없다. 툴 호출이 필요한 에이전트에는 사용하지 않는다.

---

## 실전 설정 예시

```python
from google.adk.agents import LlmAgent
from google.adk.planners import BuiltInPlanner
from google.genai import types
from pydantic import BaseModel

# 데이터 추출 에이전트 (정확성 최우선 + JSON 강제)
class ExtractResult(BaseModel):
    items: list[str]
    count: int

extraction_agent = LlmAgent(
    name="extractor",
    model="gemini-2.5-flash",
    instruction="데이터를 추출하라.",
    output_schema=ExtractResult,
    generate_content_config=types.GenerateContentConfig(
        temperature=0.0,
        max_output_tokens=1024,
    ),
)

# 분석 에이전트 (Thinking mode)
analysis_agent = LlmAgent(
    name="analyzer",
    model="gemini-2.5-pro",
    instruction="데이터를 심층 분석하라.",
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(thinking_budget=8192)
    ),
    generate_content_config=types.GenerateContentConfig(
        temperature=1.0,
        max_output_tokens=4096,
    ),
)

# 최신 모델 사용 (Preview)
latest_agent = LlmAgent(
    name="latest_agent",
    model="gemini-3-flash-preview",
    instruction="...",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.7,
    ),
)
```
