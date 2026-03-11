---
name: agent-plugin-manager
description: This skill should be used when creating, managing, or working with AI agent plugins. Plugins are dependency manifests (plugin.json) that declare which skills, agents, rules, and hooks to install together. Use this skill to create new plugins, list/validate existing ones, or apply plugins to target repositories via symlinks.
---

# Agent Plugin Manager

## Overview

Manage AI agent plugins — dependency manifests that bundle skills, agents, rules, and hooks into installable packages. Plugins don't contain files directly; they declare dependencies in `plugin.json`, and the apply script resolves them from `agent-tools` source directories.

## When to Use

- **Creating a new plugin**: Define which skills/agents/rules/hooks belong together
- **Applying a plugin**: Install a plugin's dependencies into a target project's `.claude/`
- **Managing plugins**: List, validate, or update existing plugins
- **Checking dependencies**: Verify all declared dependencies resolve to actual files

## Plugin Structure

```
plugins/plugin-name/
├── plugin.json        # Required: Dependency manifest
├── README.md          # Required: Overview and usage guide
├── settings.json      # Optional: Claude Code settings to merge
└── assets/            # Optional: Templates, configs, examples
```

Plugins do NOT contain `rules/`, `skills/`, `agents/`, or `hooks/` directories. Those files live in the central `agent-tools` directories:

| Dependency type | Source location       |
|----------------|-----------------------|
| `skills`       | `skills/shared/{path}/` |
| `agents`       | `agents/shared/{name}.md` |
| `rules`        | `rules/shared/{name}.md` |
| `hooks`        | `hooks/shared/{name}` |

## plugin.json Spec

```json
{
  "name": "plugin-name",
  "description": "Plugin purpose description",
  "depends": {
    "skills": ["dev/code-reviewer", "pipeline/workflow"],
    "agents": ["interviewer", "spec-builder"],
    "rules": ["handoff", "openspec-sdd"],
    "hooks": ["load-context", "save-context"]
  }
}
```

- `depends.skills`: paths relative to `skills/shared/`
- `depends.agents`: filenames in `agents/shared/` (without `.md`)
- `depends.rules`: filenames in `rules/shared/` (without `.md`)
- `depends.hooks`: filenames in `hooks/shared/`

## Core Capabilities

### 1. Create New Plugins

Generate a plugin through an interactive workflow.

**Workflow:**

1. Invoke this skill and specify intent to create a plugin
2. Answer guided questions about:
   - Plugin name and purpose
   - Which skills, agents, rules, hooks to include
   - Whether custom settings.json is needed
3. Receive a generated plugin directory with:
   - `plugin.json` (dependency manifest)
   - `README.md` (from template)
   - `settings.json` (if needed)

**Template location:** `assets/templates/plugin-readme-template.md`

### 2. List Existing Plugins

**Script:** `scripts/list_plugins.py`

```bash
python3 scripts/list_plugins.py
```

**Example output:**
```
Found 4 plugin(s):

📁 handoff
   Path: /path/to/plugins/handoff
   README: ✓  plugin.json: ✓  settings: ✗
   Depends: 1 agents, 1 rules, 1 hooks

📁 project-context
   Path: /path/to/plugins/project-context
   README: ✓  plugin.json: ✓  settings: ✓
   Depends: 1 skills, 1 rules, 2 hooks
```

### 3. Validate Plugin

**Script:** `scripts/validate_plugin.py`

```bash
python3 scripts/validate_plugin.py <plugin-name>
```

**Checks:**
- `plugin.json` exists, is valid JSON, has required fields (`name`, `description`, `depends`)
- `depends` keys are valid (`skills`, `agents`, `rules`, `hooks`)
- Each dependency resolves to an actual file/directory in `agent-tools`
- `README.md` exists
- `settings.json` is valid JSON (if present)

**Example output:**
```
✅ Plugin structure is valid

Directory exists: ✓
plugin.json: ✓
README.md: ✓
settings.json: — (not present)

Dependencies (3 total):
  agents/handoff-creator: ✓ (agents/shared/handoff-creator.md)
  rules/handoff: ✓ (rules/shared/handoff.md)
  hooks/load-handoffs: ✓ (hooks/shared/load-handoffs)
```

### 4. Apply Plugin to Repository

**Script:** `scripts/apply_to_repo.py`

```bash
# Preview first (recommended)
python3 scripts/apply_to_repo.py <plugin-name> --repo <alias-or-path> --dry-run

# Apply with symlinks (default)
python3 scripts/apply_to_repo.py <plugin-name> --repo <alias-or-path>

# Copy instead of symlink
python3 scripts/apply_to_repo.py <plugin-name> --repo <alias-or-path> --copy

# Overwrite existing
python3 scripts/apply_to_repo.py <plugin-name> --repo <alias-or-path> --overwrite

# List repo aliases
python3 scripts/apply_to_repo.py --list-repos
```

**How it works:**

1. Reads `plugin.json` from the plugin directory
2. For each dependency, checks if it already exists in target `.claude/`
3. Missing items are symlinked from `agent-tools` source directories
4. `settings.json` is deep-merged into target `.claude/settings.json`

**Dependency → Target mapping:**

| Source | Target |
|--------|--------|
| `skills/shared/{path}/` | `.claude/skills/{basename}/` |
| `agents/shared/{name}.md` | `.claude/agents/{name}.md` |
| `rules/shared/{name}.md` | `.claude/rules/{name}.md` |
| `hooks/shared/{name}` | `.claude/hooks/{name}` |

**Example output:**
```
🚀 Applying plugin 'handoff' to: /path/to/project

📋 Resolving dependencies...
  ✅ agents/handoff-creator — already exists, skip
  🔗 rules/handoff → symlinked
  🔗 hooks/load-handoffs → symlinked

──────────────────────────────────────────────────
✅ Done!
   Linked:  2 file(s)
   Skipped: 1 file(s)
```

**Repo aliases** are configured in `assets/config.local.json`:
```json
{
  "repos": {
    "my-project": "/path/to/my-project"
  }
}
```

### 5. Configure Plugin Location

**Configuration files:**
- `assets/config.json` — Default configuration (committed to git)
- `assets/config.local.json` — Local overrides (gitignored, takes precedence)

## Resources

### scripts/

- **list_plugins.py**: List all plugins with dependency counts
- **validate_plugin.py**: Validate plugin structure and dependency resolution
- **apply_to_repo.py**: Apply plugin dependencies to a target repository

Scripts can be executed directly without loading into context.

### references/

- **plugin-structure-guide.md**: Plugin structure standard and dependency resolution
- **claude-code-structure.md**: Claude Code `.claude/` directory layout

### assets/

- **templates/plugin-readme-template.md**: Template for new plugin README files
- **config.json**: Default configuration
- **config.local.json.example**: Example local configuration

## Best Practices

1. **Dependencies over duplication**: Never copy files into plugins — declare them in `depends`
2. **Validate after changes**: Run `validate_plugin.py` to check dependency resolution
3. **Dry-run first**: Always preview with `--dry-run` before applying
4. **Symlink by default**: Symlinks keep files in sync with `agent-tools` updates
5. **Small, focused plugins**: Each plugin should serve one clear purpose
