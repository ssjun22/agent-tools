---
name: opsx:apply
description: Apply implementation tasks for a change using OpenSpec artifacts.
license: MIT
compatibility: Requires openspec CLI.
metadata:
  author: openspec
  version: "1.0"
  customizedBy: openspec-sdd-plugin
---

Apply a change implementation from `tasks.md` and related artifacts.

**Input**: Optional change name. If omitted, ask the user to choose from active changes.

**Steps**

1. **Resolve target change**
   - If no change is provided, run:
     ```bash
     openspec list --json
     ```
   - Present available changes and ask the user to select one.
   - Do not auto-select if multiple candidates exist.

2. **Check apply readiness**
   - Run:
     ```bash
     openspec instructions apply --change "<name>" --json
     ```
   - If artifacts are missing or blocked, stop and ask the user whether to run `/opsx:continue` or `/opsx:ff` first.

3. **Apply the change**
   - Execute:
     ```bash
     openspec apply --change "<name>"
     ```
   - Treat command output as authoritative for applied steps and failures.

4. **Validate post-apply status**
   - Run:
     ```bash
     openspec status --change "<name>"
     ```
   - Summarize done/pending artifacts and recommend `/opsx:verify` next.

**Output**

- Change name
- Apply result summary (success/failure, key messages)
- Current status after apply
- Suggested next step (`/opsx:verify`, or `/opsx:continue` if blocked)

**Guardrails**

- Do not modify specs directly in `openspec/specs/` during apply.
- If major scope mismatch appears, stop and recommend `/opsx:new`.
- If the user asks to skip verification, still explicitly recommend `/opsx:verify`.
