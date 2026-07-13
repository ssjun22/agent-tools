#!/usr/bin/env python3
"""
Date and path calculator for daily-work-log skill.

This script calculates today's and yesterday's dates and generates
the appropriate file paths for Obsidian vault daily notes.

Usage:
    python date_helper.py [--config CONFIG_PATH]

Output:
    JSON object with today and yesterday information
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

DEFAULT_PROJECT_SECTIONS = ["프로젝트A", "프로젝트B", "기타"]


def get_week_of_month(d):
    """
    Calculate Monday-start week number within the month.

    Convention: weeks start on Monday and end on Sunday.
    The first week contains the 1st of the month and may be partial.

    Examples (April 2026, where 4/1 is Wednesday):
        4/1(Wed)~4/5(Sun)  -> 1주차
        4/6(Mon)~4/12(Sun) -> 2주차
        4/27(Mon)~5/3(Sun) -> 5주차
    """
    first_weekday = d.replace(day=1).weekday()  # Mon=0, Sun=6
    return (d.day + first_weekday - 1) // 7 + 1


def normalize_project_sections(value):
    """
    Normalize project section names from config.

    Args:
        value: Any config value intended for project_sections

    Returns:
        list[str]: Cleaned section names. Falls back to defaults when empty/invalid.
    """
    if not isinstance(value, list):
        return DEFAULT_PROJECT_SECTIONS.copy()

    cleaned = []
    seen = set()
    for item in value:
        if not isinstance(item, str):
            continue
        name = item.strip()
        if not name or name in seen:
            continue
        cleaned.append(name)
        seen.add(name)

    if not cleaned:
        return DEFAULT_PROJECT_SECTIONS.copy()

    return cleaned


def get_daily_paths(config_path="config.json"):
    """
    Calculate today's and yesterday's dates and generate file paths.

    Args:
        config_path: Path to config.json file

    Returns:
        dict: JSON object with today/yesterday information

    Raises:
        FileNotFoundError: If config.json doesn't exist
        KeyError: If required config keys are missing
    """
    # Read config.json
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(
            f"config.json not found at: {config_path}\n"
            "Please run the skill to create it interactively."
        )

    with open(config_file, encoding='utf-8') as f:
        config = json.load(f)

    # Validate config
    if "vault_path" not in config:
        raise KeyError("'vault_path' is required in config.json")
    if "daily_notes_path" not in config:
        raise KeyError("'daily_notes_path' is required in config.json")

    vault_path = Path(config["vault_path"]).expanduser()
    daily_notes = config["daily_notes_path"]
    project_sections = normalize_project_sections(config.get("project_sections"))

    # Backlog file path (default: <daily_notes_path>/Backlogs.md, relative to vault)
    backlog_rel = config.get("backlog_path") or f"{daily_notes}/Backlogs.md"
    backlog_path = Path(backlog_rel).expanduser()
    if not backlog_path.is_absolute():
        backlog_path = vault_path / backlog_rel

    # Calculate dates
    today = datetime.now()
    yesterday = today - timedelta(days=1)

    # Korean month/week format
    today_month_kr = f"{today.month}월"
    yesterday_month_kr = f"{yesterday.month}월"
    today_week_kr = f"{get_week_of_month(today)}주차"
    yesterday_week_kr = f"{get_week_of_month(yesterday)}주차"

    # Generate file paths (YYYY/M월/N주차/YYYY-MM-DD.md)
    today_dir = vault_path / daily_notes / str(today.year) / today_month_kr / today_week_kr
    yesterday_dir = vault_path / daily_notes / str(yesterday.year) / yesterday_month_kr / yesterday_week_kr

    today_path = today_dir / f"{today.strftime('%Y-%m-%d')}.md"
    yesterday_path = yesterday_dir / f"{yesterday.strftime('%Y-%m-%d')}.md"

    # Find most recent daily note file (excluding today)
    recent_file = None
    recent_date = None
    daily_notes_root = vault_path / daily_notes
    if daily_notes_root.exists():
        for md_file in sorted(daily_notes_root.rglob("*.md"), reverse=True):
            stem = md_file.stem
            try:
                file_date = datetime.strptime(stem, "%Y-%m-%d")
                if file_date.date() < today.date():
                    recent_file = str(md_file)
                    recent_date = stem
                    break
            except ValueError:
                continue

    return {
        "today": {
            "date": today.strftime("%Y-%m-%d"),
            "path": str(today_path),
            "dir": str(today_dir),
            "dir_exists": today_dir.exists()
        },
        "yesterday": {
            "date": yesterday.strftime("%Y-%m-%d"),
            "path": str(yesterday_path),
            "exists": yesterday_path.exists()
        },
        "recent": {
            "date": recent_date,
            "path": recent_file,
            "exists": recent_file is not None
        },
        "backlog": {
            "path": str(backlog_path),
            "exists": backlog_path.exists()
        },
        "config": {
            "project_sections": project_sections
        }
    }


def main():
    """Main entry point."""
    # Parse arguments
    config_path = "config.json"
    if len(sys.argv) > 1:
        if sys.argv[1] in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)
        elif sys.argv[1] == "--config" and len(sys.argv) > 2:
            config_path = sys.argv[2]

    try:
        result = get_daily_paths(config_path)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
