---
name: Git Commit Helper
description: git diff를 분석하여 'type: 한글 설명' 형식의 커밋 메시지를 생성합니다. 커밋 메시지 작성이나 staged 변경사항 검토 시 사용하세요.
hooks:
  PostToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "echo \"[$(date)] Git Commit Helper: Analyzed git diff for commit message\" >> ~/.claude/git-commit-helper.log"
---

# Git Commit Helper

## Quick start

Analyze staged changes and generate commit message:

```bash
# View staged changes
git diff --staged

# Generate Korean commit message based on changes
# (Claude will analyze the diff and suggest a Korean message)
```

## Commit message format

Follow conventional commits format with **Korean descriptions**:

```
<type>: <한글 설명>

[선택적 본문 - 한글]
```

**Important**: This project uses **Korean for commit message descriptions and bodies**. Only the type remains in English.

**Note**: Scope is optional and rarely used in this project.

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, missing semicolons)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples

**GOOD - Feature with refactoring:**

```
feat: DatePicker 컴포넌트 추가 및 Button 리팩토링

- DatePicker, Calendar, Popover UI 컴포넌트 추가
- Button 컴포넌트에 cva 패턴 적용하여 variant 관리 개선
- 과제 폼에서 제목 입력 필드 제거
```

**BAD - Paragraph style with periods:**

```
feat: DatePicker 컴포넌트 추가 및 Button 리팩토링

DatePicker, Calendar, Popover UI 컴포넌트를 추가했습니다.
Button 컴포넌트에 cva 패턴을 적용하여 variant 관리를 개선했습니다.
과제 폼에서 제목 입력 필드를 제거했습니다.
```

**Feature commit:**

```
feat: 평가 항목 저장 및 조회 기능 구현

- 평가 항목을 데이터베이스에 저장하고 조회할 수 있는 API 엔드포인트 추가
- 사용자가 작성한 평가 내용을 영구적으로 보관
```

**Bug fix:**

```
fix: 과제 평가 페이지 디자인 수정

- 평가 항목 입력 폼의 레이아웃이 깨지는 문제 해결
- 반응형 디자인이 모바일에서 올바르게 작동하도록 수정
```

**Chore:**

```
chore: env 포맷 파일 추가

- 환경 변수 설정을 위한 .env.example 파일 추가
- 필수 환경 변수 목록 및 설명 포함
```

**Refactor:**

```
refactor: 데이터베이스 쿼리 로직 개선

- 중복된 쿼리 패턴을 재사용 가능한 함수로 추출
- 코드 가독성 향상 및 유지보수성 개선
```

## Analyzing changes

Review what's being committed:

```bash
# Show files changed
git status

# Show detailed changes
git diff --staged

# Show statistics
git diff --staged --stat

# Show changes for specific file
git diff --staged path/to/file
```

## Commit message guidelines

**DO:**

- **Write descriptions and body in Korean** (type만 영어)
- Use noun-based endings ("추가", "수정", "구현", "개선")
- Keep first line under 50 characters
- **Keep body to maximum 3 lines** (본문은 최대 3줄 이내)
- **Use bullet points (하이픈)** for body items: `- 항목 설명`
- **No period at end of each bullet point** (각 항목 끝에 마침표 없음)
- Be clear and specific about what changed
- No period at end of summary
- Explain WHY not just WHAT in body (if needed)

**DON'T:**

- Use vague messages like "업데이트" alone
- Use scope in parentheses like `(auth)` or `(api)`
- Include technical implementation details in summary
- Write paragraphs in summary line
- Use past tense (과거형 사용 금지: "수정했음" X)
- Add Co-Authored-By footer (Co-Authored-By 추가 금지)
- Add periods at end of bullet points (bullet point 끝에 마침표 금지)

## Multi-file commits

When committing multiple related changes:

```
refactor: 인증 모듈 구조 개선

- 컨트롤러의 인증 로직을 서비스 레이어로 이동
- 검증 로직을 별도 validator로 분리
- 새 구조에 맞게 테스트 업데이트
```

## More examples

**Different types:**

- `feat: 대시보드에 로딩 스피너 추가`
- `fix: 이메일 형식 검증 오류 수정`
- `docs: API 사용 가이드 문서 작성`
- `style: 코드 포맷팅 및 린트 규칙 적용`
- `test: 사용자 인증 통합 테스트 추가`
- `chore: Node 버전을 20으로 업데이트`

## Template workflow

1. **Review changes**: `git diff --staged`
2. **Identify type**: Is it feat, fix, refactor, chore, etc.?
3. **Write summary in Korean**: Brief, clear description
4. **Add body in Korean**: Explain why and what impact (if needed)

## Interactive commit helper

Use `git add -p` for selective staging:

```bash
# Stage changes interactively
git add -p

# Review what's staged
git diff --staged

# Commit with Korean message
git commit -m "type: 한글 설명"
```

## Amending commits

Fix the last commit message:

```bash
# Amend commit message only
git commit --amend

# Amend and add more changes
git add forgotten-file.js
git commit --amend --no-edit
```

## Best practices

1. **Korean messages** - Write all commit messages in Korean (except type)
2. **Simple format** - Use `type: 한글 설명` format without scope
3. **Bullet point body** - Use `- 항목` format, maximum 3 lines, no periods at end
4. **No Co-Authored-By** - Don't add Co-Authored-By footer
5. **Atomic commits** - One logical change per commit
6. **Test before commit** - Ensure code works
7. **Reference issues** - Include issue numbers if applicable
8. **Keep it focused** - Don't mix unrelated changes
9. **Write for humans** - Future you will read this

## Commit message checklist

- [ ] Message is written in Korean (description and body)
- [ ] Type is appropriate (feat/fix/docs/chore/etc.)
- [ ] Summary is clear and concise
- [ ] Summary is under 50 characters
- [ ] No scope in parentheses (keep it simple)
- [ ] Body uses bullet points with hyphens (- 항목)
- [ ] No periods at end of bullet points
- [ ] Body is maximum 3 lines (본문 최대 3줄)
- [ ] Body explains WHY not just WHAT (if needed)
- [ ] No Co-Authored-By footer
- [ ] Related issue numbers are included (if applicable)
