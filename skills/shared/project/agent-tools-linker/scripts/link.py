#!/usr/bin/env python3
"""
Link agent-tools artifacts (strategies, skills, hooks, agents, rules)
into a target repository's .claude/ directory via symlinks or copies.

Usage:
    # Apply a full strategy
    python link.py strategy <strategy-name> --repo <alias|path>

    # Link an individual artifact
    python link.py skill <skill-name> --repo <alias|path>
    python link.py hook <hook-file> --repo <alias|path>
    python link.py agent <agent-file> --repo <alias|path>
    python link.py rule <rule-file> --repo <alias|path>

    # Utilities
    python link.py --list-repos
    python link.py --list-strategies

Options:
    --repo      Target repo alias or absolute path
    --dry-run   Preview changes without writing files
    --overwrite Overwrite existing files/symlinks (default: skip)
    --copy      Copy instead of symlink (default: symlink)
    --verbose   Show detailed output
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent
AGENT_TOOLS_ROOT = Path("/Users/choiyoungjun/agent-tools")

# strategy subdir -> .claude/ subdir
STRATEGY_DIR_MAP = {
    "rules": "rules",
    "skills": "skills",
    "agents": "agents",
    "hooks": "hooks",
}

# artifact type -> (source base dir, .claude/ target dir)
ARTIFACT_MAP = {
    "skill":  (AGENT_TOOLS_ROOT / "skills" / "shared", "skills"),
    "hook":   (AGENT_TOOLS_ROOT / ".claude" / "hooks", "hooks"),
    "agent":  (AGENT_TOOLS_ROOT / ".claude" / "agents", "agents"),
    "rule":   (AGENT_TOOLS_ROOT / ".claude" / "rules", "rules"),
}


# ── Config ──────────────────────────────────────────────────────────────────

def load_config() -> dict:
    local = SKILL_ROOT / "assets" / "config.local.json"
    default = SKILL_ROOT / "assets" / "config.json"
    path = local if local.exists() else default
    return json.loads(path.read_text()) if path.exists() else {}


def get_repos(config: dict) -> dict:
    return config.get("repos", {})


def get_strategies_dir(config: dict) -> Path:
    raw = config.get("strategies_path", str(AGENT_TOOLS_ROOT / "strategies"))
    path = Path(raw)
    return path if path.is_absolute() else (SKILL_ROOT / path).resolve()


def resolve_repo(raw: str, repos: dict) -> Path:
    if raw in repos:
        return Path(repos[raw]).expanduser().resolve()
    return Path(raw).expanduser().resolve()


# ── Linking ──────────────────────────────────────────────────────────────────

def link_file(source: Path, target: Path, *, dry_run: bool, overwrite: bool, symlink: bool) -> str:
    """
    Link or copy source → target.
    Returns: 'linked' | 'skipped' | 'created'
    """
    if target.exists() or target.is_symlink():
        if not overwrite:
            return "skipped"
        if not dry_run:
            target.unlink()

    if not dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)
        if symlink:
            target.symlink_to(source.resolve())
        else:
            shutil.copy2(source, target)
    return "linked" if symlink else "copied"


def apply_strategy(strategy_path: Path, claude_dir: Path, *, dry_run: bool, overwrite: bool, symlink: bool, verbose: bool):
    applied = skipped = created_dirs = 0

    for src_dir, tgt_dir in STRATEGY_DIR_MAP.items():
        src_base = strategy_path / src_dir
        if not src_base.exists():
            continue

        files = [f for f in src_base.rglob("*") if f.is_file()]
        for src_file in files:
            rel = src_file.relative_to(src_base)
            tgt_file = claude_dir / tgt_dir / rel

            if not tgt_file.parent.exists() and not dry_run:
                tgt_file.parent.mkdir(parents=True, exist_ok=True)
                created_dirs += 1
                print(f"  📁 Created: {tgt_file.parent}")

            result = link_file(src_file, tgt_file, dry_run=dry_run, overwrite=overwrite, symlink=symlink)

            if result == "skipped":
                skipped += 1
                if verbose:
                    print(f"  ⏭️  Skipped: {tgt_file}")
            else:
                applied += 1
                icon = "🔗" if symlink else "✅"
                verb = f"[dry-run] Would {'symlink' if symlink else 'copy'}" if dry_run else ("Symlinked" if symlink else "Copied")
                print(f"  {icon} {verb}: {src_file.name} → {tgt_file}")

    return applied, skipped, created_dirs


def apply_artifact(artifact_type: str, name: str, claude_dir: Path, *, dry_run: bool, overwrite: bool, symlink: bool, verbose: bool):
    src_base, tgt_dir = ARTIFACT_MAP[artifact_type]

    # Support both file and directory (e.g. skill directories)
    src = src_base / name
    if not src.exists():
        # Try with common extensions
        for ext in [".md", ".sh", ".py"]:
            candidate = src_base / (name + ext)
            if candidate.exists():
                src = candidate
                break

    if not src.exists():
        print(f"❌ {artifact_type} '{name}' not found in: {src_base}")
        sys.exit(1)

    tgt_base = claude_dir / tgt_dir

    if src.is_dir():
        # Link entire directory (e.g. skill package)
        tgt = tgt_base / src.name
        if tgt.exists() or tgt.is_symlink():
            if not overwrite:
                print(f"  ⏭️  Skipped (already exists): {tgt}")
                return 0, 1, 0
            if not dry_run:
                if tgt.is_symlink():
                    tgt.unlink()
                else:
                    shutil.rmtree(tgt)
        if not dry_run:
            tgt_base.mkdir(parents=True, exist_ok=True)
            if symlink:
                tgt.symlink_to(src.resolve())
            else:
                shutil.copytree(src, tgt)
        icon = "🔗" if symlink else "✅"
        verb = f"[dry-run] Would {'symlink' if symlink else 'copy'}" if dry_run else ("Symlinked" if symlink else "Copied")
        print(f"  {icon} {verb}: {src.name}/ → {tgt}")
        return 1, 0, 0
    else:
        tgt = tgt_base / src.name
        if not tgt.parent.exists() and not dry_run:
            tgt.parent.mkdir(parents=True, exist_ok=True)
        result = link_file(src, tgt, dry_run=dry_run, overwrite=overwrite, symlink=symlink)
        if result == "skipped":
            if verbose:
                print(f"  ⏭️  Skipped: {tgt}")
            return 0, 1, 0
        icon = "🔗" if symlink else "✅"
        verb = f"[dry-run] Would {'symlink' if symlink else 'copy'}" if dry_run else ("Symlinked" if symlink else "Copied")
        print(f"  {icon} {verb}: {src.name} → {tgt}")
        return 1, 0, 0


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Link agent-tools artifacts into a target repo's .claude/ directory.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "type",
        nargs="?",
        choices=["strategy", "skill", "hook", "agent", "rule"],
        help="Artifact type to link",
    )
    parser.add_argument("name", nargs="?", help="Artifact name")
    parser.add_argument("--repo", default=os.getcwd(), help="Target repo alias or path")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    parser.add_argument("--copy", action="store_true", help="Copy instead of symlink")
    parser.add_argument("--verbose", action="store_true", help="Detailed output")
    parser.add_argument("--list-repos", action="store_true", help="List configured repo aliases")
    parser.add_argument("--list-strategies", action="store_true", help="List available strategies")
    args = parser.parse_args()

    config = load_config()
    repos = get_repos(config)

    # ── Utility commands ──
    if args.list_repos:
        if not repos:
            print("No repo aliases configured. Add 'repos' to assets/config.local.json.")
        else:
            print("Configured repos:")
            for alias, path in repos.items():
                ok = "✅" if Path(path).expanduser().exists() else "❌"
                print(f"  {ok} {alias}: {path}")
        sys.exit(0)

    if args.list_strategies:
        strategies_dir = get_strategies_dir(config)
        if not strategies_dir.exists():
            print(f"❌ Strategies directory not found: {strategies_dir}")
            sys.exit(1)
        items = sorted(d.name for d in strategies_dir.iterdir() if d.is_dir())
        print(f"Available strategies ({len(items)}):")
        for name in items:
            print(f"  📁 {name}")
        sys.exit(0)

    # ── Validate args ──
    if not args.type:
        parser.error("artifact type is required (strategy | skill | hook | agent | rule)")
    if not args.name:
        parser.error(f"name is required for type '{args.type}'")

    use_symlink = not args.copy
    repo_path = resolve_repo(args.repo, repos)
    claude_dir = repo_path / ".claude"

    if not repo_path.exists():
        print(f"❌ Repo path does not exist: {repo_path}")
        if repos:
            print("\nConfigured repos:")
            for alias, path in repos.items():
                print(f"  {alias}: {path}")
        sys.exit(1)

    method = "symlink (recommended)" if use_symlink else "copy"
    dry = " [DRY RUN]" if args.dry_run else ""
    print(f"\n🚀 Linking {args.type} '{args.name}' → {repo_path}{dry}")
    print(f"   Method:    {method}")
    print(f"   Overwrite: {'yes' if args.overwrite else 'no (skip existing)'}")
    print()

    if not claude_dir.exists() and not args.dry_run:
        claude_dir.mkdir(parents=True)
        print(f"  📁 Created .claude/ directory")

    if args.type == "strategy":
        strategies_dir = get_strategies_dir(config)
        strategy_path = strategies_dir / args.name
        if not strategy_path.exists():
            print(f"❌ Strategy '{args.name}' not found at: {strategy_path}")
            sys.exit(1)
        applied, skipped, created_dirs = apply_strategy(
            strategy_path, claude_dir,
            dry_run=args.dry_run, overwrite=args.overwrite,
            symlink=use_symlink, verbose=args.verbose,
        )
    else:
        applied, skipped, created_dirs = apply_artifact(
            args.type, args.name, claude_dir,
            dry_run=args.dry_run, overwrite=args.overwrite,
            symlink=use_symlink, verbose=args.verbose,
        )

    print()
    print("─" * 50)
    print(f"✅ Done{' (dry run)' if args.dry_run else ''}!")
    verb = "Symlinked" if use_symlink else "Copied"
    print(f"   {verb}: {applied} item(s)")
    if skipped:
        print(f"   Skipped: {skipped} item(s) — use --overwrite to replace")
    if args.dry_run:
        print("\n   Run without --dry-run to apply.")


if __name__ == "__main__":
    main()
