---
name: weekly-scrum-summarizer
description: This skill should be used when a Scrum Master needs to create or update weekly team summaries from Slack scrum thread messages. It processes Slack text containing daily scrum updates (weekly plan, Wednesday/Friday daily updates) and maintains a cumulative weekly summary document in Markdown format. Use this when the user provides Slack thread text.
---

# Weekly Scrum Summarizer

## Overview

Transform Slack scrum thread messages into structured weekly team summaries in Obsidian. This skill enables Scrum Masters to maintain living weekly documents that accumulate team progress throughout the week.

**Typical workflow:**
- **한 주 요약**: Create new weekly document from weekly plan/goals
- **수요일/금요일**: Update with mid-week progress (어제 한 일, 오늘 할 일)

## When to Use

Use this skill when:
- User provides Slack thread text from daily scrum updates
- User mentions "한 주 요약", "수요일", "금요일" with Slack text
- User asks to "create weekly summary" or "update weekly summary"
- User wants to organize team member activities from chat messages

## Non-goals

이 스킬이 하지 않는 것:
- 기존 main item 수정 또는 삭제
- 과거 주차 문서 소급 수정
- 팀원 추가/삭제 (config.yaml 직접 수정 필요)
- Slack API 연동 (수동 복사-붙여넣기만 지원)
- Jira, Notion 등 외부 시스템 연동

## How It Works

### Step 1: Automatic Context Detection

The skill automatically determines:
1. **Current date** → Week number calculation
   - `scripts/update_weekly_summary.py`의 `get_week_info()`를 Bash로 호출하여 월/주차/기간을 가져온다
   - 직접 계산하지 않는다 (경계 날짜 오류 방지)
2. **Input type** (한 주 요약 vs 수/금 update):
   - "진행 중인 주요 작업" 포함 → 한 주 요약
   - "어제 한 일" 포함 → 수/금 업데이트
3. **File path**: `{OBSIDIAN_VAULT}/group meeting/{YYYY}/{N}월/{W}주차/team-scrum-summary.md`
4. **Mode**: CREATE (if file doesn't exist) or UPDATE (if exists)

### Step 2: Parse Slack Text

입력 패턴은 DESIGN.md > Slack Text Parser 참조.

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
   - No indentation in input → 파싱 결과 미리보기를 제시하고 사용자 승인 후 진행
     - 미리보기 형식: 팀원별로 감지된 항목 목록을 계층 구조로 표시
     - 승인 전까지 문서에 쓰지 않는다
4. Extract work items (line-by-line until next section)
5. **Match to projects** (for team members with 2+ projects):
   - Check explicit project mention (e.g., "차이홍 관련")
   - Match `project_keywords` from config.yaml (case-insensitive)
   - No match → ask user + suggest adding keyword

### Step 3: Create or Update Document

**CREATE mode (한 주 요약):**
1. Load template from `assets/weekly-summary-template.md`
2. Fill header with title and period (월~금)
3. For each team member:
   - Add weekly plan items as **main items** (no sub-items yet)
   - Filter out personal schedule items (반차, 휴가, etc.)
   - **Project grouping** (if team member has 2+ projects in config.yaml):
     - Group main items under project headers: `**Project Name**`
     - Single project → flat list (no grouping)
4. Save to Obsidian path

**UPDATE mode (수/금):**
1. Read existing document
2. For each team member found in Slack text:
   - Find their section in the document
   - **Filter out personal items**: 오전 반차, 오후 반차, 휴가, 병가 등
3. Parse work items with **main-sub item structure**:

   **Match with main items:**
   - For each new item:
     1. Try to match with existing main items (30%+ keyword similarity)
     2. If match found → prepare to add as sub-item
     3. If no match → prepare to add under "기타"

   **sub-item 계층화 조건:**
   - 해당 main item을 달성하기 위해 수행한 구체적인 하위 작업일 때만 계층화
   - 단순히 같은 프로젝트에 속하거나 키워드가 유사하다는 이유만으로 계층화하지 않는다
   - 관계가 불명확한 경우 동일 레벨로 배치

   **Indentation:**
   - Main items: no indent (`- 기술 스택 조사`)
   - Sub-items: tab (`	- API 문서 읽기`)

   **Project grouping:**
   - Maintained for main items (team members with 2+ projects)
   - Format: `**Project Name**` followed by main items

4. Check for missing members → add notification in "📝 참고 사항" section
5. Update "_마지막 업데이트" timestamp
6. Save

**Important notes:**
- Main items = weekly plan tasks
- Sub-items = daily updates (Wed/Fri)
- Preserve all existing content
- Always add, never remove

### Step 4: Detect and Consolidate Similar Sub-Items (Optional)

**문서 저장 완료 후** 선택적으로 실행한다. 저장과 독립된 단계이므로 이 단계 실패 시에도 저장된 문서는 보존된다.

**실행 조건:**
- 저장 완료 후 유사/중복 후보가 감지된 경우 사용자에게 "중복 항목이 N건 감지됐습니다. 정리하시겠습니까?" 확인
- 사용자가 거부하면 즉시 종료 (문서는 저장된 상태 유지)

**Detection targets:**
1. **중복 감지**: 동일 main item 아래 sub-items에서 아래 규칙으로 유사 쌍 감지
2. **진행 단계 통합 감지**: 핵심 키워드가 동일하고 뒷부분만 진행 단계(준비/완료 등) 또는 연속 동작으로 구분되는 쌍

**유사 판단 규칙 (결정적):**
1. 각 항목에서 불용어 제거: 작업, 개발, 구현, 조사, 테스트, 설정, 추가, 수정, 개선, 확인, 준비, 완료
2. 남은 핵심 단어가 **2개 이상 겹치면** 유사 항목으로 판단
3. 핵심 단어가 1개 이하인 짧은 항목은 완전 일치일 때만 중복으로 판단

**User interaction (batch mode):**
- 감지된 쌍을 최대 4개씩 묶어 AskUserQuestion으로 한 번에 제시
- 각 질문의 선택지: 그대로 유지 / 첫 번째만 / 두 번째만 / 통합
- "통합" 선택 시 후속 질문으로 통합 이름 확인 후 반영
- 통합 시 완료 단계 또는 더 포괄적인 표현을 기본 후보로 제시

**조건:**
- 동일 main item 아래 sub-items만 비교 (main item 자체는 수정하지 않는다)
- 2개 미만이면 스킵

### Step 5: Configuration

⚠️ `config.yaml`은 민감 정보 포함, git 제외 대상.

```bash
cp config.yaml.example config.yaml
```

구조 상세는 `config.yaml.example` 참조. 핵심 키:
- `obsidian.vault_path`: Obsidian vault 절대 경로
- `team.members`: 팀원 이름 목록
- `team.projects`: 팀원별 프로젝트 목록 (2개 이상인 경우만)
- `team.project_keywords`: 프로젝트 자동 매칭 키워드

### Step 6: Output Report

```
✅ 주간 요약 문서 업데이트 완료!

📄 파일: /path/to/obsidian/group meeting/YYYY/N월/W주차/team-scrum-summary.md
📅 업데이트 날짜: YYYY-MM-DD (요일)

✏️ 업데이트된 팀원 (N명): [팀원1], [팀원2], ...

⚠️ 업데이트 누락:
- 수요일 [팀원A] 내용이 없습니다.
```

파싱된 팀원이 0명이면 에러로 처리하고 저장하지 않는다.

## Error Handling

| 상황 | 처리 |
|------|------|
| Config 파일 없음 | vault 경로 요청 후 config.yaml 자동 생성 |
| Obsidian 폴더 없음 | 폴더 자동 생성 후 알림 |
| 파일 쓰기 권한 없음 | 현재 디렉토리에 백업 저장 후 알림 |
| 파싱 결과 0명 | 에러 처리, 저장 중단, 원인 안내 |

## Resources

- `assets/weekly-summary-template.md`: 신규 문서 생성용 템플릿
- `config.yaml.example`: 설정 파일 구조 참조
- `DESIGN.md`: 파싱 알고리즘, 유사도 계산, 아키텍처 상세
