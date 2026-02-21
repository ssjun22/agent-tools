---
name: skill-installer
description: Install skills from the current skills repository to other projects via symbolic links. This skill should be used when the user wants to install one or more skills into another project, set up .claude/skills/ directory structure, or manage which skills are available in a target project. Must be run from the root of a repository containing a skills/shared/ directory. Triggered when the user says "스킬 설치", "install skill", "다른 프로젝트에 스킬 추가", or similar.
allowed-tools: Read, Write, Bash, Glob
---

# Skill Installer

## Overview

현재 스킬 레포지토리에서 개발한 스킬을 다른 프로젝트에 심볼릭 링크로 설치합니다.
이 스킬은 **`skills/shared/` 디렉토리가 존재하는 레포 루트에서 실행**해야 합니다.

## Workflow

### Step 1: Check Configuration

스킬 디렉토리에 `config.json`이 있는지 확인합니다.

```bash
ls skills/shared/meta/skill-installer/config.json
```

**config.json이 없는 경우 (초기 설정):**

사용자에게 자주 사용하는 프로젝트 경로를 물어봅니다:

```
Question template:
[
  {
    "question": "자주 설치할 프로젝트 경로를 알려주세요 (나중에 config.json에서 직접 수정 가능)",
    "header": "프로젝트 경로",
    "options": [
      { "label": "예시: /Users/username/projects/my-app", "description": "절대 경로로 입력하세요" },
      { "label": "건너뛰기 (매번 직접 입력)", "description": "config.json 없이 진행" }
    ]
  }
]
```

사용자가 경로를 입력하면 `config.json` 생성:
```json
{
  "projects": [
    { "name": "프로젝트 A", "path": "/absolute/path/to/project" }
  ]
}
```

`config.json`이 있는 경우 → 내용 읽기 후 Step 2 진행.

**config.json 형식:**
```json
{
  "projects": [
    { "name": "프로젝트 A", "path": "/absolute/path/to/project-a" },
    { "name": "프로젝트 B", "path": "/absolute/path/to/project-b" }
  ]
}
```

`config.json`은 `.gitignore`에 의해 Git에서 제외됩니다 (로컬 전용 설정).

### Step 2: Verify and List Available Skills

먼저 현재 디렉토리가 유효한 스킬 레포인지 확인합니다:

```bash
pwd                          # 현재 절대경로 저장 (심볼릭 링크 생성 시 사용)
ls skills/shared/            # 없으면 에러 안내 후 중단
```

`skills/shared/`가 없으면:
```
❌ 현재 디렉토리에 skills/shared/가 없습니다.
스킬 레포 루트에서 실행해주세요.
```

유효하면 하위의 모든 스킬 목록을 수집합니다:

```bash
find skills/shared -name "SKILL.md" | sort
```

각 스킬의 경로에서 **스킬명**과 **카테고리**를 추출합니다:
- 경로 형식: `skills/shared/{카테고리}/{스킬명}/SKILL.md`
- 예: `skills/shared/log/daily-work-log-manager/SKILL.md` → `[log] daily-work-log-manager`

이미 설치된 스킬(타겟 프로젝트에 링크가 존재하는 스킬)은 `(설치됨)` 표시.

### Step 3: Select Target Project

`config.json`의 프로젝트 목록을 보여주고 선택하게 합니다:

```
Question template:
[
  {
    "question": "어느 프로젝트에 설치할까요?",
    "header": "타겟 프로젝트",
    "options": [
      { "label": "프로젝트 A (/path/to/project-a)", "description": "config.json에 저장된 프로젝트" },
      { "label": "프로젝트 B (/path/to/project-b)", "description": "config.json에 저장된 프로젝트" },
      { "label": "직접 입력", "description": "경로를 직접 입력합니다" }
    ]
  }
]
```

"직접 입력" 선택 시 → 경로 입력 요청 후, `config.json`에 추가할지 물어봄:
```
Question template:
[
  {
    "question": "이 프로젝트를 config.json에 저장할까요?",
    "header": "저장 여부",
    "options": [
      { "label": "예, 저장합니다", "description": "다음에 목록에서 선택 가능" },
      { "label": "아니오, 이번만 사용", "description": "config.json 수정 안 함" }
    ]
  }
]
```

**타겟 경로 유효성 검사:**
```bash
ls {target_path}
```
존재하지 않으면 에러 메시지 출력 후 중단.

### Step 4: Select Skills to Install

설치할 스킬을 멀티셀렉트로 선택합니다.

표시 형식:
```
[log] daily-work-log-manager        - Daily work journal manager
[dev] git-commit-helper             - Git commit message helper
[meta] skill-creator                - Skill creation guide
...
```

각 스킬의 description은 `SKILL.md`의 YAML frontmatter에서 읽어옵니다.

이미 설치된 스킬은 `(이미 설치됨)` 표시와 함께 포함 (재설치 가능).

### Step 5: Check Target Directory

타겟 프로젝트의 `.claude/skills/` 디렉토리를 확인합니다:

```bash
ls {target_path}/.claude/skills/
```

**디렉토리가 없는 경우:**
```bash
mkdir -p {target_path}/.claude/skills/
```

생성 후 안내:
```
✅ .claude/skills/ 디렉토리를 생성했습니다.
```

### Step 6: Create Symbolic Links

선택한 각 스킬에 대해 심볼릭 링크를 생성합니다:

```bash
ln -s {agent_tools_absolute_path}/skills/shared/{카테고리}/{스킬명} \
      {target_path}/.claude/skills/{스킬명}
```

**이미 링크가 존재하는 경우:**

```
Question template:
[
  {
    "question": "{스킬명}이 이미 설치되어 있습니다. 어떻게 할까요?",
    "header": "중복 처리",
    "options": [
      { "label": "덮어쓰기", "description": "기존 링크를 제거하고 새로 생성" },
      { "label": "건너뛰기", "description": "이 스킬은 설치하지 않음" },
      { "label": "모두 덮어쓰기", "description": "충돌하는 모든 스킬에 적용" },
      { "label": "모두 건너뛰기", "description": "충돌하는 모든 스킬에 적용" }
    ]
  }
]
```

**덮어쓰기 시:**
```bash
rm {target_path}/.claude/skills/{스킬명}
ln -s {절대경로}/skills/shared/{카테고리}/{스킬명} \
      {target_path}/.claude/skills/{스킬명}
```

**심볼릭 링크 생성 시 주의사항:**
- 반드시 **절대경로**를 사용해야 함 (`스킬 레포`의 실제 절대경로)
- `스킬 레포` 절대경로 확인:
  ```bash
  pwd
  ```

### Step 7: Confirm Results

설치 완료 후 결과 요약:

```
✅ 스킬 설치 완료!

📂 타겟 프로젝트: 프로젝트 A (/path/to/project-a)

설치된 스킬:
  ✅ daily-work-log-manager → .claude/skills/daily-work-log-manager
  ✅ git-commit-helper      → .claude/skills/git-commit-helper
  ⏭️  skill-creator          → 건너뜀 (이미 설치됨)

총 N개 설치, M개 건너뜀
```

**다음 단계 안내:**

타겟 프로젝트의 `.claude/settings.json`에 스킬을 등록해야 Claude Code에서 사용할 수 있습니다.
자동 등록을 원하면 Step 8을 진행합니다.

### Step 8: Register in settings.json (선택사항)

타겟 프로젝트의 `.claude/settings.json`에 설치한 스킬을 자동 등록합니다.

```
Question template:
[
  {
    "question": "설치한 스킬을 .claude/settings.json에 자동 등록할까요?",
    "header": "설정 등록",
    "options": [
      { "label": "예, 자동 등록합니다 (권장)", "description": "Claude Code에서 즉시 사용 가능" },
      { "label": "아니오, 직접 등록하겠습니다", "description": "스킬 종료" }
    ]
  }
]
```

**settings.json이 없는 경우:** 새로 생성
**있는 경우:** `skills` 배열에 추가 (중복 제외)

```json
{
  "skills": [
    ".claude/skills/daily-work-log-manager",
    ".claude/skills/git-commit-helper"
  ]
}
```

**주의:** 기존 settings.json 내용을 보존하면서 `skills` 키만 업데이트합니다.

---

## Edge Cases

| 상황 | 처리 방법 |
|------|----------|
| 타겟 경로가 존재하지 않음 | 에러 메시지 출력 후 중단 |
| `skills/shared/`에 스킬이 없음 | "설치 가능한 스킬이 없습니다" 안내 |
| Python 없이 실행 | Bash 도구로 직접 처리 |
| 링크 생성 권한 없음 | 에러 메시지 + `sudo` 안내 |
| 이미 디렉토리(링크 아님)가 존재 | 별도 경고 후 처리 방법 선택 |

---

## config.json Reference

```json
{
  "projects": [
    {
      "name": "프로젝트 A",
      "path": "/absolute/path/to/project-a"
    },
    {
      "name": "프로젝트 B",
      "path": "/absolute/path/to/project-b"
    }
  ]
}
```

**위치:** `skills/shared/meta/skill-installer/config.json`
**Git:** `.gitignore`에 의해 제외 (로컬 전용)

---

## Notes

- 이 스킬은 `skills/shared/`가 존재하는 레포 루트에서만 실행 가능합니다
- 심볼릭 링크는 절대경로를 사용하므로 스킬 레포 경로가 변경되면 재설치 필요
- 스킬 업데이트는 스킬 레포에서만 하면 됨 (링크이므로 자동 반영)
- `config.json`은 개인 설정이므로 Git에 커밋하지 않습니다
