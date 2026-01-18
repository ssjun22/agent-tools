# My Skill Template

> Last Updated: 2026-01-18
> Version: 2.0

이 템플릿은 분석한 스킬들의 패턴을 반영한 마스터 템플릿입니다.

**v2.0 업데이트 (2026-01-18)**:
- skills/local 8개 스킬 분석 결과 반영
- Description 작성 패턴 4가지 추가
- Workflow-Based 패턴 강화 및 실제 예시 추가
- Common Section Names 실제 사용 빈도 기반 재구성
- Progressive Disclosure 통계 및 실제 예시 추가
- Real-World Statistics 섹션 신규 추가

---

## SKILL.md Template

```markdown
---
name: [skill-name]
description: This skill should be used when [specific scenario/task]. [Additional context about what it does and when to trigger it.]
---

# [Skill Name]

## Overview

[1-2 sentences explaining what this skill enables]

## [Main Section - Choose Pattern Below]

### Pattern 1: Workflow-Based (순차적 프로세스)

**가장 많이 사용되는 패턴** (분석한 8개 스킬 중 5개 사용)

**When to use**: 명확한 단계별 절차가 있는 경우

**Common Section Structure**:

```markdown
---
name: skill-name
description: [Clear trigger conditions and capabilities]
---

# Skill Name

## When to Use This Skill

[Specific scenarios and trigger conditions]

## Quick Reference (Optional but Popular)

**Commands**:
- `command-name`: Brief description

**Key Concepts**:
- Concept 1
- Concept 2

## Core [Patterns/Principles/Concepts]

### Pattern 1: [Pattern Name]

[Description and usage]

### Pattern 2: [Pattern Name]

[Description and usage]

## [Main Process Name] Workflow

### Step 1: [Step Name]

[Instructions]

### Step 2: [Step Name]

[Instructions]

### Step 3: [Step Name]

[Instructions]

## Common Mistakes to Avoid

- ❌ [Mistake]: [Why to avoid]
- ❌ [Mistake]: [Why to avoid]

## Best Practices

- ✓ [Practice]
- ✓ [Practice]

## Resources (if references/ or scripts/ exist)

For detailed guides, see:
- `references/[category]/[file].md`
```

**Real Examples from Analyzed Skills**:
- `component-refactoring`: Quick Reference → Core Patterns → Workflow → Common Mistakes
- `frontend-testing`: When to Apply → Quick Reference → Core Principles → Testing Workflow
- `pr-creator`: Workflow → Principles
- `prompt-engineering-patterns`: When to Use → Core Capabilities → Quick Start → Key Patterns
- `senior-prompt-engineer`: Quick Start → Core Expertise → Production Patterns → Best Practices

---

### Pattern 2: Task-Based (작업/기능 모음)

**When to use**: 다양한 독립적인 작업을 제공하는 경우

**Structure**:
```markdown
## Quick Start

[Brief overview of how to use the skill]

## Task Category 1

### Task 1.1: [Task Name]

[Instructions]

### Task 1.2: [Task Name]

[Instructions]

## Task Category 2

### Task 2.1: [Task Name]

[Instructions]
```

**Example Skills**: PDF skill (Merge/Split/Extract)

---

### Pattern 3: Reference/Guidelines (표준/사양)

**When to use**: 표준, 가이드라인, 요구사항을 제공하는 경우

**Structure**:
```markdown
## Guidelines Overview

[What these guidelines cover]

## Category 1: [e.g., Colors]

[Specifications and rules]

## Category 2: [e.g., Typography]

[Specifications and rules]

## Usage Examples

[How to apply these guidelines]
```

**Example Skills**: Brand styling, Coding standards

---

### Pattern 4: Capabilities-Based (통합 기능)

**When to use**: 상호 연관된 여러 기능을 제공하는 경우

**Structure**:
```markdown
## Core Capabilities

This skill provides the following capabilities:

### 1. [Capability Name]

[Description and usage]

### 2. [Capability Name]

[Description and usage]

### 3. [Capability Name]

[Description and usage]
```

**Example Skills**: Product Management

---

## Resources Section (Optional but Recommended)

```markdown
## Resources

This skill includes the following resources:

### scripts/

[Brief description of what scripts are included and when to use them]

Example:
- `script_name.py`: [Purpose and usage]

### references/

[Brief description of reference documentation]

Example:
- `category/document.md`: [What information it contains]

For large reference files (>10k words), use Grep with patterns: `pattern_to_search`

### assets/

[Brief description of asset files]

Example:
- `template.html`: [What this template provides]
```

## YAML Frontmatter Guidelines

### name

- **Format**: lowercase-with-hyphens
- **Length**: 2-4 words
- **Examples**:
  - ✓ `pdf-editor`
  - ✓ `skill-pattern-analyzer`
  - ✗ `PDFEditor` (avoid CamelCase)
  - ✗ `pdf_editor` (avoid underscores)

### description

- **Voice**: 다양한 형식 사용 가능
  - Third-person: "This skill should be used when..."
  - Imperative: "Use when...", "Use this skill when..."
  - Action-focused: "Generate...", "Create...", "Trigger when..."
- **Content**:
  1. **When to use** - 구체적 시나리오/트리거 조건
  2. **What it does** - 핵심 기능 설명
  3. **When to avoid** (선택사항) - 사용하지 말아야 할 경우
- **Length**: 1-3 sentences (간결할수록 좋음)

**Patterns**:

**Pattern A: Trigger-based** (트리거 키워드 명시)
```yaml
description: "Generate Vitest + React Testing Library tests for Dify frontend components, hooks, and utilities. Triggers on testing, spec files, coverage, Vitest, RTL, unit tests, integration tests, or write/review test requests."
```
- ✓ 명확한 트리거 키워드 나열
- ✓ 무엇을 생성/수행하는지 명시

**Pattern B: Conditional** (조건부 사용)
```yaml
description: "Refactor high-complexity React components in Dify frontend. Use when `pnpm analyze-component --json` shows complexity > 50 or lineCount > 300, when the user asks for code splitting, hook extraction, or complexity reduction, or when `pnpm analyze-component` warns to refactor before testing; avoid for simple/well-structured components, third-party wrappers, or when the user explicitly wants testing without refactoring."
```
- ✓ 구체적 조건 명시 (메트릭, 명령어 결과)
- ✓ 사용/비사용 조건 모두 제시

**Pattern C: Simple use-case** (간결한 사용 사례)
```yaml
description: "Create production-ready FastAPI projects with async patterns, dependency injection, and comprehensive error handling. Use when building new FastAPI applications or setting up backend API projects."
```
- ✓ 핵심 기능 + 사용 시점
- ✓ 간결하고 명확

**Pattern D: User action-based** (사용자 요청 기반)
```yaml
description: "Trigger when the user requests a review of frontend files (e.g., `.tsx`, `.ts`, `.js`). Support both pending-change reviews and focused file reviews while applying the checklist rules."
```
- ✓ 사용자 액션에 반응
- ✓ 지원하는 시나리오 명시

❌ **Avoid**:
- "A comprehensive toolkit..." (너무 마케팅스러움)
- "You should use this when..." (second-person 지양)
- 너무 긴 설명 (3문장 이상)

## Writing Style Guidelines

### Imperative/Infinitive Form

**Use** (Recommended):
- "To accomplish X, do Y"
- "Read the file using..."
- "Configure the settings by..."

**Avoid**:
- "You should do X"
- "You need to configure..."
- "You can accomplish X by..."

### Objective & Instructional Tone

**Use**:
- "This approach provides..."
- "The script handles..."
- "Configure settings to enable..."

**Avoid**:
- "I recommend..."
- "You'll love this feature..."
- "It's amazing how this works..."

## Best Practices

### Progressive Disclosure

**실제 활용도**: 8개 스킬 중 5개가 references/ 활용 ⭐⭐⭐

1. **Keep SKILL.md concise** (< 5k words)
   - 평균 단어 수: ~930 words (분석 결과)
   - 가장 긴 스킬: 1,714 words (component-refactoring)
   - 가장 짧은 스킬: 326 words (pr-creator)

2. **Move detailed docs to references/**
   - **When to use references/**:
     - Detailed implementation guides
     - Comprehensive checklists
     - API documentation
     - Framework-specific patterns
     - Domain knowledge

   - **Real Examples**:
     - `frontend-testing`: 6개 reference 파일 (async-testing, mocking, domain-components 등)
     - `component-refactoring`: 3개 파일 (complexity-patterns, component-splitting, hook-extraction)
     - `prompt-engineering-patterns`: 5개 파일 (chain-of-thought, few-shot-learning 등)

   - **Naming Pattern**: `[category-name].md` 또는 `[category]/[topic].md`

3. **Use assets/ for templates** (2/8 스킬 사용)
   - Test templates (frontend-testing)
   - Prompt template library (prompt-engineering-patterns)
   - JSON examples (prompt-engineering-patterns)

4. **Use scripts for reusable code** (2/8 스킬 사용)
   - Python scripts for automation
   - Real examples:
     - `senior-prompt-engineer`: 3 scripts (prompt_optimizer, rag_evaluator, agent_orchestrator)
     - `prompt-engineering-patterns`: 1 script (optimize-prompt.py)

### Resource Organization

```
✓ GOOD:
skill-name/
├── SKILL.md (< 5k words, core workflow only)
├── scripts/
│   └── automation.py (reusable automation)
├── references/
│   ├── detailed-guide.md (in-depth documentation)
│   └── api-specs.md (API reference)
└── assets/
    └── template.html (output template)

✗ BAD:
skill-name/
├── SKILL.md (15k words, everything in one file)
└── (no bundled resources)
```

### Avoid Duplication

- Information should live in **either** SKILL.md **or** references, not both
- Core procedural instructions → SKILL.md
- Detailed reference material → references/
- Templates/boilerplate → assets/

## Common Section Names

**실제 스킬 분석 기반** (skills/local 8개 스킬):

### Opening Sections
- **When to Use This Skill** ⭐ (frontend-testing, prompt-engineering-patterns)
- **When to Apply This Skill** (frontend-testing)
- **Intent** (frontend-code-review)
- **Overview** / **Quick Start**

### Core Content Sections
- **Quick Reference** ⭐⭐ (component-refactoring, frontend-testing)
  - Commands, Key Concepts, Tech Stack
- **Core [Principles/Patterns/Concepts/Capabilities]** ⭐⭐⭐
  - Core Principles (frontend-testing)
  - Core Refactoring Patterns (component-refactoring)
  - Core Capabilities (prompt-engineering-patterns, senior-prompt-engineer)
  - Core Concepts (fastapi-templates)
- **[X] Workflow** / **[X] Process** ⭐⭐
  - Refactoring Workflow (component-refactoring)
  - Testing Workflow (frontend-testing)
  - Review Process (frontend-code-review)
- **Implementation Patterns** (fastapi-templates)
- **Production Patterns** (senior-prompt-engineer)

### Guidelines Sections
- **Best Practices** ⭐⭐ (많은 스킬)
- **Common Mistakes to Avoid** ⭐ (component-refactoring)
- **Common Pitfalls** (fastapi-templates, prompt-engineering-patterns)

### Supporting Sections
- **Resources** ⭐
- **References** / **Authoritative References**
- **Testing** / **Coverage Goals**
- **Required Output** (frontend-code-review)

### Special Sections
- **Design Thinking** (frontend-design)
- **Frontend Aesthetics Guidelines** (frontend-design)
- **Security & Compliance** (senior-prompt-engineer)
- **Performance Targets** (senior-prompt-engineer)

**Emoji Usage**: ⚠️, ✓, ❌ 등 시각적 표시 활용 (frontend-testing, component-refactoring)

## Template Selection Guide

**Based on 8 analyzed skills from skills/local**:

| Skill Purpose | Recommended Pattern | Real Examples (skills/local) | Usage Rate |
|---------------|-------------------|------------------------------|-----------|
| Sequential process | **Workflow-Based** | component-refactoring, frontend-testing, pr-creator, prompt-engineering-patterns, senior-prompt-engineer | ⭐⭐⭐⭐⭐ (5/8) |
| Multiple operations | **Task-Based** | fastapi-templates | ⭐ (1/8) |
| Standards/Specs | **Reference/Guidelines** | frontend-design | ⭐ (1/8) |
| Review/Analysis | **Custom/Mixed** | frontend-code-review | ⭐ (1/8) |

**Pattern Distribution**:
- 62.5% Workflow-Based (가장 인기)
- 12.5% Task-Based
- 12.5% Reference/Guidelines
- 12.5% Custom/Mixed

**Recommendation**: 대부분의 경우 **Workflow-Based** 패턴으로 시작하되, 명확한 순차 프로세스가 없다면 다른 패턴 고려

## Real-World Statistics

skills/local 8개 스킬 분석 결과:

### Document Size
- **평균 단어 수**: ~930 words
- **평균 줄 수**: ~246 lines
- **권장 범위**: 300-1,700 words

### Resource Usage
| Resource Type | Usage Rate | Average Count |
|--------------|------------|---------------|
| references/ | 62.5% (5/8) | 3.6 files |
| scripts/ | 25% (2/8) | 2 files |
| assets/ | 25% (2/8) | 2.5 files |

### Most Referenced Files
**frontend-testing** (6 references):
- async-testing.md
- checklist.md
- common-patterns.md
- domain-components.md
- mocking.md
- [1 more]

### Best Practices Compliance
- ✅ 100% (8/8): YAML frontmatter 포함
- ✅ 100% (8/8): 5k 단어 이하 유지
- ✅ 62.5% (5/8): references/ 활용
- ✅ 25% (2/8): assets/ 활용
- ✅ 25% (2/8): scripts/ 활용

## Notes

- Patterns can be mixed and matched
- Most skills combine multiple patterns
- Choose the pattern that best fits the primary use case
- Don't force a pattern if it doesn't fit naturally
