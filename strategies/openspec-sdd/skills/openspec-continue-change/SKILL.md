---
name: opsx:continue
description: Continue a change by generating or updating the next ready artifact.
license: MIT
compatibility: Requires openspec CLI.
metadata:
  author: openspec
  version: "1.0"
  customizedBy: openspec-sdd-strategy
---

Continue work on an existing change, one artifact at a time.

**Input**: Optional change name and optional target artifact. If omitted, infer from status.

**Steps**

1. **Resolve target change**
   - If no change provided, run:
     ```bash
     openspec list --json
     ```
   - Ask user to choose a change.

2. **Inspect artifact status**
   - Run:
     ```bash
     openspec status --change "<name>"
     ```
   - Identify the first `ready` artifact unless user specified one.

3. **Load instructions**
   - Run:
     ```bash
     openspec instructions "<artifact-id>" --change "<name>"
     ```
   - Use template/context to draft or update the artifact.

4. **Apply artifact update**
   - Update only the selected artifact.
   - Re-run status after update:
     ```bash
     openspec status --change "<name>"
     ```

5. **Stop for user direction**
   - Summarize what changed and what is ready next.
   - Ask whether to continue with next artifact or stop.

**Output**

- Change name
- Artifact processed
- Current completion status
- Next recommended artifact/action

**Guardrails**

- Do not skip artifact dependencies.
- Do not modify unrelated artifacts in one continue step.
- If no artifact is ready, stop and explain blockers.
