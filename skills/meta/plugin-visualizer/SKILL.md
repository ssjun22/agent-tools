---
name: plugin-visualizer
description: This skill should be used when the user wants to visualize, map, or generate an overview of AI agent plugins. It reads all plugin.json and README.md files from the plugins/ directory and generates a comprehensive OVERVIEW.md with Mermaid relationship diagrams, data flow visualizations, and component maps. Use this skill whenever the user asks to visualize plugins, generate a plugin overview, create a plugin map, or wants to understand plugin structure (e.g., "플러그인 시각화해줘", "플러그인 오버뷰 만들어줘", "플러그인 구조 정리해줘").
---

# Plugin Visualizer

plugins/ 디렉토리의 모든 플러그인을 분석하여 `plugins/OVERVIEW.md`를 생성하는 스킬.

## 목적

- 플러그인 간 관계를 한눈에 파악 (Mermaid 다이어그램)
- 플러그인별 데이터 흐름을 시각적으로 이해
- 구성요소(skills, agents, rules, hooks)를 체계적으로 정리

## 실행 절차

### 1단계: 데이터 수집

plugins/ 하위 모든 디렉토리에서 다음 파일을 읽는다:

1. **plugin.json** — 구성요소 목록 (skills, agents, rules, hooks)
2. **README.md** — 목적, Related Plugins, 데이터 흐름 정보

수집 시 `plugins/README.md`(인덱스 파일)는 제외한다.

### 2단계: OVERVIEW.md 생성

아래 3개 섹션을 **이 순서대로** 구성된 `plugins/OVERVIEW.md`를 생성한다.

관계 다이어그램을 가장 먼저 배치하는 이유: 전체 구조를 먼저 파악한 뒤 세부사항으로 내려가는 것이 관리자 관점에서 가장 효율적이다.

---

#### 섹션 1: 관계 다이어그램 (Mermaid) — 가장 먼저

플러그인 간 관계를 Mermaid flowchart로 시각화한다. 문서의 최상단에 위치하여 전체 구조를 한눈에 보여준다.

**생성 규칙:**

1. 각 플러그인을 노드로 표현
2. 노드 안에 구성요소 유형별 개수를 표기 (예: `S:3 A:10 R:0 H:0`)
3. 플러그인 간 관계를 화살표로 연결:
   - `-->` 실선: "함께 사용 권장" (README에서 추출)
   - `-.->` 점선: "선택적 조합 가능"
4. 카테고리별 subgraph 그룹핑:
   - **개발 프로세스**: dev-workflow, openspec-sdd
   - **세션/컨텍스트 관리**: handoff, project-context
   - **품질/개선**: karpathy-coding-guide, feedback-harvesting
   - 새로운 플러그인은 성격에 맞는 기존 subgraph에 배치하거나, 필요하면 새 subgraph를 생성

**형식 예시:**

```markdown
## Plugin Relations

```mermaid
flowchart TB
    subgraph "개발 프로세스"
        DW["dev-workflow<br/>S:3 A:10 R:0 H:0"]
        OS["openspec-sdd<br/>S:13 A:0 R:1 H:0"]
    end

    subgraph "세션/컨텍스트 관리"
        HO["handoff<br/>S:0 A:1 R:1 H:1"]
        PC["project-context<br/>S:1 A:0 R:1 H:2"]
    end

    subgraph "품질/개선"
        KC["karpathy-coding-guide<br/>S:1 A:0 R:1 H:0"]
        FH["feedback-harvesting<br/>S:0 A:1 R:1 H:1"]
    end

    DW --> OS
    DW -.-> PC
    ...
```​
```

- 관계는 README의 "Related Plugins" / "Relation to Other Plugins" 섹션에서 추출
- 명시적 관계가 없으면 같은 subgraph 내에서도 화살표를 그리지 않음

---

#### 섹션 2: 플러그인별 상세 (데이터 흐름)

각 플러그인의 핵심 동작을 시각적으로 표현한다. README에서 데이터 흐름, 파이프라인, 세션 라이프사이클 등 동작 구조를 추출하여 텍스트 다이어그램으로 보여준다.

이 섹션에서는 **구성요소 목록을 별도로 나열하지 않는다** — 구성요소 상세는 섹션 3(Component Map)에서 다룬다. 여기서는 동작 흐름에만 집중한다.

**형식:**

```markdown
## Plugin Details

### dev-workflow

> 11단계 개발 세션 파이프라인

**파이프라인:**
```
1. 작업사항 확인 → 2. 작업 선택
→ 3. @interviewer → 4. @spec-writer
→ 5. @designer → 6. @spec-builder
→ 7. @spec-checker → 8. 이슈 수정
→ 9. @code-reviewer → 10. @docs-updater → 11. @committer
```

### feedback-harvesting

> 사용자 피드백 자동 감지 및 스킬/에이전트 개선 제안

**데이터 흐름:**
```
피드백 메시지 발생
  → rule이 감지
  → feedback-harvester (백그라운드)
  → .claude/evolution/pending-*.md 저장
  → [다음 세션] hook 알림
  → 사용자 승인 → 반영
```
```

**데이터 흐름 추출 원칙:**
- README에 데이터 흐름/파이프라인 다이어그램이 있으면 **핵심만 요약**하여 포함
- 없는 경우 plugin.json의 구성요소와 README 설명을 바탕으로 간략한 동작 흐름을 작성
- 텍스트 기반 다이어그램 사용 (`→`, `│`, `├──` 등)

---

#### 섹션 3: 구성요소 상세 맵

플러그인별로 어떤 구성요소를 갖고 있는지 펼쳐서 보여준다.

**형식:**

```markdown
## Component Map

### dev-workflow

| 유형 | 구성요소 |
|------|---------|
| Skills | `workflow`, `code-reviewer`, `git-commit-helper` |
| Agents | `interviewer`, `spec-writer`, `designer`, ... |
| Rules | — |
| Hooks | — |

### handoff
...
```

- 비어 있는 카테고리는 `—`로 표시
- skill 이름은 **basename만** 표시 (경로 제외)
  - `pipeline/workflow` → `workflow`
  - `dev/code-reviewer` → `code-reviewer`
  - `pipeline/openspec-apply-change` → `openspec-apply-change`
  - `project/project-context-init` → `project-context-init`
- agent, rule, hook 이름은 그대로 표시
- 구성요소명은 backtick으로 감싸서 코드 스타일 적용

---

### 3단계: 파일 출력

생성된 내용을 `plugins/OVERVIEW.md`에 기록한다.

파일 상단에 다음 헤더를 추가:

```markdown
# Plugins Overview

> 이 문서는 plugin-visualizer 스킬로 생성되었습니다.
> 최종 생성일: YYYY-MM-DD
```

날짜는 실행 시점의 실제 날짜를 사용한다.

## 주의사항

- plugin.json이 없는 디렉토리는 무시한다
- 새 플러그인이 추가되었더라도 이 스킬을 재실행하면 최신 상태로 갱신된다
- 기존 OVERVIEW.md가 있으면 덮어쓴다
- Mermaid 다이어그램은 GitHub에서 렌더링 가능한 형식을 유지한다
