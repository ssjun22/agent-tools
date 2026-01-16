---
name: daily-log-maker
description: Automatically generate daily work logs in Notion based on Git commits. This skill should be used when users want to create a summary of their daily work activities by analyzing Git commit messages and posting them to a Notion database. Triggered when users request to log their work, create daily summaries, sync commits to Notion, or generate work logs.
---

# Daily Log Maker

## Overview

Automate daily work logging by collecting Git commits from the current working directory, summarizing them with AI, and posting to Notion. Transform commit messages into structured work logs without manual effort.

**Important:** This skill operates on the Git repository in your **current working directory**. Ensure Claude Code is running inside the target Git project.

## When to Use This Skill

Use this skill when:

- Creating daily work summaries from Git commits
- Generating work logs for Notion databases
- Reviewing what was accomplished during a specific date
- Maintaining a structured record of development activities

## Workflow

Follow this sequential workflow to generate a daily work log:

### Step 1: Check Notion Configuration

Before running the skill for the first time, verify that Notion is properly configured.

**First-time users:** Direct users to read `references/notion_setup.md` for complete setup instructions including:

- Creating a Notion Integration and obtaining API token
- Setting up the database with required properties
- Granting integration access to the database
- Creating `.env` file with credentials

**Returning users:** Verify that `.env` file exists in the skill directory:

```bash
ls daily-log-maker/.env
```

If `.env` file is not configured, the workflow cannot proceed to Step 3.

**Environment variable priority:**

1. System environment variables (highest priority)
2. `.env` file in skill directory
3. Command-line arguments (--notion-token, --notion-db-id)

### Step 2: Collect Git Commits

**Important:** This script collects commits from the **current working directory's Git repository**. By default, it collects **only the current Git user's commits** (업무 일지는 개인 기록이므로). Ensure Claude Code is running in the target Git repository before executing this step.

Execute the `scripts/sync_to_notion.py` script with the `collect` command to gather commit data:

```bash
python scripts/sync_to_notion.py collect [--date YYYY-MM-DD] [--author NAME] [--all-authors]
```

**Parameters:**

- `--date`: Target date in YYYY-MM-DD format (defaults to today)
- `--author`: Specific Git author name/email (defaults to current Git user from `git config user.name`)
- `--all-authors`: Include commits from all authors (기본값: 현재 사용자만)

**Example:**

```bash
# Collect today's commits (현재 Git 사용자만, 기본 동작)
python scripts/sync_to_notion.py collect

# Collect commits from a specific date (현재 사용자)
python scripts/sync_to_notion.py collect --date 2026-01-15

# Collect commits from a specific author
python scripts/sync_to_notion.py collect --author "John Doe"

# Collect commits from ALL authors (팀 전체)
python scripts/sync_to_notion.py collect --all-authors
```

**Output:** JSON array of commits with hash, message, timestamp, and author.

**Handle edge cases:**

- Empty array `[]`: No commits found for the specified date/author
- "현재 디렉토리가 Git 저장소가 아닙니다": Current directory is not a Git repository - verify the working directory
- "Git이 설치되지 않았습니다": Git is not installed on the system
- Other error messages: Git repository issues or invalid date format

### Step 3: Analyze and Summarize Commits

Parse the JSON output from Step 2 and create a concise work summary.

**Instructions for summarization:**

- Read through all commit messages to understand the work done
- Group related commits by feature, bug fix, or task type
- Create 2-4 bullet points highlighting key accomplishments
- Focus on **what was done** rather than technical implementation details
- Write in natural Korean suitable for a work log
- Use markdown formatting (bullet points, bold for emphasis)

**Example summary format:**

```
- 사용자 인증 시스템 구현 완료 (로그인/로그아웃 기능)
- 데이터베이스 스키마 리팩토링으로 쿼리 성능 개선
- 프론트엔드 UI 컴포넌트 3개 추가 (Button, Modal, Card)
```

**When no commits exist:** Use the message "오늘은 커밋이 없습니다." and skip to final confirmation without creating a Notion entry.

### Step 4: Post to Notion

Execute the `scripts/sync_to_notion.py` script with the `create` command to add the work log to Notion:

```bash
python scripts/sync_to_notion.py create \
  --date "YYYY-MM-DD" \
  --summary "YOUR_SUMMARY_HERE" \
  --commit-count N
```

**Parameters:**

- `--date`: The work log date (must match the date from Step 2)
- `--summary`: The AI-generated summary from Step 3 (use quotes for multi-line text)
- `--commit-count`: Total number of commits from Step 2

**Example:**

```bash
python scripts/sync_to_notion.py create \
  --date "2026-01-15" \
  --summary "- 사용자 인증 시스템 구현
- 데이터베이스 스키마 개선
- UI 컴포넌트 추가" \
  --commit-count 8
```

**Output verification:**

- Success: Returns Notion page URL
- Failure: Display error message and suggest checking Notion configuration

### Step 5: Confirm Completion

After successfully posting to Notion, inform the user:

- Confirm the work log was created
- Display the Notion page URL
- Show the generated summary for review
- Optionally mention commit count and date

**Example confirmation:**

```
✅ 2026-01-15 업무 일지가 Notion에 생성되었습니다!

📝 요약 내용:
- 사용자 인증 시스템 구현 완료
- 데이터베이스 스키마 리팩토링
- UI 컴포넌트 3개 추가

📊 총 8개의 커밋이 분석되었습니다.
🔗 Notion 페이지: https://notion.so/...
```

## Common Usage Patterns

### Pattern 1: Daily Log for Today

```
User: "오늘 작업 내용 정리해서 노션에 올려줘"
User: "/daily-log-maker"
```

→ Use today's date, collect current user's commits (기본 동작), summarize, and post.

### Pattern 2: Specific Date

```
User: "어제 뭐했는지 정리해줘"
User: "1월 10일 작업 내용 노션에 기록해줘"
```

→ Parse the date, use `--date` parameter in Step 2.

### Pattern 3: Other User's Commits

```
User: "김철수님의 오늘 작업 내용 정리해줘"
```

→ Use `--author "김철수"` parameter to collect specific user's commits.

### Pattern 4: Team-wide Commits

```
User: "팀 전체의 오늘 커밋 정리해줘"
User: "프로젝트 전체 커밋으로 일지 만들어줘"
```

→ Use `--all-authors` flag to include commits from all team members.

## Dependencies

**System requirements:**

- Git repository (must be run inside a Git project)
- Python 3.6+ (표준 라이브러리만 사용)
- Internet connection (for Notion API)

## Troubleshooting

### "현재 디렉토리가 Git 저장소가 아닙니다"

→ The script operates on the **current working directory's Git repository**. Ensure you are running Claude Code inside a Git repository.
→ Check current directory: `pwd` (macOS/Linux) or `cd` (Windows)
→ Verify Git repository: `git status`

### "Git이 설치되지 않았습니다"

→ Install Git on your system and ensure it's accessible from the command line.

### "NOTION_API_TOKEN 환경 변수가 설정되지 않았습니다"

→ Direct user to `references/notion_setup.md` for configuration instructions.

### "Could not find database" (Notion API error)

→ Verify the Integration has access to the database (Step 2.3 in notion_setup.md).

### "Invalid request" (Notion API error)

→ Check that database properties match expected names: "날짜" (Date), "작업 요약" (Title), "커밋 수" (Number).

## Resources

### scripts/sync_to_notion.py

Python script for Git commit collection and Notion API interaction. Provides two commands:

- `collect`: Gather Git commits as JSON
- `create`: Post work log to Notion database

### references/notion_setup.md

Complete setup guide for Notion Integration, database configuration, and environment variables. Direct first-time users here before executing the workflow.

## Notes

- This skill operates entirely within Claude Code; no external API calls to Anthropic are required
- AI summarization is performed by the Claude instance running this skill
- The script only handles data collection and Notion API communication
- Commit messages are analyzed in context without additional costs
- **Git commits are collected from the current working directory** - ensure Claude Code is running inside the target Git repository
- **By default, only the current Git user's commits are collected** (from `git config user.name`) - use `--all-authors` for team-wide logs
