---
name: ob:meeting-notes-formatter
description: This skill should be used when users provide rough meeting notes or discussions and want them formatted into structured meeting minutes following predefined templates. It handles three types of meetings (developer meetings with technical content, cross-team collaboration meetings with requirements and issues, and executive meetings with weekly progress updates), automatically searches for related spec documents in the Obsidian vault, and generates properly formatted markdown files with YAML frontmatter.
disable-model-invocation: true
---

# Meeting Notes Formatter

## Overview

Transform rough meeting notes into structured, well-formatted meeting minutes stored in Obsidian. This skill analyzes unstructured or semi-structured meeting content, selects the appropriate template based on meeting type, links to related specification documents, and generates a complete markdown file with YAML frontmatter ready for Obsidian vault management.

## When to Use This Skill

Use this skill when:
- User provides rough meeting notes or discussion points that need formatting
- User mentions creating or organizing meeting minutes
- User wants to convert free-form text or audio transcripts into structured meeting documentation
- User needs to link meeting minutes to existing specification documents in their vault

## Workflow

### Step 1: Environment Setup Verification

Before processing meeting notes, verify the `.env` file exists in the skill directory with required configuration:

```bash
# Check if .env exists
ls -la /path/to/meeting-notes-formatter/.env
```

If `.env` does not exist, prompt the user to copy `.env.example` to `.env` and configure:
- `OBSIDIAN_VAULT_PATH`: Absolute path to Obsidian vault
- `MEETING_MINUTES_DIR`: Directory within vault for storing meeting minutes
- `SPEC_DOCS_DIR`: Directory within vault containing specification documents
- `DEFAULT_MEETING_TYPE`: Default template type (dev-meeting, cross-team-meeting, or executive-meeting)

### Step 2: Analyze Meeting Content

Examine the user's input to identify:
1. **Meeting type**: Determine whether it's a developer meeting (technical discussions), cross-team collaboration meeting (requirements/issues), or executive meeting (progress updates)
2. **Key participants**: Extract attendee names or roles
3. **Main topics**: Identify discussion points, decisions, action items
4. **Mentioned documents**: Look for references to spec files, previous meetings, or related documentation

Example user input:
```
"Had a meeting with the product team about the new user profile feature.
Decided to extend the /users API endpoint. Design is due next week.
Check user-api-v2.md for current spec."
```

From this input, identify:
- Meeting type: Cross-team collaboration meeting (collaboration between teams)
- Topics: New feature (user profile), API changes, design timeline
- Related spec: user-api-v2.md

### Step 3: Select Appropriate Template

Based on the meeting type identified in Step 2, choose the matching template from `assets/`:

- **dev-meeting.md**: For technical discussions involving architecture, API changes, database schemas, technical issues
  - Contains sections: Architecture & Design, API Changes, Database Schema, Technical Issues

- **cross-team-meeting.md**: For meetings with cross-functional teams (e.g., product, design, other departments)
  - Contains sections: Requirements, Key Discussions, Issues & Concerns, Agreements, Action Items (separated by team)

- **executive-meeting.md**: For status updates with management
  - Contains sections: Weekly Progress, Completed/In Progress/Planned Tasks, Key Achievements, Issues & Risks, Resource Status

If the meeting type is ambiguous, ask the user which template to use.

### Step 4: Search for Related Documents

Search the spec documents directory for files mentioned in the meeting notes or related to the discussion topics:

1. Load `SPEC_DOCS_DIR` path from `.env`
2. Search for explicitly mentioned files (e.g., "user-api-v2.md")
3. Perform keyword-based search for implicitly related specs based on discussion topics

Example search commands:
```bash
# Search for specific file
find $OBSIDIAN_VAULT_PATH/$SPEC_DOCS_DIR -name "user-api-v2.md"

# Search for files containing keywords
grep -r "user profile" $OBSIDIAN_VAULT_PATH/$SPEC_DOCS_DIR
```

Collect all relevant document paths to include in the `related_specs` frontmatter and "관련 문서" section.

### Step 5: Generate Meeting Minutes

1. **Read the selected template** from `assets/`
2. **Replace all placeholders** with extracted information:
   - `{{DATE}}`: Current date or date mentioned in notes
   - `{{TITLE}}`: Generate descriptive title from main topics
   - `{{ATTENDEES}}`: List of participants
   - `{{PROJECT}}`: Project name if mentioned
   - Content sections: Fill with organized information from meeting notes
   - `{{RELATED_SPEC_X}}`: Wikilink format (`[[filename]]`) to related documents

3. **Format action items** as checkbox tasks:
   ```markdown
   - [ ] Design mockup by next week (Owner: Design Team)
   - [ ] Update API endpoint documentation (Owner: Dev Team)
   ```

4. **Update YAML frontmatter**:
   ```yaml
   ---
   type: meeting-minutes
   category: cross-team-meeting
   date: 2026-01-23
   attendees: [Product Team, Dev Team]
   tags: [meeting, internal, user-profile]
   related_specs: [user-api-v2]
   ---
   ```

### Step 6: Save to Obsidian Vault

1. **Generate filename**: Use format `YYYY-MM-DD-meeting-topic.md`
   - Example: `2026-01-23-user-profile-feature.md`

2. **Construct full path**:
   ```
   $OBSIDIAN_VAULT_PATH/$MEETING_MINUTES_DIR/YYYY-MM-DD-meeting-topic.md
   ```

3. **Write the file** using the Write tool

4. **Confirm to user** with:
   - File path where minutes were saved
   - List of linked related documents
   - Summary of action items

## Template Customization

Users can modify templates in `assets/` to match their organization's specific needs:

- **Add new sections**: Insert additional headers and placeholder variables
- **Modify YAML frontmatter**: Add custom fields like `priority`, `status`, `department`
- **Change formatting**: Adjust markdown structure, add tables, modify list styles
- **Create new templates**: Copy existing template and customize for new meeting types

After modifying templates, update the template selection logic in Step 3.

## Example Usage

**User input:**
```
"회의록 정리해줘:

오늘 백엔드팀이랑 신규 알림 시스템 논의
- Redis pub/sub 쓰기로 결정
- /notifications API 새로 만들기
- DB에 notification 테이블 추가 필요
- 성능 이슈: 동시 접속자 많을 때 대비
- 다음주 목요일 다시 모여서 프로토타입 리뷰

notification-service-spec.md 참고"
```

**Skill output:**
```
파일 생성됨: /Users/user/obsidian-vault/meetings/2026-01-23-notification-system.md

관련 문서 링크:
- [[notification-service-spec]]

액션 아이템:
- [ ] Redis pub/sub 프로토타입 구현
- [ ] /notifications API 설계 문서 작성
- [ ] notification 테이블 스키마 정의
- [ ] 성능 테스트 계획 수립
- [ ] 다음 회의: 2026-01-30 프로토타입 리뷰
```

## Resources

### assets/

Contains three meeting minute templates ready to be customized and used as output:

- **dev-meeting.md**: Template for technical meetings with sections for architecture decisions, API changes, database schema changes, and technical issues
- **cross-team-meeting.md**: Template for cross-team collaboration meetings with sections for requirements, discussions, agreements, and action items separated by team
- **executive-meeting.md**: Template for executive status meetings with sections for weekly progress, achievements, issues/risks, and resource status

These templates include:
- YAML frontmatter with metadata fields (type, category, date, attendees, tags, related_specs)
- Placeholder variables in `{{VARIABLE}}` format for easy replacement
- Pre-structured markdown sections appropriate for each meeting type
- Obsidian wikilink syntax for document references

### .env.example

Configuration template showing required environment variables. Copy to `.env` and customize for your Obsidian vault setup.
