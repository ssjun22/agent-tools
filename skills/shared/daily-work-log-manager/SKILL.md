---
name: daily-work-log-manager
description: Daily work journal manager with automatic TODO/Issue tracking from previous day. This skill should be used when users want to create daily work logs in Obsidian vault, migrate incomplete tasks from yesterday, or set up structured daily notes. Triggered when users request to create today's work log, start daily journal, or initialize daily work notes.
allowed-tools: Read, Write, Bash
---

# Daily Work Log Manager

## Overview

Automate daily work journal creation by migrating incomplete TODOs and unresolved Issues from yesterday's file to today's file in Obsidian vault. Transform manual daily note-taking into a streamlined workflow that preserves task continuity across days.

**Important:** This skill operates on Obsidian vault files with a specific directory structure: `Daily Notes/YYYY/M월/YYYY-MM-DD.md`

### Required Tools and Permissions

This skill requires the following Claude Code tools and permissions:

**Tools:**
- `Read` - Read yesterday's file and config.json
- `Write` - Create config.json and today's work log file
- `Bash` - Execute date_helper.py script and create directories (mkdir)
- `AskUserQuestion` - Interactive configuration and user confirmations

**Permissions needed:**
- File read access to Obsidian vault directory
- File write access to Obsidian vault directory
- Python script execution (date_helper.py)
- Directory creation (mkdir -p)

**Recommended:** Add the following to allowed prompts to avoid repeated confirmations:
- "Execute Python script for date calculation"
- "Create directory in Obsidian vault"
- "Write work log file to Obsidian vault"

## When to Use This Skill

Use this skill when:

- Starting the workday and need to create today's work log
- Migrating incomplete tasks from yesterday to today
- Setting up structured daily notes with TODOs, Issues, Notes, and Articles sections
- Maintaining daily work journals with automatic task tracking

## Workflow

Follow this sequential workflow to generate today's work log:

### Step 1: Check Configuration

Before running the skill for the first time, verify that `config.json` exists in the skill directory.

**First-time users:** Execute configuration setup interactively.

```bash
# Check if config.json exists
ls config.json
```

**If config.json does not exist:**

1. Use AskUserQuestion tool to collect configuration:

```
AskUserQuestion with questions:
[
  {
    "question": "Obsidian vault의 절대 경로를 입력하세요",
    "header": "Vault Path",
    "options": [
      {
        "label": "/Users/username/Documents/Obsidian Vault",
        "description": "기본 Obsidian vault 경로 예시"
      },
      {
        "label": "직접 입력",
        "description": "다른 경로 사용"
      }
    ],
    "multiSelect": false
  },
  {
    "question": "Daily Notes 경로를 입력하세요",
    "header": "Notes Path",
    "options": [
      {
        "label": "Daily Notes",
        "description": "기본값 (권장)"
      },
      {
        "label": "daily notes",
        "description": "소문자 버전"
      }
    ],
    "multiSelect": false
  }
]
```

2. Create config.json using Write tool:
   ```json
   {
     "vault_path": "/Users/username/Documents/Obsidian Vault",
     "daily_notes_path": "Daily Notes"
   }
   ```

4. Confirm creation:
   ```
   "✅ config.json이 생성되었습니다. 계속 진행합니다."
   ```

**Returning users:** Verify config.json exists and proceed to Step 2.

**Configuration priority:**
- `config.json` in skill directory (only option)

**Handle edge cases:**
- Invalid vault path: Display error and ask user to edit config.json
- Malformed JSON: Display error with correct format example

### Step 2: Calculate Dates and Paths

Execute the `scripts/date_helper.py` script to calculate today's and yesterday's dates and file paths:

```bash
python scripts/date_helper.py
```

**Output format (JSON):**
```json
{
  "today": {
    "date": "2026-02-10",
    "path": "/absolute/path/Daily Notes/2026/2월/2026-02-10.md",
    "dir": "/absolute/path/Daily Notes/2026/2월",
    "dir_exists": true
  },
  "yesterday": {
    "date": "2026-02-09",
    "path": "/absolute/path/Daily Notes/2026/2월/2026-02-09.md",
    "exists": true
  }
}
```

**Parse the JSON output** to extract:
- `today.date`: Today's date string
- `today.path`: Full path to today's file
- `today.dir`: Directory path for today's file
- `today.dir_exists`: Boolean indicating if directory exists
- `yesterday.date`: Yesterday's date string
- `yesterday.path`: Full path to yesterday's file
- `yesterday.exists`: Boolean indicating if yesterday's file exists

**Handle script errors:**
- `{"error": "..."}`: Display error message and troubleshooting guidance
- Python not installed: Inform user Python 3.6+ is required
- Permission denied: Suggest `chmod +x scripts/date_helper.py`

### Step 3: Read Yesterday's File

Check if yesterday's file exists using `yesterday.exists` from Step 2.

**Case A: Yesterday's file exists (`yesterday.exists = true`)**

Use Read tool to load yesterday's file:

```bash
# Example path from JSON
Read: /absolute/path/Daily Notes/2026/2월/2026-02-09.md
```

Proceed to Step 4 for parsing.

**Case B: Yesterday's file does not exist (`yesterday.exists = false`)**

Display message:
```
"어제 파일이 없습니다. 기본 템플릿을 사용합니다."
```

Skip to Step 7 (directory check) and use `assets/default-template.md` as the base template.

**Handle edge cases:**
- File permissions: If Read fails due to permissions, display error
- Corrupted file: If file cannot be parsed, offer to use default template

### Step 4: Parse Incomplete Items

Parse yesterday's file to extract incomplete TODOs and unresolved Issues.

**TODOs Parsing Rules:**

1. Locate the `## TODOs` section
2. Extract all lines matching pattern: `- [ ] ...` (unchecked items only)
3. **Preserve structure:**
   - Keep all indentation (spaces/tabs) exactly as written
   - Maintain hierarchical relationships (parent/child tasks)
   - Preserve project tags like `[글렌즈]` or `[프로젝트명]`
   - Keep all nested sub-tasks with their indentation

4. **Exclude completed items:**
   - Ignore lines matching `- [x] ...` (checked items)

**Example parsing:**

Input (yesterday's file):
```markdown
## TODOs
- [x] [글렌즈] 회의 자료 준비
- [ ] [글렌즈] 코드 리뷰
  - [ ] PR #123 리뷰
  - [x] PR #124 리뷰
- [ ] [사이드 프로젝트] 문서 작성
- [ ] 개인 학습
  - [ ] React 19 튜토리얼
  - [ ] 성능 최적화 아티클 읽기
```

Extracted TODOs (to migrate):
```markdown
- [ ] [글렌즈] 코드 리뷰
  - [ ] PR #123 리뷰
- [ ] [사이드 프로젝트] 문서 작성
- [ ] 개인 학습
  - [ ] React 19 튜토리얼
  - [ ] 성능 최적화 아티클 읽기
```

**Issues Parsing Rules:**

1. Locate the `## Issues` section
2. Extract all lines matching pattern: `- [ ] ...` (unchecked items only)
3. **Date tracking:**
   - If issue already has date format `(M/D~)`: Preserve it
   - If issue has no date: Add yesterday's date in format `(M/D~)`
   - Use simplified month/day format (e.g., `2/9~`, `12/31~`)

4. **Exclude resolved items:**
   - Ignore lines matching `- [x] ...` (checked items)

**Example parsing:**

Input (yesterday's file):
```markdown
## Issues
- [x] 로그인 버그 (2/8~)
- [ ] [글렌즈] 데이터베이스 연결 타임아웃
- [ ] API 응답 느림 (2/9~)
```

Extracted Issues (to migrate), assuming yesterday = 2026-02-09:
```markdown
- [ ] [글렌즈] 데이터베이스 연결 타임아웃 (2/9~)
- [ ] API 응답 느림 (2/9~)
```

**Notes and Articles:**
- Do NOT parse or migrate Notes section
- Do NOT parse or migrate Articles section
- These sections always start empty in today's file

### Step 5: Display Summary and Get User Confirmation

Display a summary of items to be migrated and use AskUserQuestion for approval.

**First, display the summary:**

```
📋 어제(YYYY-MM-DD)에서 이월할 항목:

## TODOs (N개)
[display extracted TODOs with full structure]

## Issues (N개)
[display extracted Issues with dates]
```

**Example summary:**

```
📋 어제(2026-02-09)에서 이월할 항목:

## TODOs (5개)
- [ ] [글렌즈] 코드 리뷰
  - [ ] PR #123 리뷰
- [ ] [사이드 프로젝트] 문서 작성
- [ ] 개인 학습
  - [ ] React 19 튜토리얼
  - [ ] 성능 최적화 아티클 읽기

## Issues (2개)
- [ ] [글렌즈] 데이터베이스 연결 타임아웃 (2/9~)
- [ ] API 응답 느림 (2/9~)
```

**Then use AskUserQuestion:**

```
AskUserQuestion with questions:
[
  {
    "question": "이대로 오늘 파일에 이월할까요?",
    "header": "Migration",
    "options": [
      {
        "label": "예, 이월합니다",
        "description": "위 항목들을 오늘 파일로 이월"
      },
      {
        "label": "아니오, 수정이 필요합니다",
        "description": "어제 파일을 먼저 수정하고 다시 실행"
      }
    ],
    "multiSelect": false
  }
]
```

**User response handling:**

- User selects "예, 이월합니다": Proceed to Step 6
- User selects "아니오, 수정이 필요합니다": Display message and exit:
  ```
  "어제 파일을 수정한 후 다시 실행하세요."
  ```

### Step 6: Check and Create Directory

Check if today's month directory exists using `today.dir_exists` from Step 2.

**Case A: Directory exists (`today.dir_exists = true`)**

Proceed to Step 7.

**Case B: Directory does not exist (`today.dir_exists = false`)**

1. Use AskUserQuestion for confirmation:

```
Display: "월별 디렉토리가 없습니다: YYYY/M월"

AskUserQuestion with questions:
[
  {
    "question": "디렉토리를 생성할까요?",
    "header": "Directory",
    "options": [
      {
        "label": "예, 생성합니다",
        "description": "월별 디렉토리 자동 생성"
      },
      {
        "label": "아니오, 수동으로 생성하겠습니다",
        "description": "스킬 종료"
      }
    ],
    "multiSelect": false
  }
]
```

2. If user selects "예, 생성합니다":
   ```bash
   mkdir -p "/absolute/path/Daily Notes/YYYY/M월"
   ```

3. Confirm creation:
   ```
   "✅ 디렉토리가 생성되었습니다."
   ```

4. If user selects "아니오": Exit skill

**Handle errors:**
- Permission denied: Display error and check vault path permissions
- Parent directory (vault) doesn't exist: Display error and verify config.json

### Step 7: Create Today's File

Generate today's work log file using Write tool.

**File structure:**

```markdown
# YYYY-MM-DD

## TODOs
[migrated TODOs from Step 4, or empty if using default template]

## Issues
[migrated Issues from Step 4 with dates, or empty if using default template]

## Notes

## Articles
```

**If using default template** (no yesterday file):

Use content from `assets/default-template.md` with `{DATE}` replaced by `today.date`.

**If migrating from yesterday**:

1. Start with header: `# {today.date}`
2. Add TODOs section with migrated items (preserve indentation/structure)
3. Add Issues section with migrated items (with dates)
4. Add empty Notes section: `## Notes\n\n`
5. Add empty Articles section: `## Articles\n\n`

**Write the file:**

```bash
Write: /absolute/path/Daily Notes/YYYY/M월/YYYY-MM-DD.md
[content as structured above]
```

**Handle file conflicts:**

If today's file already exists, use AskUserQuestion:

```
Display: "⚠️ 오늘 파일(YYYY-MM-DD.md)이 이미 존재합니다."

AskUserQuestion with questions:
[
  {
    "question": "기존 파일을 덮어쓸까요?",
    "header": "File Exists",
    "options": [
      {
        "label": "예, 덮어씁니다",
        "description": "기존 내용이 삭제되고 새로 생성됩니다"
      },
      {
        "label": "아니오, 취소합니다",
        "description": "스킬 종료 (기존 파일 유지)"
      }
    ],
    "multiSelect": false
  }
]
```

- If user selects "예, 덮어씁니다": Overwrite file
- If user selects "아니오, 취소합니다": Exit skill

### Step 8: Confirm Completion

After successfully creating today's file, display completion message:

```
✅ 오늘 업무 일지가 생성되었습니다!

📂 파일 위치: Daily Notes/YYYY/M월/YYYY-MM-DD.md

📋 이월된 항목:
- TODOs: N개
- Issues: N개

Obsidian에서 파일을 열어 작업을 시작하세요.
```

**If using default template** (no migration):

```
✅ 오늘 업무 일지가 생성되었습니다!

📂 파일 위치: Daily Notes/YYYY/M월/YYYY-MM-DD.md

기본 템플릿이 적용되었습니다. Obsidian에서 파일을 열어 작업을 시작하세요.
```

## Common Usage Patterns

### Pattern 1: Standard Morning Routine

```
User: "오늘 업무 일지 만들어줘"
User: "/daily-work-log"
```

→ Execute full workflow with yesterday's file migration

### Pattern 2: First-Time Setup

```
User: "/daily-work-log"
```

→ Prompt for config.json setup, then execute with default template

### Pattern 3: Month Transition

```
User: "/daily-work-log" (on first day of new month)
```

→ Prompt for new month directory creation, then proceed

### Pattern 4: Restart Workflow

```
User: "다시 일지 만들어줘" (after declining migration)
```

→ Re-run from Step 2 after user edits yesterday's file

## File Structure Reference

### Template Sections

**TODOs Section:**
- Purpose: Track daily tasks with checkbox completion
- Format: `- [ ] Task description`
- Supports: Nested sub-tasks, project tags, hierarchical structure
- Migration: Only unchecked items carry over to next day

**Issues Section:**
- Purpose: Track ongoing problems/bugs with date tracking
- Format: `- [ ] Issue description (M/D~)`
- Date tracking: Auto-added on first occurrence, preserved on migration
- Migration: Only unchecked items carry over with date

**Notes Section:**
- Purpose: Free-form memo space for daily reflections
- Format: Unstructured markdown
- Migration: Never migrates (always starts empty)

**Articles Section:**
- Purpose: URL collection for reference or other skill integration
- Format: Plain URLs (one per line)
- Migration: Never migrates (always starts empty)
- Use case: Feed to articles-summarizer skill or other URL processors

## Troubleshooting

### "config.json not found"

→ Run the skill and complete the interactive configuration setup (Step 1)

### "vault_path doesn't exist"

→ Verify Obsidian vault path in config.json is correct and absolute

### "Python not installed" or "python: command not found"

→ Install Python 3.6+ from https://python.org and ensure it's in PATH

### "Permission denied" (script execution)

→ Run: `chmod +x scripts/date_helper.py`

### "Permission denied" (file write)

→ Check vault directory permissions and ensure write access

### "Yesterday's file format is unexpected"

→ Verify yesterday's file has `## TODOs` and `## Issues` section headers

→ If format is broken, decline migration and choose default template option

### "Today's file already exists"

→ Decide whether to overwrite or manually edit the existing file

→ Consider backing up existing file before overwriting

## Dependencies

**System requirements:**

- Python 3.6+ (standard library only, no external packages)
- Obsidian vault (local file system)
- File system write permissions for vault directory

**No external dependencies** - Uses only Python standard library.

## Resources

### scripts/date_helper.py

Python script for date calculation and path generation. Provides today/yesterday dates and file paths in JSON format.

**Input:** config.json path (default: `./config.json`)

**Output:** JSON with today and yesterday information

**Usage:**
```bash
python scripts/date_helper.py [--config CONFIG_PATH]
```

### assets/default-template.md

Default template used when yesterday's file doesn't exist (first-time use or missing file).

Contains placeholder sections with guidance text for each section (TODOs, Issues, Notes, Articles).

### config.json (user-created)

User configuration file created interactively on first run. Not included in the skill package.

**Format:**
```json
{
  "vault_path": "/absolute/path/to/vault",
  "daily_notes_path": "Daily Notes"
}
```

**Location:** Skill directory root

**Git:** Excluded via .gitignore (user-specific configuration)

## Notes

- This skill operates entirely within Claude Code; no external API calls required
- Parsing and migration logic is performed by Claude using Read/Write tools
- The script only handles date calculations; all content processing is done by Claude
- Complex TODO structures (nested, tagged) are preserved through exact indentation matching
- Date format uses Korean month notation (e.g., "2월") for natural language consistency
- Files use YYYY-MM-DD.md naming for chronological sorting and international compatibility
