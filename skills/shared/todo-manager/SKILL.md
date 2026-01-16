---
name: todo-manager
description: Manage and prioritize TODO tasks from the todos/ directory. Use this skill when users ask about next tasks, want to see their TODO list, or need guidance on what to work on next. Scans all TODO files, sorts by priority, and recommends the next action.
---

# TODO Manager

## Overview

This skill manages TODO tasks by scanning the `todos/` directory, parsing TODO markdown files created with the `todo-maker` skill, and presenting them in priority order. It helps users stay focused by recommending the next highest-priority task to work on.

## When to Use This Skill

Use this skill when:

- User asks "What should I work on next?"
- User wants to see their TODO list
- User asks about current tasks or priorities
- User needs guidance on task prioritization
- At the start of a work session to identify the next task

## Workflow

### Step 1: Scan and Parse TODOs

Execute the parsing script to scan all TODO files:

```bash
python .claude/skills/todo-manager/scripts/parse_todos.py
```

The script will:

1. Locate the `todos/` directory (searches current and up to 3 parent directories)
2. Find all `.md` files in the directory
3. Parse each file to extract:
    - File name and title
    - Creation date
    - Task type (버그 수정, 리팩토링, etc.)
    - Priority level (Critical, High, Medium, Low)
    - Background summary
    - Problem description
    - TODO checklist items
    - Related file paths
4. Sort all TODOs by priority (Critical → High → Medium → Low)
5. Output results as JSON

### Step 2: Interpret Results

The script outputs JSON in the following format:

```json
{
	"todos_directory": "/path/to/todos",
	"todos_count": 3,
	"todos": [
		{
			"file": "fix-login-bug.md",
			"title": "버그 수정",
			"created_date": "2026-01-10",
			"type": "버그 수정",
			"priority": "Critical",
			"priority_level": 0,
			"background": "사용자 피드백을 통해 발견...",
			"problem": "로그인 페이지에서 에러 발생...",
			"todo_items": ["버그 원인 분석", "수정 방안 설계", "코드 수정"],
			"related_files": ["src/components/login/login-form.tsx"]
		}
	]
}
```

**Priority Levels:**

- `0` = Critical (최우선)
- `1` = High (높음)
- `2` = Medium (보통)
- `3` = Low (낮음)
- `999` = Unknown (우선순위 미지정)

### Step 3: Recommend Next Task

Based on the parsed results:

1. **Identify the highest-priority task**: The first item in the sorted `todos` array
2. **Present task details to user**:
    - Task title and type
    - Priority level
    - Background context
    - Problem description
    - Checklist of TODO items
    - Related files
3. **Ask user if they want to start**: "이 작업을 시작하시겠습니까?"
4. **If user agrees, begin working**: Start addressing the TODO items in order

### Step 4: Guide Task Execution

When user agrees to work on a task:

1. Read the full TODO file for complete details
2. Read related files to understand current state
3. Work through TODO checklist items sequentially
4. Provide updates as each item is completed
5. Ask user about archiving when all items are done

## Example Interaction

**User:** "다음에 뭐 해야 해?"

**Assistant Actions:**

1. Run `parse_todos.py` script
2. Parse JSON output
3. Identify highest-priority task

**Assistant Response:**

```
현재 3개의 TODO가 있습니다.

가장 우선순위가 높은 작업:
📌 [Critical] 버그 수정 - 로그인 페이지 에러

작성일: 2026-01-10
배경: 사용자 피드백을 통해 로그인 페이지에서 에러가 발견됨...
문제: 특정 조건에서 로그인이 실패하는 버그...

TODO 항목:
- [ ] 버그 원인 분석
- [ ] 수정 방안 설계
- [ ] 코드 수정
- [ ] 테스트 케이스 작성

관련 파일:
- src/components/login/login-form.tsx

이 작업을 시작하시겠습니까?
```

## Error Handling

### No todos/ Directory Found

If the script cannot find the `todos/` directory:

```json
{
	"error": "todos/ directory not found",
	"message": "Could not find todos/ directory in current or parent directories"
}
```

**Response:** Inform user that no `todos/` directory exists and ask if they want to create one.

### No TODO Files Found

If `todos/` exists but contains no `.md` files:

```json
{
	"error": "No TODO files found",
	"message": "No .md files found in /path/to/todos",
	"todos_count": 0,
	"todos": []
}
```

**Response:** Inform user there are no pending tasks and congratulate them, or offer to create a new TODO.

## Best Practices

1. **Always run the script first**: Don't guess or assume TODO contents—always scan the directory
2. **Present one task at a time**: Focus user attention on the single highest-priority task
3. **Be specific**: Show concrete TODO items and related files
4. **Encourage action**: Ask if user wants to start the task
5. **Track progress**: As TODO items are completed, acknowledge progress
6. **Remind about archiving**: When all items are done, remind user to archive the completed TODO

## Notes

- The skill assumes TODO files follow the `todo-maker` format
- Completed TODOs are archived and removed from `todos/`, so only pending tasks appear
- Priority is determined by which checkbox is marked with `[x]` in the priority section
- The script searches up to 3 parent directories to find `todos/`, making it flexible for different working directories
