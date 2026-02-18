#!/usr/bin/env python3
from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None

if tomllib is None:  # pragma: no cover
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ModuleNotFoundError:
        tomllib = None


DIRECT_COPY = "direct-copy"
TRANSFORM = "transform"
REPORT_ONLY = "report-only"


@dataclass
class Change:
    action: str
    change_type: str
    rule_id: str
    source: Path
    target: Path
    target_kind: str
    content: bytes | None = None
    link_target: str | None = None
    diff_summary: str | None = None


@dataclass
class Report:
    rule_id: str
    source: str
    target: str
    reason: str


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def utc_stamp(dt: datetime) -> str:
    return dt.strftime("%Y%m%dT%H%M%SZ")


def path_str(path: Path, workspace: Path) -> str:
    try:
        return str(path.relative_to(workspace))
    except ValueError:
        return str(path)


def format_diff(old: str, new: str, source: str, target: str, max_lines: int = 12) -> str:
    diff_lines = list(
        difflib.unified_diff(
            old.splitlines(),
            new.splitlines(),
            fromfile=source,
            tofile=target,
            lineterm="",
        )
    )
    if not diff_lines:
        return ""
    return "\n".join(diff_lines[:max_lines])


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_bytes(path: Path) -> bytes:
    return path.read_bytes()


def convert_claude_to_agents(text: str) -> str:
    converted = text
    converted = converted.replace("# CLAUDE.md", "# AGENTS.md", 1)
    converted = converted.replace("Claude Code (claude.ai/code)", "Codex")
    converted = converted.replace(".claude/", ".codex/")
    return converted


def convert_agents_to_claude(text: str) -> str:
    converted = text
    converted = converted.replace("# AGENTS.md", "# CLAUDE.md", 1)
    converted = converted.replace("Codex", "Claude Code (claude.ai/code)")
    converted = converted.replace(".codex/", ".claude/")
    return converted


def json_settings_to_toml(src_bytes: bytes) -> bytes:
    data = json.loads(src_bytes.decode("utf-8"))
    allow = data.get("permissions", {}).get("allow", [])
    if not isinstance(allow, list):
        raise ValueError("permissions.allow must be an array")

    lines: list[str] = []
    lines.append("# Generated from .claude/settings.local.json by sync-ai-settings")
    lines.append("")
    lines.append("[permissions]")
    lines.append("allow = [")
    for entry in allow:
        lines.append(f"  {json.dumps(entry, ensure_ascii=False)},")
    lines.append("]")
    lines.append("")
    return ("\n".join(lines)).encode("utf-8")


def toml_settings_to_json(src_bytes: bytes) -> bytes:
    text = src_bytes.decode("utf-8")

    if tomllib is not None:
        data = tomllib.loads(text)
        allow = data.get("permissions", {}).get("allow", [])
        if not isinstance(allow, list):
            raise ValueError("[permissions].allow must be an array")
    else:
        block_match = re.search(r"\[permissions\](.*?)(?:\n\[[^\]]+\]|$)", text, re.DOTALL)
        if block_match is None:
            raise ValueError("missing [permissions] section")
        block = block_match.group(1)
        allow_match = re.search(r"allow\s*=\s*\[(.*?)\]", block, re.DOTALL)
        if allow_match is None:
            raise ValueError("missing permissions.allow array")
        allow_raw = "[" + allow_match.group(1) + "]"
        allow_raw = re.sub(r"#.*", "", allow_raw)
        allow = json.loads(allow_raw)
        if not isinstance(allow, list):
            raise ValueError("parsed permissions.allow is not an array")

    output = {"permissions": {"allow": allow}}
    return (json.dumps(output, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def collect_tree_entries(root: Path) -> list[Path]:
    if not root.exists():
        return []
    entries: list[Path] = []
    for current_root, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current_root)
        kept_dirs: list[str] = []
        for dirname in dirnames:
            candidate = current_path / dirname
            if candidate.is_symlink():
                entries.append(candidate)
            else:
                kept_dirs.append(dirname)
        dirnames[:] = kept_dirs

        for filename in filenames:
            entries.append(current_path / filename)
    return entries


def plan_copy_entry(
    *,
    source: Path,
    target: Path,
    rule_id: str,
    change_type: str,
    workspace: Path,
) -> tuple[Change | None, Report | None]:
    if source.is_symlink():
        source_link = os.readlink(source)
        if target.exists() and not target.is_symlink():
            return None, Report(
                rule_id=rule_id,
                source=path_str(source, workspace),
                target=path_str(target, workspace),
                reason="target exists as non-symlink; skipping unsafe replacement",
            )
        if target.is_symlink() and os.readlink(target) == source_link:
            return None, None
        action = "create" if not target.exists() and not target.is_symlink() else "update"
        return (
            Change(
                action=action,
                change_type=change_type,
                rule_id=rule_id,
                source=source,
                target=target,
                target_kind="symlink",
                link_target=source_link,
            ),
            None,
        )

    if not source.is_file():
        return None, Report(
            rule_id=rule_id,
            source=path_str(source, workspace),
            target=path_str(target, workspace),
            reason="source is not a regular file or symlink",
        )

    if target.exists() and target.is_dir():
        return None, Report(
            rule_id=rule_id,
            source=path_str(source, workspace),
            target=path_str(target, workspace),
            reason="target exists as directory; skipping unsafe replacement",
        )

    content = read_bytes(source)
    if not target.exists() and not target.is_symlink():
        return (
            Change(
                action="create",
                change_type=change_type,
                rule_id=rule_id,
                source=source,
                target=target,
                target_kind="file",
                content=content,
            ),
            None,
        )

    try:
        target_content = read_bytes(target)
    except Exception as exc:
        return None, Report(
            rule_id=rule_id,
            source=path_str(source, workspace),
            target=path_str(target, workspace),
            reason=f"failed to read target: {exc}",
        )

    if content == target_content:
        return None, None

    diff_summary = format_diff(
        target_content.decode("utf-8", errors="replace"),
        content.decode("utf-8", errors="replace"),
        path_str(target, workspace),
        path_str(source, workspace),
    )
    return (
        Change(
            action="update",
            change_type=change_type,
            rule_id=rule_id,
            source=source,
            target=target,
            target_kind="file",
            content=content,
            diff_summary=diff_summary,
        ),
        None,
    )


def plan_transform_file(
    *,
    source: Path,
    target: Path,
    rule_id: str,
    transform: Callable[[bytes], bytes],
    workspace: Path,
) -> tuple[Change | None, Report | None]:
    if not source.exists():
        return None, Report(
            rule_id=rule_id,
            source=path_str(source, workspace),
            target=path_str(target, workspace),
            reason="source file missing",
        )
    if source.is_symlink() or source.is_file():
        src_bytes = read_bytes(source)
    else:
        return None, Report(
            rule_id=rule_id,
            source=path_str(source, workspace),
            target=path_str(target, workspace),
            reason="source is not a file-like entry",
        )

    try:
        converted = transform(src_bytes)
    except Exception as exc:
        return None, Report(
            rule_id=rule_id,
            source=path_str(source, workspace),
            target=path_str(target, workspace),
            reason=f"transform failed: {exc}",
        )

    if target.exists() and target.is_dir():
        return None, Report(
            rule_id=rule_id,
            source=path_str(source, workspace),
            target=path_str(target, workspace),
            reason="target exists as directory; skipping unsafe replacement",
        )

    if not target.exists() and not target.is_symlink():
        return (
            Change(
                action="create",
                change_type=TRANSFORM,
                rule_id=rule_id,
                source=source,
                target=target,
                target_kind="file",
                content=converted,
            ),
            None,
        )

    try:
        target_content = read_bytes(target)
    except Exception as exc:
        return None, Report(
            rule_id=rule_id,
            source=path_str(source, workspace),
            target=path_str(target, workspace),
            reason=f"failed to read target: {exc}",
        )

    if converted == target_content:
        return None, None

    diff_summary = format_diff(
        target_content.decode("utf-8", errors="replace"),
        converted.decode("utf-8", errors="replace"),
        path_str(target, workspace),
        path_str(source, workspace),
    )
    return (
        Change(
            action="update",
            change_type=TRANSFORM,
            rule_id=rule_id,
            source=source,
            target=target,
            target_kind="file",
            content=converted,
            diff_summary=diff_summary,
        ),
        None,
    )


def plan_directory_copy(
    *,
    source_dir: Path,
    target_dir: Path,
    rule_id: str,
    workspace: Path,
) -> tuple[list[Change], list[Report], set[str]]:
    changes: list[Change] = []
    reports: list[Report] = []
    touched_targets: set[str] = set()

    if not source_dir.exists():
        reports.append(
            Report(
                rule_id=rule_id,
                source=path_str(source_dir, workspace),
                target=path_str(target_dir, workspace),
                reason="source directory missing",
            )
        )
        return changes, reports, touched_targets

    for entry in collect_tree_entries(source_dir):
        rel = entry.relative_to(source_dir)
        target = target_dir / rel
        touched_targets.add(path_str(target, workspace))
        change, report = plan_copy_entry(
            source=entry,
            target=target,
            rule_id=rule_id,
            change_type=DIRECT_COPY,
            workspace=workspace,
        )
        if change:
            changes.append(change)
        if report:
            reports.append(report)

    return changes, reports, touched_targets


def build_plan(workspace: Path, direction: str) -> tuple[list[Change], list[Report], dict]:
    changes: list[Change] = []
    reports: list[Report] = []
    touched_targets: set[str] = set()
    mapped_target_entries: set[str] = set()
    timestamp = utc_stamp(now_utc())
    backup_path = workspace / ".sync-backup" / timestamp / direction

    def track(change: Change | None, report: Report | None) -> None:
        if change:
            changes.append(change)
            touched_targets.add(path_str(change.target, workspace))
            mapped_target_entries.add(path_str(change.target, workspace))
        if report:
            reports.append(report)

    def copy_file(rule_id: str, source: Path, target: Path) -> None:
        mapped_target_entries.add(path_str(target, workspace))
        change, report = plan_copy_entry(
            source=source,
            target=target,
            rule_id=rule_id,
            change_type=DIRECT_COPY,
            workspace=workspace,
        )
        track(change, report)

    def transform_file(
        rule_id: str,
        source: Path,
        target: Path,
        transform: Callable[[bytes], bytes],
    ) -> None:
        mapped_target_entries.add(path_str(target, workspace))
        change, report = plan_transform_file(
            source=source,
            target=target,
            rule_id=rule_id,
            transform=transform,
            workspace=workspace,
        )
        track(change, report)

    def copy_dir(rule_id: str, source_dir: Path, target_dir: Path) -> None:
        dir_changes, dir_reports, dir_touched = plan_directory_copy(
            source_dir=source_dir,
            target_dir=target_dir,
            rule_id=rule_id,
            workspace=workspace,
        )
        changes.extend(dir_changes)
        reports.extend(dir_reports)
        touched_targets.update(dir_touched)
        for item in dir_touched:
            mapped_target_entries.add(item)

    claude = workspace / ".claude"
    codex = workspace / ".codex"

    if direction == "cc-to-codex":
        copy_dir("skills-dir-copy", claude / "skills", codex / "skills")
        copy_dir("commands-dir-copy", claude / "commands", codex / "commands")
        copy_dir("hooks-dir-copy", claude / "hooks", codex / "hooks")
        copy_file(
            "project-memory-copy",
            claude / "project-memory-config.yaml",
            codex / "project-memory-config.yaml",
        )
        copy_file("legacy-claude-md-copy", claude / "CLAUDE.md", codex / "CLAUDE.md")
        copy_file(
            "legacy-settings-json-copy",
            claude / "settings.local.json",
            codex / "settings.local.json",
        )
        transform_file(
            "guidance-transform",
            claude / "CLAUDE.md",
            codex / "AGENTS.md",
            lambda raw: convert_claude_to_agents(raw.decode("utf-8")).encode("utf-8"),
        )
        transform_file(
            "settings-transform",
            claude / "settings.local.json",
            codex / "config.toml",
            json_settings_to_toml,
        )
    else:
        copy_dir("skills-dir-copy", codex / "skills", claude / "skills")
        copy_dir("commands-dir-copy", codex / "commands", claude / "commands")
        copy_dir("hooks-dir-copy", codex / "hooks", claude / "hooks")
        copy_file(
            "project-memory-copy",
            codex / "project-memory-config.yaml",
            claude / "project-memory-config.yaml",
        )
        agents_source = codex / "AGENTS.md"
        legacy_guidance = codex / "CLAUDE.md"
        if agents_source.exists():
            transform_file(
                "guidance-transform",
                agents_source,
                claude / "CLAUDE.md",
                lambda raw: convert_agents_to_claude(raw.decode("utf-8")).encode("utf-8"),
            )
        else:
            copy_file("legacy-claude-md-copy", legacy_guidance, claude / "CLAUDE.md")

        config_source = codex / "config.toml"
        legacy_settings = codex / "settings.local.json"
        if config_source.exists():
            transform_file(
                "settings-transform",
                config_source,
                claude / "settings.local.json",
                toml_settings_to_json,
            )
        else:
            copy_file(
                "legacy-settings-json-copy",
                legacy_settings,
                claude / "settings.local.json",
            )

    changes.sort(key=lambda item: path_str(item.target, workspace))
    reports.sort(key=lambda item: (item.rule_id, item.target))

    summary = {
        "create": sum(1 for item in changes if item.action == "create"),
        "update": sum(1 for item in changes if item.action == "update"),
        "report_only": len(reports),
        "conflict_like_updates": sum(1 for item in changes if item.action == "update"),
    }

    kept_target_only = sorted(mapped_target_entries - touched_targets)

    plan_metadata = {
        "direction": direction,
        "generated_at_utc": now_utc().isoformat(),
        "backup_path": path_str(backup_path, workspace),
        "summary": summary,
        "target_only_preserved_count": len(kept_target_only),
        "target_only_preserved_sample": kept_target_only[:20],
    }

    return changes, reports, plan_metadata


def write_plan_file(
    *,
    workspace: Path,
    direction: str,
    changes: list[Change],
    reports: list[Report],
    metadata: dict,
) -> Path:
    plan_dir = workspace / ".sync-plans"
    plan_dir.mkdir(parents=True, exist_ok=True)
    plan_path = plan_dir / f"{utc_stamp(now_utc())}-{direction}.json"

    payload = {
        "direction": direction,
        "generated_at_utc": metadata["generated_at_utc"],
        "backup_path": metadata["backup_path"],
        "summary": metadata["summary"],
        "target_only_preserved_count": metadata["target_only_preserved_count"],
        "target_only_preserved_sample": metadata["target_only_preserved_sample"],
        "changes": [
            {
                "action": item.action,
                "type": item.change_type,
                "rule_id": item.rule_id,
                "source": path_str(item.source, workspace),
                "target": path_str(item.target, workspace),
                "target_kind": item.target_kind,
                "diff_summary": item.diff_summary or "",
            }
            for item in changes
        ],
        "report_only": [
            {
                "rule_id": item.rule_id,
                "source": item.source,
                "target": item.target,
                "reason": item.reason,
            }
            for item in reports
        ],
    }
    plan_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return plan_path


def backup_target(backup_root: Path, workspace: Path, target: Path) -> None:
    if not target.exists() and not target.is_symlink():
        return

    rel = target.relative_to(workspace)
    backup_target_path = backup_root / rel
    ensure_parent(backup_target_path)

    if target.is_symlink():
        if backup_target_path.exists() or backup_target_path.is_symlink():
            backup_target_path.unlink()
        os.symlink(os.readlink(target), backup_target_path)
        return

    if target.is_file():
        shutil.copy2(target, backup_target_path)


def apply_changes(workspace: Path, changes: list[Change], backup_path: Path) -> None:
    for change in changes:
        backup_target(backup_path, workspace, change.target)

    for change in changes:
        ensure_parent(change.target)

        if change.target_kind == "symlink":
            if change.target.exists() and not change.target.is_symlink():
                raise RuntimeError(f"refusing to replace non-symlink target: {change.target}")
            if change.target.is_symlink():
                change.target.unlink()
            os.symlink(change.link_target or "", change.target)
            continue

        if change.content is None:
            raise RuntimeError(f"missing file content for: {change.target}")
        if change.target.is_symlink():
            change.target.unlink()
        change.target.write_bytes(change.content)


def print_plan(
    *,
    workspace: Path,
    plan_path: Path,
    metadata: dict,
    changes: list[Change],
    reports: list[Report],
    executed: bool,
) -> None:
    summary = metadata["summary"]
    print(f"Direction: {metadata['direction']}")
    print(f"Workspace: {workspace}")
    print(
        "Summary: "
        f"create={summary['create']} "
        f"update={summary['update']} "
        f"report_only={summary['report_only']} "
        f"conflict_like_updates={summary['conflict_like_updates']}"
    )
    print(f"Backup path: {metadata['backup_path']}")
    print(f"Plan file: {path_str(plan_path, workspace)}")
    print(f"Target-only preserved: {metadata['target_only_preserved_count']}")

    if changes:
        print("\nPlanned changes:")
        for item in changes:
            print(
                f"- [{item.action}] [{item.change_type}] "
                f"{path_str(item.source, workspace)} -> {path_str(item.target, workspace)} "
                f"(rule={item.rule_id})"
            )
            if item.diff_summary:
                print("  diff:")
                for line in item.diff_summary.splitlines():
                    print(f"    {line}")

    if reports:
        print("\nReport-only items:")
        for item in reports:
            print(
                f"- {item.rule_id}: {item.source} -> {item.target} "
                f"({REPORT_ONLY}: {item.reason})"
            )

    if not executed:
        print("\nNo files were changed.")
        print("If this plan looks good, ask the user and then run with --execute.")
    else:
        print("\nExecution completed.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync .claude and .codex settings by direction")
    parser.add_argument(
        "direction",
        choices=["cc-to-codex", "codex-to-cc"],
        help="sync direction",
    )
    parser.add_argument(
        "--workspace",
        default=".",
        help="workspace root path (default: current directory)",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="apply planned changes after creating backup",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    workspace = Path(args.workspace).resolve()

    changes, reports, metadata = build_plan(workspace=workspace, direction=args.direction)
    backup_path = workspace / metadata["backup_path"]
    plan_path = write_plan_file(
        workspace=workspace,
        direction=args.direction,
        changes=changes,
        reports=reports,
        metadata=metadata,
    )

    if args.execute and changes:
        backup_path.mkdir(parents=True, exist_ok=True)
        apply_changes(workspace=workspace, changes=changes, backup_path=backup_path)

    print_plan(
        workspace=workspace,
        plan_path=plan_path,
        metadata=metadata,
        changes=changes,
        reports=reports,
        executed=args.execute,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
