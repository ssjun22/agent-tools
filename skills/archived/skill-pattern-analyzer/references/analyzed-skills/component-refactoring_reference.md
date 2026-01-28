# component-refactoring - Skill Analysis

> Analyzed on: 2026-01-18

## Folder Structure

```
component-refactoring/
├── SKILL.md
├── references/
│   ├── complexity-patterns.md
│   ├── component-splitting.md
│   ├── hook-extraction.md
```

## YAML Frontmatter

```yaml
name: component-refactoring
description: Refactor high-complexity React components in Dify frontend. Use when `pnpm analyze-component --json` shows complexity > 50 or lineCount > 300, when the user asks for code splitting, hook extraction, or complexity reduction, or when `pnpm analyze-component` warns to refactor before testing; avoid for simple/well-structured components, third-party wrappers, or when the user explicitly wants testing without refactoring.
```

## Structure Pattern

**Detected Pattern**: Workflow-Based

## Section Structure

- Quick Reference (Level 2)
  - Commands (run from `web/`) (Level 3)
  - Complexity Analysis (Level 3)
  - Complexity Score Interpretation (Level 3)
- Core Refactoring Patterns (Level 2)
  - Pattern 1: Extract Custom Hooks (Level 3)
  - Pattern 2: Extract Sub-Components (Level 3)
  - Pattern 3: Simplify Conditional Logic (Level 3)
  - Pattern 4: Extract API/Data Logic (Level 3)
  - Pattern 5: Extract Modal/Dialog Management (Level 3)
  - Pattern 6: Extract Form Logic (Level 3)
- Dify-Specific Refactoring Guidelines (Level 2)
  - 1. Context Provider Extraction (Level 3)
  - 2. Workflow Node Components (Level 3)
  - 3. Configuration Components (Level 3)
  - 4. Tool/Plugin Components (Level 3)
- Refactoring Workflow (Level 2)
  - Step 1: Generate Refactoring Prompt (Level 3)
  - Step 2: Analyze Details (Level 3)
  - Step 3: Plan (Level 3)
  - Step 4: Execute Incrementally (Level 3)
  - Step 5: Verify (Level 3)
- Common Mistakes to Avoid (Level 2)
  - ❌ Over-Engineering (Level 3)
  - ❌ Breaking Existing Patterns (Level 3)
  - ❌ Premature Abstraction (Level 3)
- References (Level 2)
  - Dify Codebase Examples (Level 3)
  - Related Skills (Level 3)

## Statistics

- **Word Count**: 1714
- **Line Count**: 483
- **Scripts**: 0
- **References**: 3
- **Assets**: 0

## Best Practices Observations

- ✓ Separates detailed documentation into references
- ✓ Keeps SKILL.md concise (< 5k words)
- ✓ Includes required frontmatter (name, description)

