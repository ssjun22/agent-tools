# Dev Workflow

## Overview

11단계 개발 세션 파이프라인을 제공하는 플러그인. `@interviewer`부터 `@committer`까지 에이전트를 순차 호출하며, 각 단계의 CLEAR/BLOCKED 신호에 따라 자동 진행 또는 정지한다.

## When to Use

- 새 기능 개발이나 버그 수정을 체계적으로 진행하고 싶을 때
- OpenSpec 기반 Spec Driven Development 워크플로우를 사용할 때
- 코드 리뷰 → 문서 갱신 → 커밋까지 일관된 파이프라인이 필요할 때

## Workflow

```
1. 작업사항 확인 → 2. 작업 선택
→ 3. @interviewer → 4. @spec-writer
→ 5. @designer (프론트엔드만) → 6. @spec-builder
→ 7. @spec-checker → 8. 이슈 수정 (FAIL 시)
→ 9. @code-reviewer → 10. @docs-updater → 11. @committer
```

## Dependencies

`plugin.json` 참조. 1개 워크플로우 스킬 + 2개 개발 스킬 + 10개 에이전트로 구성.

## Usage

```bash
# Preview
python3 scripts/apply_to_repo.py dev-workflow --repo /path/to/project --dry-run

# Apply
python3 scripts/apply_to_repo.py dev-workflow --repo /path/to/project
```

적용 후 `/workflow`로 세션을 시작하면 체크리스트 기반 안내가 시작된다.

## Related Plugins

- **openspec-sdd** — Spec Driven Development 스펙 관리 (함께 사용 권장)
- **project-context** — 세션 간 프로젝트 상태 유지
