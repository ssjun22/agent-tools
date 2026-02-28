# 세션 및 메모리 관리

## 개요

ADK에서 세션(Session)은 에이전트와 사용자 간의 대화 컨텍스트를 유지하는 단위다.
Runner가 세션을 생성하고 관리하며, 에이전트는 세션의 `state`를 통해 데이터를 주고받는다.

---

## 기본 구조

```
Runner
├── Session
│   ├── state: dict        # 에이전트 간 공유 데이터
│   └── history: list      # 대화 히스토리
└── Agent (실행 대상)
```

---

## 세션 State 활용

`output_key`로 저장한 값은 `session.state`에 저장되어 파이프라인의 다른 에이전트에서 참조할 수 있다.

```python
# 에이전트 A: 결과를 state에 저장
agent_a = LlmAgent(
    name="agent_a",
    output_key="my_result",  # session.state["my_result"]에 저장
    ...
)

# 에이전트 B: instruction에서 state 값 참조
agent_b = LlmAgent(
    name="agent_b",
    instruction="이전 결과를 활용하라: {my_result}",
    ...
)
```

---

## InMemorySessionService (기본)

개발/테스트 시 사용하는 메모리 기반 세션 서비스. 프로세스 종료 시 데이터가 소멸된다.

```python
from google.adk.sessions import InMemorySessionService

session_service = InMemorySessionService()
session = session_service.create_session(
    app_name="my_app",
    user_id="user_001",
)
```

---

## 영속적 세션 (심화)

프로덕션 환경에서 대화 히스토리를 유지하려면 `DatabaseSessionService` 또는
`VertexAiSessionService`를 사용한다. 이 부분은 프로젝트 요구사항에 따라 별도로 구현한다.

> **참고**: 현재 대부분의 사용 사례는 단일 세션 처리로 충분하다.
> 멀티 턴 대화나 사용자별 히스토리가 필요한 경우에만 영속적 세션을 고려하라.

---

## 관련 문서

- [ADK Sessions 공식 문서](https://google.github.io/adk-docs/sessions/)
