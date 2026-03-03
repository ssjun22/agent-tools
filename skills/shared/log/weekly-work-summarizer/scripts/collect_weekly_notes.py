#!/usr/bin/env python3
"""
Weekly notes collector for weekly-work-summarizer skill.

Reads daily notes from the previous week (Mon-Sun), extracts TODOs
from project sections (excluding "기타"), deduplicates repeated items,
and classifies them as completed or in-progress.

Usage:
    python collect_weekly_notes.py [--config CONFIG_PATH]

Output:
    JSON object with weekly summary data
"""

import json
import math
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

DEFAULT_PROJECT_SECTIONS = ["프로젝트A", "프로젝트B", "기타"]
EXCLUDE_SECTION = "기타"


def normalize_project_sections(value):
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

    return cleaned if cleaned else DEFAULT_PROJECT_SECTIONS.copy()


def get_week_range(today=None):
    """Return (monday, sunday) of the previous week."""
    if today is None:
        today = datetime.now().date()
    # Find last Monday
    days_since_monday = today.weekday()  # 0=Mon, 6=Sun
    this_monday = today - timedelta(days=days_since_monday)
    last_monday = this_monday - timedelta(weeks=1)
    last_sunday = last_monday + timedelta(days=6)
    return last_monday, last_sunday


def build_file_path(vault_path, daily_notes_path, date):
    """Build Obsidian daily note file path for given date."""
    month_kr = f"{date.month}월"
    week_kr = f"{math.ceil(date.day / 7)}주차"
    return (
        Path(vault_path)
        / daily_notes_path
        / str(date.year)
        / month_kr
        / week_kr
        / f"{date.strftime('%Y-%m-%d')}.md"
    )


def parse_meetings_section(content):
    """
    Parse the ## Meetings section from daily note content.

    Returns list of {"text": str, "children": [...]} (no checkboxes).
    """
    meetings_match = re.search(r'^## Meetings\s*\n(.*?)(?=^## |\Z)', content, re.MULTILINE | re.DOTALL)
    if not meetings_match:
        return []

    meetings_text = meetings_match.group(1)
    lines = meetings_text.split('\n')

    def get_indent(line):
        return len(line) - len(line.lstrip('\t '))

    root = []
    item_stack = []  # list of (indent, item_dict)

    for line in lines:
        if not line.strip():
            continue

        indent = get_indent(line)
        stripped = line.strip()

        plain_match = re.match(r'^- (.+)$', stripped)
        if not plain_match:
            continue

        text = plain_match.group(1).strip()
        # Skip placeholder text
        if text.startswith('(') and text.endswith(')'):
            continue

        item = {"text": text, "children": []}

        while item_stack and item_stack[-1][0] >= indent:
            item_stack.pop()

        if item_stack:
            item_stack[-1][1]["children"].append(item)
        else:
            root.append(item)

        item_stack.append((indent, item))

    return root


def assign_meeting_to_project(meeting_text, project_sections):
    """
    Find the best matching project for a meeting title.
    Returns the project name if found, else None.
    Matches by checking if any project name is a substring of the meeting title.
    Prefers the longest matching project name.
    """
    best = None
    best_len = 0
    for section in project_sections:
        if section in meeting_text and len(section) > best_len:
            best = section
            best_len = len(section)
    return best


def parse_todos_section(content, project_sections):
    """
    Parse the ## TODOs section from daily note content.

    Returns dict: { project_name: [{"text": str, "checked": bool, "children": [...]}] }
    """
    # Extract TODOs section
    todos_match = re.search(r'^## TODOs\s*\n(.*?)(?=^## |\Z)', content, re.MULTILINE | re.DOTALL)
    if not todos_match:
        return {}

    todos_text = todos_match.group(1)
    lines = todos_text.split('\n')

    result = {}
    current_project = None
    # Stack of (indent_level, item_dict)
    item_stack = []

    def get_indent(line):
        return len(line) - len(line.lstrip('\t '))

    for line in lines:
        if not line.strip():
            continue

        indent = get_indent(line)
        stripped = line.strip()

        # Check if it's a checkbox item
        checkbox_match = re.match(r'^- \[([ x])\] (.+)$', stripped)

        if not checkbox_match:
            # Plain text bullet - could be project name
            plain_match = re.match(r'^- (.+)$', stripped)
            if plain_match and indent == 0:
                project_name = plain_match.group(1).strip()
                if project_name in project_sections:
                    current_project = project_name
                    if current_project not in result:
                        result[current_project] = []
                    item_stack = []
            continue

        if current_project is None:
            continue

        checked = checkbox_match.group(1) == 'x'
        text = checkbox_match.group(2).strip()

        item = {"text": text, "checked": checked, "children": []}

        # Determine parent based on indent
        # Pop stack items with indent >= current
        while item_stack and item_stack[-1][0] >= indent:
            item_stack.pop()

        if item_stack:
            # Add as child of top item
            item_stack[-1][1]["children"].append(item)
        else:
            # Top-level item under project
            result[current_project].append(item)

        item_stack.append((indent, item))

    return result


def normalize_text(text):
    """Remove date annotations like (M/D~) for comparison."""
    return re.sub(r'\s*\(\d{1,2}/\d{1,2}~\)', '', text).strip()


def items_equal(a, b):
    """Compare two items by normalized text."""
    return normalize_text(a["text"]) == normalize_text(b["text"])


def merge_item(existing, new_item):
    """
    Merge new_item into existing item.
    - If new_item is checked, mark existing as checked (완료 우선)
    - Recursively merge children
    """
    if new_item["checked"]:
        existing["checked"] = True

    for new_child in new_item["children"]:
        matched = None
        for ex_child in existing["children"]:
            if items_equal(ex_child, new_child):
                matched = ex_child
                break
        if matched:
            merge_item(matched, new_child)
        else:
            existing["children"].append(new_child)


def merge_project_items(base_list, new_list):
    """Merge new_list into base_list with deduplication."""
    for new_item in new_list:
        matched = None
        for existing in base_list:
            if items_equal(existing, new_item):
                matched = existing
                break
        if matched:
            merge_item(matched, new_item)
        else:
            base_list.append(new_item)


def classify_items(items):
    """
    Recursively classify items into completed and in_progress.
    An item is completed if checked=True AND all children are also completed.
    """
    completed = []
    in_progress = []

    for item in items:
        child_completed, child_in_progress = classify_items(item["children"])

        if item["checked"] and not child_in_progress:
            # Fully completed
            completed.append({
                "text": normalize_text(item["text"]),
                "children": child_completed
            })
        else:
            # In progress (unchecked, or has incomplete children)
            in_progress.append({
                "text": normalize_text(item["text"]),
                "children": child_completed + child_in_progress
            })

    return completed, in_progress


def collect_weekly_notes(config_path="config.json"):
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(
            f"config.json not found at: {config_path}\n"
            "Please run the daily-work-log-manager skill to create it."
        )

    with open(config_file, encoding='utf-8') as f:
        config = json.load(f)

    if "vault_path" not in config:
        raise KeyError("'vault_path' is required in config.json")
    if "daily_notes_path" not in config:
        raise KeyError("'daily_notes_path' is required in config.json")

    vault_path = Path(config["vault_path"]).expanduser()
    daily_notes_path = config["daily_notes_path"]
    all_sections = normalize_project_sections(config.get("project_sections"))

    # Exclude "기타" section
    project_sections = [s for s in all_sections if s != EXCLUDE_SECTION]

    # Calculate previous week range
    today = datetime.now().date()
    monday, sunday = get_week_range(today)

    # Build week label (e.g., "2/16 ~ 2/22")
    week_label = f"{monday.month}/{monday.day} ~ {sunday.month}/{sunday.day}"

    # Collect data per day
    files_found = []
    files_missing = []
    merged_projects = {section: [] for section in project_sections}
    # meetings per project: { project_name: [{"text", "date", "children"}] }
    project_meetings = {section: [] for section in project_sections}

    current = monday
    while current <= sunday:
        file_path = build_file_path(vault_path, daily_notes_path, current)
        date_str = current.strftime('%Y-%m-%d')

        if file_path.exists():
            files_found.append(date_str)
            try:
                content = file_path.read_text(encoding='utf-8')
                day_todos = parse_todos_section(content, project_sections)
                day_meetings = parse_meetings_section(content)

                for section in project_sections:
                    if section in day_todos and day_todos[section]:
                        merge_project_items(merged_projects[section], day_todos[section])

                date_label = f"{current.month}/{current.day}"
                for meeting in day_meetings:
                    project = assign_meeting_to_project(meeting["text"], project_sections)
                    if project is None:
                        continue
                    # Check for duplicate meeting title in project_meetings
                    existing = next(
                        (m for m in project_meetings[project] if m["text"] == meeting["text"]),
                        None
                    )
                    if existing is None:
                        project_meetings[project].append({
                            "text": meeting["text"],
                            "date": date_label,
                            "children": meeting["children"]
                        })
            except Exception as e:
                # Log error but continue
                files_missing.append(date_str)
                files_found.remove(date_str)
        else:
            files_missing.append(date_str)

        current += timedelta(days=1)

    # Classify items into completed / in_progress
    projects_output = {}
    for section in project_sections:
        items = merged_projects[section]
        meetings = project_meetings[section]
        if not items and not meetings:
            continue
        completed, in_progress = classify_items(items)
        if completed or in_progress or meetings:
            projects_output[section] = {
                "completed": completed,
                "in_progress": in_progress,
                "meetings": meetings
            }

    return {
        "week_range": {
            "start": monday.strftime('%Y-%m-%d'),
            "end": sunday.strftime('%Y-%m-%d')
        },
        "week_label": week_label,
        "projects": projects_output,
        "files_found": files_found,
        "files_missing": files_missing
    }


def main():
    config_path = "config.json"
    if len(sys.argv) > 1:
        if sys.argv[1] in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)
        elif sys.argv[1] == "--config" and len(sys.argv) > 2:
            config_path = sys.argv[2]

    try:
        result = collect_weekly_notes(config_path)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
