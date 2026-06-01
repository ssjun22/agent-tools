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
      "meta/skill-creator"
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
| `depends.skills` | `skills/` | `"dev/code-reviewer"` | `skills/dev/code-reviewer/` |
| `depends.agents` | `agents/` | `"handoff-creator"` | `agents/handoff-creator.md` |
| `depends.rules` | `rules/` | `"handoff"` | `rules/handoff.md` |
| `depends.hooks` | `hooks/` | `"load-handoffs"` | `hooks/load-handoffs` |

## README.md

Every plugin must include a `README.md` with:

1. **Purpose** — what the plugin does (2-3 sentences)
2. **When to Use** — scenarios and triggers
3. **Dependencies** — summary of what gets installed
4. **Usage** — how to apply and use the plugin

## settings.json (Optional)

플러그인의 `settings.json`은 대상 프로젝트의 `.claude/settings.local.json`에 deep merge됩니다.

- **대상 파일:** `.claude/settings.local.json` (gitignore, 개인 범위)
- **기존 파일이 있는 경우:** 기존 설정과 deep merge (플러그인 값이 충돌 시 우선)
- **기존 파일이 없는 경우:** 새로 생성

> ⚠️ `.claude/settings.json`(팀 공유)이 아닌 `.claude/settings.local.json`(개인)에 머지됩니다.

**hooks 형식 주의:** hooks는 반드시 배열 구조로 작성해야 합니다. 문자열 형식은 동작하지 않습니다.

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "bash .claude/hooks/load-context", "timeout": 30 }
        ]
      }
    ]
  }
}
```

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
