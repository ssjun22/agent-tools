---
name: sync-ai-settings
description: Keep local `.claude` and `.codex` folders in sync on demand with directional arguments (`cc-to-codex`, `codex-to-cc`). Use this skill when the user wants manual bidirectional sync with plan-first review, explicit confirmation, backup before writes, and no target-only deletions.
allowed-tools:
  - Bash
  - Read
  - Write
---

# Sync AI Settings

## Overview

Synchronize repository-local `.claude` and `.codex` settings and skills in a chosen direction.
Default behavior is plan-first: generate a dry-run report, ask `진행할까요?`, and only execute after explicit user confirmation.

Supported directions:
- `cc-to-codex`
- `codex-to-cc`

## Rules

- Run plan mode first.
- Print summary: create/update/report-only counts.
- Show conflict-like updates with short diffs.
- Keep target-only files unchanged.
- Ask `진행할까요?` before any write.
- Execute only after explicit positive confirmation.
- Create backup before writes at `.sync-backup/<timestamp>/<direction>/`.

## Workflow

1. Parse `$ARGUMENTS` and validate direction.
2. Run:
   - `python3 .codex/skills/sync-ai-settings/scripts/sync_ai_settings.py <direction>`
3. Present plan output to user and ask:
   - `진행할까요?`
4. If user confirms, run:
   - `python3 .codex/skills/sync-ai-settings/scripts/sync_ai_settings.py <direction> --execute`
5. Report changed files and backup path.

## Mapping Scope

Primary mappings:
- `.claude/skills/**` <-> `.codex/skills/**` (`direct-copy`)
- `.claude/CLAUDE.md` <-> `.codex/AGENTS.md` (`transform`)
- `.claude/settings.local.json` <-> `.codex/config.toml` (`transform`)
- `.claude/project-memory-config.yaml` <-> `.codex/project-memory-config.yaml` (`direct-copy`)

Report-only examples:
- Unsupported or invalid transform inputs
- Files without safe deterministic mapping

See mapping notes in:
- `references/mapping.md`
