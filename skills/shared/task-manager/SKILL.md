---
name: task-manager
description: This skill should be used when the user needs to manage project tasks with Jira integration. It handles task organization, assignee tracking, priorities, dependencies, and automatic Jira ticket creation and synchronization. Use this when the user mentions task management, team assignments, Jira tickets, or project work distribution.
---

# Task Manager (Jira-Integrated)

## Overview

This skill enables systematic management of development tasks with Jira integration. It maintains tasks.md as the source of truth for local task management while optionally synchronizing with Jira for team collaboration. Features include automatic Jira ticket creation on task- **Jira Integration**: Bidirectional sync between local `tasks.md` and Jira.
- **Content Sync Rules**: 
    - **Full Description Sync**: Always extract the *entire* block under `- **설명**:` (including sub-bullets and formatting) when syncing to Jira.
    - **Markdown Preservation**: Preserve all Markdown syntax for rich-text conversion via ADF.
    - **Traceability**: In the `상세 내용` (checklists) within `설명`, use descriptive task titles or keywords instead of local indices (e.g., `#1`) to ensure clarity when viewed as standalone Jira tickets.
- **Automatic Jira Key Management**: Stores and uses Jira Keys to maintain links.th Jira priority.

## Core Capabilities

### 1. Task Management (Core Features)

**Adding new tasks:**
- Read `tasks.md` to understand current task list structure and find next available index
- Parse user requirements (natural language description of work items)
- Structure each task with:
  - **Index**: `[#N]` format (N = last index + 1)
  - Clear, descriptive task name
  - Assignee (A, B, C, or "미지정" - default to "미지정" during initial task organization)
  - Priority level (높음/중간/낮음)
  - Estimated time (e.g., "2일", "1주")
  - Status (대기/진행중/완료)
  - **Jira Key**: (optional, added after assignee is set)
  - **Dependencies**: Task dependencies and execution order (e.g., "없음", "#1 이후 진행", "#2를 진행하는 담당자가 진행하는 것이 효율적")
  - Detailed description of requirements
- Add tasks under "진행 중인 업무" section
- IMPORTANT: Analyze task relationships and specify dependencies clearly

**Modifying existing tasks:**
- Locate the specific task in `tasks.md` by index (e.g., "#3")
- Update requested fields (assignee, priority, time estimate, description, status, dependencies)
- **If Jira Key exists**: Automatically push changes to Jira using `scripts/jira_client.py`
- Preserve other task information unchanged
- When dependencies change, verify consistency with related tasks

**Deleting tasks:**
- Before deletion, check if other tasks depend on this task (search for references to its index)
- If dependencies exist, warn user and update dependent tasks or recommend alternative approach
- Remove task entry from `tasks.md`
- DO NOT reuse the deleted task's index number
- NOTE: Deleting a task does NOT delete the Jira ticket (manual cleanup required)

**Moving tasks to completion:**
- Move task from "진행 중인 업무" to "완료된 업무" section
- Change index from `[#N]` to `[#완료N]` format
- Add completion date (완료일: YYYY-MM-DD)
- Change status to "완료"
- **If Jira Key exists**: Update Jira status to "Done"

### 2. Assignee Management

**Assigning tasks:**
- Update the "담당자" field for specified tasks
- Use designations: A, B, C, or "미지정"
- **IMPORTANT: Jira Ticket Creation Trigger**
  - When assignee changes from "미지정" to actual person (A/B/C), automatically create Jira ticket:
    1. Use `scripts/jira_client.py` to create Jira issue
    2. Map task fields to Jira:
       - Summary: Task title (strip index like [#N] automatically)
       - Description: Task description
       - Priority: 높음 → High, 중간 → Normal, 낮음 → Low
       - Status: Use project-specific mapping (e.g., OPEN, 개발 시작, 개발 완료)
       - Due Date: Map from **작업 기한**
       - Parent: Map from **Jira Parent**
       - Assignee: Use mapping from config.json
    3. Store returned Jira Key (e.g., GLENS-123) in tasks.md
    4. Provide Jira URL to user: `https://your-domain.atlassian.net/browse/GLENS-123`
- Consider team member roles from `references/project-info.md` when making recommendations

**Viewing assignments:**
- Filter and display tasks by assignee
- Show workload distribution across team members
- Display Jira Keys and URLs when available

**Reassigning tasks:**
- Update assignee field when responsibilities change
- **If Jira Key exists**: Update Jira assignee field
- Document reassignment in task history if needed

### 3. Jira Integration (New Features)

#### 3.1 Dual-Write (Jira Ticket Creation)

**Trigger**: Assignee changes from "미지정" to A/B/C

**Process**:
1. Update assignee in tasks.md
2. Call `scripts/jira_client.py` create_issue():
   ```python
   from scripts.jira_client import JiraClient
   client = JiraClient()
   jira_key = client.create_issue(
       summary=task_title,
       description=task_description,
       assignee=assignee,  # A, B, or C
       priority=priority,  # 높음/중간/낮음
       status=status  # 대기/진행중/완료
   )
   ```
3. Add "- **Jira Key**: {jira_key}" field to tasks.md (after 상태 field)
4. Confirm to user with Jira URL

**Example Output**:
```
✅ [#3] 업무를 B에게 배정하고 Jira 티켓(GLENS-123)을 생성했습니다.
Jira에서 확인: https://your-domain.atlassian.net/browse/GLENS-123
```

#### 3.2 Active Sync - Push (Local → Jira)

**Trigger**: Status, priority, or assignee changes on tasks with Jira Key

**Process**:
1. Detect changes in tasks.md
2. Check if Jira Key exists
3. Call `scripts/jira_client.py` update_issue():
   ```python
   client.update_issue(
       issue_key=jira_key,
       status=new_status,  # Optional
       priority=new_priority,  # Optional
       assignee=new_assignee  # Optional
   )
   ```
4. Confirm sync to user

**Example Output**:
```
✅ [#3] 상태를 '진행중'으로 변경하고 Jira(GLENS-123)에도 반영했습니다.
```

#### 3.3 Active Sync - Pull (Jira → Local)

**Trigger**: User command "/sync-from-jira" or "Jira에서 변경사항 가져와줘"

**Process**:
1. Call `scripts/sync_manager.py` pull_from_jira():
   ```python
   from scripts.sync_manager import SyncManager
   from pathlib import Path

   manager = SyncManager(Path("tasks.md"))
   result = manager.pull_from_jira()
   ```
2. For each task with Jira Key:
   - Fetch Jira issue status
   - Compare with local status
   - **Conflict Resolution: Jira takes priority**
3. Update tasks.md with Jira changes
4. Display summary of changes to user

**Example Output**:
```
✅ Jira 동기화 완료:
- [#3] 상태: 대기 → 진행중 (Jira에서 변경됨)
- [#5] 변경 없음
- [#8] 상태: 진행중 → 완료 (Jira에서 변경됨)
```

#### 3.4 Error Handling

**Jira API errors:**
- Network timeout (10 seconds)
- Authentication failure (.env not configured)
- API rate limiting (100 requests/minute)

**Behavior on error:**
- Local changes are always preserved
- Display clear error message to user
- Suggest retry or manual sync
- Continue with local-only mode if .env not configured

### 4. Task Queries and Views

**Common query patterns:**
- "현재 진행 중인 업무 보여줘" → Display all tasks under "진행 중인 업무" (include Jira Keys if present)
- "A의 업무 확인해줘" → Filter tasks where 담당자 = A (show Jira URLs)
- "높은 우선순위 업무만 보여줘" → Filter by 우선순위 = 높음
- "미지정 업무 리스트" → Filter tasks where 담당자 = 미지정 (no Jira tickets expected)
- "완료된 업무 보여줘" → Display "완료된 업무" section
- "#3번 업무 확인해줘" → Show specific task by index (include Jira URL)
- "#1에 의존하는 업무가 뭐야?" → Find tasks that depend on #1
- "독립적으로 진행 가능한 업무 보여줘" → Filter tasks where 연관 업무 = "없음"
- "업무 순서도 보여줘" → Display tasks in dependency order with relationships

**Response format:**
- Present tasks in clear, readable format
- Include Jira Key and clickable URL when available
- Highlight important information (high priority, unassigned, etc.)

### 5. Project Context Management

**Project information:**
- `references/project-info.md` contains project domain knowledge and Jira account mappings
- Read this file when structuring new tasks to ensure consistency
- Use project context to:
  - Recommend appropriate assignees based on expertise
  - Estimate time more accurately
  - Structure task descriptions with relevant technical details
  - Understand system architecture and dependencies
  - Map assignees to Jira account IDs

**Updating project information:**
- When user provides new project context, update `references/project-info.md`
- Keep project overview, tech stack, features, team composition, and Jira mappings current

## File Structure

### tasks.md (root directory)

Primary working file containing all task data. Read and update this file for all task operations.

**Format (with Jira integration):**
```markdown
# 프로젝트 업무 리스트

## 📋 진행 중인 업무

### [#1] 로그인 API 개발
- **담당자**: B
- **우선순위**: 높음
- **예상 소요시간**: 3일
- **상태**: 진행중
- **Jira Key**: GLENS-123
- **연관 업무**: 없음
- **설명**:
  - 구체적인 요구사항
  - 기술적 고려사항

### Task Template
```markdown
### [#ID] Task Title
- **담당자**: [미지정/JIRA_ASSIGNEE_D/JIRA_ASSIGNEE_A]
- **보고자**: [미지정/JIRA_ASSIGNEE_D/없음]
- **우선순위**: [높음/중간/낮음]
- **작업 기한**: [YYYY-MM-DD/없음]
- **Jira Parent**: [KEY/없음]
- **상태**: [OPEN/웹 대기/웹 개발중 등]
- **Jira Key**: [자동 생성]
- **연관 업무**: [#ID or none]
- **설명**:
  - **목표**: ...
  - **배경**: ...
  - **상세 내용**:
    - [ ] ...
  - **산출물**: ...
```

### Fields Explanation
- **담당자**: Assignee. Use environment variable keys from `.env` (e.g., `JIRA_ASSIGNEE_D`) to preserve privacy in shared repositories.
- **보고자**: Reporter. Use environment variable keys from `.env`. If not specified or "없음", Jira will use the API caller as the default reporter.
- **우선순위**: Priority level. Maps to Jira High/Normal/Low.
- **작업 기한**: Due date in YYYY-MM-DD format. Syncs to Jira `duedate`.
- **Jira Parent**: Parent Epic or Task key. Syncs to Jira `parent`.
- **상태**: Current progress status. Must match `config.json`'s `status_list`.
- **Jira Key**: Unique identifier from Jira. Do not edit manually.
- **연관 업무**: Local links between tasks for workflow planning.
- **설명**: Full detailed content. Captured entirely by the stateful parser.

## ✅ 완료된 업무

### [#완료1] Task Title
- **담당자**: me
- **우선순위**: 높음
- **작업 기한**: 2026-01-20
- **완료일**: 2026-01-20
- **Jira Key**: GLENS-120
- **상태**: 완료
- **연관 업무**: 없음
- **설명**:
  - Done items...
```

**Index 관리 규칙:**
- 진행 중인 업무: `[#1]`, `[#2]`, `[#3]` 형식 (숫자 인덱스)
- 완료된 업무: `[#완료1]`, `[#완료2]` 형식으로 구분
- 새 업무 추가 시: 마지막 인덱스 번호 + 1
- 업무 삭제 시: 인덱스는 재사용하지 않음 (순번 유지)
- 완료로 이동 시: `[#3]` → `[#완료3]`으로 변경

**Jira Key 및 Parent 필드 규칙:**
- 선택적 필드 (담당자가 "미지정"인 경우 없음)
- 담당자 배정 시 자동 추가
- 형식: GLENS-XXX (프로젝트 키 + 번호)
- 위치: 상태 필드 다음 또는 이전
- **Jira Parent**: 상위 에픽 또는 태스크 키 명시 (sync to Jira `parent` field)

### config.json (root directory)

Jira integration configuration for static status and priority mappings.

```json
{
  "jira": {
    "status_list": [
      "OPEN",
      "웹 개발중",
      "완료"
    ],
    "priority_mapping": {
      "높음": "High",
      "중간": "Medium",
      "낮음": "Low"
    }
  }
}
```

**Update assignee_mapping** with actual Jira account IDs from `references/project-info.md`.

### .env (root directory, not committed)

Jira API credentials. Must be created by user based on `.env.example`.

```bash
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token
JIRA_PROJECT_KEY=GLENS
JIRA_LABELS=AI_GLENS

# Assignee mappings (JIRA_ASSIGNEE_NAME=accountId)
JIRA_ASSIGNEE_ME=...
JIRA_ASSIGNEE_A=...
```

**If .env is not configured:**
- Jira features are automatically disabled
- Task management continues in local-only mode
- No errors are thrown

### scripts/ directory

**jira_client.py**: Jira REST API wrapper
- `create_issue()`: Create Jira ticket
- `update_issue()`: Update Jira fields
- `get_issue()`: Fetch Jira issue details
- CLI usage: `python scripts/jira_client.py create/get <args>`

**sync_manager.py**: Bidirectional sync manager
- `pull_from_jira()`: Sync Jira changes to local
- CLI usage: `python scripts/sync_manager.py pull`

**requirements.txt**: Python dependencies
- Install: `pip install -r scripts/requirements.txt`

### references/project-info.md

Project domain information, team context, and Jira account mappings. Read this file to understand:
- Project purpose and goals
- Technical stack and architecture
- Current development focus
- Team member roles and expertise
- **Jira account IDs for assignee mapping**

Update this file when user provides new project information or Jira mappings.

### assets/task-template.md

Reference template showing task structure format. Use this as a guide for consistent task formatting. Do not modify this template file.

## Usage Examples

**Example 1: Adding tasks from requirements (no Jira yet)**
```
User: "다음과 같은 요구사항이 있어, 이 내용을 정리해서 업무 리스트에 업데이트 해줘:
       - DB 마이그레이션 스크립트 작성
       - 로그인 API 개발
       - 회원가입 페이지 UI 작성"

Process:
1. Read tasks.md to find last index (e.g., last task was [#5])
2. Read references/project-info.md for context
3. Analyze dependencies and structure tasks:
   - [#6] DB 마이그레이션 스크립트 (높음 우선순위, 연관 업무: 없음)
   - [#7] 로그인 API 개발 (높음 우선순위, 연관 업무: #6 완료 후 진행 가능)
   - [#8] 회원가입 페이지 UI 작성 (중간 우선순위, 연관 업무: #7 완료 후 진행 가능)
4. Add tasks to "진행 중인 업무" with proper indices and dependencies
5. Set all 담당자 to "미지정" (during organization phase, no Jira tickets created yet)
6. Confirm completion to user with dependency explanation
```

**Example 2: Assigning tasks with Jira ticket creation**
```
User: "#7번 로그인 API 개발 업무는 B 개발자에게 할당했어, 이 내용 업데이트 해줘"

Process:
1. Read tasks.md
2. Find task [#7] by index
3. Update 담당자: "미지정" → "B"
4. Since assignee changed from 미지정, create Jira ticket:
   - Import JiraClient from scripts/jira_client.py
   - Call create_issue(summary="[#7] 로그인 API 개발", description=..., assignee="B", priority="높음", status="대기")
   - Receive jira_key (e.g., "GLENS-145")
5. Add "- **Jira Key**: GLENS-145" to task [#7] in tasks.md
6. Check dependencies - if #8 depends on #7 with "동일 담당자 권장", suggest assigning #8 to B as well
7. Confirm assignment to user:
   "✅ [#7] 업무를 B에게 배정하고 Jira 티켓(GLENS-145)을 생성했습니다.
    Jira에서 확인: https://your-domain.atlassian.net/browse/GLENS-145"
```

**Example 3: Status change with Jira push**
```
User: "#7번 업무를 진행중으로 변경해줘"

Process:
1. Read tasks.md
2. Find task [#7] by index
3. Update 상태: "대기" → "진행중"
4. Check if Jira Key exists (GLENS-145)
5. Push to Jira:
   - Import JiraClient from scripts/jira_client.py
   - Call update_issue(issue_key="GLENS-145", status="웹 개발중", duedate="2026-02-01")
   - Jira status transitions: OPEN → 웹 개발중
6. Save tasks.md
7. Confirm to user:
   "✅ [#7] 상태를 '진행중'으로 변경하고 Jira(GLENS-145)에도 반영했습니다."
```

**Example 4: Sync from Jira (Pull)**
```
User: "/sync-from-jira" 또는 "Jira에서 변경사항 가져와줘"

Process:
1. Import SyncManager from scripts/sync_manager.py
2. Call pull_from_jira():
   manager = SyncManager(Path("tasks.md"))
   result = manager.pull_from_jira()
3. Result example:
   {
     "updated_count": 2,
     "updated_tasks": [
       {"index": "7", "title": "로그인 API 개발", "jira_key": "GLENS-145", "changes": ["상태: 대기 → 진행중"]},
       {"index": "8", "title": "회원가입 페이지 UI", "jira_key": "GLENS-146", "changes": ["상태: 진행중 → 완료"]}
     ],
     "errors": []
   }
4. Display summary to user:
   "✅ Jira 동기화 완료:
    - [#7] 상태: 대기 → 진행중 (Jira에서 변경됨)
    - [#8] 상태: 진행중 → 완료 (Jira에서 변경됨)"
```

**Example 5: Viewing tasks with Jira links**
```
User: "B의 현재 업무 확인해줘"

Process:
1. Read tasks.md
2. Filter tasks where 담당자 = B
3. Display filtered tasks with Jira URLs:
   "B의 현재 업무:

    ### [#7] 로그인 API 개발
    - 우선순위: 높음
    - 상태: 진행중
    - Jira: https://your-domain.atlassian.net/browse/GLENS-145

    ### [#2] 회원가입 API 개발
    - 우선순위: 높음
    - 상태: 대기
    - Jira: https://your-domain.atlassian.net/browse/GLENS-124

    총 2개 업무"
```

## Important Notes

### Jira Integration Requirements

**Environment setup:**
- .env file with Jira credentials (see .env.example)
- Python 3.7+ with requests library: `pip install -r scripts/requirements.txt`
- config.json with assignee account IDs

**Optional Jira integration:**
- Jira Key field is optional (tasks without it remain local-only)
- If .env is not configured, Jira features are automatically disabled
- Task management continues seamlessly without Jira

**Conflict resolution:**
- Pull operations: Jira takes priority (overwrites local changes)
- Push operations: Local changes are sent to Jira
- On push failure: Local changes are preserved, error message displayed

### Task Management Best Practices

- Preserve existing task structure and formatting
- Use project context from references/project-info.md to provide informed recommendations
- Default new tasks to "미지정" assignee unless explicitly specified (during task organization phase)
- Keep task descriptions clear and actionable
- When moving tasks to completion, always add completion date and change index to `[#완료N]` format
- Jira ticket creation is triggered ONLY when assignee changes from "미지정" to actual person

### Index and Dependency Management

- Always assign sequential indices to new tasks (`[#N]`)
- Never reuse deleted task indices
- Carefully analyze task relationships and specify dependencies
- When deleting tasks, check for dependent tasks first
- When assigning tasks, consider dependencies for efficient work distribution
- Validate dependency chains to prevent circular dependencies

### Jira Sync Strategy

- **Push (Local → Jira)**: Automatic on every status/priority/assignee change
- **Pull (Jira → Local)**: Manual command only (/sync-from-jira)
- **Frequency**: Pull when collaboration occurs (e.g., daily standup, before planning)
- **Dependencies**: Not synced to Jira (local-only field)
