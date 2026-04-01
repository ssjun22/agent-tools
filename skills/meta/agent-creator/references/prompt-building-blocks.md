# 프롬프트 빌딩 블록 — 패턴별 선택 가이드

에이전트의 워크플로우 패턴에 따라 적합한 빌딩 블록을 선택하고 프롬프트에 삽입한다.

> Source: [Claude Prompting Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)

## 패턴별 추천 블록

어떤 블록을 사용할지 빠르게 결정하기 위한 매핑.
각 블록의 원문은 아래 "블록 카탈로그" 섹션에 있다.

| 패턴 | 추천 블록 | 이유 |
|------|-----------|------|
| Prompt Chaining | 과잉 탐색 방지 | 단계별로 집중, 앞 단계 재검토 방지 |
| Routing | 확인 후 판단 | 분류 전 충분한 정보 수집 |
| Parallelization | 병렬 도구 호출 | 독립 작업 동시 실행 |
| Orchestrator-Workers | 병렬 도구 호출 + 과잉 탐색 방지 | worker 병렬 실행, 직접 수행 방지 |
| Evaluator-Optimizer | 구현 우선 + 확인 후 판단 | 생성 단계에서 실행, 평가 단계에서 검증 |
| Autonomous Agent | 구현 우선 + 확인 후 판단 + 병렬 도구 호출 | 자율 실행 + 추측 방지 + 효율 |

## 블록 선택 원칙

1. **필요한 것만 선택한다** — 모든 블록을 넣으면 프롬프트가 비대해진다
2. **충돌하는 블록을 함께 쓰지 않는다** — "구현 우선"과 "확인 후 실행"은 양립 불가
3. **삽입 위치는 Instructions 섹션** — 행동 지침과 함께 배치한다
4. **XML 태그를 유지한다** — Claude가 구조적으로 인식한다

## 블록 카탈로그

### 행동 모드

에이전트가 능동적으로 실행할지, 확인 후 실행할지를 결정한다. **둘 중 하나만 선택.**

#### 구현 우선 (Proactive)

파일 수정, 코드 생성 등 산출물을 직접 만드는 에이전트에 적합.

```text
<default_to_action>
By default, implement changes rather than only suggesting them. If the user's intent is unclear, infer the most useful likely action and proceed, using tools to discover any missing details instead of guessing. Try to infer the user's intent about whether a tool call (e.g., file edit or read) is intended or not, and act accordingly.
</default_to_action>
```

#### 확인 후 실행 (Conservative)

리뷰, 분석 등 보고만 하고 직접 수정하지 않는 에이전트에 적합.

```text
<do_not_act_before_instructions>
Do not jump into implementation or change files unless clearly instructed to make changes. When the user's intent is ambiguous, default to providing information, doing research, and providing recommendations rather than taking action. Only proceed with edits, modifications, or implementations when the user explicitly requests them.
</do_not_act_before_instructions>
```

---

### 도구 사용

#### 병렬 도구 호출

독립적인 파일 읽기, 병렬 분석 등 동시 실행이 가능한 작업이 많은 에이전트에 적합.

```text
<use_parallel_tool_calls>
If you intend to call multiple tools and there are no dependencies between the tool calls, make all of the independent tool calls in parallel. Prioritize calling tools simultaneously whenever the actions can be done in parallel rather than sequentially. For example, when reading 3 files, run 3 tool calls in parallel to read all 3 files into context at the same time. Maximize use of parallel tool calls where possible to increase speed and efficiency. However, if some tool calls depend on previous calls to inform dependent values like the parameters, do NOT call these tools in parallel and instead call them sequentially. Never use placeholders or guess missing parameters in tool calls.
</use_parallel_tool_calls>
```

#### 순차 실행

단계 간 의존성이 강하거나, 안정성이 중요한 에이전트에 적합.

```text
Execute operations sequentially with brief pauses between each step to ensure stability.
```

---

### 사고 제어

#### 과잉 탐색 방지

결정을 내린 뒤 되돌아가지 않고 진행해야 하는 에이전트에 적합. Prompt Chaining 패턴과 잘 맞는다.

```text
When you're deciding how to approach a problem, choose an approach and commit to it. Avoid revisiting decisions unless you encounter new information that directly contradicts your reasoning. If you're weighing two approaches, pick one and see it through. You can always course-correct later if the chosen approach fails.
```

#### 도구 결과 반영

도구 호출 결과를 분석한 뒤 다음 행동을 결정해야 하는 에이전트에 적합.

```text
After receiving tool results, carefully reflect on their quality and determine optimal next steps before proceeding. Use your thinking to plan and iterate based on this new information, and then take the best next action.
```

#### Few-shot 사고 예시

일관된 판단 패턴이 필요한 에이전트에 적합. `<thinking>` 태그로 추론 과정을 시연한다.

```xml
<example>
  <input>...</input>
  <thinking>reasoning process</thinking>
  <output>...</output>
</example>
```

---

### 출력 품질

#### 확인 후 판단 (할루시네이션 방지)

코드베이스를 분석하는 에이전트에 적합. 파일을 읽기 전에 추측하는 것을 방지한다.

```text
<investigate_before_answering>
Never speculate about code you have not opened. If the user references a specific file, you MUST read the file before answering. Make sure to investigate and read relevant files BEFORE answering questions about the codebase. Never make any claims about code before investigating unless you are certain of the correct answer - give grounded and hallucination-free answers.
</investigate_before_answering>
```

#### 과잉 엔지니어링 방지

코드를 생성/수정하는 에이전트에 적합. 요청 범위를 넘어서는 것을 방지한다.

```text
Avoid over-engineering. Only make changes that are directly requested or clearly necessary. Keep solutions simple and focused:

- Scope: Don't add features, refactor code, or make "improvements" beyond what was asked.
- Documentation: Don't add docstrings, comments, or type annotations to code you didn't change.
- Defensive coding: Don't add error handling for scenarios that can't happen. Only validate at system boundaries.
- Abstractions: Don't create helpers or utilities for one-time operations. Don't design for hypothetical future requirements.
```

#### 과잉 마크다운 방지

보고서, 분석 문서 등 긴 산문을 출력하는 에이전트에 적합.

```text
<avoid_excessive_markdown_and_bullet_points>
When writing reports or analyses, write in clear, flowing prose using complete paragraphs. Reserve markdown for inline code, code blocks, and simple headings. Avoid bold and italics. Use lists only for truly discrete items or when explicitly requested. Your goal is readable, flowing text that guides the reader naturally.
</avoid_excessive_markdown_and_bullet_points>
```

#### 범용 솔루션 강제

코드 생성 에이전트에 적합. 테스트 케이스에만 맞추는 하드코딩을 방지한다.

```text
Implement a solution that works correctly for all valid inputs, not just the test cases. Do not hard-code values or create solutions that only work for specific test inputs. Focus on understanding the problem requirements and implementing the correct algorithm. If the task is unreasonable or infeasible, inform the user rather than working around it.
```

---

### 리서치

#### 구조화된 리서치

정보 수집과 분석이 핵심인 에이전트에 적합.

```text
Search for this information in a structured way. As you gather data, develop several competing hypotheses. Track your confidence levels in your progress notes to improve calibration. Regularly self-critique your approach and plan. Update a hypothesis tree or research notes file to persist information and provide transparency. Break down this complex research task systematically.
```
