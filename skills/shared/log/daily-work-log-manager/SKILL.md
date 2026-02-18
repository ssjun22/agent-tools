---
name: daily-work-log-manager
description: Daily work journal manager with automatic TODO/Issue/Notes tracking from previous day. This skill should be used when users want to create daily work logs in Obsidian vault, migrate incomplete tasks from yesterday, or set up structured daily notes. Triggered when users request to create today's work log, start daily journal, or initialize daily work notes.
allowed-tools: Read, Write, Bash
---

# Daily Work Log Manager

## Overview

Automate daily work journal creation by migrating incomplete TODOs, unresolved Issues, and incomplete Notes from yesterday's file to today's file in Obsidian vault. Transform manual daily note-taking into a streamlined workflow that preserves task continuity across days.

**Important:** This skill operates on Obsidian vault files with a specific directory structure: `Daily Notes/YYYY/M월/YYYY-MM-DD.md`

### Required Tools and Permissions

This skill requires the following tools and permissions:

**Tools:**
- `Read` - Read yesterday's file and config.json
- `Write` - Create config.json and today's work log file
- `Bash` - Execute date_helper.py script and create directories (mkdir)
- Interactive user prompts (chat or runtime-supported question tool) - Configuration and confirmations

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
- Setting up structured daily notes with TODOs, Meetings, Issues, Notes, and Articles sections
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

1. Ask the user the following configuration questions:

```
Question template:
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
  },
  {
    "question": "TODO 기본 프로젝트 섹션을 선택하세요",
    "header": "Projects",
    "options": [
      {
        "label": "프로젝트A, 프로젝트B, 기타",
        "description": "기본 프로젝트 섹션 사용 (권장)"
      },
      {
        "label": "생성 후 직접 수정",
        "description": "config.json의 project_sections를 원하는 값으로 수정"
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
     "daily_notes_path": "Daily Notes",
     "project_sections": ["프로젝트A", "프로젝트B", "기타"]
   }
   ```

3. Confirm creation:
   ```
   "✅ config.json이 생성되었습니다. 계속 진행합니다."
   ```

**Returning users:** Verify config.json exists and proceed to Step 2.

**Configuration priority:**
- `config.json` in skill directory (only option)

**Handle edge cases:**
- Invalid vault path: Display error and ask user to edit config.json
- Malformed JSON: Display error with correct format example
- `project_sections` missing/empty/invalid: Fallback to `["프로젝트A", "프로젝트B", "기타"]`

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
  },
  "config": {
    "project_sections": ["프로젝트A", "프로젝트B", "기타"]
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
- `config.project_sections`: TODO 기본 프로젝트 섹션 목록

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

Parse yesterday's file to extract incomplete TODOs, unresolved Issues, and incomplete Notes.

**Origin Date Tracking Rule (all sections):**

이월 시 `- [ ]` 항목에 시작일 `(M/D~)` 을 계층적으로 추가합니다:
- 이미 `(M/D~)` 가 있는 항목: **그대로 유지** (최초 시작일 보존)
- `(M/D~)` 가 없는 항목: **어제 날짜를 `(M/D~)` 형식으로 추가**
- **계층적 날짜 규칙** (중복 제거):
  - 부모와 모든 직계 자식이 **같은 날짜**인 경우: 부모에만 날짜 표시, 자식은 생략
  - 자식이 **다른 날짜**를 가진 경우: 해당 자식에만 별도 날짜 표시
  - 형제 항목 간에도 같은 날짜면 가장 상위 공통 부모에만 표시
  - 이를 통해 가독성을 높이고 불필요한 날짜 중복을 제거
- 날짜는 0 패딩 없이 표기 (예: `(2/9~)`, `(12/1~)`)
- `[x]` 항목이나 plain text 항목(프로젝트명 헤더 등)에는 날짜를 추가하지 않음
- 날짜는 항목 텍스트 맨 끝에 공백 하나 후 추가: `- [ ] 내용 (M/D~)`

**TODOs Parsing Rules:**

1. Locate the `## TODOs` section
2. **TODOs는 프로젝트별 그룹 구조를 사용:**
   - 프로젝트명은 `- 프로젝트명` 형식의 plain text bullet (체크박스 없음)
   - TODO 항목은 프로젝트명 아래 들여쓰기된 `- [ ] ...` 형식
3. **Preserve structure:**
   - Keep all indentation (spaces/tabs) exactly as written
   - Maintain hierarchical relationships (project → task → sub-task)
   - Keep all nested sub-tasks with their indentation
   - **Preserve inline formatting exactly as written:** `==highlight==`, `**bold**`, `*italic*`, `<mark>...</mark>` etc.
   - Do NOT strip or modify any inline markdown syntax within item text

4. **Handle nested TODOs with completed parents:**
   - If parent is `[x]` but has child `[ ]` items: Include entire tree (parent + all children)
   - Preserve parent's `[x]` status to maintain context

5. **Include project header if it has unchecked children:**
   - If a project group has any `[ ]` items, include the project name header
   - Exclude project groups where all items are `[x]` (fully completed)

6. **Exclude fully completed items:**
   - Only ignore `[x]` items that have no unchecked children

7. **Exclude template placeholders:**
   - Skip items matching: `오늘 할 일을 작성하세요` or similar placeholder text

8. **Add origin date:** Apply Origin Date Tracking Rule to all `- [ ]` items

**Example parsing:**

Input (yesterday's file, date = 2026-02-09):
```markdown
## TODOs
- 프로젝트A
	- [x] 회의 자료 준비
	- [ ] ==코드 리뷰==
		- [ ] PR #123 리뷰
		- [x] PR #124 리뷰
- 프로젝트B
	- [x] 유형 4,5 에이전트 개발
		- [ ] 테스트 구조 잡아야지 않을까?
- 기타
	- [ ] 문서 작성 (2/7~)
	- [ ] 개인 학습
		- [ ] React 19 튜토리얼
		- [ ] 성능 최적화 아티클 읽기
	- [ ] 오늘 할 일을 작성하세요
```

Extracted TODOs (to migrate):
```markdown
- 프로젝트A
	- [ ] ==코드 리뷰== (2/9~)
		- [ ] PR #123 리뷰
- 프로젝트B
	- [x] 유형 4,5 에이전트 개발
		- [ ] 테스트 구조 잡아야지 않을까? (2/9~)
- 기타
	- [ ] 문서 작성 (2/7~)
	- [ ] 개인 학습 (2/9~)
		- [ ] React 19 튜토리얼
		- [ ] 성능 최적화 아티클 읽기
```

Note:
- `프로젝트A` header is included (has unchecked children)
- `[x] 회의 자료 준비` is excluded (fully completed, no children)
- `[x] 유형 4,5 에이전트 개발` is included (has unchecked child) but no date added (it's `[x]`)
- `오늘 할 일을 작성하세요` is excluded (template placeholder)
- `문서 작성 (2/7~)` preserves existing origin date
- **`==코드 리뷰==` highlight is preserved exactly** — origin date appended after the closing `==`
- **Hierarchical date rule applied:** child items under same-dated parents have dates removed
  - `==코드 리뷰== (2/9~)` parent has date, child `PR #123 리뷰` inherits from parent
  - `개인 학습 (2/9~)` parent has date, children inherit from parent

**Issues Parsing Rules:**

1. Locate the `## Issues` section
2. Extract all lines matching pattern: `- [ ] ...` (unchecked items only)
3. **Exclude template placeholders:**
   - Skip items containing: `발생한 문제를 기록하세요`, `발생한 이슈를 기록하세요`, or similar placeholder text
   - Skip items with `(예:` pattern (example indicators)

4. **Exclude resolved items:**
   - Ignore lines matching `- [x] ...` (checked items)

5. **Add origin date:** Apply Origin Date Tracking Rule to all `- [ ]` items

**Example parsing:**

Input (yesterday's file, date = 2026-02-09):
```markdown
## Issues
- [x] 로그인 버그 (2/8~)
- [ ] 발생한 문제를 기록하세요 (예: 로그인 API 500 에러)
- [ ] [프로젝트A] 데이터베이스 연결 타임아웃
- [ ] API 응답 느림 (2/8~)
```

Extracted Issues (to migrate):
```markdown
- [ ] [프로젝트A] 데이터베이스 연결 타임아웃 (2/9~)
- [ ] API 응답 느림 (2/8~)
```

Note:
- `로그인 버그` is excluded (resolved with `[x]`)
- `발생한 문제를 기록하세요` is excluded (template placeholder)
- `데이터베이스 연결 타임아웃` gets `(2/9~)` added (no existing date)
- `API 응답 느림 (2/8~)` preserves existing origin date

**Notes Parsing Rules:**

1. Locate the `## Notes` section
2. Extract all lines matching pattern: `- [ ] ...` (unchecked items only) and their parent context
3. **Include parent context for nested `[ ]` items:**
   - If a `- [ ]` item is nested under a plain text bullet, include the parent bullet for context
   - Preserve indentation hierarchy
4. **Exclude template placeholders:**
   - Skip items containing: `자유롭게 메모를 작성하세요` or similar placeholder text
5. **Exclude resolved items:**
   - Ignore lines matching `- [x] ...` (checked items)

6. **Add origin date:** Apply Origin Date Tracking Rule to all `- [ ]` items

**Example parsing:**

Input (yesterday's file, date = 2026-02-09):
```markdown
## Notes
- openspec 기반 SDD 전략 정리중
	- openspec을 single source로 한다는 내용을 rules에 명시
	- [ ] 이미 존재하는 코드 기반으로 spec을 정리해야하는 경우 구현중 (seed)
	- [ ] 이미 존재하는 spec에서 변경사항이 생긴 케이스 테스트 필요 (2/8~)
- 점심 메뉴 고민
```

Extracted Notes (to migrate):
```markdown
- openspec 기반 SDD 전략 정리중
	- [ ] 이미 존재하는 코드 기반으로 spec을 정리해야하는 경우 구현중 (seed) (2/9~)
	- [ ] 이미 존재하는 spec에서 변경사항이 생긴 케이스 테스트 필요 (2/8~)
```

Note:
- Parent bullet `openspec 기반 SDD 전략 정리중` is included for context (has `[ ]` children), no date added (plain text)
- Plain text child `openspec을 single source로...` is excluded (no `[ ]`)
- `점심 메뉴 고민` is excluded (no `[ ]` items)
- `spec 정리 구현중` gets `(2/9~)` added (no existing date)
- `변경사항 테스트 필요 (2/8~)` preserves existing origin date (different from yesterday)
- Since the two `[ ]` items have different dates, each keeps its own date

**Example with hierarchical date rule:**

Input (yesterday's file, date = 2026-02-14):
```markdown
## Notes
- openspec 기반 SDD 전략 정리중
	- [ ] verify-spec 추가했음
		- [ ] commands, skill 차이 확인 필요
		- [ ] seed 이후 verify-spec 정리 필요
		- [ ] codex에선 어떻게 쓰지?
```

Extracted Notes (to migrate):
```markdown
- openspec 기반 SDD 전략 정리중
	- [ ] verify-spec 추가했음 (2/14~)
		- [ ] commands, skill 차이 확인 필요
		- [ ] seed 이후 verify-spec 정리 필요
		- [ ] codex에선 어떻게 쓰지?
```

Note:
- **Hierarchical date rule applied:** parent `verify-spec 추가했음` has date, all children inherit (no duplicate dates)
- All items started on the same date (2/14), so only the parent shows `(2/14~)`
- This improves readability by removing redundant date markers

**Articles:**
- Do NOT parse or migrate Articles section
- Articles section always starts empty in today's file

### Step 5: Display Summary and Get User Confirmation

Display a summary of items to be migrated and ask for explicit approval.

**First, display the summary:**

```
📋 어제(YYYY-MM-DD)에서 이월할 항목:

## TODOs (N개)
[display extracted TODOs with full structure]

## Issues (N개)
[display extracted Issues]

## Notes (N개)
[display extracted Notes with [ ] items and parent context]
```

**Example summary:**

```
📋 어제(2026-02-09)에서 이월할 항목:

## TODOs (5개)
- 프로젝트A
	- [ ] 코드 리뷰 (2/9~)
		- [ ] PR #123 리뷰 (2/9~)
- 기타
	- [ ] 문서 작성 (2/7~)
	- [ ] 개인 학습 (2/9~)
		- [ ] React 19 튜토리얼 (2/9~)
		- [ ] 성능 최적화 아티클 읽기 (2/9~)

## Issues (2개)
- [ ] [프로젝트A] 데이터베이스 연결 타임아웃 (2/9~)
- [ ] API 응답 느림 (2/8~)

## Notes (2개)
- openspec 기반 SDD 전략 정리중
	- [ ] spec 정리 구현중 (seed) (2/9~)
	- [ ] 변경사항이 생긴 케이스 테스트 필요 (2/8~)
```

**Then ask the user:**

```
Question template:
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

1. Ask for confirmation:

```
Display: "월별 디렉토리가 없습니다: YYYY/M월"

Question template:
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
[migrated TODOs from Step 4, or config.project_sections 기반 project template if no items to migrate]

## Meetings
- (회의 내용을 기록하세요)

## Issues
[migrated Issues from Step 4 without inline dates, or "- [ ] (발생한 이슈를 기록하세요)" if no items to migrate]

## Notes
[migrated Notes with [ ] items from Step 4, or "- (자유롭게 메모를 작성하세요)" if no items to migrate]

## Articles
- (관심있는 기사 URL을 입력하세요)
```

**If using default template** (no yesterday file):

Use content from `assets/default-template.md` with two replacements:
- `{DATE}` → `today.date`
- `{PROJECT_TODOS}` → `config.project_sections`를 아래 형식으로 렌더링한 문자열
  - 형식: `프로젝트명` 줄 다음 `- [ ] (오늘 할 일을 작성하세요)`
  - 각 프로젝트 블록 사이에 빈 줄 1개 추가

**If migrating from yesterday**:

1. Start with header: `# {today.date}`
2. Add TODOs section:
   - If items to migrate: Add migrated TODOs (preserve indentation/structure)
   - If no items: Build project template from `config.project_sections`
     ```markdown
     {project_name_1}
     - [ ] (오늘 할 일을 작성하세요)

     {project_name_2}
     - [ ] (오늘 할 일을 작성하세요)

     {project_name_3}
     - [ ] (오늘 할 일을 작성하세요)
     ```
3. Add Meetings section with placeholder: `## Meetings\n- (회의 내용을 기록하세요)\n\n`
4. Add Issues section:
   - If items to migrate: Add migrated Issues (without inline dates)
   - If no items: Add placeholder: `- [ ] (발생한 이슈를 기록하세요)`
5. Add Notes section:
   - If `[ ]` items to migrate: Add migrated Notes (with parent context)
   - If no items: Add placeholder: `- (자유롭게 메모를 작성하세요)`
6. Add Articles section with placeholder: `## Articles\n- (관심있는 기사 URL을 입력하세요)\n\n`

**Write the file:**

```bash
Write: /absolute/path/Daily Notes/YYYY/M월/YYYY-MM-DD.md
[content as structured above]
```

**Handle file conflicts:**

If today's file already exists, ask whether to overwrite:

```
Display: "⚠️ 오늘 파일(YYYY-MM-DD.md)이 이미 존재합니다."

Question template:
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
- Notes: N개

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
- Default format (from `config.project_sections`):
  ```markdown
  {project_name}
  - [ ] (오늘 할 일을 작성하세요)
  ```
- Default value when config is missing/invalid: `["프로젝트A", "프로젝트B", "기타"]`
- Supports: Nested sub-tasks, project tags, hierarchical structure
- Migration: Only unchecked items carry over to next day

**Meetings Section:**
- Purpose: Record meeting notes and discussions
- Format: Unstructured markdown
- Migration: Never migrates (always starts empty)

**Issues Section:**
- Purpose: Track ongoing problems/bugs
- Format: `- [ ] Issue description`
- Migration: Only unchecked items carry over (inline dates removed if present)

**Notes Section:**
- Purpose: Free-form memo space for daily reflections
- Format: Unstructured markdown with optional `- [ ]` tasks
- Migration: Only `- [ ]` items (and their parent context) carry over to next day

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

Contains placeholders for dynamic rendering:
- `{DATE}` for title date
- `{PROJECT_TODOS}` for TODO blocks generated from `config.project_sections`

### config.json (user-created)

User configuration file created interactively on first run. Not included in the skill package.

**Format:**
```json
{
  "vault_path": "/absolute/path/to/vault",
  "daily_notes_path": "Daily Notes",
  "project_sections": ["프로젝트A", "프로젝트B", "기타"]
}
```

**Location:** Skill directory root

**Git:** Excluded via .gitignore (user-specific configuration)

## Notes

- This skill operates entirely within Claude Code; no external API calls required
- Parsing and migration logic is performed by Claude using Read/Write tools
- The script handles date/path calculation and normalized `project_sections`; content parsing is done by Claude
- Complex TODO structures (nested, tagged) are preserved through exact indentation matching
- Date format uses Korean month notation (e.g., "2월") for natural language consistency
- Files use YYYY-MM-DD.md naming for chronological sorting and international compatibility
