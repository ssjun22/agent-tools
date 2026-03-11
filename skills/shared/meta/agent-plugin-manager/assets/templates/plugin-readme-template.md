# [Plugin Name]

## Overview

[2-3 sentences describing what this plugin addresses and why it's valuable]

## Purpose

[Explain the specific problem or challenge this plugin solves]

## When to Use

This plugin is applicable when:

- [Scenario 1]
- [Scenario 2]
- [Scenario 3]

## Core Principles

### 1. [Principle Name]

[Description of the first core principle]

### 2. [Principle Name]

[Description of the second core principle]

### 3. [Principle Name]

[Description of the third core principle]

## Dependencies

This plugin declares its dependencies in `plugin.json`. The manifest specifies which rules, skills, agents, hooks, and settings the plugin requires from the central repository.

```json
{
  "name": "[plugin-name]",
  "description": "[Brief description]",
  "depends": {
    "skills": ["[category/skill-name]"],
    "agents": ["[agent-name]"],
    "rules": ["[rule-name]"],
    "hooks": ["[hook-name]"]
  }
}
```

See this plugin's [`plugin.json`](../plugin.json) for the full dependency list.

## Usage Examples

### Example 1: [Scenario]

**Context**: [Describe the situation]

**Application**: [Show how to apply the plugin]

**Result**: [What outcome to expect]

### Example 2: [Scenario]

**Context**: [Describe the situation]

**Application**: [Show how to apply the plugin]

**Result**: [What outcome to expect]

## Integration Guide

Apply this plugin to a target project using `apply_to_repo.py`:

```bash
# Preview first (recommended)
python3 scripts/apply_to_repo.py [plugin-name] --repo /path/to/project --dry-run

# Apply (symlink by default)
python3 scripts/apply_to_repo.py [plugin-name] --repo /path/to/project
```

The script reads `plugin.json`, resolves all dependencies from the central repository, and symlinks the required components into the target project's `.claude/` directory.

**Options**:

- `--dry-run`: Preview which files would be applied without making changes
- `--copy`: Copy files instead of creating symlinks
- `--overwrite`: Overwrite existing files (default: skip)

## Key Guidelines

1. [Guideline 1]
2. [Guideline 2]
3. [Guideline 3]
4. [Guideline 4]

## References

- [Link to relevant skills, agents, or rules in the central repository]
- [External resources or documentation]

## Version History

- **v1.0.0** - Initial plugin creation ([Date])

---

**Author**: [Your Name]
**Last Updated**: [Date]
