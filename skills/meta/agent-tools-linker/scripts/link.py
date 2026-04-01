#!/usr/bin/env python3
"""
Link agent-tools skills and agents into a target repository's .claude/ directory
via symlinks or copies.

Usage:
    python link.py skill <skill-name> --repo <alias|path>
    python link.py agent <agent-name> --repo <alias|path>

    # Utilities
    python link.py --list-repos

Options:
    --repo      Target repo alias or absolute path
    --dry-run   Preview changes without writing files
    --overwrite Overwrite existing files/symlinks (default: skip)
    --copy      Copy instead of symlink (default: symlink)
    --verbose   Show detailed output
    --no-deps   Skip dependency resolution for agents
"""

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent
AGENT_TOOLS_ROOT = Path("/Users/choiyoungjun/agent-tools")

# artifact type -> (source base dir, .claude/ target dir)
ARTIFACT_MAP = {
    "skill": (AGENT_TOOLS_ROOT / "skills", "skills"),
    "agent": (AGENT_TOOLS_ROOT / "agents", "agents"),
}


# ── Config ──────────────────────────────────────────────────────────────────

def load_config() -> dict:
    local = SKILL_ROOT / "assets" / "config.local.json"
    default = SKILL_ROOT / "assets" / "config.json"
    path = local if local.exists() else default
    return json.loads(path.read_text()) if path.exists() else {}


def get_repos(config: dict) -> dict:
    return config.get("repos", {})


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


def find_skill(name: str, skills_base: Path) -> Path | None:
    """skills/<category>/<name> 구조에서 스킬 디렉토리를 탐색한다."""
    # 직접 경로
    direct = skills_base / name
    if direct.exists():
        return direct
    # 카테고리 하위 탐색
    for category in skills_base.iterdir():
        if category.is_dir():
            candidate = category / name
            if candidate.exists():
                return candidate
    return None


def parse_agent_dependencies(agent_path: Path) -> list[str]:
    """에이전트 .md 파일의 YAML frontmatter에서 skills 의존성을 추출한다."""
    if not agent_path.exists() or not agent_path.is_file():
        return []
    text = agent_path.read_text(encoding="utf-8")
    # YAML frontmatter 추출: --- ... ---
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return []
    frontmatter = match.group(1)
    # skills: 배열 파싱 (간단한 YAML 파서 — 외부 의존성 없이)
    skills: list[str] = []
    in_skills = False
    for line in frontmatter.splitlines():
        stripped = line.strip()
        if stripped.startswith("skills:"):
            # inline 값이 있으면 무시 (배열 형태만 지원)
            in_skills = True
            continue
        if in_skills:
            if stripped.startswith("- "):
                skills.append(stripped[2:].strip().strip("'\""))
            else:
                break
    return skills


def apply_artifact(artifact_type: str, name: str, claude_dir: Path, *, dry_run: bool, overwrite: bool, symlink: bool, verbose: bool, resolve_deps: bool = True):
    src_base, tgt_dir = ARTIFACT_MAP[artifact_type]

    if artifact_type == "skill":
        src = find_skill(name, src_base)
        if src is None:
            print(f"❌ skill '{name}' not found in: {src_base} (카테고리 하위 포함)")
            sys.exit(1)
    else:
        # agent: agents/<name>.md 또는 agents/<name>/
        src = src_base / name
        if not src.exists():
            candidate = src_base / (name + ".md")
            if candidate.exists():
                src = candidate

    if not src.exists():
        print(f"❌ {artifact_type} '{name}' not found in: {src_base}")
        sys.exit(1)

    tgt_base = claude_dir / tgt_dir
    total_applied = 0
    total_skipped = 0

    # ── 에이전트 의존성 해결 ──
    if artifact_type == "agent" and resolve_deps and src.is_file():
        dep_skills = parse_agent_dependencies(src)
        if dep_skills:
            skills_base = ARTIFACT_MAP["skill"][0]
            print(f"  📦 Resolving {len(dep_skills)} dependency skill(s)...")
            for skill_name in dep_skills:
                skill_src = find_skill(skill_name, skills_base)
                if skill_src is None:
                    print(f"  ⚠️  Dependency skill '{skill_name}' not found — skipping")
                    continue
                a, s, _ = apply_artifact(
                    "skill", skill_name, claude_dir,
                    dry_run=dry_run, overwrite=overwrite,
                    symlink=symlink, verbose=verbose,
                    resolve_deps=False,
                )
                total_applied += a
                total_skipped += s

    if src.is_dir():
        # Link entire directory (e.g. skill package)
        tgt = tgt_base / src.name
        if tgt.exists() or tgt.is_symlink():
            if not overwrite:
                print(f"  ⏭️  Skipped (already exists): {tgt}")
                return total_applied, total_skipped + 1, 0
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
        return total_applied + 1, total_skipped, 0
    else:
        tgt = tgt_base / src.name
        if not tgt.parent.exists() and not dry_run:
            tgt.parent.mkdir(parents=True, exist_ok=True)
        result = link_file(src, tgt, dry_run=dry_run, overwrite=overwrite, symlink=symlink)
        if result == "skipped":
            if verbose:
                print(f"  ⏭️  Skipped: {tgt}")
            return total_applied, total_skipped + 1, 0
        icon = "🔗" if symlink else "✅"
        verb = f"[dry-run] Would {'symlink' if symlink else 'copy'}" if dry_run else ("Symlinked" if symlink else "Copied")
        print(f"  {icon} {verb}: {src.name} → {tgt}")
        return total_applied + 1, total_skipped, 0


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Link agent-tools artifacts into a target repo's .claude/ directory.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "type",
        nargs="?",
        choices=["skill", "agent"],
        help="Artifact type to link",
    )
    parser.add_argument("name", nargs="?", help="Artifact name")
    parser.add_argument("--repo", default=os.getcwd(), help="Target repo alias or path")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    parser.add_argument("--copy", action="store_true", help="Copy instead of symlink")
    parser.add_argument("--verbose", action="store_true", help="Detailed output")
    parser.add_argument("--no-deps", action="store_true", help="Skip dependency resolution for agents")
    parser.add_argument("--list-repos", action="store_true", help="List configured repo aliases")
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

    # ── Validate args ──
    if not args.type:
        parser.error("artifact type is required (skill | agent)")
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

    applied, skipped, created_dirs = apply_artifact(
        args.type, args.name, claude_dir,
        dry_run=args.dry_run, overwrite=args.overwrite,
        symlink=use_symlink, verbose=args.verbose,
        resolve_deps=not args.no_deps,
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
