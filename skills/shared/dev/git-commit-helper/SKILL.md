---
name: git-commit-helper
description: "This skill should be used when the user wants to create a Git commit message. Analyzes staged changes and generates a commit message in 'type: 한글 설명' format. Triggered when the user asks for a commit message, wants to review staged changes, or needs help with conventional commits in Korean."
---

# Git Commit Helper

Analyze staged changes and generate a Korean commit message following conventional commits format.

## Workflow

1. Run `scripts/show-staged.sh` (or `git diff --staged`) to review changes
2. Identify the appropriate type
3. If staged changes span multiple types (e.g., `chore` + `docs`, `feat` + `refactor`), consider splitting into separate commits — but ask the user first before proceeding
4. Write a Korean summary (under 50 characters)
5. Add a bullet-point body in Korean if needed (max 3 lines)

## Commit Message Format

```
<type>: <한글 설명>

- 변경 이유나 영향 (선택)
- 추가 항목 (최대 3줄)
```

**Rules:**
- Type is English, everything else is Korean
- No scope (e.g., `(auth)` 금지)
- No period at end of summary or bullet points
- No Co-Authored-By footer
- Use noun endings: "추가", "수정", "구현", "개선"
- No past tense: "수정했음" (X)

## Types

| Type | When to use |
|------|-------------|
| `feat` | 새 기능 추가 |
| `fix` | 버그 수정 |
| `docs` | 문서 변경 |
| `style` | 코드 스타일 (포맷팅) |
| `refactor` | 기능 변경 없는 코드 개선 |
| `test` | 테스트 추가/수정 |
| `chore` | 빌드, 설정, 유지보수 |

## Checklist

- [ ] 한글로 작성 (type만 영어)
- [ ] 요약 50자 이내
- [ ] scope 없음
- [ ] bullet point 사용, 마침표 없음
- [ ] 본문 최대 3줄
- [ ] Co-Authored-By 없음
- [ ] 여러 type이 혼재하면 커밋 분리 여부를 사용자에게 확인

## References

For detailed examples by type, see `references/examples.md`.
