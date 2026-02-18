# Artifact Specification

## Base Path

Store every artifact under:
`[project]/.codex/skills/skill-feedback-refiner/feedbacks/[target-skill-name]/`

`[project]` resolution:
1. `git rev-parse --show-toplevel`
2. Fallback to current working directory

## Filename Rule

Format:
`YYYY-MM-DD_HHMM_내용.md`

Rules:
- Build `내용` from automatic kebab-case slug.
- Allow manual override when user provides explicit label.
- If collision occurs, append `-v2`, `-v3`, and so on.

## Required Artifacts

1. Session Feedback (`..._session-feedback.md`)
- Purpose: preserve evidence and classification.
- Required sections:
  - Session metadata
  - Target skill detection evidence
  - Raw feedback excerpts
  - Classified feedback table
  - Priority queue

2. Update Proposal (`..._update-proposal.md`)
- Purpose: define what to change and why.
- Required sections:
  - Problem summary
  - Root-cause hypotheses
  - Proposed changes by file/section
  - Expected impact and risks
  - Rollout sequence

3. Patch Draft (`..._patch-draft.md`)
- Purpose: provide reviewable, non-applied patch text.
- Required sections:
  - Scope
  - Unified diff blocks
  - Notes for manual application

4. Validation Checklist (`..._validation-checklist.md`)
- Purpose: support user-driven verification in next real run.
- Required sections:
  - Test scenarios
  - Prompt examples
  - Expected outputs
  - Pass/fail criteria
