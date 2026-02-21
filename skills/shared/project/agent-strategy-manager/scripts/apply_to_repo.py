#!/usr/bin/env python3
"""
Apply an agent strategy to a target repository's .claude/ directory.

Usage:
    python scripts/apply_to_repo.py <strategy-name> --repo <target-repo-path> [options]

Options:
    --strategy  Strategy name to apply
    --repo      Target repository path (default: current working directory)
    --dry-run   Preview changes without writing files
    --overwrite Overwrite existing files (default: skip)
    --verbose   Show detailed output
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path


# Claude Code target directories mapping: strategy dir -> .claude/ subdir
CLAUDE_CODE_DIR_MAP = {
    "rules": "rules",
    "skills": "skills",
    "agents": "agents",
    "hooks": "hooks",
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
        return {"strategies_path": "./strategies"}


def resolve_strategies_path(skill_root: Path, config: dict) -> Path:
    """Resolve strategies path from config (relative to skill root or absolute)."""
    strategies_path = config.get("strategies_path", "./strategies")
    path = Path(strategies_path)
    if not path.is_absolute():
        path = (skill_root / path).resolve()
    return path


def get_strategy_path(strategies_dir: Path, strategy_name: str) -> Path:
    """Get and validate the strategy directory path."""
    strategy_path = strategies_dir / strategy_name
    if not strategy_path.exists():
        print(f"❌ Strategy '{strategy_name}' not found at: {strategy_path}")
        available = [d.name for d in strategies_dir.iterdir() if d.is_dir()]
        if available:
            print(f"\nAvailable strategies: {', '.join(available)}")
        sys.exit(1)
    return strategy_path


def collect_files_to_apply(strategy_path: Path) -> dict[str, list[Path]]:
    """
    Collect files from strategy subdirectories that map to Claude Code dirs.
    Returns dict: { "rules": [...files], "skills": [...files], "agents": [...files] }
    """
    result = {}
    for source_dir, target_dir in CLAUDE_CODE_DIR_MAP.items():
        source_path = strategy_path / source_dir
        if source_path.exists() and source_path.is_dir():
            files = list(source_path.rglob("*"))
            files = [f for f in files if f.is_file()]
            if files:
                result[source_dir] = files
    return result


def apply_files(
    files_map: dict[str, list[Path]],
    strategy_path: Path,
    claude_dir: Path,
    dry_run: bool,
    overwrite: bool,
    verbose: bool,
    symlink: bool,
) -> tuple[int, int, int]:
    """
    Copy or symlink files to target .claude/ directory.
    Returns (applied, skipped, created_dirs) counts.
    """
    applied = 0
    skipped = 0
    created_dirs = 0

    for source_dir, files in files_map.items():
        target_base = claude_dir / CLAUDE_CODE_DIR_MAP[source_dir]
        source_base = strategy_path / source_dir

        for source_file in files:
            # Preserve relative path within the source dir
            relative = source_file.relative_to(source_base)
            target_file = target_base / relative

            # Create parent directories if needed
            if not target_file.parent.exists():
                if not dry_run:
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                created_dirs += 1
                action = "[dry-run] " if dry_run else ""
                print(f"  📁 {action}Created directory: {target_file.parent}")

            # Handle existing files/symlinks
            if target_file.exists() or target_file.is_symlink():
                if not overwrite:
                    if verbose:
                        kind = "symlink" if target_file.is_symlink() else "file"
                        print(f"  ⏭️  Skipped (already exists as {kind}): {target_file}")
                    skipped += 1
                    continue
                if not dry_run:
                    target_file.unlink()

            if symlink:
                if not dry_run:
                    target_file.symlink_to(source_file.resolve())
                status = "[dry-run] " if dry_run else ""
                verb = "Would symlink" if dry_run else "Symlinked"
                print(f"  🔗 {status}{verb}: {source_file.name} → {target_file}")
            else:
                if not dry_run:
                    shutil.copy2(source_file, target_file)
                status = "[dry-run] " if dry_run else ""
                verb = "Would copy" if dry_run else "Copied"
                print(f"  ✅ {status}{verb}: {source_file.name} → {target_file}")
            applied += 1

    return applied, skipped, created_dirs


def main():
    parser = argparse.ArgumentParser(
        description="Apply an agent strategy to a target repository's .claude/ directory."
    )
    parser.add_argument("strategy", nargs="?", help="Strategy name to apply")
    parser.add_argument(
        "--repo",
        default=os.getcwd(),
        help="Target repository path (default: current working directory)",
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

    # --list-repos: show configured aliases and exit
    if args.list_repos:
        _skill_root = Path(__file__).parent.parent
        _config = load_config(_skill_root)
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

    # Resolve paths
    skill_root = Path(__file__).parent.parent
    config = load_config(skill_root)

    # strategy is required unless --list-repos
    if not args.strategy:
        parser.error("the following arguments are required: strategy")

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

    strategies_dir = resolve_strategies_path(skill_root, config)

    # Get strategy
    strategy_path = get_strategy_path(strategies_dir, args.strategy)

    # Collect files
    files_map = collect_files_to_apply(strategy_path)

    if not files_map:
        print(f"⚠️  Strategy '{args.strategy}' has no rules/, skills/, or agents/ to apply.")
        print("   Only README.md-only strategies have nothing to apply to a repository.")
        sys.exit(0)

    # Determine mode: --copy overrides default symlink
    use_symlink = not args.copy

    # Summary header
    mode = " [DRY RUN]" if args.dry_run else ""
    method = "symlink (recommended)" if use_symlink else "copy"
    print(f"\n🚀 Applying strategy '{args.strategy}' to: {repo_path}{mode}")
    print(f"   .claude/ target: {claude_dir}")
    print(f"   Method:    {method}")
    print(f"   Overwrite: {'yes' if args.overwrite else 'no (skip existing)'}")
    print()

    # Create .claude/ if needed
    if not claude_dir.exists():
        if not args.dry_run:
            claude_dir.mkdir(parents=True, exist_ok=True)
        action = "[dry-run] " if args.dry_run else ""
        print(f"  📁 {action}Created .claude/ directory")

    # Apply files
    applied, skipped, created_dirs = apply_files(
        files_map,
        strategy_path,
        claude_dir,
        dry_run=args.dry_run,
        overwrite=args.overwrite,
        verbose=args.verbose,
        symlink=use_symlink,
    )

    # Summary footer
    print()
    print("─" * 50)
    print(f"✅ Done{' (dry run)' if args.dry_run else ''}!")
    verb = "Symlinked" if use_symlink else "Copied"
    print(f"   {verb}: {applied} file(s)")
    if skipped:
        print(f"   Skipped: {skipped} file(s) (already exist, use --overwrite to replace)")
    if created_dirs:
        print(f"   Created: {created_dirs} director{'y' if created_dirs == 1 else 'ies'}")

    if args.dry_run:
        print()
        print("   Run without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
