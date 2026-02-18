# Target Skill Detection Rules

## Goal
Select one primary target skill per run using deterministic evidence scoring.

## Evidence Sources

1. Explicit skill block in conversation:
- Example: `<skill><name>weekly-scrum-summarizer</name>...`

2. Skill markdown link in conversation:
- Example: `[$skill-name](/path/to/SKILL.md)`

3. Explicit skill name mentions:
- Exact mention of known skill names.

4. Skill path mentions:
- Path that ends with `/SKILL.md` and maps to known skill.

## Scoring

- Explicit skill block: +70
- Skill markdown link: +55
- Explicit path mapped to skill: +40
- Exact skill-name mention in plain text: +20 per distinct mention (max +40)
- Recent mention in latest user message: +10

## Selection

1. Calculate score per candidate skill.
2. Select highest score as primary target.
3. Keep non-selected candidates as secondary context.

## Tie-Break Rules

1. Prefer skill mentioned most recently.
2. If still tied, prefer skill with more direct user feedback lines.
3. If still tied, require `target_skill_name` override from user.

## Confidence

- High: score >= 70
- Medium: 45 <= score < 70
- Low: score < 45

When confidence is low, ask for explicit target skill confirmation before creating artifacts.
