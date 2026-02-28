# Google ADK 커스텀 툴 정의

## 개요

ADK에서 툴은 에이전트가 외부 시스템과 상호작용하거나 특정 기능을 수행할 수 있도록 하는 Python 함수다.

---

## 기본 패턴: 함수형 툴 + 외부 API 연동 툴

일반 Python 함수에 독스트링을 작성하면 ADK가 자동으로 툴 스키마를 생성한다.

> Skeleton 코드: `assets/custom_tool.py` (함수형 + 비동기 API 연동 두 가지 패턴 포함)

> **중요**: 독스트링의 품질이 LLM이 툴을 올바르게 사용하는 데 직결된다. Args와 Returns를 반드시 명시하라.

---

## Built-in 툴

ADK가 제공하는 기본 툴:

| 툴 | import | 설명 |
|----|--------|------|
| Google Search | `from google.adk.tools import google_search` | 웹 검색 |
| Code Execution | `from google.adk.tools import built_in_code_execution` | Python 코드 실행 |

---

## 툴 작성 시 주의사항

- 반환값은 항상 **직렬화 가능한 타입** (dict, list, str, int 등)으로 반환하라
- 에러 발생 시 예외를 직접 raise하지 말고, 에러 정보를 dict로 반환하는 것을 고려하라
- 비동기 API 호출은 `async def`로 정의하라
- 민감한 정보(API Key 등)는 환경변수로 관리하라
