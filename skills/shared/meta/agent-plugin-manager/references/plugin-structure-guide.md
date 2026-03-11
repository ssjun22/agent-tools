# Plugin Structure Guide

Plugins are lightweight packages that declare dependencies on existing skills, agents, rules, and hooks. They do not contain these resources directly — instead, they reference shared resources via `plugin.json`.

## Directory Structure

```
plugins/
└── plugin-name/
    ├── plugin.json      # Required: dependency declarations
    ├── README.md        # Required: overview and usage
    ├── settings.json    # Optional: Claude Code settings to merge
    └── assets/          # Optional: templates, configs, etc.
```

## plugin.json

The manifest file declares what the plugin depends on. All dependency paths are resolved from the `agent-tools` root.

```json
{
  "name": "handoff-plugin",
  "description": "Agent task delegation and handoff patterns",
  "depends": {
    "skills": [
      "dev/code-reviewer",
      "meta/skill-critic"
    ],
    "agents": [
      "handoff-creator",
      "code-review-agent"
    ],
    "rules": [
      "handoff",
      "context-minimization"
    ],
    "hooks": [
      "load-handoffs"
    ]
  }
}
```

### Dependency Resolution

| Field | Resolved From | Example Value | Resolves To |
|-------|--------------|---------------|-------------|
| `depends.skills` | `skills/shared/` | `"dev/code-reviewer"` | `skills/shared/dev/code-reviewer/` |
| `depends.agents` | `agents/shared/` | `"handoff-creator"` | `agents/shared/handoff-creator.md` |
| `depends.rules` | `rules/shared/` | `"handoff"` | `rules/shared/handoff.md` |
| `depends.hooks` | `hooks/shared/` | `"load-handoffs"` | `hooks/shared/load-handoffs` |

## README.md

Every plugin must include a `README.md` with:

1. **Purpose** — what the plugin does (2-3 sentences)
2. **When to Use** — scenarios and triggers
3. **Dependencies** — summary of what gets installed
4. **Usage** — how to apply and use the plugin

## settings.json (Optional)

Contains Claude Code settings to merge into the target project's `.claude/settings.json`. Only new keys are added; existing settings are preserved.

## Applying a Plugin to a Project

When a plugin is applied to a target project:

1. **Resolve dependencies** — each entry in `depends` is located in the corresponding `agent-tools` root directory.
2. **Symlink resources** — resolved files/directories are symlinked into the target project's `.claude/` (e.g., skills go to `.claude/skills/`, agents to `.claude/agents/`).
3. **Skip existing** — if a resource already exists at the target path, it is skipped (no overwrite).
4. **Merge settings** — if `settings.json` exists, its contents are merged into the target `.claude/settings.json`.

## Best Practices

1. **No embedded resources** — never put skills, agents, rules, or hooks inside the plugin directory. Declare them as dependencies.
2. **Keep it small** — a plugin is a manifest plus documentation, not a monolith.
3. **Use assets/ sparingly** — only for plugin-specific templates or configs that don't belong in shared resources.
4. **Descriptive README** — the README is the primary user-facing documentation.
