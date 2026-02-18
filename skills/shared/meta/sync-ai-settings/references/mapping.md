# Mapping Notes

This skill syncs repository-local `.claude` and `.codex` with directional rules.

## Directions

- `cc-to-codex`: `.claude` is source, `.codex` is target
- `codex-to-cc`: `.codex` is source, `.claude` is target

## Rule Types

- `direct-copy`: byte-for-byte copy (files and symlinks)
- `transform`: deterministic conversion between known file formats
- `report-only`: surfaced in plan, never auto-written

## Primary Rules

- `skills-dir-copy`
  - `.claude/skills/**` <-> `.codex/skills/**`
- `project-memory-copy`
  - `.claude/project-memory-config.yaml` <-> `.codex/project-memory-config.yaml`
- `guidance-transform`
  - `.claude/CLAUDE.md` -> `.codex/AGENTS.md`
  - `.codex/AGENTS.md` -> `.claude/CLAUDE.md`
- `settings-transform`
  - `.claude/settings.local.json` -> `.codex/config.toml`
  - `.codex/config.toml` -> `.claude/settings.local.json`

## Compatibility Rules

- Keep legacy mirrors for coexistence:
  - `.claude/CLAUDE.md` -> `.codex/CLAUDE.md`
  - `.claude/settings.local.json` -> `.codex/settings.local.json`
- If `.codex/AGENTS.md` or `.codex/config.toml` is missing, reverse sync falls back to:
  - `.codex/CLAUDE.md`
  - `.codex/settings.local.json`

## Safety

- Plan-first default (no write)
- Ask user confirmation before execute
- Backup before writes: `.sync-backup/<timestamp>/<direction>/`
- Keep target-only files (no delete)
