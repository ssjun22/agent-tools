---
name: weekly-scrum-summarizer
description: This skill should be used when a Scrum Master needs to create or update weekly team summaries from Slack scrum thread messages. It processes Slack text containing daily scrum updates (weekly plan, Wednesday/Friday daily updates) and maintains a cumulative weekly summary document in Markdown format. Use this when the user provides Slack thread text.
---

# Weekly Scrum Summarizer

## Overview

Transform Slack scrum thread messages into structured weekly team summaries in Obsidian. This skill enables Scrum Masters to maintain living weekly documents that accumulate team progress throughout the week.

**Typical workflow:**
- **한 주 요약**: Create new weekly document from weekly plan/goals
- **수요일/금요일**,: Update with mid-week progress (어제 한 일, 오늘 할 일)

## When to Use

Use this skill when:
- User provides Slack thread text from daily scrum updates
- User mentions "한 주 요약", "수요일", "금요일" with Slack text
- User asks to "create weekly summary" or "update weekly summary"
- User wants to organize team member activities from chat messages

## How It Works

### Step 1: Automatic Context Detection

The skill automatically determines:
1. **Current date** → Week number calculation
2. **Input type** (한 주 요약 vs 수/금 update):
   - "진행 중인 주요 작업" 포함 → 한 주 요약
   - "어제 한 일" 포함 → 수/금 업데이트
3. **File path**: `{OBSIDIAN_VAULT}/group meeting/{YYYY}/{N}월 {W}주차.md`
4. **Mode**: CREATE (if file doesn't exist) or UPDATE (if exists)

**Week calculation:**
- 매월 1일이 속한 주 = 1주차
- 예: 2026-02-06 (금) → 2월 1주차

### Step 2: Parse Slack Text

**Recognized patterns:**

**한 주 요약 format:**
```
이름  [시간]
진행 중인 주요 작업
작업 항목 1
작업 항목 2
...
```

**수/금 format:**
```
이름
  요일 오후 H:MM
어제 한 일  (또는: 어제 한일, 어제한 일)
작업 항목 1
작업 항목 2
오늘 할 일  (또는: 오늘 한 일, 오늘할일)
작업 항목 1
작업 항목 2
```

**Parsing logic:**
1. Extract team member names (한글 2-4자 패턴)
2. Identify section headers (flexible matching):
   - "진행 중인 주요 작업", "이번 주 목표", "주간 계획"
   - "어제 한 일", "어제한일", "어제 한일"
   - "오늘 할 일", "오늘 한 일", "오늘할일"
3. **Parse indentation (parent-child relationships)**:
   - Indentation (spaces/tabs) = hierarchical structure
   - No indent → main item or top-level task
   - Indented → sub-item under previous non-indented line
   - No indentation in input → infer from context or ask user
4. Extract work items (line-by-line until next section)
5. **Match to projects** (for team members with 2+ projects):
   - Check explicit project mention (e.g., "차이홍 관련")
   - Match `project_keywords` from config.yaml (case-insensitive)
   - No match → ask user + suggest adding keyword

### Step 3: Create or Update Document

**CREATE mode (한 주 요약):**
1. Load template from `assets/weekly-summary-template.md`
2. Fill header:
   - Title: "주간 작업 요약 (2026년 2월 1주차)"
   - Period: "2026-02-02 ~ 2026-02-06" (월~금)
3. For each team member:
   - Create member section with 1 section only:
     - 📋 진행 중인 작업
   - Add weekly plan items as **main items** (no sub-items yet)
   - Filter out personal schedule items (반차, 휴가, etc.)
   - **Project grouping** (if team member has 2+ projects in config.yaml):
     - Apply project matching logic (Step 2.5)
     - Group main items under project headers: `**Project Name**`
     - Single project → flat list (no grouping)
4. Save to Obsidian path

**UPDATE mode (수/금):**
1. Read existing document
2. For each team member found in Slack text:
   - Find their section in the document
   - **Filter out personal items**: 오전 반차, 오후 반차, 휴가, 병가 등

3. Parse work items with **main-sub item structure**:

   **Step 1: Match with main items**
   - For each new item:
     1. Try to match with existing main items (30%+ keyword similarity)
     2. If match found → prepare to add as sub-item
     3. If no match → prepare to add under "기타"

   **Step 2: Add sub-items**
   - Add all items without completion markers
   - Both "어제 한 일" and "오늘 할 일" are added as-is
   - No duplicate checking during this step (will be done in Step 4)

   **Indentation:**
   - Main items: no indent (`- 기술 스택 조사`)
   - Sub-items: tab (`	- API 문서 읽기`)

   **Project grouping:**
   - Maintained for main items (team members with 2+ projects)
   - Format: `**Project Name**` followed by main items

4. Check for missing members:
   - Compare parsed members vs existing members in doc
   - Add notification in "📝 참고 사항" section:
     "⚠️ 수요일 이승 내용이 없습니다."

5. Update "_마지막 업데이트" timestamp

6. Save

**Important notes:**
- Main items = weekly plan tasks
- Sub-items = daily updates (Wed/Fri)
- Preserve all existing content
- Always add, never remove

### Step 4: Detect and Consolidate Similar Sub-Items

After creating/updating the document (before final save), scan each team member's section to detect potentially duplicate sub-items:

**Detection process:**
1. For each main item, compare all sub-items with each other (pairwise)
2. Calculate similarity between every pair of sub-items
3. If similarity is **50% or higher**:
   - Collect the pair for batch processing
4. Process all similar pairs in batches (up to 4 at once)

**Similarity calculation:**
- Extract keywords from both sub-items
- Remove common words: "기능", "작업", "개발", "구현", "조사", "테스트", "설정",
  "추가", "수정", "개선", "확인", "미팅", "회의", "버그", "이슈", "기술", "성능" etc.
- Calculate Jaccard similarity
- Threshold: **50% or higher** = Add to batch

**User interaction (batch mode):**

Present multiple similar pairs to the user at once:

```
questions:
  - question: "[팀원명] - [Main Item] 중복 항목 처리"
    header: "팀원명"
    options:
      - label: "그대로 유지"
        description: "두 항목 모두 유지 (별개 작업)"
      - label: "첫 번째만"
        description: "[첫 번째 항목 전체 텍스트]"
      - label: "두 번째만"
        description: "[두 번째 항목 전체 텍스트]"
      - label: "통합"
        description: "두 항목을 하나로 합치기 (새 이름 필요)"
```

**Example:**
```
question: "이준형 - 리스닛핏 인프라 관리 중복 처리"
header: "이준형"
options:
  - label: "그대로 유지"
    description: "두 항목 모두 유지 (별개 작업)"
  - label: "첫 번째만"
    description: "인프라 on/off 스케줄러 구성"
  - label: "두 번째만"
    description: "인프라 on/off 스케줄러 동작 확인 및 에러 해결"
  - label: "통합"
    description: "두 항목을 하나로 합치기"
```

**Batch processing rules:**
- Default batch size: 4 questions (adjust based on client capability)
- If more than 4 similar pairs found, process in multiple batches
- Each question shows: team member, main item, and both similar sub-items
- User can see all duplicates at once and make decisions efficiently

**Consolidation behavior:**
- **"그대로 유지"**: Keep both items unchanged
- **"첫 번째만" or "두 번째만"**: Delete the other item
- **"통합"**: Ask for new name in follow-up, then merge both into one item

**Important notes:**
- Only compares **sub-items** within the same **main item**
- Does NOT modify or merge main items
- Process similar pairs in batches sized for the current client capability
- User has full control over all decisions
- More efficient UX with tabbed/button interface

**When to trigger:**
- After all CREATE or UPDATE operations complete
- Before final document save
- Only if 2+ sub-items under same main item have 50%+ similarity

**Benefits:**
- Helps identify redundant task descriptions
- User can see full context before deciding
- Improves document clarity and accuracy

### Step 5: Configuration

**First-time setup:**

⚠️ **Security Note**: `config.yaml` contains sensitive information (personal paths, team member names, project details) and is excluded from git via `.gitignore`.

1. Copy `config.yaml.example` to `config.yaml`:
   ```bash
   cp config.yaml.example config.yaml
   ```

2. Edit `config.yaml` with your actual values:
   - Obsidian vault path
   - Team member names
   - Project names and keywords

**config.yaml structure:**
```yaml
obsidian:
  vault_path: "/Users/username/Documents/Obsidian Vault"
  weekly_folder: "group meeting"

team:
  members:
    - [팀원1]
    - [팀원2]
    - [팀원3]

  # 팀원별 프로젝트 (2개 이상인 경우만)
  projects:
    팀원1:
      - 프로젝트A
      - 프로젝트B
    팀원2:
      - 프로젝트A

  # 프로젝트별 키워드 매칭
  project_keywords:
    프로젝트A:
      - 키워드1
      - 키워드2
    프로젝트B:
      - 키워드3
      - 키워드4
```

To edit config: Open `config.yaml` in the skill directory

### Step 6: Output Report

After processing, display:
```
✅ 주간 요약 문서 업데이트 완료!

📄 파일: /path/to/obsidian/group meeting/N월 W주차.md
📅 업데이트 날짜: YYYY-MM-DD (요일)

✏️ 업데이트된 팀원 (5명):
- [팀원1]
- [팀원2]
- [팀원3]
- ...

⚠️ 업데이트 누락:
- 수요일 [팀원A] 내용이 없습니다.
- 금요일 [팀원B] 내용이 없습니다.
```

## Error Handling

### Config file missing
```
→ Prompt user for Obsidian vault path
→ Create config.yaml automatically
→ Proceed with processing
```

### Obsidian folder doesn't exist
```
→ Create "group meeting" folder automatically
→ Notify user: "✨ Created 'group meeting' folder in Obsidian vault"
```

### File write permission denied
```
→ Save to current directory as backup
→ Alert: "권한 문제로 ./weekly-summary-backup.md에 저장했습니다"
```

## Tips

1. **Consistency**: Encourage team to use consistent section headers ("어제 한 일", "오늘 할 일")
2. **Clean input**: Slack text should include name + content (timestamps are optional)
3. **Missing members**: Skill will automatically alert you
4. **Main-sub structure**: Weekly plan items = main, daily updates = sub-items
5. **Duplicate detection**: Similar sub-items (50%+ similarity) are detected and user is asked to consolidate
6. **User control**: All duplicate decisions require user confirmation (no automatic merging)
7. **Config updates**: Edit `config.yaml` to add/remove team members
8. **Personal schedules**: Items like "오전 반차", "휴가" are automatically filtered out
9. **Project grouping**: Team members with 2+ projects get automatic project grouping based on keyword matching
10. **Indentation**: Preserve indentation (spaces/tabs) when copying from Slack for accurate parsing
11. **Year folders**: Weekly summaries are organized by year (e.g., `group meeting/2026/1월 1주차.md`)
12. **기타 category**: Unmatched tasks go under "기타" main item automatically

## Resources

### assets/weekly-summary-template.md
Base template for creating new weekly summary documents. Contains standard structure with team member sections and weekly summary areas.

### config.yaml
Configuration file for Obsidian path and team member list. Created automatically on first run.
