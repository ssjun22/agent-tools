---
name: weekly-report-maker
description: This skill should be used when the user needs to create a weekly work report in markdown format. It guides through collecting project progress, issues, and meeting notes for multiple projects, optionally includes Git commit analysis, and saves the report to a specified Obsidian vault path. Use this when the user asks to "create a weekly report", "summarize this week's work", or "prepare a status update for the week".
---

# Weekly Report Maker

## Overview

이 스킬은 주간 업무 보고서를 마크다운 형식으로 생성합니다. 여러 프로젝트의 진행 상황, 이슈, 미팅 내용을 체계적으로 수집하고, 선택적으로 Git 커밋 이력을 포함하여 Obsidian 볼트에 저장합니다.

**주요 기능:**
- 2개 프로젝트의 주간 보고서를 하나의 파일로 생성
- 대화형 입력을 통한 진행 상황, 이슈, 미팅 내용 수집
- Git 커밋 분석 (선택사항)
- Obsidian 볼트 내 프로젝트 정보 파일 연동
- 자동 히스토리 업데이트

## Prerequisites

스킬 사용 전 다음을 준비해야 합니다:

1. **프로젝트 정보 파일 생성** (Obsidian 볼트 내)
   - 경로 예시: `/Users/{username}/Documents/Obsidian Vault/{vault-name}/프로젝트 정보.md`
   - 형식은 `assets/project-info-example.md` 참조

2. **스킬 설정 파일 생성** (최초 1회)
   - 경로: `~/.claude/weekly-report-config.yaml`
   - 내용:
     ```yaml
     project_info_path: "/full/path/to/프로젝트 정보.md"
     ```

3. **프로젝트 메모리 설정** (선택사항, MEMORY 참조 기능 사용 시)
   - 경로: `~/.claude/project-memory-config.yaml`
   - 내용:
     ```yaml
     projects:
       - name: "글렌즈"
         base_path: "/Users/choiyoungjun/Documents/Obsidian Vault/ob-glens"
       - name: "차이홍 톡톡"
         base_path: "/Users/choiyoungjun/Documents/Obsidian Vault/차이홍 톡톡"
     ```
   - 각 프로젝트 디렉토리에 `MEMORY.md` 파일 필요
   - project-memory-manager 스킬과 설정 파일 공유

## Workflow

### Step 1: 초기화 및 날짜 설정

1. **사용자에게 보고 기간 입력 요청:**
   ```
   질문: "보고할 기간을 입력해주세요. (예: 2/2 ~ 2/6)"
   ```

2. **날짜 파싱:**
   - 입력 형식: `M/D ~ M/D`, `M/D~M/D`, `M-D ~ M-D` 등 유연하게 허용
   - 시작일(start_date)과 종료일(end_date) 추출
   - 예: "2/2 ~ 2/6" → start: 2026-02-02, end: 2026-02-06

3. **파일명 계산:**
   - 종료일 다음 월요일 계산 (실제 보고하는 날짜)
   - Python 예시:
     ```python
     from datetime import datetime, timedelta
     end = datetime(2026, 2, 6)  # 목요일
     days_until_monday = (7 - end.weekday()) % 7
     if days_until_monday == 0:
         days_until_monday = 7
     report_date = end + timedelta(days=days_until_monday)
     filename = f"{report_date.month}.{report_date.day}.md"
     # 결과: "2.9.md"
     ```

4. **설정 파일 로드:**
   - `~/.claude/weekly-report-config.yaml` 읽기
   - 프로젝트 정보 파일 경로 확인
   - 프로젝트 정보 파일(`프로젝트 정보.md`) 읽기 및 파싱:
     - 프로젝트 이름 추출 (## 프로젝트 A, ## 프로젝트 B)
     - Git 경로 추출 (- **Git 경로:** ...)
     - Obsidian 저장 경로 추출 (## 보고서 저장 경로 아래 첫 줄)

5. **MEMORY 필터링** (선택사항):
   - `~/.claude/project-memory-config.yaml` 존재 확인
   - 있으면 프로젝트별 MEMORY.md 읽기
   - 보고 기간의 내용만 필터링:
     ```
     1. MEMORY.md 전체 읽기
     2. ### YYYY-MM-DD 형식의 날짜 섹션 파싱
     3. start_date <= 날짜 <= end_date 인 섹션만 추출
     4. 예: 2/2~2/6 보고서 → 2/3, 2/5 날짜 섹션 추출
     ```
   - 프로젝트별 필터링된 MEMORY 저장

6. **확인 메시지:**
   ```
   "다음 프로젝트에 대한 보고서를 생성합니다:
   - 프로젝트 A: [Git 경로]
   - 프로젝트 B: [Git 경로]
   보고 기간: 2026-02-02 ~ 2026-02-06
   저장 파일: 2.9.md"
   ```

### Step 2: 프로젝트 A 데이터 수집

프로젝트별로 3가지 섹션의 내용을 수집합니다.

**메시지:** "프로젝트 A에 대해 입력해주세요."

1. **진행 상황 입력:**
   ```
   질문: "이번 주 진행한 작업 사항을 입력해주세요:"

   💡 MEMORY 참고 (2/2~2/6):
   - 2/3: API 응답 속도 개선 (Redis 캐싱)
   - 2/5: 주간 스프린트 회의 - 다음 주 목표: 사용자 인증 완료
   ```
   - 프로젝트 MEMORY가 있으면 필터링된 내용 표시
   - 사용자로부터 여러 줄 텍스트 입력 받기
   - 빈 입력 시 재요청 (필수 항목)

2. **이슈 입력:**
   ```
   질문: "발생한 이슈나 해결한 문제가 있나요?"

   💡 MEMORY 참고:
   - 2/3: API 응답 속도 이슈 → Redis 캐싱으로 해결 (500ms→50ms)
   ```
   - MEMORY에서 이슈 관련 내용 표시
   - 사용자로부터 여러 줄 텍스트 입력 받기
   - "없음" 또는 빈 입력 허용

3. **미팅 내용 입력:**
   ```
   질문: "참조할 회의록 파일이 있나요? 파일 경로를 입력하거나 'skip'을 입력해주세요:"
   ```
   - 파일 경로 입력 시:
     - Read 도구로 파일 읽기
     - 파일 내용 전체를 저장
   - 'skip', '없음', 빈 입력 시:
     - "미팅 내용 없음" 저장

### Step 3: 프로젝트 B 데이터 수집

**메시지:** "이제 프로젝트 B로 넘어갑니다."

- Step 2와 동일한 과정 반복 (진행 상황 → 이슈 → 미팅 내용)

### Step 4: Git 커밋 포함 여부 (선택)

```
질문: "Git 커밋 이력을 참고자료로 포함하시겠습니까? (yes/no)"
```

**Yes 선택 시:**
- 각 프로젝트의 Git 경로에 대해 `scripts/analyze_commits.py` 실행
- 명령어:
  ```bash
  python scripts/analyze_commits.py \
    --repo /path/to/project-a \
    --start 2026-02-02 \
    --end 2026-02-06
  ```
- JSON 결과 파싱하여 저장

**No 선택 시:**
- Git 커밋 섹션 생략

### Step 5: 보고서 생성 및 저장

1. **템플릿 로드:**
   - `assets/report-template.md` 읽기

2. **플레이스홀더 치환:**
   - `{{WEEK_RANGE}}`: "2026.2.2 - 2026.2.6"
   - `{{PROJECT_A_NAME}}`: 프로젝트 A 이름
   - `{{PROJECT_A_PROGRESS}}`: 진행 상황 텍스트
   - `{{PROJECT_A_ISSUES}}`: 이슈 텍스트
   - `{{PROJECT_A_MEETINGS}}`: 미팅 내용 텍스트
   - `{{PROJECT_B_*}}`: 프로젝트 B 동일
   - `{{GIT_COMMITS}}`: Git 커밋 섹션 (있을 경우)

3. **Git 커밋 포맷팅 (포함 시):**
   ```markdown
   ## 참고: Git 커밋 이력

   ### 프로젝트 A
   - [2026-02-03] feat: 새 기능 추가 (3 files, +45/-12)
   - [2026-02-04] fix: 버그 수정 (1 file, +5/-3)

   **통계:** 15 commits, 47 files changed, 523 insertions(+), 89 deletions(-)

   ### 프로젝트 B
   - [2026-02-02] refactor: 코드 리팩토링 (8 files, +120/-95)

   **통계:** 8 commits, 23 files changed, 234 insertions(+), 156 deletions(-)
   ```

4. **파일 저장:**
   - 저장 경로: `{obsidian_vault_path}/{filename}`
   - 예: `/Users/choiyoungjun/Documents/Obsidian Vault/ob-glens/작업 리뷰/2026/2.9.md`
   - Write 도구 사용

5. **프로젝트 정보 파일 업데이트:**
   - `프로젝트 정보.md` 읽기
   - 각 프로젝트의 "### 최근 활동" 섹션에 새 항목 추가:
     ```markdown
     - 2026-02-09: 주간 보고서 작성 [[2.9]]
     ```
   - Edit 도구로 업데이트

6. **완료 메시지:**
   ```
   "주간 보고서가 생성되었습니다!
   📍 위치: /path/to/2.9.md
   📅 기간: 2026.2.2 - 2026.2.6

   프로젝트 정보 파일도 업데이트되었습니다."
   ```

## Error Handling

### 날짜 입력 오류
- 형식이 잘못되었거나 유효하지 않은 날짜 → 재입력 요청
- 다양한 구분자 허용 (`~`, `-`, `to` 등)

### 파일 경로 오류
- **프로젝트 정보 파일 없음:**
  - 에러 메시지 + `assets/project-info-example.md` 참조 안내
  - 대화형으로 프로젝트 정보 수집 제안

- **Obsidian 저장 경로 없음:**
  - 디렉토리 자동 생성 시도
  - 실패 시 대체 경로 제안

- **회의록 파일 없음:**
  - 경고 후 "미팅 내용 없음"으로 진행

### Git 관련 오류
- **Git 경로 무효:** Git 커밋 섹션 생략하고 진행
- **Git 미설치:** 경고 후 Git 커밋 생략
- **커밋 없음:** "해당 기간 커밋 없음" 표시

### 사용자 입력 오류
- **필수 항목 비어있음:** "진행 상황"은 필수이므로 재입력 요청
- **이슈/미팅 비어있음:** "없음" 또는 공란으로 진행

### MEMORY 파일 오류
- **설정 파일 없음:** MEMORY 참조 기능 스킵, 기존대로 진행
- **MEMORY.md 없음:** 경고 후 MEMORY 참조 없이 진행
- **날짜 파싱 실패:** MEMORY 전체를 참조로 표시

---

## Integration with project-memory-manager

이 스킬은 `project-memory-manager` 스킬과 연동하여 프로젝트 메모리를 참조합니다.

### 연동 방식

**1. 설정 파일 공유**
- 두 스킬 모두 `~/.claude/project-memory-config.yaml` 사용
- 프로젝트 경로 일관성 유지

**2. MEMORY 읽기 전용 참조**
- weekly-report-maker는 MEMORY.md를 읽기만 함
- 수정/추가는 project-memory-manager가 담당

**3. 날짜 범위 필터링**
```
보고 기간: 2/2 ~ 2/6
    ↓
각 프로젝트의 MEMORY.md 읽기
    ↓
### 2026-02-02 ~ ### 2026-02-06 섹션만 추출
    ↓
보고서 작성 시 참고자료로 제공
```

### 워크플로우 통합

```
project-memory-manager
    ↓ (업데이트)
MEMORY.md (시간순 이벤트)
    ↓ (읽기)
weekly-report-maker
    ↓ (필터링: 보고 기간 내 섹션)
보고서 작성 시 참조
```

### 사용자 경험

MEMORY가 있을 때:
```
질문: "이번 주 진행한 작업 사항을 입력해주세요:"

💡 MEMORY 참고 (2/2~2/6):
- 2/3: API 응답 속도 개선 (Redis 캐싱)
- 2/5: 주간 스프린트 회의

[사용자 입력...]
```

MEMORY가 없을 때:
```
질문: "이번 주 진행한 작업 사항을 입력해주세요:"

[사용자 입력...]
```

### 설정 예시

**~/.claude/project-memory-config.yaml:**
```yaml
projects:
  - name: "글렌즈"
    base_path: "/Users/choiyoungjun/Documents/Obsidian Vault/ob-glens"
    # MEMORY.md 위치: {base_path}/MEMORY.md

  - name: "차이홍 톡톡"
    base_path: "/Users/choiyoungjun/Documents/Obsidian Vault/차이홍 톡톡"
    # MEMORY.md 위치: {base_path}/MEMORY.md
```

---

## Resources

### scripts/analyze_commits.py
Git 커밋 분석 Python 스크립트. 지정된 기간의 커밋 메시지와 파일 변경 통계를 JSON 형식으로 출력합니다.

**사용법:**
```bash
python scripts/analyze_commits.py \
  --repo /path/to/git/repo \
  --start 2026-02-02 \
  --end 2026-02-06
```

**출력 예시:**
```json
{
  "commits": [
    {
      "hash": "abc123",
      "date": "2026-02-03",
      "message": "feat: 새 기능 추가",
      "files_changed": 3,
      "insertions": 45,
      "deletions": 12
    }
  ],
  "summary": {
    "total_commits": 15,
    "total_files_changed": 47,
    "total_insertions": 523,
    "total_deletions": 89
  }
}
```

### assets/report-template.md
보고서 마크다운 템플릿. 플레이스홀더를 실제 데이터로 치환하여 최종 보고서를 생성합니다.

### assets/project-info-example.md
프로젝트 정보 파일 예제. Obsidian 볼트에 생성해야 하는 파일 형식을 보여줍니다.

### assets/config-example.yaml
스킬 설정 파일 예제. `~/.claude/weekly-report-config.yaml`로 복사하여 사용합니다.

### references/report-structure.md
보고서 각 섹션 작성 가이드 및 예시. 필요 시 참조하세요.
