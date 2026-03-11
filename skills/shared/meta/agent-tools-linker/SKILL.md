---
name: agent-tools-linker
description: This skill should be used when the user wants to link agent-tools skills or agents into a target project repository's .claude/ directory via symlinks or copies. Triggered by requests like "Y 레포에 X 스킬 심링크 걸어줘", "Y 레포에 X 에이전트 연결해줘", or "link skill X to repo Y".
---

# Agent Tools Linker

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

# 에이전트 링크
python3 scripts/link.py agent <name> --repo <alias>

# 옵션
--dry-run    # 미리보기 (파일 변경 없음)
--overwrite  # 기존 파일/심링크 덮어쓰기
--copy       # 복사 방식 (기본: 심링크)
--verbose    # 상세 출력
```

## Source Paths

| 타입    | 소스 위치                              | 적용 위치           |
|-------|--------------------------------------|------------------|
| skill | `agent-tools/skills/shared/<name>/`  | `.claude/skills/` |
| agent | `agent-tools/agents/shared/<name>.md`| `.claude/agents/` |

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
