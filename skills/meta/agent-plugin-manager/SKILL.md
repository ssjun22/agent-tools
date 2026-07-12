---
name: agent-plugin-manager
description: This skill should be used when creating, managing, or working with AI agent plugins. Plugins are dependency manifests (plugin.json) that declare which skills, agents, rules, and hooks to install together. Use this skill to create new plugins, list/validate existing ones, or apply plugins to target repositories via symlinks.
argument-hint: <plugin-name> <repo-alias>
---

# Agent Plugin Manager

## Command Arguments

슬래시 커맨드로 호출 시 인자를 전달할 수 있습니다.

### Apply (기본 동작)

```
/agent-plugin-manager <plugin-name> <repo-alias>
```

- `$0` — 플러그인명 (예: `karpathy-coding-guide`)
- `$1` — 대상 레포지토리 alias (예: `my-app`, `my-service`)

인자가 2개 모두 전달되면 validate → dry-run → apply 워크플로우를 바로 실행합니다.
인자가 없거나 부족하면 대화형으로 확인합니다.

**예시:**
- `/agent-plugin-manager karpathy-coding-guide my-app` — karpathy-coding-guide 플러그인을 my-app에 적용

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
| `skills`       | `skills/{path}/` |
| `agents`       | `agents/{name}.md` |
| `rules`        | `rules/{name}.md` |
| `hooks`        | `hooks/{name}` |

## plugin.json Spec

```json
{
  "name": "plugin-name",
  "description": "Plugin purpose description",
  "depends": {
    "skills": ["dev/code-reviewer", "dev/git-commit-helper"],
    "agents": ["code-reviewer", "researcher"],
    "rules": ["karpathy-skills"],
    "hooks": []
  }
}
```

- `depends.skills`: paths relative to `skills/`
- `depends.agents`: filenames in `agents/` (without `.md`)
- `depends.rules`: filenames in `rules/` (without `.md`)
- `depends.hooks`: filenames in `hooks/`

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
Found 1 plugin(s):

📁 karpathy-coding-guide
   Path: /path/to/plugins/karpathy-coding-guide
   README: ✓  plugin.json: ✓  settings: ✗
   Depends: 1 skills, 1 rules
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

Dependencies (2 total):
  skills/dev/karpathy-guidelines: ✓ (skills/dev/karpathy-guidelines/)
  rules/karpathy-skills: ✓ (rules/karpathy-skills.md)
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
| `skills/{path}/` | `.claude/skills/{basename}/` |
| `agents/{name}.md` | `.claude/agents/{name}.md` |
| `rules/{name}.md` | `.claude/rules/{name}.md` |
| `hooks/{name}` | `.claude/hooks/{name}` |

**Example output:**
```
🚀 Applying plugin 'karpathy-coding-guide' to: /path/to/project

📋 Resolving dependencies...
  ✅ skills/karpathy-guidelines — already exists, skip
  🔗 rules/karpathy-skills → symlinked

──────────────────────────────────────────────────
✅ Done!
   Linked:  1 file(s)
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
