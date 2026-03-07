---
name: agent-plugin-manager
description: This skill should be used when creating, managing, or working with AI agent plugins. It provides tools and templates for systematically organizing agent usage patterns, decision frameworks, and best practices into reusable plugin packages. Use this skill when defining how to use agents effectively, documenting agent coordination patterns, or establishing agent-related guidelines that can be referenced across projects.
---

# Agent Plugin Manager

## Overview

Manage AI agent plugins through creation, validation, and organization tools. This skill provides a structured approach to documenting agent usage patterns, decision frameworks, and coordination plugins that work across different AI platforms (Claude Code, Cursor, Codex, etc.).

## When to Use

Use this skill when:

- **Creating a new plugin**: Document agent usage patterns, handoff logic, prompting techniques, or coordination approaches
- **Managing existing plugins**: List, validate, update, or organize existing plugin definitions
- **Integrating plugins**: Reference or adapt plugins for use in specific projects
- **Standardizing agent practices**: Establish consistent patterns for agent usage across teams or projects

## Core Capabilities

### 1. Create New Plugins

Generate structured plugin directories through an interactive workflow.

**Workflow:**

1. Invoke this skill and specify intent to create a plugin
2. Answer guided questions about:
   - Plugin name and purpose
   - Target scenarios and use cases
   - Core principles and guidelines
   - Required components (rules, skills, agents)
3. Receive a generated plugin directory with:
   - `README.md` (populated from template)
   - Optional `rules/`, `skills/`, `agents/` directories
   - Structured according to best practices

**Template location:** `assets/templates/plugin-readme-template.md`

**Example interaction:**
```
User: "I want to create a plugin for agent handoff decisions"
Assistant: [Asks guided questions about handoff patterns, triggers, context passing]
Assistant: [Creates plugins/handoff/ with README and rules/]
```

### 2. List Existing Plugins

View all plugins in the configured plugins directory.

**Script:** `scripts/list_plugins.py`

**Usage:**
```bash
python scripts/list_plugins.py
```

**Output:**
- Plugin names
- Directory paths
- README presence status
- Contained components (rules, skills, agents)

**Example:**
```
Found 2 plugin(s):

📁 handoff
   Path: /path/to/plugins/handoff
   README: ✓
   Contains: rules, skills

📁 project-context
   Path: /path/to/plugins/project-context
   README: ✓
   Contains: rules
```

### 3. Validate Plugin Structure

Check if a plugin meets structural requirements.

**Script:** `scripts/validate_plugin.py`

**Usage:**
```bash
python scripts/validate_plugin.py <plugin-name>
```

**Validation checks:**
- Directory exists and is accessible
- Required `README.md` is present
- Optional directories (if present) are properly structured
- Files exist within optional directories

**Example:**
```bash
python scripts/validate_plugin.py handoff

✅ Plugin structure is valid

Directory exists: ✓
README.md: ✓

Optional directories:
  rules/: 3 file(s)
  skills/: 1 file(s)
```

### 4. Apply Plugin to a Repository (Claude Code)

Apply a plugin's `rules/`, `skills/`, and `agents/` files directly into a target project's `.claude/` directory, following Claude Code's standard structure.

**Script:** `scripts/apply_to_repo.py`

**Usage:**
```bash
# List configured repo aliases
python scripts/apply_to_repo.py --list-repos

# Apply to a registered repo alias
python scripts/apply_to_repo.py <plugin-name> --repo <alias>

# Apply to a specific repo path
python scripts/apply_to_repo.py <plugin-name> --repo /path/to/project

# Preview changes without writing files (recommended first)
python scripts/apply_to_repo.py <plugin-name> --repo <alias> --dry-run

# Overwrite existing files
python scripts/apply_to_repo.py <plugin-name> --repo <alias> --overwrite
```

**Repo aliases** are configured in `assets/config.local.json` under the `repos` key:
```json
{
  "repos": {
    "my-project": "/path/to/my-project",
    "other-project": "/path/to/other-project"
  }
}
```

**What it does:**

| Plugin source     | Copies to                          |
|-------------------|------------------------------------|
| `rules/*.md`      | `.claude/rules/`                   |
| `skills/*/`       | `.claude/skills/`                  |
| `agents/*.md`     | `.claude/agents/`                  |
| `hooks/*`         | `.claude/hooks/`                   |

- Creates `.claude/` and subdirectories if they don't exist
- Skips existing files by default (use `--overwrite` to replace)
- `--dry-run` shows what would be copied without making changes

**Example:**
```
🚀 Applying plugin 'karpathy-skills' to: /path/to/my-project

  📁 Created directory: .claude/rules
  ✅ Copied: karpathy-skills.md → .claude/rules/karpathy-skills.md

──────────────────────────────────────────────────
✅ Done!
   Copied:  1 file(s)
   Created: 1 directory
```

**Reference:** See `references/claude-code-structure.md` for details on Claude Code's `.claude/` directory layout.

### 5. Update and Maintain Plugins


Modify existing plugins by:

- Adding new rules to `rules/` directory
- Updating README.md with new examples or guidelines
- Adding skills or agent definitions
- Reorganizing content for clarity

**Best practices:**
- Keep README.md focused on overview and core principles
- Move detailed content to `rules/` files
- Use clear, descriptive file names
- Reference external files from README.md

### 5. Configure Plugin Location

Customize where plugins are stored via configuration files.

**Configuration files:**
- `assets/config.json` - Default configuration (committed to git)
- `assets/config.local.json` - Local overrides (gitignored, takes precedence)

**Default configuration:**
```json
{
  "plugins_path": "./plugins"
}
```

**To customize:**
1. Copy `assets/config.local.json.example` to `assets/config.local.json`
2. Edit `config.local.json` with your local settings
3. Set `plugins_path` to desired location (relative to skill directory)
4. All scripts will prioritize `config.local.json` over `config.json`

**Example custom configuration:**
```json
{
  "plugins_path": "/Users/username/custom-plugins"
}
```

## Plugin Structure Standard

Each plugin follows a consistent structure:

```
plugins/plugin-name/
├── README.md          # Required: Overview, purpose, usage guide
├── rules/             # Optional: Detailed guidelines and decision trees
├── skills/            # Optional: Related skill definitions
└── agents/            # Optional: Agent configurations
```

**Detailed structure guide:** `references/plugin-structure-guide.md`

## Integration Patterns

Plugins serve as **packages** that can be integrated flexibly:

### For AGENTS.md / CLAUDE.md

Copy relevant sections or reference entire files:

```markdown
# Agent Handoff Plugin

See: agent-tools/skills/shared/agent-plugin-manager/plugins/handoff/

Apply the following rules when deciding task delegation:
[Content from rules/when-to-handoff.md]
```

### For Skills

Reference plugin rules within skill instructions:

```markdown
When performing multi-step tasks, follow the handoff plugin:
- Review rules/subagent-selection.md for choosing the right subagent
- Apply context-minimization principles from rules/context-passing.md
```

### For Agents

Include plugin guidelines in agent system prompts or configuration files.

### For Project Documentation

Copy entire plugin directories into project repositories and customize as needed.

## Resources

### scripts/

- **list_plugins.py**: List all plugins with metadata
- **validate_plugin.py**: Validate plugin structure
- **apply_to_repo.py**: Apply a plugin's files to a target repository's `.claude/` directory

Scripts can be executed directly without loading into context.

### references/

- **plugin-structure-guide.md**: Comprehensive guide to plugin organization, best practices, and validation criteria
- **claude-code-structure.md**: Claude Code `.claude/` directory layout and plugin-to-project mapping guide

Load these references when:
- Creating complex plugins
- Unsure about structural decisions
- Applying plugins to Claude Code projects
- Need detailed examples

### assets/

- **templates/plugin-readme-template.md**: Template for creating new plugin README files
- **config.json**: Default configuration (committed to git)
- **config.local.json.example**: Example local configuration
- **config.local.json**: Local overrides (gitignored, create from .example)

Templates are copied and customized during plugin creation. Configuration files control where plugins are stored and how they're structured.

## Example: Creating a Handoff Plugin

**User request:**
> "Help me create a plugin for when to delegate tasks to other agents"

**Process:**

1. **Clarify scope** through questions:
   - What types of tasks should be delegated?
   - What decision criteria matter (complexity, context size, specialization)?
   - Should this include parallel vs sequential execution guidance?

2. **Create structure:**
   ```
   plugins/handoff/
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
   python scripts/validate_plugin.py handoff
   ```

5. **Use in projects:**
   - Reference in AGENTS.md
   - Copy specific rules into project guidelines
   - Adapt for project-specific needs

## Best Practices

1. **Start small**: Create minimal plugins and expand based on real usage
2. **Use templates**: Leverage provided templates for consistency
3. **Validate frequently**: Run validation after structural changes
4. **Keep README focused**: Move details to rules/, skills/, or agents/
5. **Platform-agnostic**: Use AGENTS.md instead of tool-specific names
6. **Concrete examples**: Always include real-world usage scenarios
7. **Version awareness**: Note when plugins are updated or expanded

## Notes

- Plugins are **packages of .claude/ components**, not executable code
- Structure is flexible: not all plugins need rules/, skills/, and agents/
- Configuration allows customizing plugin storage location
- Scripts provide automation for common tasks but aren't required for manual management
