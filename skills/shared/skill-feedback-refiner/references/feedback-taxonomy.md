# Feedback Taxonomy

## Goal
Classify session feedback into consistent buckets so update proposals stay comparable across runs.

## Category Definitions

1. Trigger mismatch
- Skill should have triggered but did not.
- Skill triggered in a situation where it should not.

2. Workflow gap
- Step order is unclear, missing, or too rigid for real usage.
- Decision points are missing (for example, single vs multi-target handling).

3. Output quality gap
- Artifact structure is missing required fields.
- Output depth, language, or format does not match user expectation.

4. Resource gap
- Required script/template/reference is missing or weak.
- Existing resource exists but is hard to discover from `SKILL.md`.

5. Safety or guardrail gap
- Skill performs auto-mutations when proposal-only behavior is expected.
- Failure handling is unsafe or ambiguous.

## Severity Scale

- `S0-blocker`: Cannot complete expected task.
- `S1-high`: Major friction, incorrect outcome likely.
- `S2-medium`: Task completes but quality/efficiency is poor.
- `S3-low`: Minor polish issue.

## Frequency Scale

- `F3-repeated`: Observed multiple times in the same session.
- `F2-occasional`: Observed once with moderate impact.
- `F1-rare`: Edge-case observation.

## Prioritization Heuristic

Use this default priority order:
1. `S0` and `S1` first.
2. Then higher frequency (`F3` before `F2` before `F1`).
3. For ties, prioritize changes that only touch docs/templates before script-level changes.
