# Strategy Structure Guide

This document defines the standard structure for AI agent strategies.

## Directory Structure

Each strategy should be organized as a self-contained directory:

```
strategies/
└── strategy-name/
    ├── README.md          # Required: Strategy overview and usage
    ├── rules/             # Optional: Core rules and guidelines
    ├── skills/            # Optional: Related skill definitions
    └── agents/            # Optional: Agent configurations
```

## Required Components

### README.md

Every strategy MUST include a `README.md` file that contains:

1. **Strategy Name and Purpose**
   - Clear, descriptive title
   - 2-3 sentence overview of what this strategy addresses

2. **When to Use**
   - Specific scenarios where this strategy applies
   - Context or triggers for using this strategy

3. **Core Principles**
   - Key concepts or decision-making frameworks
   - High-level guidance

4. **Usage Examples**
   - Concrete examples of applying the strategy
   - Before/after comparisons (if applicable)

5. **Integration Guide**
   - How to incorporate this strategy into projects
   - References to which files to use (rules, skills, agents)

## Optional Components

### rules/

Contains detailed guidelines, decision trees, and specific rules.

**When to include:**
- Strategy requires specific, detailed procedures
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

Contains skill definitions that implement or support the strategy.

**When to include:**
- Strategy can be partially automated through skills
- Specific workflows benefit from dedicated skill files

**Structure:**
- Each skill follows standard SKILL.md format with YAML frontmatter
- Skills can reference strategy rules in their implementation

**Example:**
```
skills/
└── handoff-helper/
    └── SKILL.md
```

### agents/

Contains agent configurations or prompts that embody the strategy.

**When to include:**
- Strategy defines a specialized agent persona
- Strategy includes agent-specific instructions or context

**Structure:**
- Agent definition files (.md)
- Configuration or system prompts

**Example:**
```
agents/
├── code-reviewer.md
└── architecture-planner.md
```

## Strategy Metadata (Optional)

Strategies may include a `.strategy-meta.json` file for additional metadata:

```json
{
  "name": "handoff-strategy",
  "version": "1.0.0",
  "author": "Your Name",
  "tags": ["task-delegation", "agent-coordination"],
  "ai_platforms": ["claude-code", "codex", "cursor"],
  "created": "2024-01-30",
  "updated": "2024-01-30"
}
```

## Best Practices

1. **Keep README.md focused**: Core strategy only, detailed rules go in `rules/`
2. **Use relative references**: Link to other files within the strategy using relative paths
3. **Platform-agnostic**: Use AGENTS.md instead of CLAUDE.md for broader compatibility
4. **Progressive disclosure**: Start with overview, then link to details
5. **Concrete examples**: Always include real-world usage examples
6. **Clear integration path**: Explain exactly how to use the strategy in projects

## Validation

Use `validate_strategy.py` to check if a strategy meets structural requirements:

```bash
python scripts/validate_strategy.py <strategy-name>
```

Required checks:
- ✅ Strategy directory exists
- ✅ README.md is present
- ✅ Optional directories (if present) contain files

## Examples

See existing strategies for reference:
- `handoff-strategy/` - Agent task delegation patterns
- `prompting-strategy/` - Effective prompt engineering techniques
- `context-strategy/` - Context window management approaches
