---
name: weekly-work-summarizer
description: |
  This skill should be used when the user wants to summarize the previous week's work
  for team sharing. Reads daily notes (created by daily-work-log-manager) for the previous
  week (Mon-Sun), extracts company tasks (excluding "기타" personal tasks), deduplicates
  repeated items across days, and generates a clean weekly summary in Markdown format.
  Triggered when users request "주간 요약 만들어줘", "이번 주 작업 정리해줘",
  "팀 공유용 주간 정리", or "weekly summary".
allowed-tools: Read, Write, Bash
---

# Weekly Work Summarizer

## Overview

전주(월~일) daily notes에서 회사 태스크만 자동으로 추출·중복 제거하여 팀 공유용 주간 요약 Markdown 파일을 생성합니다.

- **입력**: `daily-work-log-manager/config.json` (공유)
- **출력**: `{group_meeting_path}/YYYY/M월/W주차/weekly-work-summary.md`
- **제외**: `기타` 프로젝트 섹션 (개인 태스크)
- **파싱 대상**: TODOs 섹션 + Meetings 섹션 (Issues/Notes/Retrospect 제외)

> **향후 확장 예정**: Issues/Notes 섹션도 포함 예정.

---

## Workflow

### Step 1: 설정 파일 확인

`daily-work-log-manager/config.json` 경로에서 설정을 읽습니다.

```bash
# config.json 존재 여부 확인
ls ../daily-work-log-manager/config.json
```

**config.json이 없는 경우:**
- `daily-work-log-manager` 스킬을 먼저 실행하여 config.json을 생성하세요.
- 또는 사용자에게 config.json 경로를 직접 물어보세요.

**config.json 형식:**
```json
{
  "vault_path": "/absolute/path/to/vault",
  "daily_notes_path": "Daily Notes",
  "project_sections": ["프로젝트A", "프로젝트B", "기타"],
  "group_meeting_path": "/absolute/path/to/group meeting"
}
```

**group_meeting_path 설정:**
- 팀 스크럼 요약(`team-scrum-summary.md`)과 같은 폴더에 저장됨
- 없으면 에러 메시지 표시 후 사용자에게 config.json에 추가 안내

### Step 2: 스크립트 실행

```bash
python scripts/collect_weekly_notes.py --config ../daily-work-log-manager/config.json
```

**출력 JSON 구조:**
```json
{
  "week_range": {"start": "2026-02-16", "end": "2026-02-22"},
  "week_label": "2/16 ~ 2/22",
  "projects": {
    "프로젝트A": {
      "completed": [{"text": "항목1", "children": []}],
      "in_progress": [{"text": "항목2", "children": [{"text": "하위 항목", "children": []}]}],
      "meetings": [{"text": "미팅 제목", "date": "2/24", "children": [{"text": "세부 내용", "children": []}]}]
    }
  },
  "files_found": ["2026-02-16", "2026-02-17", "2026-02-18"],
  "files_missing": ["2026-02-19", "2026-02-20", "2026-02-21", "2026-02-22"]
}
```

**에러 처리:**
- `{"error": "..."}`: 에러 메시지 표시 후 사용자에게 안내
- `files_missing`이 있는 경우: 정상 (해당 날 일지 없음). 계속 진행.
- `projects`가 비어있는 경우: "지난 주 TODOs 항목이 없습니다." 메시지 표시 후 종료

### Step 3: Markdown 요약본 생성

JSON 결과를 아래 형식으로 변환합니다.

**출력 형식:**
```markdown
## 주간 작업 요약 (2/16 ~ 2/22)

### 프로젝트A
> 한 줄 요약 (완료한 핵심 내용 + 진행 중 주요 항목, 2줄 이내)

**완료**
- 항목1

**진행 중**
- 항목2
	- 하위 항목

### 프로젝트B
> 한 줄 요약

**완료**
- ...

**진행 중**
- ...

---

### 미팅
- 미팅 제목
	- 세부 내용
		- 더 깊은 내용
```

**변환 규칙:**
- 프로젝트명(`### 프로젝트A`) 바로 아래에 `>` blockquote로 3줄 이내 핵심 요약 작성
  - 완료 항목 중 가장 중요한 내용 + 진행 중 주요 항목 + 주요 미팅 내용을 Claude가 직접 판단하여 요약
  - 항목이 많아도 반드시 3줄 이내로 압축
- `completed` 항목 → `**완료**` 하위 목록
- `in_progress` 항목 → `**진행 중**` 하위 목록
- `children`은 탭(\t) 들여쓰기로 재귀 표현
- `completed` 또는 `in_progress`가 비어있으면 해당 소제목 생략
- 프로젝트 섹션 전체가 비어있으면 해당 섹션 생략
- **미팅**: 각 프로젝트 섹션 내 `**미팅**` 소제목으로 추가
  - 미팅 제목에 프로젝트명이 포함된 경우 해당 프로젝트에 자동 귀속 (예: "차이홍 관련 허들" → 차이홍)
  - 어느 프로젝트에도 매핑되지 않는 미팅은 생략
  - 미팅 항목 형식: `- 미팅 제목 (M/D)` — 날짜 포함
  - `meetings` 배열이 비어있으면 해당 `**미팅**` 소제목 생략
  - 계층 구조는 탭(\t) 들여쓰기로 재귀 표현 (TODOs와 동일)
  - 별도 요약(blockquote) 없이 원문 그대로 나열

**children 렌더링 예시:**
```json
{"text": "기능 구현", "children": [{"text": "API 연동", "children": []}]}
```
→
```markdown
- 기능 구현
	- API 연동
```

### Step 4: 파일 저장

**저장 경로 계산:**
1. `vault_path` + `daily_notes_path` + `YYYY` + `M월` + `YYYY-WNN-summary.md`
2. ISO 주차(WNN)는 `week_range.start`의 ISO week number 사용
3. `M월`은 `week_range.start` 날짜의 월 기준

**예시:**
- `week_range.start`: `2026-02-16` → 월: `2월`, 주차: `ceil(16/7)` = 3주차
- 저장 경로: `{group_meeting_path}/2026/2월/3주차/weekly-work-summary.md`

**Python으로 월/주차 계산:**
```python
import math
from datetime import datetime
d = datetime.strptime("2026-02-16", "%Y-%m-%d")
month_kr = f"{d.month}월"       # → "2월"
week_num = math.ceil(d.day / 7) # → 3
week_kr = f"{week_num}주차"      # → "3주차"
```

**디렉토리 생성 (없는 경우):**
```bash
mkdir -p "{group_meeting_path}/YYYY/M월/W주차"
```

**파일 저장:**
Write 도구로 Markdown 파일 저장.

### Step 5: 완료 메시지

```
✅ 주간 요약이 생성되었습니다!

📂 파일 위치: {group_meeting_path}/YYYY/M월/W주차/weekly-work-summary.md
📅 기간: M/D ~ M/D
📊 요약:
- 분석한 파일: N개 (M/D, M/D, ...)
- 파일 없음: N일 (해당 날 일지 없음)

Obsidian에서 파일을 열어 팀 공유 내용을 확인하세요.
```

---

## 스크립트 레퍼런스

### scripts/collect_weekly_notes.py

**역할**: 전주 daily notes 파싱, 중복 제거, 분류

**입력:**
```bash
python scripts/collect_weekly_notes.py [--config CONFIG_PATH]
```

**주요 동작:**
1. 오늘 날짜 기준 전주 월~일 범위 계산
2. config.json에서 vault_path, daily_notes_path, project_sections 읽기
3. `기타` 섹션 제외
4. 날짜별 파일 경로: `{vault_path}/{daily_notes_path}/{YYYY}/{M}월/{N}주차/{YYYY-MM-DD}.md`
5. TODOs 섹션 파싱 (## TODOs) + Meetings 섹션 파싱 (## Meetings)
6. 체크박스 텍스트 기준 중복 제거 (날짜 annotation 제거 후 비교)
7. 완료 우선: 어느 날이든 `[x]`이면 완료
8. 계층 구조 보존
9. Meetings: 미팅 제목 기준 중복 제거 후 계층 구조 병합

**중복 제거 기준:**
- `(M/D~)` 날짜 annotation 제거 후 텍스트 비교
- 같은 텍스트가 여러 날 등장 → 하나로 합침
- 완료 여부: 임의 날에 `[x]`로 체크 → 전체 "완료" 처리

---

## config.json 공유 규칙

이 스킬은 `daily-work-log-manager`와 동일한 config.json을 사용합니다.

**기본 경로**: `../daily-work-log-manager/config.json`

```json
{
  "vault_path": "/path/to/vault",
  "daily_notes_path": "Daily Notes",
  "project_sections": ["프로젝트A", "프로젝트B", "기타"]
}
```

---

## 사용 패턴

### 패턴 1: 월요일 아침 팀 공유 준비

```
User: "팀 공유용 주간 요약 만들어줘"
User: "지난 주 작업 정리해줘"
User: "/weekly-work-summarizer"
```

→ 전주 daily notes 자동 파싱 후 Markdown 요약 파일 생성

### 패턴 2: 특정 주차 요약 (향후 지원 예정)

현재는 항상 직전 주를 기준으로 동작합니다.

---

## 트러블슈팅

### "config.json not found"
→ `daily-work-log-manager` 스킬을 먼저 실행하여 config.json 생성

### "projects가 비어있음"
→ 지난 주 daily notes 파일에 회사 프로젝트 TODOs가 없거나 파일이 모두 없는 경우

### "파일이 많이 missing"
→ 주말(토/일)은 일지를 작성하지 않는 경우 정상. `files_found`에 평일 파일이 있으면 정상 동작.

### "Python not found"
→ Python 3.6+ 설치 필요. `python3 scripts/collect_weekly_notes.py` 시도.
