---
name: agent-creator
description: "Claude Code 서브 에이전트를 단계별로 설계하고 작성하는 워크플로우 스킬. brainstorming을 통해 목적을 탐색하고, Anthropic 워크플로우 패턴에 맞는 프롬프트 콘텐츠를 대화형으로 유도한다."
---

# Agent Creator

Claude Code 서브 에이전트 프롬프트를 체계적으로 설계·작성하는 워크플로우.
단순 scaffolding이 아니라, Anthropic의 워크플로우 패턴 분류에 따라 프롬프트 콘텐츠 작성을 유도한다.

## 참조 리소스

워크플로우 진행 중 필요 시 다음 파일을 읽는다:

| 리소스 | 경로 | 용도 |
|--------|------|------|
| 워크플로우 패턴 가이드 | `references/agent-types.md` | 패턴 판별 및 패턴별 강조 요소 |
| 프롬프트 템플릿 | `references/prompt-template.md` | 에이전트 파일의 기대 구조 |
| 프롬프팅 원칙 | `references/prompting-principles.md` | 프롬프트 작성 원칙 |
| 프롬프트 빌딩 블록 | `references/prompt-building-blocks.md` | 재사용 가능한 프롬프트 스니펫 |

## 체크리스트

```
□ 1. 목적 탐색       — brainstorming 호출, Understanding Lock까지 진행
□ 2. 패턴 판별       — 워크플로우 패턴 결정 + building-blocks 추천
□ 3. Frontmatter 확정 — name, description, tools, model 결정
□ 4. 콘텐츠 작성     — 섹션별 대화형 유도 (Role → Instructions → Constraints → Output Format → Checklist)
□ 5. 셀프 점검       — 작성 원칙 준수 여부 확인
     → PASS: 6번으로
     → FAIL: 4번으로 돌아가 수정
□ 6. 파일 생성       — agents/ 디렉토리에 저장
```

## 각 단계 상세

### 1. 목적 탐색

brainstorming 스킬을 호출하여 에이전트의 목적을 탐색한다.

**brainstorming 호출 시 전달할 컨텍스트:**
- "Claude Code 서브 에이전트를 설계하려 합니다"
- 사용자가 언급한 초기 아이디어

**brainstorming에서 확보할 것:**
- 에이전트가 해결할 문제/역할
- 대상 사용자 (누가 이 에이전트를 호출하는가)
- 성공 기준
- 명시적 비목표 (Non-goals)
- 확정된 가정 목록

**종료 조건:** brainstorming의 Understanding Lock이 확인되면 진행한다. Socratic Challenge까지 완료할 필요는 없다 — 에이전트 설계 수준에서는 Understanding Lock으로 충분하다.

**이 단계는 항상 멈춘다** — 사용자 확인 없이 다음으로 넘어가지 않는다.

### 2. 패턴 판별

`references/agent-types.md`를 읽고, brainstorming 결과를 기반으로 워크플로우 패턴을 판별한다.

**수행 절차:**
1. agent-types.md의 패턴 판별 질문 흐름을 순서대로 적용한다
2. 해당 패턴의 프롬프트 섹션별 강조 요소를 확인한다
3. 해당 패턴의 추천 building-blocks 목록을 제시한다
4. `references/prompt-building-blocks.md`에서 해당 스니펫 원문을 읽어 사용자에게 보여준다

**출력:**
```
워크플로우 패턴: [패턴명]
선택 근거: [brainstorming 결과에서 판별 질문에 매칭된 이유]
추천 building-blocks:
  - [블록명]: [채택 이유]
  - ...
```

사용자에게 패턴 판별 결과를 확인받고 진행한다.

### 3. Frontmatter 확정

`references/prompt-template.md`를 읽고, frontmatter 필드를 하나씩 결정한다.

| 필드 | 결정 방법 |
|------|-----------|
| `name` | brainstorming 결과에서 핵심 역할을 kebab-case로 변환. 사용자와 확인 |
| `description` | 1-2문장, 역할 + 언제 사용하는지 ("...할 때 사용하는 에이전트") |
| `tools` | 패턴별 권장 tools를 기본값으로 제안, 사용자와 조정 |
| `model` | 패턴별 권장 model을 기본값으로 제안, 사용자와 조정 |

**출력:** 확정된 frontmatter 블록을 보여주고 확인받는다.

```yaml
---
name: example-agent
description: "..."
tools: Read, Edit, Write, Glob, Grep
model: sonnet
---
```

### 4. 콘텐츠 작성

`references/prompt-template.md`의 기대 구조에 따라 섹션별로 작성한다.
작성 원칙은 `references/prompting-principles.md`를 참조한다.

**진행 방식:** 한 섹션씩 순서대로 작성한다. 각 섹션에서:
1. 2단계에서 결정된 패턴의 강조 요소를 안내한다
2. 유도 질문을 던져 내용을 이끌어낸다
3. 초안을 작성하여 보여준다
4. 사용자 피드백을 반영하여 수정한다
5. 확인되면 다음 섹션으로 넘어간다

#### 4-1. Role

**유도 질문:**
- "이 에이전트의 전문 도메인은 무엇인가요?"
- "에이전트의 행동 원칙을 한 줄로 표현하면?"

**작성 기준:**
- 1-3문장으로 간결하게
- 전문 도메인 + 행동 방식 + 범위
- prompting-principles의 "역할 정의" 원칙 적용

#### 4-2. Instructions

**유도 질문:**
- "이 에이전트가 호출되면 가장 먼저 할 일은?"
- "핵심 판단 기준이나 실행 절차가 있나요?"
- "경계 케이스는 어떻게 처리하나요?"

**작성 기준:**
- 핵심 작업을 실행 가능한 단계로 분해
- 패턴에 따라 차별화 (`references/agent-types.md`의 패턴별 Instructions 강조 요소 참조):
  - Prompt Chaining: 단계별 절차, 검증 게이트
  - Routing: 분류 기준, 카테고리별 처리 로직
  - Parallelization: 독립 분석 차원, 결과 종합 방법
  - Orchestrator-Workers: 작업 분해 기준, worker 호출/종합 방법
  - Evaluator-Optimizer: 생성 기준 + 평가 기준 분리, 반복 조건
  - Autonomous Agent: 목표 정의, 도구 용도, 의사결정 기준
- 2단계에서 채택한 building-blocks를 적절한 위치에 삽입

#### 4-3. Constraints

**유도 질문:**
- "이 에이전트가 절대 하면 안 되는 것은?"
- "범위 밖으로 빠지기 쉬운 상황이 있나요?"

**작성 기준:**
- 긍정 프레이밍 우선 ("~한다" > "~하지 않는다")
- 비목표(Non-goals)를 Constraints로 변환
- 오탐/과잉 행동 방지 규칙

#### 4-4. Output Format

**유도 질문:**
- "이 에이전트의 최종 산출물 형태는? (보고서, 코드, JSON, 자유 형식 등)"
- "산출물에 반드시 포함되어야 할 필드나 섹션이 있나요?"

**작성 기준:**
- 구체적 스키마 또는 구조 정의
- 예시 포함 권장
- 패턴에 따라 (`references/agent-types.md`의 패턴별 Output Format 강조 요소 참조)

#### 4-5. Checklist

**유도 질문:**
- "이 에이전트가 작업을 마치기 전에 반드시 확인해야 할 것은?"

**작성 기준:**
- 5-7개 항목
- Instructions의 핵심 검증 포인트를 반영
- 체크리스트 형식 (`- [ ]`)

### 5. 셀프 점검

`references/prompting-principles.md`의 작성 원칙을 기준으로 완성된 프롬프트를 훑는다.

**점검 항목:**
1. `prompt-template.md`의 기대 구조(Frontmatter + 5개 섹션)를 빠짐없이 갖추었는가
2. 과잉 강조 표현(MUST, CRITICAL, ALWAYS, NEVER)이 안전 규칙 외에 사용되지 않았는가
3. 비자명한 규칙에 "왜"가 포함되었는가
4. 부정 프레이밍("하지 마라")을 긍정 프레이밍("이렇게 해라")으로 바꿀 수 있는가
5. 선택한 building-blocks 간 충돌이 없는가 (예: 구현 우선 + 확인 후 실행)

**결과 처리:**
- 구조 누락 또는 블록 충돌 발견 → 해당 섹션으로 돌아가 수정 (4번으로)
- 톤/프레이밍 이슈만 → 즉석 수정 후 진행
- 이슈 없음 → 6번으로 진행

상세한 품질 리뷰가 필요하면 파일 생성 후 `claude-agent-reviewer` 스킬을 실행한다.

### 6. 파일 생성

**저장 위치 결정:**
사용자에게 확인한다:
- `agents/` — 범용 에이전트 (여러 프로젝트에서 사용)
- 사용자 지정 경로

**파일 조립 및 검증:**
1. 3단계의 frontmatter + 4단계의 섹션들을 `prompt-template.md` 순서대로 조립한다
2. 조립된 전체 파일을 사용자에게 보여준다
3. 확인 후 Write 도구로 저장한다
- 파일명: `{name}.md` (frontmatter의 name 사용)

**완료 메시지:**
```
에이전트 생성 완료: {경로}
에이전트 호출 방법: @{name}

추가 검증이 필요하면 claude-agent-reviewer 스킬을 실행하세요.
```

## 자동 진행 규칙

| 단계 | 조건 | 동작 |
|------|------|------|
| 1. 목적 탐색 | 항상 멈춤 | brainstorming 결과를 사용자가 확인 |
| 2. 패턴 판별 | 패턴이 명확하면 | 확인만 받고 자동 진행 |
| 3. Frontmatter | 항상 멈춤 | 사용자 확인 필수 |
| 4. 콘텐츠 작성 | 섹션별로 멈춤 | 각 섹션 확인 후 다음 섹션으로 |
| 5. 셀프 점검 | 구조/블록 이슈 없으면 | 자동 진행 |
| 6. 파일 생성 | 항상 멈춤 | 저장 위치 확인 필수 |

## 행동 규칙

1. `/agent-creator` 호출 시 현재 위치를 파악하고, 체크리스트에서 다음 단계를 안내한다.
2. 각 단계의 종료 조건이 충족되면 자동 진행 규칙에 따라 진행하거나 멈춘다.
3. 사용자가 특정 단계를 건너뛰고 싶다면 허용한다 — 체크리스트를 그에 맞춰 갱신한다.
4. brainstorming 호출 시, 사용자의 초기 아이디어를 원문 그대로 전달한다. 요약하지 않는다.
5. 참조 리소스는 해당 단계에서 필요할 때 읽는다. 모든 리소스를 미리 로드하지 않는다.
6. 에이전트 프롬프트 작성 시 prompting-principles.md의 "4.6 모델 과잉 프롬프팅 방지" 원칙을 준수한다 — MUST, CRITICAL, ALWAYS 같은 과잉 강조 표현을 지양한다.
