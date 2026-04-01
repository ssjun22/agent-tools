# PR Review Workflow

PR 리뷰 시 다음 단계를 따라 체계적으로 검토하세요.

## Step 1: Identify PR Scope

먼저 PR의 변경 범위를 파악하여 검토할 카테고리를 결정합니다.

**변경된 파일 확인:**

```bash
# GitHub CLI 사용
gh pr diff <pr-number>

# Git 명령어 사용
git diff main...feature-branch --name-only
```

**카테고리 매핑:**
- `*.tsx`, `*.ts` (components/, pages/, app/) → **Frontend** (`01_frontend/`)
- `*.py` (routers/, services/, models/) → **Backend** (`02_backend/`)
- Prompt 관련 코드 → **AI/LLM** (`03_ai_llm/`)
- 모든 코드 → **Code Quality** (`04_code_quality/`)
- `*.test.*`, `*.spec.*` → **Testing** (`05_testing/`)

## Step 2: Manual Pattern Review

각 카테고리별로 우선순위에 따라 패턴을 확인합니다.

### Frontend Changes

**CRITICAL 패턴 우선 확인:**

1. **Async Waterfalls** (`async-*`)
   - Sequential await 사용 여부
   - Promise.all() 사용 가능한지 확인
   - 참조: `references/01_frontend/async-defer-await.md`

2. **Bundle Size** (`bundle-*`)
   - Barrel imports (index.ts) 사용 여부
   - Dynamic imports 가능한지 확인
   - 참조: `references/01_frontend/bundle-*.md`

**HIGH 패턴:**

3. **Server Components** (`server-*`)
   - 'use client' 지시어가 필요한 곳에만 있는지
   - 참조: `references/01_frontend/server-client-components.md`

4. **Re-render Optimization** (`rerender-*`)
   - 불필요한 리렌더링 발생 여부
   - 참조: `references/01_frontend/rerender-*.md`

### Backend Changes

**HIGH 패턴 확인:**

1. **Async/Await** - I/O 작업에 async 사용
2. **N+1 Query** - 쿼리 최적화
3. **Pydantic Validation** - 입력 검증
4. **Exception Handling** - 적절한 예외 처리

각 패턴의 상세 내용: `references/02_backend/`

### Code Quality (모든 PR에 적용)

**SOLID 원칙 체크:**

1. **Single Responsibility** - 함수/클래스가 하나의 책임만
2. **Dependency Inversion** - 구체적 구현이 아닌 추상화에 의존

**기본 원칙:**

3. **Meaningful Naming** - 의도를 드러내는 이름
4. **Function Size** - 함수 길이와 복잡도
5. **DRY Principle** - 중복 코드 제거

각 패턴의 상세 내용: `references/04_code_quality/`

## Step 3: Write Review Comments

발견한 위반 사항을 리뷰 코멘트로 작성합니다.

**참조 문서:**
- **출력 포맷:** `references/pr_review/output_format.md` - 리뷰 코멘트 구조
- **작성 규칙:** `references/pr_review/rules.md` - DO/DON'T 가이드라인
- **예시:** `references/pr_review/examples.md` - 실제 리뷰 코멘트 예시

**우선순위별 코멘트 작성 전략:**
- **Critical/Important:** 상세한 설명 + Before/After 코드 예시 + 파일:라인 참조
- **Minor:** 간단한 설명, 코드 예시는 선택적

## Step 4: Prioritize Feedback

발견한 모든 위반 사항을 우선순위별로 분류합니다.

**Priority 1 - BLOCKING (PR 머지 불가):**
- CRITICAL 패턴 위반 (async waterfalls, bundle size 폭발)
- 보안 이슈 (prompt injection, SQL injection)
- 심각한 성능 문제 (N+1 query)

**Priority 2 - REQUEST CHANGES:**
- HIGH 패턴 위반 (server components 오용, SOLID 위반)
- 명백한 버그 가능성
- 테스트 누락

**Priority 3 - SUGGESTIONS:**
- MEDIUM 패턴 위반 (re-render 최적화 누락)
- 코드 가독성 개선
- 테스트 개선

**Priority 4 - NITPICKS (선택):**
- LOW 패턴 (advanced optimizations)
- 스타일 개선
- 마이너한 리팩토링 제안

**리뷰 코멘트 작성 시 표시:**

```markdown
🚫 [BLOCKING] ...
⚠️ [REQUEST CHANGES] ...
💡 [SUGGESTION] ...
🔧 [NITPICK] ...
```

## Step 5: Generate Summary (Optional)

Create a summary for large PRs using the following template:

```markdown
## PR Review Summary

**Reviewed by:** [Your name]
**Date:** YYYY-MM-DD
**PR:** #123 - [PR Title]

### Overview
- **Files changed:** X files
- **Categories reviewed:** Frontend, Backend, Code Quality
- **Total findings:** X (BLOCKING: X, HIGH: X, MEDIUM: X, LOW: X)

### Critical Issues (Must Fix)
1. [async-01] Waterfalls in API calls - src/components/UserProfile.tsx:45
2. [bundle-02] Barrel import causing large bundle - src/index.ts:10

### High Priority (Recommended)
1. [server-01] Unnecessary 'use client' - src/components/Header.tsx:1

### Suggestions (Optional)
1. [rerender-03] Consider memoizing expensive component

### Overall Assessment
[종합 의견 및 권장사항]
```
