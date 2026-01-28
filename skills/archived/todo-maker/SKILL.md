---
name: todo-maker
description: Provide standardized TODO templates for different task types (bug fixes, refactoring). Use this skill when creating structured TODO documents to ensure consistent format across the project. Triggered when users request TODO templates or need to create new task documentation.
---

# Todo Maker

## Overview

This skill provides standardized Markdown templates for creating TODO documents. It ensures consistent structure across all task documentation in the project, eliminating the need to recreate TODO formats from scratch each time.

## Quick Start

When creating a new TODO document:

1. Identify the task type (bug fix or refactoring)
2. Use the corresponding template from `assets/`
3. Copy the template content to the new TODO file
4. Fill in the sections with task-specific information
5. Update the creation date to the current date

## Available Templates

### Bug Fix Template

Use `assets/bug-fix-template.md` for bug-related tasks.

**Structure:**

- **작성일**: Document creation date (YYYY-MM-DD format)
- **타입**: Task type (버그 수정)
- **우선순위**: Priority level (Critical/High/Medium/Low) with checkbox selection
- **배경**: Context about how the bug was discovered
- **문제 상황**: Detailed bug description with:
    - Reproduction steps
    - Expected behavior
    - Actual behavior
    - Error messages (if applicable)
- **TODO**: Checklist of tasks to fix the bug
- **관련 파일**: List of related file paths

**Example Usage:**
When a user reports "Create a TODO for the login page error," copy the bug fix template and fill in the specific details about the login page issue.

### Refactoring Template

Use `assets/refactoring-template.md` for code improvement tasks.

**Structure:**

- **작성일**: Document creation date (YYYY-MM-DD format)
- **타입**: Task type (리팩토링)
- **우선순위**: Priority level (Critical/High/Medium/Low) with checkbox selection
- **배경**: Context about why refactoring is needed
- **문제 상황**: Description of current code issues with:
    - Current state
    - Improvement goals
- **TODO**: Checklist of refactoring steps including:
    - Code analysis
    - Strategy planning
    - Test verification
    - Step-by-step implementation
- **관련 파일**: List of files to be refactored

**Example Usage:**
When a user says "Create a TODO for refactoring the authentication module," use the refactoring template and outline the specific components that need improvement.

## Usage Guidelines

### Creating a TODO Document

To create a new TODO document from a template:

1. Read the appropriate template file from `assets/`
2. Copy the entire template content
3. Create or write to the target TODO file
4. Replace placeholder values:
    - Update `작성일` to current date (format: YYYY-MM-DD)
    - Select appropriate priority checkbox
    - Fill in background and problem description
    - Add specific TODO items relevant to the task
    - List all related file paths

### Template Selection

**Choose Bug Fix Template when:**

- Fixing broken functionality
- Addressing user-reported issues
- Resolving errors or exceptions
- Correcting unexpected behavior

**Choose Refactoring Template when:**

- Improving code structure
- Reducing technical debt
- Enhancing maintainability
- Optimizing performance
- Applying design patterns

### Customization Tips

- **TODO Section**: Expand or modify checklist items based on task complexity
- **Priority**: Always select exactly one priority level
- **Related Files**: Include all files that will be read, modified, or tested
- **Problem Description**: Be as specific as possible to help future developers understand the context

## Best Practices

- Keep the template structure consistent across all TODO documents
- Update the creation date to reflect when the TODO was actually created
- Select only one priority level (do not check multiple boxes)
- Use concrete file paths in the "관련 파일" section (e.g., `src/components/login/login-form.tsx`)
- Write clear, actionable items in the TODO checklist
- Include reproduction steps for bugs when applicable
- Define measurable improvement goals for refactoring tasks
