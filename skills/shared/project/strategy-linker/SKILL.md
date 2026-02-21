---
name: strategy-linker
description: This skill should be used when the user wants to apply an agent strategy to a specific project repository. It symlinks (or copies) strategy files (rules/, skills/, agents/, hooks/) into the target repo's .claude/ directory using the apply_to_repo.py script. Triggered by requests like "X 전략을 Y 레포에 반영해줘", "X 전략 심링크 걸어줘", or "apply strategy X to repo Y".
---

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
