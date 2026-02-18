#!/usr/bin/env python3
"""
Build deterministic output paths for skill-feedback-refiner artifacts.

Usage:
  python scripts/path_builder.py --skill-name weekly-scrum-summarizer --label update-proposal
"""

from __future__ import annotations

import argparse
import re
import subprocess
from datetime import datetime
from pathlib import Path


def resolve_project_root(start_dir: Path) -> Path:
    """Resolve project root from git; fallback to start_dir."""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=start_dir,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return Path(result.stdout.strip()).resolve()
    return start_dir.resolve()


def slugify(text: str) -> str:
    """Convert text to kebab-case slug."""
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "artifact"


def ensure_unique(path: Path) -> Path:
    """Append -vN suffix when same filename already exists."""
    if not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix
    version = 2
    while True:
        candidate = path.with_name(f"{stem}-v{version}{suffix}")
        if not candidate.exists():
            return candidate
        version += 1


def build_path(
    start_dir: Path,
    skill_name: str,
    label: str,
    timestamp: datetime | None = None,
) -> Path:
    """Build artifact path from project root + naming rules."""
    now = timestamp or datetime.now()
    project_root = resolve_project_root(start_dir)
    slug = slugify(label)
    base_dir = (
        project_root
        / ".codex"
        / "skills"
        / "skill-feedback-refiner"
        / "feedbacks"
        / skill_name
    )
    filename = f"{now:%Y-%m-%d_%H%M}_{slug}.md"
    return ensure_unique(base_dir / filename)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build output artifact path for skill-feedback-refiner."
    )
    parser.add_argument("--skill-name", required=True, help="Target skill name.")
    parser.add_argument("--label", required=True, help="Artifact label for filename slug.")
    parser.add_argument(
        "--start-dir",
        default=".",
        help="Directory used to resolve project root (default: current directory).",
    )
    parser.add_argument(
        "--print-project-root",
        action="store_true",
        help="Print resolved project root before artifact path.",
    )
    parser.add_argument(
        "--no-mkdir",
        action="store_true",
        help="Do not create parent directories.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    start_dir = Path(args.start_dir).resolve()
    project_root = resolve_project_root(start_dir)
    artifact_path = build_path(start_dir=start_dir, skill_name=args.skill_name, label=args.label)

    if not args.no_mkdir:
        artifact_path.parent.mkdir(parents=True, exist_ok=True)

    if args.print_project_root:
        print(project_root)
    print(artifact_path)


if __name__ == "__main__":
    main()
