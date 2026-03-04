---
name: google-adk
description: Guide for building agents with Google Agent Development Kit (ADK) Python SDK. This skill should be used when adding new agent features to a project, implementing multi-agent orchestration patterns, defining custom tools, or configuring model settings such as temperature, thinking mode, and structured output.
---

# Google ADK 개발 가이드

Google Agent Development Kit(ADK) Python SDK를 활용한 에이전트 개발을 지원한다.

## 언제 사용하는가

- 기존 프로젝트에 신규 ADK 에이전트 기능을 추가할 때
- 멀티 에이전트 파이프라인 패턴을 구현할 때
- 커스텀 툴을 정의하거나 외부 API를 연동할 때
- temperature, thinking mode 등 모델 설정을 조정할 때

## 설치

```bash
pip install google-adk
```

---

## References

필요한 주제의 레퍼런스를 로드하여 참조하라.

| 파일                          | 내용                                                                 |
| ----------------------------- | -------------------------------------------------------------------- |
| `references/agent-types.md`   | LlmAgent, SequentialAgent, ParallelAgent, LoopAgent 정의 및 파라미터 |
| `references/tools.md`         | 커스텀 툴 작성 원칙, Built-in 툴 목록, 주의사항                      |
| `references/orchestration.md` | 멀티 에이전트 패턴 선택 가이드 및 구현 예시                          |
| `references/model-config.md`  | temperature, thinking mode, max_output_tokens 설정                   |
| `references/session.md`       | 세션/메모리 개념 및 기본 사용법                                      |

---

## Assets (Skeleton 코드)

`assets/` 디렉토리의 파일을 프로젝트에 복사하여 시작점으로 사용하라.

| 파일                            | 설명                                 |
| ------------------------------- | ------------------------------------ |
| `assets/single_agent.py`        | 단일 LlmAgent 기본 구조              |
| `assets/sequential_pipeline.py` | SequentialAgent 파이프라인           |
| `assets/parallel_pipeline.py`   | ParallelAgent + SequentialAgent 조합 |
| `assets/custom_tool.py`         | 커스텀 툴 정의 (함수형 + 비동기 API) |
| `assets/runner_setup.py`        | Runner + Session 초기화 및 실행      |

---

## 빠른 시작 워크플로우

### 신규 에이전트 기능 추가 시

1. **패턴 결정**: `references/orchestration.md`의 패턴 선택 가이드 참조
2. **Skeleton 복사**: 결정한 패턴에 맞는 `assets/` 파일을 프로젝트에 복사
3. **에이전트 수정**: `references/agent-types.md` 참조하여 name, instruction, tools 수정
4. **툴 추가**: `assets/custom_tool.py`를 기반으로 커스텀 툴 구현
5. **모델 설정**: `references/model-config.md` 참조하여 temperature, thinking mode 조정
6. **실행 설정**: `assets/runner_setup.py`를 기반으로 Runner 초기화

### 특정 패턴 구현 시

- 멀티 에이전트 → `references/orchestration.md` + 해당 `assets/` 파일
- 툴 정의 → `references/tools.md` + `assets/custom_tool.py`
- 모델 튜닝 → `references/model-config.md`

---

## 핵심 원칙

- `output_key`는 파이프라인 내에서 **고유한 이름**을 사용하라
- 툴의 독스트링(Args, Returns)을 명확하게 작성하라 — LLM이 툴을 올바르게 사용하는 데 직결됨
- LoopAgent는 반드시 `max_iterations`를 설정하라
- Thinking mode는 `generate_content_config`가 아닌 `planner=BuiltInPlanner(thinking_config=...)`로 제어하라
- Thinking mode 사용 시 `temperature=1.0`을 권장한다 — 낮은 값은 루핑/성능 저하를 유발할 수 있다
- 단순한 작업에 thinking mode를 사용하지 않는다 (비용 증가)
- JSON 응답 강제 시 `output_schema`에 Pydantic 모델을 전달하라 — `tools`와 함께 사용 불가
- 멀티 에이전트에서 `description`을 반드시 작성하라 — 라우터가 위임 결정 시 참조한다
