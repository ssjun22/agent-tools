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

## Pattern Format

All patterns follow this structure:

````markdown
---
title: Pattern Name
impact: HIGH | MEDIUM | LOW
impactDescription: one-line explanation
tags: tag1, tag2, tag3
---

## Pattern Name

Brief explanation

**Incorrect (why it's wrong):**

```language
// Bad code example
```
````

**Correct (why it's right):**

```language
// Good code example
```

**Note:** Additional context

````

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
