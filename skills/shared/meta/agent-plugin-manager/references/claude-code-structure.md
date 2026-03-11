# Claude Code Directory Structure

Claude Code uses a `.claude/` directory in the project root to store project-specific configurations, rules, skills, and agents.

## Standard Structure

```
project-root/
└── .claude/
    ├── CLAUDE.md        # Project-level instructions for Claude Code
    ├── settings.json    # Claude Code settings
    ├── rules/           # Project-specific rules (auto-loaded by Claude Code)
    │   └── *.md
    ├── skills/          # Skills available in this project
    │   └── skill-name/
    │       └── SKILL.md
    └── agents/          # Agent definitions for this project
        └── agent-name.md
```

## Directory Roles

### `rules/`

- Contains `.md` files with guidelines, conventions, or constraints
- All `.md` files in `rules/` are **automatically loaded** into Claude Code's context as project instructions
- Use for: coding style guides, architecture decisions, team conventions, domain-specific rules

**Example files:**
```
.claude/rules/
├── coding-style.md
├── api-conventions.md
└── testing-guidelines.md
```

### `skills/`

- Contains skill packages (each skill is a subdirectory with a `SKILL.md`)
- Skills provide specialized workflows and domain knowledge
- Loaded on-demand when triggered by user requests

**Example structure:**
```
.claude/skills/
└── my-skill/
    ├── SKILL.md
    ├── scripts/
    └── references/
```

### `agents/`

- Contains agent definition files (`.md`)
- Defines specialized agent personas or subagent configurations
- Referenced when creating or delegating to specific agents

**Example files:**
```
.claude/agents/
├── code-reviewer.md
└── documentation-writer.md
```

## Plugin → Claude Code Mapping

A plugin's `plugin.json` declares dependencies on shared resources in the `agent-tools` repository. When applying a plugin to a project, these dependencies are resolved from the agent-tools root directories and **symlinked** into the target project's `.claude/` subdirectories.

| Source in agent-tools          | Target in project          | Method   |
|--------------------------------|----------------------------|----------|
| `skills/shared/{name}/`       | `.claude/skills/{name}/`   | Symlink  |
| `agents/shared/{name}.md`     | `.claude/agents/{name}.md` | Symlink  |
| `rules/shared/{name}.md`      | `.claude/rules/{name}.md`  | Symlink  |
| `hooks/shared/{name}`         | `.claude/hooks/{name}`     | Symlink  |
| Plugin's `settings.json`      | `.claude/settings.json`    | Merge    |

### Resolution flow

1. Read `plugin.json` to get the list of dependencies (skills, agents, rules, hooks)
2. Resolve each dependency to its absolute path under the agent-tools repository
3. Create symlinks from the target project's `.claude/` subdirectories to the resolved paths
4. If the plugin includes a `settings.json`, merge its contents into the target project's `.claude/settings.json`

> **Note:** The plugin's `README.md` is not symlinked, as it serves as documentation for the plugin itself, not as a project configuration.

## Reference

- [Claude Code documentation](https://docs.anthropic.com/en/docs/claude-code)
- Use `scripts/apply_to_repo.py` to automate applying a plugin to a project.
