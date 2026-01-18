# My Skill Template

> Last Updated: 2026-01-18
> Version: 1.0

이 템플릿은 분석한 스킬들의 패턴을 반영한 마스터 템플릿입니다.

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

**When to use**: 명확한 단계별 절차가 있는 경우

**Structure**:
```markdown
## Workflow Decision Tree

[Simple decision tree or flowchart]

## Step 1: [First Step Name]

[Instructions for step 1]

## Step 2: [Second Step Name]

[Instructions for step 2]

## Step 3: [Final Step Name]

[Instructions for step 3]
```

**Example Skills**: DOCX skill, PDF skill

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

- **Voice**: Third-person ("This skill should be used when...")
- **Content**:
  1. When to use (specific scenarios, file types, tasks)
  2. What it does (brief functionality description)
- **Length**: 1-3 sentences
- **Examples**:
  - ✓ "This skill should be used when working with PDF files to merge, split, extract text, or fill form fields. It provides Python scripts for common PDF operations."
  - ✓ "This skill should be used when analyzing Claude Code skills to extract folder structure and SKILL.md writing patterns."
  - ✗ "Use this skill for PDFs" (too vague, second-person)
  - ✗ "A comprehensive PDF manipulation toolkit with advanced features..." (too verbose, not scenario-focused)

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

1. **Keep SKILL.md concise** (< 5k words)
2. **Move detailed docs to references/**
   - API documentation
   - Database schemas
   - Comprehensive guides
3. **Use scripts for reusable code**
   - Repeatedly rewritten code
   - Deterministic operations

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

Based on analysis of popular skills:

- **Overview** / **Introduction**
- **Quick Start**
- **Workflow** / **Usage**
- **Core Capabilities** / **Features**
- **Resources** / **Bundled Resources**
- **Examples** / **Usage Examples**
- **Guidelines** / **Best Practices**

## Template Selection Guide

| Skill Purpose | Recommended Pattern | Example |
|---------------|-------------------|---------|
| Sequential process | Workflow-Based | Document editing, Data pipeline |
| Multiple operations | Task-Based | File manipulation, API client |
| Standards/Specs | Reference/Guidelines | Brand guide, Coding standards |
| Integrated system | Capabilities-Based | Product management, Analytics |

## Notes

- Patterns can be mixed and matched
- Most skills combine multiple patterns
- Choose the pattern that best fits the primary use case
- Don't force a pattern if it doesn't fit naturally
