---
name: ob:spec-first-architect
description: This skill should be used when the user wants to design and document software features before writing code. It creates detailed specification documents in Obsidian format, focusing on business logic, API design, and data models. The skill enforces a "spec-first" approach where no source code is modified until the specification is confirmed by the user.
---

# Spec-First Architect

## Overview

Spec-First Architect enables designing and documenting software features before writing any code. Transform user requirements into comprehensive specification documents within Obsidian, complete with business logic flows, API schemas, and acceptance criteria. The specification serves as the single source of truth, ensuring all stakeholders align on design before implementation begins.

### Spec Types & Categories

This skill supports three specification types, each with tailored templates:

1. **Agent Spec**: For designing LLM agents, focusing on:
   - Agent architecture and orchestration
   - Prompt design and optimization
   - Tools/Functions integration
   - Evaluation logic (LLM vs rule-based)
   - Token usage optimization
   - **Category**: Saved in `specs/agent/`

2. **Backend Spec**: For APIs and backend features, focusing on:
   - API endpoints and schemas
   - Data models and business logic
   - Migration strategies
   - Test plans
   - **Category**: Saved in `specs/backend/`

3. **Frontend Spec**: For UI and client-side features, focusing on:
   - Component design and structure
   - User interactions and flows
   - State management
   - UI/UX considerations
   - **Category**: Saved in `specs/frontend/`

**Usage**: The skill automatically detects the spec type and category based on the user's request. If unclear, it will ask the user to clarify the category (agent/backend/frontend).

## Core Principles

### 1. Design Before Code

**Never modify source code until the specification is confirmed.**

- All design decisions, business rules, and technical specifications must be documented first
- Code changes only occur after the user explicitly marks the spec as `✅ Confirmed`
- The specification document becomes the authoritative reference for implementation

### 2. Obsidian-Native Documentation

**Embrace Obsidian's features for rich, interconnected documentation.**

- Use wiki links `[[Document]]` to connect related specs
- Use callouts `> [!info]` to highlight important information
- Store specs in project-specific directories: `Projects/[project-name]/specs/`

### 3. Clear Documentation

**Focus on clear, structured text descriptions.**

- Use Obsidian's markdown features (callouts, tables, lists) for clarity
- Organize information hierarchically
- Link related specifications using wiki links

### 4. Iterative Refinement

**Collaborate with the user through a feedback loop.**

- Start with an initial draft (status: `🏗 Draft`)
- Refine based on user feedback and clarifying questions
- Only mark as `✅ Confirmed` when the user explicitly approves

## Configuration

This skill uses a configuration file located at `skills/shared/ob-spec-first-architect/.env`.

**First-time setup**: Copy `.env.example` to `.env` and configure the required settings.

### Key Settings

- **OBSIDIAN_VAULT_PATH** (required): Absolute path to your Obsidian vault
- **BASE_DIR** (default: `ob-glens`): Base directory within vault
- **SPECS_DIR** (default: `specs`): Directory name for specifications
- **USE_PROJECT_ROOT** (default: `false`):
  - `false`: Specs saved in `{BASE_DIR}/{SPECS_DIR}/{category}/`
  - `true`: Specs saved in `{BASE_DIR}/{PROJECT_ROOT}/{SPECS_DIR}/{category}/`

### Example Directory Structure

```
ObsidianVault/
└── ob-glens/              # BASE_DIR
    └── specs/             # SPECS_DIR
        ├── agent/         # Agent specs
        ├── backend/       # Backend specs
        └── frontend/      # Frontend specs
```

See `.env.example` for detailed configuration options and project mappings.

## User Interaction Guidelines

This section provides best practices for interacting with users when creating and updating specification documents.

### Asking Effective Questions

When requirements are unclear, ask specific, targeted questions:

**Good Examples**:

- "What should happen if the user tries to cancel an order that's already shipped?"
- "Should the API support pagination? If so, what's the maximum page size?"
- "When a payment fails, should we retry automatically or require user action?"

**Avoid Generic Questions**:

- ❌ "Is this correct?"
- ❌ "Do you want anything else?"

### Presenting Updates

After each update, inform the user clearly:

```
The specification has been updated:
- Added edge case handling for concurrent requests
- Defined retry policy for external API failures
- Updated state diagram to include 'Refunding' state

Location: Projects/ecommerce/specs/order-management.md

Would you like to confirm this specification, or should I refine it further?
```

### Escalating Decisions

If encountering a design choice with trade-offs, present options:

```
I've identified two approaches for handling inventory reservation:

Option A: Pessimistic Locking
- Pros: Prevents overselling
- Cons: Reduced concurrency

Option B: Optimistic Locking with Retry
- Pros: Better performance
- Cons: Users might see "out of stock" after adding to cart

Which approach aligns better with your requirements?
```

### Confirming File Selection

When multiple spec files exist, always confirm with the user:

**Clear Match**:
```
I found `user-authentication-api.md`. Should I update this file or create a new one?
```

**Multiple Matches**:
```
I found these related files:
- user-authentication-ui.md
- login-form.md

Which one should I update, or should I create a new file?
```

**No Match**:
```
No existing spec found for this feature. I'll create a new document.
What filename would you like? (Suggested: user-login-flow.md)
```

## Workflow

### Step 0: Load Configuration and Determine Category

Before starting, load configuration and determine the spec category:

1. **Read configuration** from `skills/shared/ob-spec-first-architect/.env`:
   - Extract OBSIDIAN_VAULT_PATH, BASE_DIR, SPECS_DIR, USE_PROJECT_ROOT

2. **Determine spec category** by analyzing the user's request:
   - **agent**: Keywords like "agent", "LLM", "prompt", "orchestration"
   - **backend**: Keywords like "API", "endpoint", "database", "backend", "service"
   - **frontend**: Keywords like "UI", "component", "frontend", "interface", "page"
   - If unclear, ask the user to choose between agent/backend/frontend

3. **Construct target directory path**:
   - If `USE_PROJECT_ROOT=false`: `{VAULT}/{BASE_DIR}/{SPECS_DIR}/{category}/`
   - If `USE_PROJECT_ROOT=true`: `{VAULT}/{BASE_DIR}/{PROJECT_ROOT}/{SPECS_DIR}/{category}/`

### Step 1: Search Existing Specs (Filename-Based)

**Search only by filename** to minimize token usage:

1. **List all spec files** in the target category directory:
   - Use Glob to find all markdown files: `${TARGET_DIR}/*.md`
   - Extract filenames only (do NOT read file contents)

2. **Identify potential matches**:
   - Look for similar feature names in filenames
   - Example: User requests "user login" → Look for `user-authentication.md`, `login-api.md`, etc.

3. **Present findings to user**:
   - If clear match found: "I found `user-authentication-api.md`. Should I update this file or create a new one?"
   - If multiple matches: "I found these related files: [list]. Which one should I update, or should I create a new file?"
   - If no match: Proceed to Step 2 (Create new document)

**Important**: Only read file contents AFTER the user confirms which file to update.

### Step 2: Decide Create vs Update

Based on Step 1 results and user confirmation:

**Option A: Update Existing Document**
- User confirmed an existing file should be updated
- Read the confirmed file to understand current content
- Ask clarifying questions about what to add/modify
- Proceed to Step 3 (Update mode)

**Option B: Create New Document**
- No matching file exists, OR
- User wants a new file despite existing matches
- Ask clarifying questions about requirements
- Proceed to Step 3 (Create mode)

### Step 3: Create or Update Document

**Mode A: Create New Document**

Select the appropriate template based on spec category (from Step 0):

- **Agent Spec**: Use `assets/templates/agent-spec-template.md`
- **Backend Spec**: Use `assets/templates/spec-document.md`
- **Frontend Spec**: Use `assets/templates/spec-document.md` (adapted)

**Mode B: Update Existing Document**

- Read the existing document
- Identify sections to modify based on user requirements
- Update relevant sections while preserving existing content
- Update the `updated` date in frontmatter

**Document Content**: Follow the category-specific guidelines for detailed instructions:
- **Agent specs**: `references/agent-content-guidelines.md`
- **Backend specs**: `references/backend-content-guidelines.md`
- **Frontend specs**: `references/frontend-content-guidelines.md`

**Save the Document**:

- For **new documents**: Ask user for filename (suggest kebab-case based on feature name)
- For **updates**: Save to the existing file path
- Create target directory if needed: `mkdir -p "${TARGET_DIR}"`
- Examples:
  - Agent spec → `ob-glens/specs/agent/format-scores-generator.md`
  - Backend spec → `ob-glens/specs/backend/user-authentication-api.md`
  - Frontend spec → `ob-glens/specs/frontend/dashboard-redesign.md`

### Step 4: Refinement Loop

After creating or updating the document:

1. **Present the spec** to the user with a summary
2. **Ask for feedback**: "The spec document has been saved at `[path]`. Would you like to review it, or should I refine any specific sections?"
3. **Iterate based on feedback**:
   - Add missing requirements
   - Clarify ambiguous sections
   - Expand edge case handling

4. **Update the `updated` field** in frontmatter after each revision

### Step 5: Confirmation

Once the user is satisfied:

1. **Ask explicitly**: "Is this specification ready to be confirmed?"
2. **Update status** to `✅ Confirmed` in the frontmatter
3. **Inform completion**: "The specification has been confirmed and saved."


## Document Structure

All specs follow a common structure with category-specific variations. See templates for detailed examples.

### Common Elements (All Specs)

- **YAML Frontmatter**: status, created, updated, related_docs, tags
- **Context**: Why this exists, problems being solved
- **Requirements**: Functional, non-functional, out of scope
- **Acceptance Criteria**: Success metrics, test scenarios

### Category-Specific Focus

**Agent Specs** (`assets/templates/agent-spec-template.md`):
- Agent Architecture: roles, prompts, tools/functions, orchestration
- Edge Cases: API failures, cost optimization
- Tags: `[spec, agent, llm]`

**Backend Specs** (`assets/templates/spec-document.md`):
- Technical Design: data models, API endpoints, business logic
- Migration Strategy: for changes to existing systems
- Tags: `[spec, api, backend]`

**Frontend Specs** (`assets/templates/spec-document.md` adapted):
- UI Design: components, user flows, responsive design
- Accessibility: requirements and considerations
- Tags: `[spec, ui, frontend]`


## Resources

### Templates

- **`assets/templates/agent-spec-template.md`**: Template for LLM agent specifications
- **`assets/templates/spec-document.md`**: Template for Backend/Frontend specifications

### Reference Guides

**Content Guidelines** (category-specific):
- **`references/agent-content-guidelines.md`**: Agent spec writing guide
- **`references/backend-content-guidelines.md`**: Backend spec writing guide
- **`references/frontend-content-guidelines.md`**: Frontend spec writing guide

**General Guides**:
- **`references/obsidian-syntax.md`**: Obsidian markdown features

### Configuration

- **`.env`**: Obsidian vault path and project mappings (copy from `.env.example`)

## Common Scenarios

### Scenario 1: Creating New Agent Spec

**User Request**: "Design the format_scores_generator LLM agent architecture"

**Workflow**:

1. **Step 0**: Determine category → `agent` (keywords: "agent", "LLM")
2. **Step 1**: Search `specs/agent/` by filename → No matching files found
3. **Step 2**: User confirms → Create new document
4. **Step 3**: Create spec using `agent-spec-template.md`:
   - Agent architecture, prompt design, tools/functions
   - Edge cases: API failures, cost optimization
5. **Step 4-5**: Refine with user feedback → Confirm
6. **Result**: `specs/agent/format-scores-generator.md`

### Scenario 2: Updating Existing Backend Spec

**User Request**: "Add OAuth support to the authentication API"

**Workflow**:

1. **Step 0**: Determine category → `backend` (keywords: "authentication", "API")
2. **Step 1**: Search `specs/backend/` by filename → Found `user-authentication-api.md`
3. **Ask user**: "I found `user-authentication-api.md`. Should I update this file?"
4. **User confirms** → Update existing file
5. **Step 3**: Read existing file, add OAuth section to requirements and technical design
6. **Step 4-5**: Refine with user feedback → Confirm
7. **Result**: Updated `specs/backend/user-authentication-api.md`

### Scenario 3: Ambiguous Match - Ask User

**User Request**: "Design a user login flow"

**Workflow**:

1. **Step 0**: Determine category → Could be `backend` or `frontend`
2. **Ask user**: "Is this a backend API or frontend UI feature?"
3. **User chooses**: `frontend`
4. **Step 1**: Search `specs/frontend/` → Found `user-authentication-ui.md`, `login-form.md`
5. **Ask user**: "I found these files: `user-authentication-ui.md`, `login-form.md`. Should I update one of these, or create a new file?"
6. **User chooses**: Update `login-form.md`
7. **Step 3-5**: Read, update, refine, confirm


## Constraints

### What This Skill Does

✅ Create and update specification documents in Obsidian format
✅ Define API schemas, data models, and agent architectures
✅ Design LLM agent prompts and orchestration
✅ Ask clarifying questions to refine requirements
✅ Search and reference existing specs for context
✅ Adapt spec structure based on type (Agent/Backend/Frontend)

### What This Skill Does NOT Do

❌ Modify source code files (`.ts`, `.py`, `.go`, etc.)
❌ Create implementation plans or task breakdowns (use separate tools)
❌ Generate boilerplate code or scaffolding
❌ Run tests or validate implementations

### Spec Type-Specific Constraints

**For Agent Specs**:

- ✅ Focus on agent architecture, prompts, and orchestration
- ❌ Avoid directory structure (implementation detail)
- ❌ Avoid detailed migration strategies (unless critical)
- ❌ Avoid extensive test plans (focus on edge cases)

**For Backend Specs**:

- ✅ Include API endpoints, data models, and business logic
- ✅ Include migration strategy and test plans
- ✅ Include acceptance criteria and success metrics

**For Frontend Specs**:

- ✅ Focus on component structure, user interactions, and state
- ✅ Include visual requirements and accessibility
- ❌ Avoid backend implementation details

**Golden Rule**: This skill focuses solely on specification design. Code implementation is handled by separate tools.

## Success Metrics

A well-crafted specification should:

- Be understandable by both technical and non-technical stakeholders
- Define explicit acceptance criteria
- Anticipate edge cases and error scenarios
- Link to related specifications for context
- Receive explicit user confirmation before being marked as confirmed
