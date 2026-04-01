---
name: agent-tools-linker
description: This skill should be used when the user wants to link agent-tools skills or agents into a target project repository's .claude/ directory via symlinks or copies. Triggered by requests like "Y 레포에 X 스킬 심링크 걸어줘", "Y 레포에 X 에이전트 연결해줘", or "link skill X to repo Y".
argument-hint: <type> <name> <repo-alias>
---

# Agent Tools Linker

## Command Arguments

슬래시 커맨드로 호출 시 인자를 전달할 수 있습니다.

```
/agent-tools-linker <type> <name> <repo-alias>
```

- `$0` — 아티팩트 타입 (`skill`, `agent`)
- `$1` — 아티팩트 이름 (예: `git-commit-helper`, `gemini-prompt-evaluator`)
- `$2` — 대상 레포지토리 alias (예: `my-app`, `my-service`)

인자가 3개 모두 전달되면 dry-run → apply 워크플로우를 바로 실행합니다.
인자가 없거나 부족하면 대화형으로 확인합니다.

**예시:**
- `/agent-tools-linker skill git-commit-helper my-app` — 스킬을 my-app에 심링크
- `/agent-tools-linker agent gemini-prompt-evaluator my-app` — 에이전트와 의존 스킬을 함께 심링크

## Overview

`agent-tools`의 스킬과 에이전트를 대상 프로젝트 레포의 `.claude/` 디렉토리에 심링크(기본) 또는 복사로 연결한다.

## Script

```
scripts/link.py
```

## Workflow

1. `--list-repos`로 등록된 레포 확인
2. `--dry-run --verbose`로 미리보기
3. 실제 적용

## Commands

```bash
# 등록된 레포 목록 확인
python3 scripts/link.py --list-repos

# 스킬 링크
python3 scripts/link.py skill <name> --repo <alias>

# 에이전트 링크 (의존 스킬도 함께 링크됨)
python3 scripts/link.py agent <name> --repo <alias>

# 에이전트 링크 (의존성 무시)
python3 scripts/link.py agent <name> --repo <alias> --no-deps

# 옵션
--dry-run    # 미리보기 (파일 변경 없음)
--overwrite  # 기존 파일/심링크 덮어쓰기
--copy       # 복사 방식 (기본: 심링크)
--verbose    # 상세 출력
--no-deps    # 의존성 자동 링크 비활성화
```

## Dependency Resolution

에이전트(`.md`) 파일의 YAML frontmatter에 `skills:` 필드가 선언되어 있으면, 해당 스킬들을 자동으로 함께 링크한다.

**예시 — gemini-prompt-evaluator.md:**
```yaml
---
name: gemini-prompt-evaluator
skills:
  - gemini3-prompt-reviewer
  - prompt-reviewer
---
```

위 에이전트를 링크하면 `gemini3-prompt-reviewer`와 `prompt-reviewer` 스킬도 `.claude/skills/`에 자동으로 심링크된다.

`--no-deps` 옵션으로 이 동작을 비활성화할 수 있다.

## Source Paths

| 타입    | 소스 위치                              | 적용 위치           |
|-------|--------------------------------------|------------------|
| skill | `agent-tools/skills/<name>/`  | `.claude/skills/` |
| agent | `agent-tools/agents/<name>.md`| `.claude/agents/` |

- skill은 카테고리(dev, log, meta 등) 하위까지 자동 탐색

## Config

레포 별칭은 `assets/config.local.json`의 `repos` 키로 관리한다.

```json
{
  "repos": {
    "my-project": "/path/to/my-project"
  }
}
```

## Notes

- 심링크 방식은 원본 수정 시 연결된 모든 레포에 즉시 반영됨
- `.claude/` 및 하위 폴더가 없으면 자동 생성
- 기존 파일은 기본적으로 스킵 (`--overwrite`로 교체 가능)
- 에이전트 링크 시 frontmatter의 `skills:` 의존성도 자동으로 함께 링크됨
