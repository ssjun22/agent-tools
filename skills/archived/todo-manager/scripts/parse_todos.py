#!/usr/bin/env python3
"""
TODO Parser Script

Scans the todos/ directory for markdown files, parses their content,
and sorts them by priority.
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Optional


def find_todos_dir() -> Optional[Path]:
    """Find the todos/ directory starting from current directory."""
    current = Path.cwd()

    # Check current directory and .claude subdirectory
    for subpath in ["todos", ".claude/todos"]:
        todos_dir = current / subpath
        if todos_dir.exists() and todos_dir.is_dir():
            return todos_dir

    # Check parent directories (up to 3 levels)
    for _ in range(3):
        current = current.parent
        for subpath in ["todos", ".claude/todos"]:
            todos_dir = current / subpath
            if todos_dir.exists() and todos_dir.is_dir():
                return todos_dir

    return None


def parse_priority(content: str) -> tuple[str, int]:
    """
    Parse priority from content.
    Returns (priority_name, priority_level) where lower level = higher priority.
    """
    priority_patterns = [
        (r"- \[x\] 긴급 \(Critical\)", "Critical", 0),
        (r"- \[x\] 높음 \(High\)", "High", 1),
        (r"- \[x\] 보통 \(Medium\)", "Medium", 2),
        (r"- \[x\] 낮음 \(Low\)", "Low", 3),
    ]

    for pattern, name, level in priority_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return name, level

    return "Unknown", 999


def extract_section(content: str, section_name: str) -> str:
    """Extract content of a specific section."""
    # Pattern to match section header and capture content until next ## header
    pattern = rf"## {re.escape(section_name)}\s*\n(.*?)(?=\n##|\Z)"
    match = re.search(pattern, content, re.DOTALL)

    if match:
        section_content = match.group(1).strip()
        # Remove HTML comments
        section_content = re.sub(r"<!--.*?-->", "", section_content, flags=re.DOTALL)
        return section_content.strip()

    return ""


def extract_todo_items(content: str) -> List[str]:
    """Extract TODO checklist items."""
    todo_section = extract_section(content, "TODO")

    if not todo_section:
        return []

    # Find all checkbox items
    items = re.findall(r"- \[ \] (.+)", todo_section)
    return [item.strip() for item in items]


def extract_related_files(content: str) -> List[str]:
    """Extract related file paths."""
    related_section = extract_section(content, "관련 파일")

    if not related_section:
        return []

    # Find all code-formatted paths
    files = re.findall(r"`([^`]+)`", related_section)
    return [f.strip() for f in files if f.strip() and not f.startswith("path/to")]


def parse_todo_file(file_path: Path) -> Optional[Dict]:
    """Parse a single TODO markdown file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract basic fields
        title = content.split("\n")[0].replace("#", "").strip()
        created_date = extract_section(content, "작성일")
        task_type = extract_section(content, "타입")
        background = extract_section(content, "배경")
        problem = extract_section(content, "문제 상황")

        # Parse priority
        priority_name, priority_level = parse_priority(content)

        # Extract TODO items and related files
        todo_items = extract_todo_items(content)
        related_files = extract_related_files(content)

        return {
            "file": file_path.name,
            "title": title,
            "created_date": created_date,
            "type": task_type,
            "priority": priority_name,
            "priority_level": priority_level,
            "background": background[:200] + "..." if len(background) > 200 else background,
            "problem": problem[:200] + "..." if len(problem) > 200 else problem,
            "todo_items": todo_items,
            "related_files": related_files,
        }

    except Exception as e:
        print(f"Error parsing {file_path}: {e}", file=sys.stderr)
        return None


def main():
    """Main function to parse and display TODOs."""
    # Find todos directory
    todos_dir = find_todos_dir()

    if not todos_dir:
        print(json.dumps({
            "error": "todos/ directory not found",
            "message": "Could not find todos/ directory in current or parent directories"
        }, indent=2, ensure_ascii=False))
        sys.exit(1)

    # Find all markdown files
    md_files = list(todos_dir.glob("*.md"))

    if not md_files:
        print(json.dumps({
            "error": "No TODO files found",
            "message": f"No .md files found in {todos_dir}",
            "todos_count": 0,
            "todos": []
        }, indent=2, ensure_ascii=False))
        sys.exit(0)

    # Parse all files
    todos = []
    for md_file in md_files:
        parsed = parse_todo_file(md_file)
        if parsed:
            todos.append(parsed)

    # Sort by priority level (lower = higher priority)
    todos.sort(key=lambda x: x["priority_level"])

    # Output results
    result = {
        "todos_directory": str(todos_dir),
        "todos_count": len(todos),
        "todos": todos
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
