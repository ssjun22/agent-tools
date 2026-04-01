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

### `settings.json` / `settings.local.json`

Claude Code는 범위(scope)별 설정 파일을 사용합니다:

| 파일 | 범위 | Git | 용도 |
|------|------|-----|------|
| `~/.claude/settings.json` | 사용자 전역 | 비추적 | 모든 프로젝트에 적용되는 개인 설정 |
| `.claude/settings.json` | 프로젝트 | 커밋 | 팀 공유 설정 |
| `.claude/settings.local.json` | 로컬 | gitignore | 개인 오버라이드, 머신별 설정 |

**우선순위:** local > project > user (더 구체적인 범위가 우선)

플러그인 적용 시에는 `settings.local.json`(개인 범위)에 머지합니다.

#### Hooks 설정 형식

hooks는 **배열 구조**로 정의해야 합니다. 문자열 단축 형식은 지원되지 않습니다.

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/load-context",
            "timeout": 30
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/save-context",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

**matcher 값:**

| 이벤트 | matcher 값 |
|--------|-----------|
| SessionStart | `"startup"`, `"resume"`, `"clear"`, `"compact"`, `""` (전체) |
| SessionEnd | `"clear"`, `"logout"`, `"prompt_input_exit"`, `"other"`, `""` (전체) |

## Plugin → Claude Code Mapping

A plugin's `plugin.json` declares dependencies on shared resources in the `agent-tools` repository. When applying a plugin to a project, these dependencies are resolved from the agent-tools root directories and **symlinked** into the target project's `.claude/` subdirectories.

| Source in agent-tools          | Target in project          | Method   |
|--------------------------------|----------------------------|----------|
| `skills/{name}/`       | `.claude/skills/{name}/`   | Symlink  |
| `agents/{name}.md`     | `.claude/agents/{name}.md` | Symlink  |
| `rules/{name}.md`      | `.claude/rules/{name}.md`  | Symlink  |
| `hooks/{name}`         | `.claude/hooks/{name}`     | Symlink  |
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
