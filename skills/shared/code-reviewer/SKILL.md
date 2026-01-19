---
name: code-reviewer
description: Comprehensive code review guidelines for React, Next.js, FastAPI, and AI/LLM applications. Contains 77 patterns across 5 categories for optimal code quality, performance, and maintainability. Use when writing, reviewing, or refactoring code to ensure best practices.
license: MIT
metadata:
  author: knowre
  version: "1.0.0"
  tech_stack: "React 19, Next.js 15, FastAPI, Python, TypeScript"
---

# Code Reviewer

Comprehensive code review guidelines for modern full-stack applications with AI/LLM integration. Contains 77 patterns across 5 categories, prioritized by impact to guide code reviews and refactoring.

## When to Apply

Reference these guidelines when:

- Writing new React/Next.js components or FastAPI endpoints
- Implementing AI/LLM prompt engineering patterns
- Reviewing pull requests for code quality issues
- Refactoring existing code for better maintainability
- Setting up test strategies and writing test code
- Applying SOLID principles and clean code practices

## Rule Categories by Priority

| Priority | Category                                | Impact | Rules | Prefix                                                              |
| -------- | --------------------------------------- | ------ | ----- | ------------------------------------------------------------------- |
| 1        | Frontend (Next.js + React + TypeScript) | HIGH   | 45    | `async-`, `bundle-`, `server-`, `client-`, `rerender-`, `rendering-`, `js-`, `advanced-` |
| 2        | Backend (Python + FastAPI)              | HIGH   | 8     | `backend-`                                                          |
| 3        | AI/LLM (Prompt Engineering)             | MEDIUM | 8     | `ai-`                                                               |
| 4        | Code Quality & Design Principles        | HIGH   | 8     | `quality-`                                                          |
| 5        | Testing                                 | MEDIUM | 8     | `test-`                                                             |

## Quick Reference

### 1. Frontend (Next.js + React + TypeScript) - HIGH

`references/01_frontend/` - React Best Practices (45 patterns across 8 categories)

Pattern prefixes by category:
- `async-` for Eliminating Waterfalls (CRITICAL)
- `bundle-` for Bundle Size Optimization (CRITICAL)
- `server-` for Server-Side Performance (HIGH)
- `client-` for Client-Side Data Fetching (MEDIUM-HIGH)
- `rerender-` for Re-render Optimization (MEDIUM)
- `rendering-` for Rendering Performance (MEDIUM)
- `js-` for JavaScript Performance (LOW-MEDIUM)
- `advanced-` for Advanced Patterns (LOW)

### 2. Backend (Python + FastAPI) - HIGH

`references/02_backend/`

- `async-await.md` - Async/Await for I/O Operations
- `pydantic-validation.md` - Pydantic Model Validation
- `dependency-injection.md` - Dependency Injection Pattern
- `exception-handling.md` - Proper Exception Handling
- `query-optimization.md` - Database Query Optimization
- `type-hints.md` - Type Hints Usage
- `transaction-management.md` - Transaction Management
- `api-response.md` - API Response Structure

### 3. AI/LLM (Prompt Engineering) - MEDIUM

`references/03_ai_llm/`

- `prompt-templates.md` - Structured Prompt Templates
- `role-separation.md` - System/User/Assistant Role Separation
- `few-shot-learning.md` - Few-shot Learning Examples
- `token-optimization.md` - Token Usage Optimization
- `json-parsing.md` - JSON Response Parsing
- `prompt-injection.md` - Prompt Injection Prevention
- `error-recovery.md` - Error Recovery Strategy
- `context-management.md` - Context Window Management

### 4. Code Quality & Design Principles - HIGH

`references/04_code_quality/`

- `single-responsibility.md` - Single Responsibility Principle
- `open-closed.md` - Open/Closed Principle
- `dependency-inversion.md` - Dependency Inversion
- `meaningful-naming.md` - Meaningful Naming
- `function-size.md` - Function Size and Complexity
- `dry-principle.md` - DRY (Don't Repeat Yourself)
- `kiss-principle.md` - KISS (Keep It Simple)
- `magic-numbers.md` - Magic Numbers and Strings

### 5. Testing - MEDIUM

`references/05_testing/`

- `aaa-pattern.md` - AAA Pattern (Arrange-Act-Assert)
- `test-isolation.md` - Test Isolation
- `test-naming.md` - Meaningful Test Names
- `mocking-strategy.md` - Mock vs Real Dependencies
- `async-testing.md` - Async Test Handling
- `test-builders.md` - Test Data Builders
- `error-cases.md` - Testing Error Cases
- `flaky-tests.md` - Avoiding Flaky Tests

## Tech Stack

**Languages:** TypeScript, Python
**Frontend:** React 19, Next.js 15
**Backend:** FastAPI, Python 3.10+
**Database:** PostgreSQL, Prisma
**State Management:** Zustand, React Query (TanStack Query), tRPC
**Testing:** Jest, Vitest, Pytest
**Validation:** Zod, Pydantic
**AI/LLM:** Prompt Engineering, LiteLLM

## How to Use

Browse individual pattern files by category:

```
references/01_frontend/server-client-components.md
references/01_frontend/memoized-components.md
references/02_backend/async-await.md
references/02_backend/pydantic-validation.md
references/03_ai_llm/prompt-templates.md
references/04_code_quality/single-responsibility.md
references/05_testing/aaa-pattern.md
...
```

Or explore by category folder:

- `references/01_frontend/` - All frontend patterns
- `references/02_backend/` - All backend patterns
- `references/03_ai_llm/` - All AI/LLM patterns
- `references/04_code_quality/` - All code quality patterns
- `references/05_testing/` - All testing patterns

Each pattern includes:

- **Frontmatter** with title, impact level, and tags
- **Brief explanation** of why it matters
- **Incorrect code example** with explanation
- **Correct code example** with explanation
- **Note** with additional context

## Review Comment Format

PR 리뷰 코멘트 작성 시 다음 참조 문서를 활용하세요:

- **출력 포맷:** `references/review_output_format.md` - PR 리뷰 코멘트의 전체 구조
- **작성 규칙:** `references/review_rules.md` - DO/DON'T 가이드라인
- **예시:** `references/review_examples.md` - 실제 리뷰 코멘트 예시

각 패턴은 일관된 구조(title, impact, incorrect/correct examples)를 따르며, 리뷰 코멘트는 Issue 제목, Impact 레벨, 문제 설명, 개선 방법을 포함해야 합니다.

## PR Review Workflow

PR 리뷰 시 다음 단계를 따라 체계적으로 검토하세요.

### Step 1: Identify PR Scope

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

### Step 2: Automated Quick Scan (Optional)

**대형 PR (10+ 파일)의 경우:**

자동화 스크립트를 먼저 실행하여 명백한 위반 사항을 빠르게 식별합니다.

```bash
# PR 전체 분석
python scripts/pr_analyzer.py <project-path> --verbose

# 특정 디렉토리만 분석
python scripts/code_quality_checker.py src/components/ --verbose
```

**스크립트 출력 분석:**
- HIGH impact 위반 사항 우선 확인
- CRITICAL 패턴 위반이 있는지 체크
- 결과를 바탕으로 수동 리뷰 계획 수립

**소규모 PR (< 10 파일)의 경우:**
- 스크립트 없이 바로 Step 3로 진행

### Step 3: Manual Pattern Review

각 카테고리별로 우선순위에 따라 패턴을 확인합니다.

#### Frontend Changes

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

#### Backend Changes

**HIGH 패턴 확인:**

1. **Async/Await** - I/O 작업에 async 사용
2. **N+1 Query** - 쿼리 최적화
3. **Pydantic Validation** - 입력 검증
4. **Exception Handling** - 적절한 예외 처리

각 패턴의 상세 내용: `references/02_backend/`

#### Code Quality (모든 PR에 적용)

**SOLID 원칙 체크:**

1. **Single Responsibility** - 함수/클래스가 하나의 책임만
2. **Dependency Inversion** - 구체적 구현이 아닌 추상화에 의존

**기본 원칙:**

3. **Meaningful Naming** - 의도를 드러내는 이름
4. **Function Size** - 함수 길이와 복잡도
5. **DRY Principle** - 중복 코드 제거

각 패턴의 상세 내용: `references/04_code_quality/`

### Step 4: Write Review Comments

발견한 위반 사항을 리뷰 코멘트로 작성합니다.

**참조 문서:**
- **출력 포맷:** `references/review_output_format.md` - 리뷰 코멘트 구조
- **작성 규칙:** `references/review_rules.md` - DO/DON'T 가이드라인
- **예시:** `references/review_examples.md` - 실제 리뷰 코멘트 예시

**우선순위별 코멘트 작성 전략:**
- **Critical/Important:** 상세한 설명 + Before/After 코드 예시 + 파일:라인 참조
- **Minor:** 간단한 설명, 코드 예시는 선택적

### Step 5: Prioritize Feedback

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

### Step 6: Generate Summary (Optional)

대형 PR의 경우 리뷰 요약을 자동 생성할 수 있습니다.

```bash
python scripts/review_report_generator.py \
  --input review_findings.json \
  --output review_summary.md \
  --format markdown
```

**수동 요약 템플릿:**

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

## Best Practices Summary

### Frontend
- Eliminate waterfalls: use Promise.all(), defer await, use Suspense boundaries
- Optimize bundle size: avoid barrel imports, use dynamic imports
- Server-side: use React.cache() and LRU caching, parallelize fetches
- Client-side: use SWR for deduplication, deduplicate event listeners
- Re-render: extract memoized components, use functional setState
- Rendering: hoist static JSX, use content-visibility for long lists
- JavaScript: cache property access, use Set/Map for lookups
- Advanced: use refs for event handlers, useLatest for stable callbacks

### Backend
- Always use async/await for I/O operations
- Validate inputs with Pydantic models
- Prevent N+1 queries with proper query optimization
- Use dependency injection for testability

### AI/LLM
- Structure prompts with templates
- Separate System/User/Assistant roles clearly
- Optimize token usage by minimizing context
- Prevent prompt injection with input sanitization

### Code Quality
- Follow SOLID principles, especially SRP and DIP
- Use meaningful names that reveal intent
- Keep functions small and focused
- Eliminate duplication (DRY)

### Testing
- Structure tests with AAA pattern
- Ensure test isolation and independence
- Mock only external dependencies
- Test error cases and edge cases

## Automated Scripts

This skill provides automated analysis tools:

```bash
# Code Quality Checker
python scripts/code_quality_checker.py <target-path> [--verbose]

# PR Analyzer
python scripts/pr_analyzer.py <project-path> [options]

# Review Report Generator
python scripts/review_report_generator.py [arguments] [options]
````

## Resources

- **Frontend Guide:** `references/01_frontend/` (45 patterns)
- **Backend Guide:** `references/02_backend/` (8 patterns)
- **AI/LLM Guide:** `references/03_ai_llm/` (8 patterns)
- **Code Quality Guide:** `references/04_code_quality/` (8 patterns)
- **Testing Guide:** `references/05_testing/` (8 patterns)
- **Tool Scripts:** `scripts/` directory
