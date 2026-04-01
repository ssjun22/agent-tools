---
name: git-commit-helper
description: "Analyzes staged changes and generates a commit message in 'type: 한글 설명' format. Use this skill whenever the user asks to commit code (e.g., '커밋해줘', '방금 작업 커밋해줘', 'commit this', 'commit'), wants a commit message, or needs help with conventional commits in Korean. Also trigger when the user says '커밋 메시지 만들어줘', '변경사항 정리해줘', or asks to review staged changes before committing."
---

# Git Commit Helper

Analyze staged changes and generate a Korean commit message following conventional commits format.

## Workflow

1. Run `git status` to see all changes (staged, unstaged, untracked)
2. Run `git diff --staged` (or `scripts/show-staged.sh`) to review staged contents in detail
3. If there are unstaged or untracked files relevant to the task, stage them with `git add <files>` before proceeding
4. Identify the appropriate commit type
5. Decide whether to split or merge commits:
   - If changes span multiple types (e.g., `chore` + `docs`, `feat` + `refactor`), ask the user whether to split
   - However, docs changes that exist *because of* the code change (e.g., context docs updated to reflect a config change, README updated alongside a new feature) belong in the same commit — they're part of the same logical unit of work, not an independent documentation effort
6. **If splitting commits:**
   - Run `git restore --staged .` to unstage everything
   - Stage only the files for the first commit with `git add <files>`
   - Run `git diff --staged` to verify staged contents before committing
   - Commit, then repeat for the next commit
7. Write a Korean summary (under 50 characters)
8. Add a bullet-point body in Korean if needed (max 3 lines)

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
| `docs` | 문서만 단독으로 변경 |
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
- [ ] 코드 변경에 수반되는 문서 업데이트는 코드 type으로 합침
- [ ] 커밋 분리 시, 커밋 직전 `git diff --staged`로 스테이징 내용 재확인

## References

For detailed examples by type, see `references/examples.md`.
