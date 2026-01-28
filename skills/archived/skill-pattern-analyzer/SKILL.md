---
name: skill-pattern-analyzer
description: This skill should be used when analyzing Claude Code skills to extract folder structure, SKILL.md writing patterns, and best practices. Use it to reverse-engineer successful skills and maintain a personal skill template.
---

# Skill Pattern Analyzer

## Overview

This skill analyzes existing Claude Code skills to identify patterns in folder structure, SKILL.md organization, and best practices. It helps create and maintain a personal skill template based on successful patterns observed in popular skills.

## Quick Start

This skill provides two main capabilities:

1. **Analyze Skills**: Examine a skill's structure and extract patterns
2. **Update Template**: Maintain your master skill template based on analysis results

## Task 1: Analyze a Skill

When you want to analyze an existing skill's patterns and structure.

### Usage

To analyze a skill, provide the path to the skill directory:

**User request examples**:
- "code-reviewer 스킬을 분석해줘"
- "pdf-editor 스킬의 구조를 분석하고 패턴을 정리해줘"
- "/Users/username/skills/my-skill 를 분석해서 참고자료로 만들어줘"

### Process

1. **Locate the skill**: Find the skill directory path
2. **Run analysis script**: Execute `scripts/analyze_skill.py` with the skill path
3. **Save results**: Save the analysis to `references/analyzed-skills/{skill-name}_reference.md`
4. **Review findings**: Examine the analysis for notable patterns

### Analysis Output

The analysis includes:
- **Folder Structure**: Directory tree with scripts/, references/, assets/
- **YAML Frontmatter**: How name and description are written
- **Structure Pattern**: Workflow-based, Task-based, Reference/Guidelines, or Capabilities-based
- **Section Structure**: Hierarchical organization of SKILL.md
- **Statistics**: Word count, line count, resource counts
- **Best Practices**: Observed patterns and recommendations

### Example

```bash
python scripts/analyze_skill.py /path/to/skill-name -o references/analyzed-skills/skill-name_reference.md
```

## Task 2: Update Your Skill Template

When you want to incorporate learned patterns into your master template.

### Usage

After analyzing one or more skills, update the master template to reflect new insights.

**User request examples**:
- "code-reviewer의 섹션 구조를 내 템플릿에 반영해줘"
- "최근 분석한 3개 스킬의 공통 패턴을 템플릿에 업데이트해줘"
- "Workflow-Based 패턴을 템플릿에 추가해줘"

### Process

1. **Review analyzed skills**: Read analysis files from `references/analyzed-skills/`
2. **Identify patterns**: Look for common structures, naming conventions, best practices
3. **Update template**: Modify `references/my-skill-template.md` to incorporate new patterns
4. **Document changes**: Note what was updated and why

### Template Sections

The master template (`references/my-skill-template.md`) includes:
- **Structure Patterns**: Examples of different organizational approaches
- **Frontmatter Guidelines**: Name and description conventions
- **Writing Style**: Voice, tone, and formatting rules
- **Best Practices**: Progressive disclosure, resource organization
- **Common Section Names**: Frequently used section titles

### Update Criteria

Update the template when:
- A more effective structure or writing style is discovered
- Common patterns are identified across multiple skills
- Better organization methods are found
- User explicitly requests pattern incorporation

## Resources

### scripts/

- **analyze_skill.py**: Python script that analyzes a skill directory and generates a structured markdown report

**Usage**:
```bash
python scripts/analyze_skill.py <skill_path> [-o <output_file>]
```

**Arguments**:
- `skill_path`: Path to the skill directory to analyze
- `-o, --output`: (Optional) Output file path for the analysis report

### references/

- **analysis-guidelines.md**: Comprehensive checklist and guidelines for analyzing skills
  - Analysis checklist (folder structure, SKILL.md content, writing style)
  - Best practices identification criteria
  - Template update criteria

- **my-skill-template.md**: Master template that evolves based on analyzed patterns
  - SKILL.md structure templates for different patterns
  - YAML frontmatter guidelines
  - Writing style guidelines
  - Best practices and common section names

- **analyzed-skills/**: Directory containing analysis reports for individual skills
  - Each file named `{skill-name}_reference.md`
  - Contains structured analysis of a specific skill

For detailed analysis guidelines, load `references/analysis-guidelines.md` into context.
