---
name: opsx:archive
description: Archive a completed change and merge delta specs into main specs.
license: MIT
compatibility: Requires openspec CLI.
metadata:
  author: openspec
  version: "1.0"
  customizedBy: openspec-sdd-strategy
---

Archive a completed OpenSpec change.

**Input**: Optional change name. If omitted, ask the user to choose.

**Steps**

1. **Resolve target change**
   - If missing, run:
     ```bash
     openspec list --json
     ```
   - Ask the user which change to archive.

2. **Pre-check status**
   - Run:
     ```bash
     openspec status --change "<name>"
     ```
   - If tasks/artifacts are incomplete, stop and ask whether to continue anyway.
   - Recommend `/opsx:verify` before archive when verification is not done.

3. **Optional sync before archive**
   - Ask whether to run a pre-archive sync.
   - If yes, run:
     ```bash
     openspec sync --change "<name>"
     ```

4. **Archive**
   - Run:
     ```bash
     openspec archive --change "<name>"
     ```
   - This should archive the change and merge delta spec updates into main specs.

5. **Confirm results**
   - Run:
     ```bash
     openspec status --change "<name>"
     ```
   - If archived correctly, report archive path and merged domains.

**Output**

- Archived change name
- Archive result summary
- Main spec merge summary (ADDED/MODIFIED/REMOVED where available)
- Follow-up recommendation (open a new change if more work remains)

**Guardrails**

- Do not archive silently when status is clearly incomplete.
- Do not directly edit archived outputs after command execution.
- If archive fails, stop and provide actionable remediation steps.
