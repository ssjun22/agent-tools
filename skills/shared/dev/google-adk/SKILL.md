---
name: google-adk
description: Guide for building agents with Google Agent Development Kit (ADK) Python SDK. Use when adding new ADK agent features, implementing multi-agent orchestration, defining custom tools, or configuring model settings.
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

## 개발 프로세스

### Step 1: 에이전트 요구사항 파악

추가할 에이전트 기능의 목적과 요구사항을 파악하라.

- 어떤 작업을 수행하는 에이전트인가?
- 단독으로 동작하는가, 다른 에이전트와 협력하는가?
- 외부 API나 커스텀 툴이 필요한가?

### Step 2: 오케스트레이션 패턴 선택

`references/orchestration.md`를 로드하여 적합한 패턴을 선택하라.

- 작업들이 순서대로 의존한다 → SequentialAgent
- 작업들이 독립적으로 병렬 처리 가능하다 → ParallelAgent
- 조건 충족까지 반복이 필요하다 → LoopAgent
- 단일 에이전트로 충분하다 → LlmAgent

### Step 3: Skeleton 코드 생성

결정한 패턴에 따라 스크립트를 실행하여 skeleton 코드를 생성하라.

단일 에이전트가 필요한 경우:
```bash
scripts/single_agent.py --output <생성할 파일 경로>
```

Sequential 파이프라인이 필요한 경우:
```bash
scripts/sequential_pipeline.py --output <생성할 파일 경로>
```

병렬 처리 후 종합이 필요한 경우:
```bash
scripts/parallel_pipeline.py --output <생성할 파일 경로>
```

커스텀 툴을 정의해야 하는 경우:
```bash
scripts/custom_tool.py --output <생성할 파일 경로>
```

Runner와 Session 초기화 코드가 필요한 경우:
```bash
scripts/runner_setup.py --output <생성할 파일 경로>
```

### Step 4: 에이전트 구성

생성된 skeleton을 프로젝트 요구사항에 맞게 수정하라.

- `name`, `description`, `instruction`, `tools` 수정 → `references/agent-types.md` 로드
- `temperature`, thinking mode, 모델 조정 → `references/model-config.md` 로드
