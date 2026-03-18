#!/usr/bin/env python3
"""
Apply an agent plugin to a target repository's .claude/ directory.

Reads plugin.json from the plugin directory and resolves dependencies
(skills, agents, rules, hooks) by creating symlinks from agent-tools
source into the target repo's .claude/ structure.

Usage:
    python scripts/apply_to_repo.py <plugin-name> --repo <target-repo-path> [options]

Options:
    --repo        Target repository path or alias (default: cwd)
    --dry-run     Preview changes without writing files
    --overwrite   Overwrite existing files/symlinks (default: skip)
    --symlink     Create symlinks (default, recommended)
    --copy        Copy files instead of symlinks
    --verbose     Show detailed output
    --list-repos  List configured repo aliases and exit
"""

import argparse
import json
import os
import shutil
import sys
from copy import deepcopy
from pathlib import Path


# Resolve agent-tools root: script → scripts/ → agent-plugin-manager/ → meta/ → shared/ → skills/ → root
AGENT_TOOLS_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent

# Default source paths for each dependency type
SOURCE_PATHS = {
    "skills": AGENT_TOOLS_ROOT / "skills" / "shared",
    "agents": AGENT_TOOLS_ROOT / "agents" / "shared",
    "rules": AGENT_TOOLS_ROOT / "rules" / "shared",
    "hooks": AGENT_TOOLS_ROOT / "hooks" / "shared",
}


def load_config(skill_root: Path) -> dict:
    """Load config, preferring config.local.json over config.json."""
    local_config_path = skill_root / "assets" / "config.local.json"
    default_config_path = skill_root / "assets" / "config.json"

    if local_config_path.exists():
        with open(local_config_path) as f:
            return json.load(f)
    elif default_config_path.exists():
        with open(default_config_path) as f:
            return json.load(f)
    else:
        return {"plugins_path": "./plugins"}


def resolve_plugins_path(skill_root: Path, config: dict) -> Path:
    """Resolve plugins path from config (relative to skill root or absolute)."""
    plugins_path = config.get("plugins_path", "./plugins")
    path = Path(plugins_path)
    if not path.is_absolute():
        path = (skill_root / path).resolve()
    return path


def get_plugin_path(plugins_dir: Path, plugin_name: str) -> Path:
    """Get and validate the plugin directory path."""
    plugin_path = plugins_dir / plugin_name
    if not plugin_path.exists():
        print(f"❌ Plugin '{plugin_name}' not found at: {plugin_path}")
        available = [d.name for d in plugins_dir.iterdir() if d.is_dir()]
        if available:
            print(f"\nAvailable plugins: {', '.join(sorted(available))}")
        sys.exit(1)
    return plugin_path


def load_plugin_json(plugin_path: Path) -> dict:
    """Load and validate plugin.json from the plugin directory."""
    plugin_json_path = plugin_path / "plugin.json"
    if not plugin_json_path.exists():
        print(f"❌ plugin.json not found in: {plugin_path}")
        print("   Every plugin must have a plugin.json with a 'depends' block.")
        sys.exit(1)

    with open(plugin_json_path) as f:
        data = json.load(f)

    if "depends" not in data:
        print(f"❌ plugin.json is missing 'depends' block: {plugin_json_path}")
        sys.exit(1)

    return data


def deep_merge(base: dict, override: dict) -> dict:
    """Deep merge two dicts. Override values take precedence for conflicts."""
    result = deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def resolve_dependency(
    dep_type: str,
    dep_name: str,
    claude_dir: Path,
    dry_run: bool,
    overwrite: bool,
    use_symlink: bool,
    verbose: bool,
) -> str:
    """
    Resolve a single dependency. Returns status: 'linked', 'copied', 'skipped', 'error'.

    - skills: dep_name is a relative path under skills/shared/ (e.g. "dev/code-reviewer")
              → symlink the directory to .claude/skills/{basename}/
    - agents: dep_name is a filename without .md (e.g. "handoff-creator")
              → symlink .md file to .claude/agents/
    - rules:  dep_name is a filename without .md (e.g. "handoff")
              → symlink .md file to .claude/rules/
    - hooks:  dep_name is a filename (e.g. "load-handoffs")
              → symlink file to .claude/hooks/
    """
    source_base = SOURCE_PATHS[dep_type]

    if dep_type == "skills":
        # Source is a directory: skills/shared/{dep_name}/
        source = source_base / dep_name
        basename = Path(dep_name).name
        target = claude_dir / "skills" / basename

        if not source.exists():
            print(f"  ❌ {dep_type}/{dep_name} — source not found: {source}")
            return "error"

        # Check existence by directory name
        if target.exists() or target.is_symlink():
            if not overwrite:
                if verbose:
                    kind = "symlink" if target.is_symlink() else "directory"
                    print(f"  ✅ {dep_type}/{basename} — already exists ({kind}), skip")
                else:
                    print(f"  ✅ {dep_type}/{basename} — already exists, skip")
                return "skipped"
            if not dry_run:
                if target.is_symlink():
                    target.unlink()
                elif target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()

        # Ensure parent directory exists
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)

        if use_symlink:
            if not dry_run:
                target.symlink_to(source.resolve())
            label = f"[dry-run] " if dry_run else ""
            print(f"  🔗 {label}{dep_type}/{basename} → symlinked")
            return "linked"
        else:
            if not dry_run:
                shutil.copytree(source, target)
            label = f"[dry-run] " if dry_run else ""
            print(f"  📄 {label}{dep_type}/{basename} → copied")
            return "copied"

    else:
        # agents, rules, hooks: individual files
        if dep_type in ("agents", "rules"):
            # Add .md extension if not present
            filename = dep_name if dep_name.endswith(".md") else f"{dep_name}.md"
        else:
            # hooks: use filename as-is
            filename = dep_name

        source = source_base / filename
        target = claude_dir / dep_type / filename

        if not source.exists():
            print(f"  ❌ {dep_type}/{dep_name} — source not found: {source}")
            return "error"

        if target.exists() or target.is_symlink():
            if not overwrite:
                display_name = dep_name
                if verbose:
                    kind = "symlink" if target.is_symlink() else "file"
                    print(f"  ✅ {dep_type}/{display_name} — already exists ({kind}), skip")
                else:
                    print(f"  ✅ {dep_type}/{display_name} — already exists, skip")
                return "skipped"
            if not dry_run:
                target.unlink()

        # Ensure parent directory exists
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)

        if use_symlink:
            if not dry_run:
                target.symlink_to(source.resolve())
            label = f"[dry-run] " if dry_run else ""
            print(f"  🔗 {label}{dep_type}/{dep_name} → symlinked")
            return "linked"
        else:
            if not dry_run:
                shutil.copy2(source, target)
            label = f"[dry-run] " if dry_run else ""
            print(f"  📄 {label}{dep_type}/{dep_name} → copied")
            return "copied"


def merge_settings(plugin_path: Path, claude_dir: Path, dry_run: bool) -> int:
    """
    Merge plugin's settings.json into target's .claude/settings.local.json.
    Uses settings.local.json (gitignored, personal scope) by default.
    If the target file already exists, its contents are deep-merged with
    the plugin settings (plugin values take precedence on conflict).
    Returns the number of top-level keys merged, or -1 if no settings.json.
    """
    plugin_settings_path = plugin_path / "settings.json"
    if not plugin_settings_path.exists():
        return -1

    with open(plugin_settings_path) as f:
        plugin_settings = json.load(f)

    target_settings_path = claude_dir / "settings.local.json"

    if target_settings_path.exists():
        with open(target_settings_path) as f:
            existing_settings = json.load(f)
    else:
        existing_settings = {}

    merged = deep_merge(existing_settings, plugin_settings)
    keys_merged = len(plugin_settings)

    if not dry_run:
        claude_dir.mkdir(parents=True, exist_ok=True)
        with open(target_settings_path, "w") as f:
            json.dump(merged, f, indent=2, ensure_ascii=False)
            f.write("\n")

    return keys_merged


def main():
    parser = argparse.ArgumentParser(
        description="Apply an agent plugin to a target repository's .claude/ directory."
    )
    parser.add_argument("plugin", nargs="?", help="Plugin name to apply")
    parser.add_argument(
        "--repo",
        default=os.getcwd(),
        help="Target repository path or alias (default: current working directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files/symlinks (default: skip)",
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--symlink",
        action="store_true",
        default=True,
        help="Create symlinks instead of copying files (default, recommended)",
    )
    mode_group.add_argument(
        "--copy",
        action="store_true",
        help="Copy files instead of creating symlinks",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output",
    )
    parser.add_argument(
        "--list-repos",
        action="store_true",
        help="List configured repo aliases and exit",
    )
    args = parser.parse_args()

    # Skill root for config loading
    skill_root = Path(__file__).resolve().parent.parent

    # --list-repos: show configured aliases and exit
    if args.list_repos:
        _config = load_config(skill_root)
        repos = _config.get("repos", {})
        if not repos:
            print("No repo aliases configured in config.local.json.")
            print("Add a 'repos' key to assets/config.local.json to register repos.")
        else:
            print("Configured repo aliases:")
            for alias, path in repos.items():
                exists = "✅" if Path(path).expanduser().exists() else "❌"
                print(f"  {exists} {alias}: {path}")
        sys.exit(0)

    config = load_config(skill_root)

    # plugin is required unless --list-repos
    if not args.plugin:
        parser.error("the following arguments are required: plugin")

    # Resolve repo path: support alias from config.repos or raw path
    repos = config.get("repos", {})
    raw_repo = args.repo

    if raw_repo in repos:
        repo_path = Path(repos[raw_repo]).expanduser().resolve()
        print(f"   Using repo alias '{raw_repo}' → {repo_path}")
    else:
        repo_path = Path(raw_repo).expanduser().resolve()

    claude_dir = repo_path / ".claude"

    # Validate target repo
    if not repo_path.exists():
        print(f"❌ Target repository path does not exist: {repo_path}")
        if repos:
            print(f"\nConfigured repo aliases:")
            for alias, path in repos.items():
                print(f"  {alias}: {path}")
        sys.exit(1)

    # Resolve plugin
    plugins_dir = resolve_plugins_path(skill_root, config)
    plugin_path = get_plugin_path(plugins_dir, args.plugin)

    # Load plugin.json
    plugin_data = load_plugin_json(plugin_path)
    depends = plugin_data["depends"]
    use_symlink = not args.copy

    # Summary header
    mode_label = " [DRY RUN]" if args.dry_run else ""
    print(f"\n🚀 Applying plugin '{args.plugin}' to: {repo_path}{mode_label}")
    if args.verbose:
        method = "symlink (recommended)" if use_symlink else "copy"
        print(f"   Method:    {method}")
        print(f"   Overwrite: {'yes' if args.overwrite else 'no (skip existing)'}")

    # Create .claude/ if needed
    if not claude_dir.exists() and not args.dry_run:
        claude_dir.mkdir(parents=True, exist_ok=True)

    # Resolve dependencies
    total_deps = sum(len(deps) for deps in depends.values())
    if total_deps == 0:
        print(f"\n⚠️  Plugin '{args.plugin}' has no dependencies declared.")
        sys.exit(0)

    print(f"\n📋 Resolving dependencies...")

    linked = 0
    skipped = 0
    errors = 0

    for dep_type in ("skills", "agents", "rules", "hooks"):
        dep_list = depends.get(dep_type, [])
        for dep_name in dep_list:
            status = resolve_dependency(
                dep_type=dep_type,
                dep_name=dep_name,
                claude_dir=claude_dir,
                dry_run=args.dry_run,
                overwrite=args.overwrite,
                use_symlink=use_symlink,
                verbose=args.verbose,
            )
            if status in ("linked", "copied"):
                linked += 1
            elif status == "skipped":
                skipped += 1
            elif status == "error":
                errors += 1

    # Merge settings.json if present
    settings_status = None
    keys_merged = merge_settings(plugin_path, claude_dir, args.dry_run)
    if keys_merged >= 0:
        print(f"\n⚙️  Merging settings.local.json...")
        label = "[dry-run] " if args.dry_run else ""
        print(f"  ✅ {label}Merged {keys_merged} key(s) into .claude/settings.local.json")
        settings_status = "merged"

    # Summary footer
    print()
    print("─" * 50)
    dry_suffix = " (dry run)" if args.dry_run else ""
    if errors:
        print(f"⚠️  Done{dry_suffix} (with errors)")
    else:
        print(f"✅ Done{dry_suffix}!")

    verb = "Linked" if use_symlink else "Copied"
    print(f"   {verb}:   {linked} file(s)")
    if skipped:
        print(f"   Skipped: {skipped} file(s)")
    if errors:
        print(f"   Errors:  {errors} file(s)")
    if settings_status:
        print(f"   Settings: {settings_status}")

    if args.dry_run:
        print()
        print("   Run without --dry-run to apply changes.")

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
