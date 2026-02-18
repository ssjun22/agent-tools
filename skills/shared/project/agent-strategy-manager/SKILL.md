---
name: agent-strategy-manager
description: This skill should be used when creating, managing, or working with AI agent strategies. It provides tools and templates for systematically organizing agent usage patterns, decision frameworks, and best practices into reusable strategy documents. Use this skill when defining how to use agents effectively, documenting agent coordination patterns, or establishing agent-related guidelines that can be referenced across projects.
---

# Agent Strategy Manager

## Overview

Manage AI agent strategies through creation, validation, and organization tools. This skill provides a structured approach to documenting agent usage patterns, decision frameworks, and coordination strategies that work across different AI platforms (Claude Code, Cursor, Codex, etc.).

## When to Use

Use this skill when:

- **Creating a new strategy**: Document agent usage patterns, handoff logic, prompting techniques, or coordination approaches
- **Managing existing strategies**: List, validate, update, or organize existing strategy definitions
- **Integrating strategies**: Reference or adapt strategies for use in specific projects
- **Standardizing agent practices**: Establish consistent patterns for agent usage across teams or projects

## Core Capabilities

### 1. Create New Strategies

Generate structured strategy directories through an interactive workflow.

**Workflow:**

1. Invoke this skill and specify intent to create a strategy
2. Answer guided questions about:
   - Strategy name and purpose
   - Target scenarios and use cases
   - Core principles and guidelines
   - Required components (rules, skills, agents)
3. Receive a generated strategy directory with:
   - `README.md` (populated from template)
   - Optional `rules/`, `skills/`, `agents/` directories
   - Structured according to best practices

**Template location:** `assets/templates/strategy-readme-template.md`

**Example interaction:**
```
User: "I want to create a strategy for agent handoff decisions"
Assistant: [Asks guided questions about handoff patterns, triggers, context passing]
Assistant: [Creates strategies/handoff-strategy/ with README and rules/]
```

### 2. List Existing Strategies

View all strategies in the configured strategies directory.

**Script:** `scripts/list_strategies.py`

**Usage:**
```bash
python scripts/list_strategies.py
```

**Output:**
- Strategy names
- Directory paths
- README presence status
- Contained components (rules, skills, agents)

**Example:**
```
Found 2 strategy/strategies:

📁 handoff-strategy
   Path: /path/to/strategies/handoff-strategy
   README: ✓
   Contains: rules, skills

📁 prompting-strategy
   Path: /path/to/strategies/prompting-strategy
   README: ✓
   Contains: rules
```

### 3. Validate Strategy Structure

Check if a strategy meets structural requirements.

**Script:** `scripts/validate_strategy.py`

**Usage:**
```bash
python scripts/validate_strategy.py <strategy-name>
```

**Validation checks:**
- Directory exists and is accessible
- Required `README.md` is present
- Optional directories (if present) are properly structured
- Files exist within optional directories

**Example:**
```bash
python scripts/validate_strategy.py handoff-strategy

✅ Strategy structure is valid

Directory exists: ✓
README.md: ✓

Optional directories:
  rules/: 3 file(s)
  skills/: 1 file(s)
```

### 4. Update and Maintain Strategies

Modify existing strategies by:

- Adding new rules to `rules/` directory
- Updating README.md with new examples or guidelines
- Adding skills or agent definitions
- Reorganizing content for clarity

**Best practices:**
- Keep README.md focused on overview and core principles
- Move detailed content to `rules/` files
- Use clear, descriptive file names
- Reference external files from README.md

### 5. Configure Strategy Location

Customize where strategies are stored via configuration files.

**Configuration files:**
- `assets/config.json` - Default configuration (committed to git)
- `assets/config.local.json` - Local overrides (gitignored, takes precedence)

**Default configuration:**
```json
{
  "strategies_path": "./strategies"
}
```

**To customize:**
1. Copy `assets/config.local.json.example` to `assets/config.local.json`
2. Edit `config.local.json` with your local settings
3. Set `strategies_path` to desired location (relative to skill directory)
4. All scripts will prioritize `config.local.json` over `config.json`

**Example custom configuration:**
```json
{
  "strategies_path": "/Users/username/custom-strategies"
}
```

## Strategy Structure Standard

Each strategy follows a consistent structure:

```
strategies/strategy-name/
├── README.md          # Required: Overview, purpose, usage guide
├── rules/             # Optional: Detailed guidelines and decision trees
├── skills/            # Optional: Related skill definitions
└── agents/            # Optional: Agent configurations
```

**Detailed structure guide:** `references/strategy-structure-guide.md`

## Integration Patterns

Strategies serve as **reference material** that can be integrated flexibly:

### For AGENTS.md / CLAUDE.md

Copy relevant sections or reference entire files:

```markdown
# Agent Handoff Strategy

See: agent-tools/skills/shared/agent-strategy-manager/strategies/handoff-strategy/

Apply the following rules when deciding task delegation:
[Content from rules/when-to-handoff.md]
```

### For Skills

Reference strategy rules within skill instructions:

```markdown
When performing multi-step tasks, follow the handoff strategy:
- Review rules/subagent-selection.md for choosing the right subagent
- Apply context-minimization principles from rules/context-passing.md
```

### For Agents

Include strategy guidelines in agent system prompts or configuration files.

### For Project Documentation

Copy entire strategy directories into project repositories and customize as needed.

## Resources

### scripts/

- **list_strategies.py**: List all strategies with metadata
- **validate_strategy.py**: Validate strategy structure

Scripts can be executed directly without loading into context.

### references/

- **strategy-structure-guide.md**: Comprehensive guide to strategy organization, best practices, and validation criteria

Load this reference when:
- Creating complex strategies
- Unsure about structural decisions
- Need detailed examples

### assets/

- **templates/strategy-readme-template.md**: Template for creating new strategy README files
- **config.json**: Default configuration (committed to git)
- **config.local.json.example**: Example local configuration
- **config.local.json**: Local overrides (gitignored, create from .example)

Templates are copied and customized during strategy creation. Configuration files control where strategies are stored and how they're structured.

## Example: Creating a Handoff Strategy

**User request:**
> "Help me create a strategy for when to delegate tasks to other agents"

**Process:**

1. **Clarify scope** through questions:
   - What types of tasks should be delegated?
   - What decision criteria matter (complexity, context size, specialization)?
   - Should this include parallel vs sequential execution guidance?

2. **Create structure:**
   ```
   strategies/handoff-strategy/
   ├── README.md (from template)
   └── rules/
       ├── when-to-handoff.md
       ├── subagent-selection.md
       └── context-passing.md
   ```

3. **Populate content:**
   - README: Overview of delegation principles
   - rules/when-to-handoff.md: Decision tree for delegation
   - rules/subagent-selection.md: Criteria for choosing subagents
   - rules/context-passing.md: How to provide context efficiently

4. **Validate:**
   ```bash
   python scripts/validate_strategy.py handoff-strategy
   ```

5. **Use in projects:**
   - Reference in AGENTS.md
   - Copy specific rules into project guidelines
   - Adapt for project-specific needs

## Best Practices

1. **Start small**: Create minimal strategies and expand based on real usage
2. **Use templates**: Leverage provided templates for consistency
3. **Validate frequently**: Run validation after structural changes
4. **Keep README focused**: Move details to rules/, skills/, or agents/
5. **Platform-agnostic**: Use AGENTS.md instead of tool-specific names
6. **Concrete examples**: Always include real-world usage scenarios
7. **Version awareness**: Note when strategies are updated or expanded

## Notes

- Strategies are **reference material**, not executable code
- Structure is flexible: not all strategies need rules/, skills/, and agents/
- Configuration allows customizing strategy storage location
- Scripts provide automation for common tasks but aren't required for manual management
