# Plugin Structure Guide

This document defines the standard structure for AI agent plugins.

## Directory Structure

Each plugin should be organized as a self-contained directory:

```
plugins/
└── plugin-name/
    ├── README.md          # Required: Plugin overview and usage
    ├── rules/             # Optional: Core rules and guidelines
    ├── skills/            # Optional: Related skill definitions
    └── agents/            # Optional: Agent configurations
```

## Required Components

### README.md

Every plugin MUST include a `README.md` file that contains:

1. **Plugin Name and Purpose**
   - Clear, descriptive title
   - 2-3 sentence overview of what this plugin addresses

2. **When to Use**
   - Specific scenarios where this plugin applies
   - Context or triggers for using this plugin

3. **Core Principles**
   - Key concepts or decision-making frameworks
   - High-level guidance

4. **Usage Examples**
   - Concrete examples of applying the plugin
   - Before/after comparisons (if applicable)

5. **Integration Guide**
   - How to incorporate this plugin into projects
   - References to which files to use (rules, skills, agents)

## Optional Components

### rules/

Contains detailed guidelines, decision trees, and specific rules.

**When to include:**
- Plugin requires specific, detailed procedures
- Multiple related guidelines that should be organized separately
- Content is reference material for AGENTS.md or other contexts

**Structure:**
- One rule per file (e.g., `handoff-decision-tree.md`)
- Or organized by category (e.g., `parallel-execution.md`, `context-passing.md`)

**Example:**
```
rules/
├── when-to-handoff.md
├── subagent-selection.md
└── context-minimization.md
```

### skills/

Contains skill definitions that implement or support the plugin.

**When to include:**
- Plugin can be partially automated through skills
- Specific workflows benefit from dedicated skill files

**Structure:**
- Each skill follows standard SKILL.md format with YAML frontmatter
- Skills can reference plugin rules in their implementation

**Example:**
```
skills/
└── handoff-helper/
    └── SKILL.md
```

### agents/

Contains agent configurations or prompts that embody the plugin.

**When to include:**
- Plugin defines a specialized agent persona
- Plugin includes agent-specific instructions or context

**Structure:**
- Agent definition files (.md)
- Configuration or system prompts

**Example:**
```
agents/
├── code-reviewer.md
└── architecture-planner.md
```

## Plugin Metadata (Optional)

Plugins may include a `.plugin-meta.json` file for additional metadata:

```json
{
  "name": "handoff-plugin",
  "version": "1.0.0",
  "author": "Your Name",
  "tags": ["task-delegation", "agent-coordination"],
  "ai_platforms": ["claude-code", "codex", "cursor"],
  "created": "2024-01-30",
  "updated": "2024-01-30"
}
```

## Best Practices

1. **Keep README.md focused**: Core plugin only, detailed rules go in `rules/`
2. **Use relative references**: Link to other files within the plugin using relative paths
3. **Platform-agnostic**: Use AGENTS.md instead of CLAUDE.md for broader compatibility
4. **Progressive disclosure**: Start with overview, then link to details
5. **Concrete examples**: Always include real-world usage examples
6. **Clear integration path**: Explain exactly how to use the plugin in projects

## Validation

Use `validate_plugin.py` to check if a plugin meets structural requirements:

```bash
python scripts/validate_plugin.py <plugin-name>
```

Required checks:
- ✅ Plugin directory exists
- ✅ README.md is present
- ✅ Optional directories (if present) contain files

## Examples

See existing plugins for reference:
- `handoff-plugin/` - Agent task delegation patterns
- `prompting-plugin/` - Effective prompt engineering techniques
- `context-plugin/` - Context window management approaches
