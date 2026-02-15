---
name: opsx:sync
description: Sync delta specs from an active change into main specs without archiving.
license: MIT
compatibility: Requires openspec CLI.
metadata:
  author: openspec
  version: "1.0"
  customizedBy: openspec-sdd-strategy
---

Synchronize delta spec updates into main specs for long-running changes.

**Input**: Optional change name. If omitted, ask user to choose.

**Steps**

1. **Resolve target change**
   - Run:
     ```bash
     openspec list --json
     ```
   - Ask user which change to sync.

2. **Pre-check sync readiness**
   - Run:
     ```bash
     openspec status --change "<name>"
     ```
   - Ensure delta specs exist for the change.
   - If no delta specs are present, stop and explain there is nothing to sync.

3. **Execute sync**
   - Run:
     ```bash
     openspec sync --change "<name>"
     ```
   - Capture affected domains/requirements from command output.

4. **Verify post-sync state**
   - Re-run status and summarize what remains in the change.
   - Recommend `/opsx:archive` only when work is complete.

**Output**

- Change name
- Sync result summary
- Affected main spec areas
- Next recommended command

**Guardrails**

- Sync is not archive; do not mark change complete automatically.
- Do not directly edit merged main specs after sync unless explicitly requested.
- If sync produces conflicts or errors, stop and report concrete remediation.
