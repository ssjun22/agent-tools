---
name: skill-feedback-refiner
description: This skill should be used when the user expresses dissatisfaction, suggests improvements, or gives feedback—explicit or implicit—about a skill used in the current session. If the feedback is vague or still forming, engage in conversation to draw out and clarify improvement points first. Once feedback is clear, produce structured improvement artifacts (feedback summary, update proposal, patch draft, validation checklist) to help the skill gradually adapt to the user's preferences.
---

# Skill Feedback Refiner

## Overview

Convert current-session feedback into structured improvement artifacts for a target skill.
Produce review-ready drafts (feedback summary, update proposal, patch draft, validation checklist) without modifying target skill files directly.

## When To Use

- A skill was used in the current session and the user provides improvement feedback.
- The user asks to summarize feedback or prepare update drafts for `SKILL.md` or bundled resources.
- The user requests a post-session skill retrospective with saved artifacts.

Trigger examples:
- "방금 쓴 스킬 피드백 정리해서 업데이트안 만들어줘"
- "이 세션 대화 기준으로 스킬 개선 초안 만들어줘"
- "스킬 회고해서 패치 초안과 체크리스트까지 만들어줘"

## Inputs

Collect these inputs in order:
1. Current session conversation (default evidence source).
2. Optional user-provided raw feedback text when session evidence is insufficient.
3. Optional `target_skill_name` override argument.

## Workflow

### 1) Collect Session Evidence

Extract:
- Skill usage evidence (`<skill>` blocks, skill links, explicit skill-name mentions).
- User feedback statements (pain points, corrections, missing behaviors, desired behavior).
- Context constraints (project path, output preferences, safety constraints).

If fewer than 3 actionable feedback items are found, request extra feedback snippets before proceeding.

### 2) Detect Target Skill

Apply scoring rules in `references/target-skill-detection-rules.md`.
Select exactly one target skill (highest score).
If detection confidence is low or a tie persists, ask for explicit `target_skill_name` confirmation.

### 3) Normalize and Classify Feedback

Apply taxonomy in `references/feedback-taxonomy.md`.
Map each feedback item into:
- Category
- Severity
- Frequency
- Evidence snippet
- Suggested change surface (`SKILL.md`, `references/*`, `scripts/*`, `assets/*`)

### 4) Build Change Mapping

Create explicit mapping per feedback item:
- `Issue → Root cause hypothesis → Proposed change → Expected impact → Risk`

Keep proposals decision-complete and implementation-ready.

### 5) Resolve Output Paths

Run `scripts/path_builder.py` for deterministic path generation.
Follow artifact storage rules in `references/artifact-spec.md`.

```bash
python scripts/path_builder.py --skill-name <target-skill-name> --label <artifact-label>
```

### 6) Produce Output Artifacts

Generate 4 markdown files using templates in `assets/` and requirements in `references/artifact-spec.md`:
1. `session-feedback` — evidence and classification
2. `update-proposal` — what to change and why
3. `patch-draft` — reviewable diff text
4. `validation-checklist` — test scenarios for next real run

### 7) Return Result

Report:
- Target skill name and detection confidence
- Saved file paths
- High-priority changes (S0/S1) summary

After reporting, prompt the user to apply the patch draft to the target skill and run `/skill-creator` to review the updated skill structure.

## Guardrails

- Never edit target skill files directly in this workflow.
- Prefer session evidence first; request extra input only when fewer than 3 actionable items are found.
- Select one primary target skill per run; record other candidates as secondary context.
