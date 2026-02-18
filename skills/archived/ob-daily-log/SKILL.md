---
name: ob:daily-log
description: This skill should be used when users want to automatically generate a professional daily work log by analyzing today's git commits and code changes. It creates a structured markdown note in an Obsidian vault, summarizing key accomplishments, code changes, issues, and plans. Trigger phrases include "create today's log", "generate daily note", "make work log", or when users mention daily logging or Obsidian daily notes.
disable-model-invocation: true
---

# Obsidian Daily Log Generator

## Overview

Automatically generate professional daily work logs by analyzing git commit history and code changes. This skill eliminates manual logging effort by intelligently inferring business logic improvements and key accomplishments from code diffs, creating a structured Obsidian-compatible markdown note.

## When to Use This Skill

Use this skill when:
- User requests a daily work log or daily note
- User mentions creating an Obsidian daily log
- User wants to summarize today's coding work
- User asks to analyze git changes for logging purposes
- Trigger phrases: "create today's log", "generate daily note", "make daily work log"

## Configuration

This skill uses a single configuration file located at `skills/shared/ob-daily-log/.env`.

Before first use, edit the `.env` file to set:
1. **OBSIDIAN_VAULT_PATH**: Absolute path to your Obsidian vault (required)
2. **BASE_DIR**: Base directory within vault for organizing daily logs (default: `ob-glens`)
3. **USE_PROJECT_ROOT**: Whether to organize logs by project (default: `false`)
4. **FILTER_AUTHOR**: Filter commits by author - `me` (default) or `all`
5. **Project mappings**: Optional mappings from project paths to Obsidian folder names (only if USE_PROJECT_ROOT=true)

The daily notes will be saved to:
- If `USE_PROJECT_ROOT=false`: `{OBSIDIAN_VAULT_PATH}/{BASE_DIR}/Daily/YYYY-MM-DD.md`
- If `USE_PROJECT_ROOT=true`: `{OBSIDIAN_VAULT_PATH}/{BASE_DIR}/{PROJECT_ROOT}/Daily/YYYY-MM-DD.md`

Default structure: `ObsidianVault/ob-glens/Daily/YYYY-MM-DD.md`

### Configuration File Structure

**Location**: `skills/shared/ob-daily-log/.env`

**Required setting**:
```bash
OBSIDIAN_VAULT_PATH=/Users/yourusername/Documents/ObsidianVault
```

**Optional base directory** (default: `ob-glens`):
```bash
# Base directory within vault for organizing all daily logs
BASE_DIR=ob-glens
```

**Optional project root organization** (default: `false`):
```bash
# Set to true to organize logs by project folder
# false: All logs in {BASE_DIR}/Daily/
# true: Logs in {BASE_DIR}/{PROJECT_ROOT}/Daily/
USE_PROJECT_ROOT=false
```

**Optional git author filter** (default: `me`):
```bash
# Filter commits by author
# "me": Only include commits by current git user (default)
# "all": Include all commits from all authors
FILTER_AUTHOR=me
```

**Optional project mappings** (only if USE_PROJECT_ROOT=true, format: `/absolute/project/path=folder-name`):
```bash
# If not mapped, the skill will auto-detect the folder name from:
#   1. Git repository name
#   2. Current directory name (fallback)

# Examples:
/Users/yourusername/projects/agent-tools=agent-tools
/Users/yourusername/work/my-long-repo-name=my-app
/Users/yourusername/monorepo/frontend=frontend
```

### Project Root Detection

The Obsidian folder name (`PROJECT_ROOT`) is determined in this order:

1. **Explicit mapping in .env file**: If current project path is mapped, use the specified folder name
2. **Git repository name**: Extract from `git remote get-url origin` (e.g., `https://github.com/user/agent-tools.git` → `agent-tools`)
3. **Current directory name**: Use `basename "$(pwd)"` as fallback
4. **Manual input**: If all detection fails, ask the user

**When to add a project mapping**:
- Git repo name is too long or not descriptive
- Working in a monorepo subdirectory
- Want a different Obsidian folder name than the project/repo name

**Example structure (USE_PROJECT_ROOT=false)**:
```
ObsidianVault/
└── ob-glens/
    └── Daily/
        ├── 2026-01-20.md
        ├── 2026-01-21.md
        └── 2026-01-22.md
```

**Example structure (USE_PROJECT_ROOT=true)**:
```
ObsidianVault/
└── ob-glens/
    ├── agent-tools/
    │   └── Daily/
    │       ├── 2026-01-20.md
    │       └── 2026-01-22.md
    ├── my-frontend/
    │   └── Daily/
    │       └── 2026-01-22.md
    └── backend-api/
        └── Daily/
            └── 2026-01-22.md
```

## Usage Workflow

Follow these steps to generate a daily work log:

### 1. Determine Today's Date

Calculate today's date in `YYYY-MM-DD` format.

### 2. Load Configuration and Detect Project Root

Read the configuration file and determine the Obsidian folder name:

**Step 2a: Read .env file**
```bash
# Read the .env file located at skills/shared/ob-daily-log/.env
CONFIG_FILE="skills/shared/ob-daily-log/.env"

# Extract OBSIDIAN_VAULT_PATH
OBSIDIAN_VAULT_PATH=$(grep "^OBSIDIAN_VAULT_PATH=" "$CONFIG_FILE" | cut -d'=' -f2)

# Extract BASE_DIR (default: ob-glens)
BASE_DIR=$(grep "^BASE_DIR=" "$CONFIG_FILE" | cut -d'=' -f2)
if [ -z "$BASE_DIR" ]; then
    BASE_DIR="ob-glens"
fi

# Extract USE_PROJECT_ROOT (default: false)
USE_PROJECT_ROOT=$(grep "^USE_PROJECT_ROOT=" "$CONFIG_FILE" | cut -d'=' -f2)
if [ -z "$USE_PROJECT_ROOT" ]; then
    USE_PROJECT_ROOT="false"
fi

# Extract FILTER_AUTHOR (default: me)
FILTER_AUTHOR=$(grep "^FILTER_AUTHOR=" "$CONFIG_FILE" | cut -d'=' -f2)
if [ -z "$FILTER_AUTHOR" ]; then
    FILTER_AUTHOR="me"
fi
```

If `OBSIDIAN_VAULT_PATH` is not set, ask the user to configure it and offer to update the .env file.

**Step 2b: Determine PROJECT_ROOT (only if USE_PROJECT_ROOT=true)**

If USE_PROJECT_ROOT is false, skip this step and use `{OBSIDIAN_VAULT_PATH}/{BASE_DIR}/Daily/` as the target directory.

If USE_PROJECT_ROOT is true:

Get the current project's absolute path:
```bash
CURRENT_PROJECT_PATH=$(pwd)
```

Check if there's a mapping for this project in the .env file:
```bash
# Look for a line matching the current project path
# Format: /path/to/project=folder-name
PROJECT_ROOT=$(grep "^${CURRENT_PROJECT_PATH}=" "$CONFIG_FILE" | cut -d'=' -f2)
```

If no mapping exists, auto-detect in this order:

**Priority 1: Git repository name**
```bash
git remote get-url origin 2>/dev/null | sed 's/.*\///' | sed 's/\.git$//'
```

**Priority 2: Current directory name**
```bash
basename "$CURRENT_PROJECT_PATH"
```

If auto-detection succeeds, optionally offer to save the mapping to the .env file for future use.

If all methods fail, ask the user to provide the Obsidian folder name.

### 3. Analyze Git History

**Step 3a: Determine author filter**

If `FILTER_AUTHOR=me` (default), get current git user information:
```bash
GIT_USER_NAME=$(git config user.name)
GIT_USER_EMAIL=$(git config user.email)
```

Construct author filter argument:
```bash
if [ "$FILTER_AUTHOR" = "me" ]; then
    # Filter by current user's email (more reliable than name)
    AUTHOR_FILTER="--author=$GIT_USER_EMAIL"
else
    # No filter, include all authors
    AUTHOR_FILTER=""
fi
```

**Step 3b: Analyze commits from today (00:00 to current time)**

Get current date in YYYY-MM-DD format:
```bash
TODAY=$(date +%Y-%m-%d)
```

Get today's commits:
```bash
# Get today's commits with author and message
git log --since="${TODAY} 00:00" --until="${TODAY} 23:59" $AUTHOR_FILTER --pretty=format:"%h - %an, %ar : %s"

# Get commit hashes for diff analysis
COMMITS=$(git log --since="${TODAY} 00:00" --until="${TODAY} 23:59" $AUTHOR_FILTER --pretty=format:"%H")
```

**For FILTER_AUTHOR=me (default)**: Analyze each commit individually to avoid including other authors' changes

```bash
# Show changes from each commit by the filtered author
for commit in $COMMITS; do
    git show --stat $commit
done
```

This ensures only the filtered author's changes are included in the analysis.

**For FILTER_AUTHOR=all**: Use range-based diff

```bash
FIRST_COMMIT=$(git log --since="${TODAY} 00:00" --until="${TODAY} 23:59" --pretty=format:"%h" | tail -1)
LAST_COMMIT=$(git log --since="${TODAY} 00:00" --until="${TODAY} 23:59" --pretty=format:"%h" | head -1)

if [ -n "$FIRST_COMMIT" ]; then
    git diff --stat ${FIRST_COMMIT}^..${LAST_COMMIT}
    git diff ${FIRST_COMMIT}^..${LAST_COMMIT}
fi
```

If there are no commits today by the filtered author, inform the user and ask if they want to analyze recent commits instead.

### 4. Infer Business Logic and Key Accomplishments

Go beyond simple file modifications. Analyze the diffs to understand:
- **Features**: What new functionality was added?
- **Fixes**: What bugs or issues were resolved?
- **Refactoring**: What code improvements were made?
- **Architecture**: What structural changes occurred?

Look for patterns in:
- Function/class additions or modifications
- API endpoint changes
- Database schema updates
- Configuration changes
- Test additions or modifications

### 5. Extract Issues and TODOs

Search the codebase for:
- TODO comments added or modified today
- FIXME comments
- Code comments mentioning "issue", "bug", or "problem"
- Incomplete implementations (stub functions, placeholder logic)

### 6. Generate Tomorrow's Plan

Based on:
- Incomplete tasks from today
- TODO comments found
- Natural next steps from today's work (e.g., if backend API was added, suggest frontend integration)

### 7. Populate Template and Save

Use the template from `assets/daily-note-template.md` to create the daily note:

1. Read the template file
2. Replace placeholders with analyzed content:
   - `{{date}}`: Today's date (YYYY-MM-DD format)
   - `{{project}}`: Project root name
   - `{{작업한 핵심 기능명}}`: Inferred key features
   - `{{해결된 버그나 이슈}}`: Identified fixes
   - `{{파일명}}`: Changed file names
   - `{{변경 내용 요약}}`: Brief summary of changes per file
   - `{{코드 내 TODO 주석이나 미해결 사항 추출}}`: Extracted TODOs and blockers
   - `{{오늘 마무리하지 못한 작업을 기반으로 추천}}`: Suggested next steps

3. Create daily directory if needed:
   - If `USE_PROJECT_ROOT=false`: `{OBSIDIAN_VAULT_PATH}/{BASE_DIR}/Daily/`
   - If `USE_PROJECT_ROOT=true`: `{OBSIDIAN_VAULT_PATH}/{BASE_DIR}/{PROJECT_ROOT}/Daily/`
4. Save to:
   - If `USE_PROJECT_ROOT=false`: `{OBSIDIAN_VAULT_PATH}/{BASE_DIR}/Daily/{YYYY-MM-DD}.md`
   - If `USE_PROJECT_ROOT=true`: `{OBSIDIAN_VAULT_PATH}/{BASE_DIR}/{PROJECT_ROOT}/Daily/{YYYY-MM-DD}.md`

### 8. Confirm Completion

Inform the user that the daily log has been created and provide:
- The file path
- A brief summary of what was logged
- Option to review or edit the generated note

## Output Format

The generated daily note follows Obsidian-compatible markdown format with:
- Emoji headers for visual clarity
- Callout blocks (`> [!info]`) for key information
- Task checkboxes (`- [ ]`) for actionable items
- Code formatting for file names (`` `file.ts` ``)

## Resources

### Configuration
- `.env`: Central configuration file for Obsidian vault path and project mappings

### assets/
- `daily-note-template.md`: The template structure for generated daily notes

## Example Usage

**User**: "Create today's daily log"

**Claude workflow**:
1. Read `skills/shared/ob-daily-log/.env` file
2. Extract `OBSIDIAN_VAULT_PATH` (e.g., `/Users/me/Documents/ObsidianVault`) and `BASE_DIR` (e.g., `ob-glens`)
3. Get current project path (e.g., `/Users/me/projects/agent-tools`)
4. Check .env for project mapping → not found
5. Auto-detect project root: "agent-tools" (from git repo name)
6. Get today's date (2026-01-22)
7. Run `git log --since="today 00:00"` to get commits
8. Run `git diff` to analyze changes
9. Identify that user added authentication feature and fixed a bug in API
10. Extract TODO comments about missing error handling
11. Create directory if needed: `~/Documents/ObsidianVault/ob-glens/agent-tools/Daily/`
12. Generate daily note at `~/Documents/ObsidianVault/ob-glens/agent-tools/Daily/2026-01-22.md`
13. Confirm: "Created daily work log at ob-glens/agent-tools/Daily/2026-01-22.md. Logged 2 key accomplishments (authentication feature, API bug fix), 3 file changes, and 1 blocker (error handling TODO)."
