---
name: code-reviewer
description: This skill should be used when refactoring code, reviewing pull requests, or checking code quality. Provides 78 prioritized patterns across frontend, backend, AI/LLM, code quality, and testing categories with incorrect/correct examples for each pattern.
---

# Code Reviewer

Comprehensive code review guidelines for modern full-stack applications with AI/LLM integration. Contains 78 patterns across 5 categories, prioritized by impact to guide code reviews and refactoring.

## When to Use

Identify your goal before using this skill:

### 🔧 Refactoring

Improve existing code quality and apply best practices.

**Approach:**
1. Identify which category applies (Frontend/Backend/AI/Quality/Testing)
2. Review relevant patterns in `references/`
3. Apply fixes based on priority (CRITICAL → HIGH → MEDIUM)

**Example:**
- Frontend performance issues → Check `references/01_frontend/async-*`, `bundle-*` patterns
- Backend optimization → Check `references/02_backend/query-optimization.md`, `async-await.md`

### 📝 PR Review

Comprehensive pull request review with structured feedback.

**Approach:**
- Detailed workflow: `references/pr_review/workflow.md`
- Comment format: `references/pr_review/output_format.md`
- Writing rules: `references/pr_review/rules.md`
- Examples: `references/pr_review/examples.md`



### 🔍 Code Quality Check

Analyze specific files or directories against patterns.

**Approach:**
1. Identify relevant pattern categories for the code
2. Read applicable patterns from `references/`
3. Review code against CRITICAL and HIGH priority patterns
4. Report findings with file:line references

## Pattern Categories

| Priority | Category                                | Impact | Rules | Prefix                                                              |
| -------- | --------------------------------------- | ------ | ----- | ------------------------------------------------------------------- |
| 1        | Frontend (Next.js + React + TypeScript) | HIGH   | 46    | `async-`, `bundle-`, `server-`, `client-`, `rerender-`, `rendering-`, `js-`, `advanced-` |
| 2        | Backend (Python + FastAPI)              | HIGH   | 8     | `backend-`                                                          |
| 3        | AI/LLM (Prompt Engineering)             | MEDIUM | 8     | `ai-`                                                               |
| 4        | Code Quality & Design Principles        | HIGH   | 8     | `quality-`                                                          |
| 5        | Testing                                 | MEDIUM | 8     | `test-`                                                             |

## Pattern Files

### 1. Frontend (Next.js + React + TypeScript) - HIGH

`references/01_frontend/` - React Best Practices (46 patterns across 8 categories)

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

## Pattern File Structure

Each pattern file includes:

- **Frontmatter** with title, impact level, and tags
- **Brief explanation** of why it matters
- **Incorrect code example** with explanation
- **Correct code example** with explanation
- **Note** with additional context

## Tech Stack

**Languages:** TypeScript, Python  
**Frontend:** React 19, Next.js 15  
**Backend:** FastAPI, Python 3.10+  
**Database:** PostgreSQL, Prisma  
**State Management:** Zustand, React Query (TanStack Query), tRPC  
**Testing:** Jest, Vitest, Pytest  
**Validation:** Zod, Pydantic  
**AI/LLM:** Prompt Engineering, LiteLLM



## Resources

- **Frontend Guide:** `references/01_frontend/` (46 patterns)
- **Backend Guide:** `references/02_backend/` (8 patterns)
- **AI/LLM Guide:** `references/03_ai_llm/` (8 patterns)
- **Code Quality Guide:** `references/04_code_quality/` (8 patterns)
- **Testing Guide:** `references/05_testing/` (8 patterns)
- **PR Review:** `references/pr_review/` (workflow, format, rules, examples)
