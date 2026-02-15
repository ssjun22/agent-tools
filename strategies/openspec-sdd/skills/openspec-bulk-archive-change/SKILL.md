---
name: opsx:bulk-archive
description: Archive multiple completed changes in one workflow.
license: MIT
compatibility: Requires openspec CLI.
metadata:
  author: openspec
  version: "1.0"
  customizedBy: openspec-sdd-strategy
---

Archive multiple changes safely.

**Input**: Optional list of change names. If omitted, ask the user to select from active changes.

**Steps**

1. **Collect target changes**
   - Run:
     ```bash
     openspec list --json
     ```
   - Show active changes and ask user which ones to archive.
   - If none selected, stop.

2. **Pre-check each change**
   - For each selected change, run:
     ```bash
     openspec status --change "<name>"
     ```
   - Classify as `ready`, `warning`, or `blocked`.

3. **Ask for final confirmation**
   - Present summary table with readiness per change.
   - Ask user to confirm bulk archive.

4. **Archive sequentially**
   - For each confirmed change:
     - Optional sync (if user requested):
       ```bash
       openspec sync --change "<name>"
       ```
     - Archive:
       ```bash
       openspec archive --change "<name>"
       ```
   - Continue on per-change failure and collect failures.

5. **Report**
   - Provide success/failure list and suggested follow-ups.

**Output**

- Archived changes
- Failed changes (with reason)
- Merge summary by change where available

**Guardrails**

- Never archive changes the user did not explicitly select.
- Keep failures isolated to each change; avoid aborting the whole run unless requested.
- Recommend `/opsx:verify` for borderline changes before retrying archive.
