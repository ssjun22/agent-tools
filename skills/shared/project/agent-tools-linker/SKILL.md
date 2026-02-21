---
name: agent-tools-linker
description: This skill should be used when the user wants to link agent-tools artifacts (strategies, skills, hooks, agents, rules) into a target project repository's .claude/ directory via symlinks or copies. Triggered by requests like "X 전략을 Y 레포에 반영해줘", "Y 레포에 X 스킬 심링크 걸어줘", "link X hook to Y repo", or "apply X to Y".
---

# Agent Tools Linker

## Overview

`agent-tools`의 전략, 스킬, 훅, 에이전트, 룰 파일을 대상 프로젝트 레포의 `.claude/` 디렉토리에 심링크(기본) 또는 복사로 연결한다.

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

# 사용 가능한 전략 목록 확인
python3 scripts/link.py --list-strategies

# 전략 전체 적용 (rules/ skills/ agents/ hooks/ 모두)
python3 scripts/link.py strategy <name> --repo <alias>

# 개별 아티팩트 적용
python3 scripts/link.py skill  <name> --repo <alias>
python3 scripts/link.py hook   <name> --repo <alias>
python3 scripts/link.py agent  <name> --repo <alias>
python3 scripts/link.py rule   <name> --repo <alias>

# 옵션
--dry-run    # 미리보기 (파일 변경 없음)
--overwrite  # 기존 파일/심링크 덮어쓰기
--copy       # 복사 방식 (기본: 심링크)
--verbose    # 상세 출력
```

## Artifact Source Paths

| 타입       | 소스 위치                             | 적용 위치           |
|----------|-------------------------------------|------------------|
| strategy | `agent-tools/strategies/<name>/`    | `.claude/` 하위 전체 |
| skill    | `agent-tools/skills/shared/<name>/` | `.claude/skills/` |
| hook     | `agent-tools/.claude/hooks/<name>`  | `.claude/hooks/`  |
| agent    | `agent-tools/.claude/agents/<name>` | `.claude/agents/` |
| rule     | `agent-tools/.claude/rules/<name>`  | `.claude/rules/`  |

## Strategy Mapping

전략 적용 시 하위 디렉토리를 `.claude/`에 매핑:

| 전략 디렉토리 | 적용 위치          |
|-------------|-------------------|
| `rules/`    | `.claude/rules/`  |
| `skills/`   | `.claude/skills/` |
| `agents/`   | `.claude/agents/` |
| `hooks/`    | `.claude/hooks/`  |

## Config

레포 별칭은 `assets/config.local.json`의 `repos` 키로 관리한다.
`config.local.json`이 없으면 `config.json`을 사용한다.

```json
{
  "strategies_path": "/path/to/agent-tools/strategies",
  "repos": {
    "my-project": "/path/to/my-project"
  }
}
```

## Notes

- 심링크 방식은 원본 수정 시 연결된 모든 레포에 즉시 반영됨
- `.claude/` 및 하위 폴더가 없으면 자동 생성
- 기존 파일은 기본적으로 스킵 (`--overwrite`로 교체 가능)

# Strategy Linker

## Overview

Apply agent strategies from the central `agent-tools` repository to target project repositories by creating symlinks (recommended) or copies in the project's `.claude/` directory.

## Script

All operations delegate to:

```
/Users/choiyoungjun/agent-tools/skills/shared/project/agent-strategy-manager/scripts/apply_to_repo.py
```

## Workflow

1. `--list-repos`로 등록된 레포 별칭 확인
2. `--dry-run --verbose`로 적용될 파일 미리보기
3. 문제 없으면 실제 적용

## Commands

```bash
# 등록된 레포 목록 확인
python3 <script> --list-repos

# 전략을 레포에 심링크로 적용 (기본, 추천)
python3 <script> <strategy-name> --repo <alias>

# 적용 전 미리보기
python3 <script> <strategy-name> --repo <alias> --dry-run --verbose

# 기존 파일 덮어쓰기
python3 <script> <strategy-name> --repo <alias> --overwrite

# 복사 방식으로 적용
python3 <script> <strategy-name> --repo <alias> --copy
```

## Mapping

| 전략 디렉토리 | 적용 위치          |
|-------------|-------------------|
| `rules/`    | `.claude/rules/`  |
| `skills/`   | `.claude/skills/` |
| `agents/`   | `.claude/agents/` |
| `hooks/`    | `.claude/hooks/`  |

## Repo Aliases

등록된 레포 별칭은 `agent-strategy-manager/assets/config.local.json`의 `repos` 키에서 관리한다. 새 레포 추가 시 해당 파일에 키-값을 추가한다.

## Notes

- 심링크 방식은 원본 전략 파일 수정 시 자동으로 모든 연결된 레포에 반영됨
- 복사 방식은 독립적인 커스터마이즈가 필요한 경우에 사용
- `.claude/` 디렉토리와 하위 폴더가 없으면 자동 생성됨
