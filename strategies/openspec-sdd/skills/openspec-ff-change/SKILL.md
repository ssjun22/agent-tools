---
name: opsx:ff
description: Fast-forward artifact generation for a change from proposal to tasks.
license: MIT
compatibility: Requires openspec CLI.
metadata:
  author: openspec
  version: "1.0"
  customizedBy: openspec-sdd-strategy
---

Fast-forward a change by generating all required artifacts in sequence.

**Input**: Optional change name. If missing, ask user for the target change or desired scope.

**Steps**

1. **Resolve target change**
   - If not provided, list and ask:
     ```bash
     openspec list --json
     ```
   - If no suitable change exists, recommend starting with `/opsx:new`.

2. **Read workflow status**
   - Run:
     ```bash
     openspec status --change "<name>"
     ```
   - Determine pending/ready artifact order.

3. **Generate artifacts in order**
   - For each ready artifact:
     - Load instructions:
       ```bash
       openspec instructions "<artifact-id>" --change "<name>"
       ```
     - Draft/update artifact according to template and context.
     - Re-check status before moving next.

4. **Completion check**
   - Run final status:
     ```bash
     openspec status --change "<name>"
     ```
   - If all artifacts are complete, recommend `/opsx:apply`.

**Output**

- Change name
- Artifacts generated/updated
- Remaining blockers, if any
- Next step recommendation (`/opsx:apply` or `/opsx:continue`)

**Guardrails**

- Respect artifact dependency order.
- Do not fabricate missing context; ask user when ambiguity blocks quality.
- If generation quality is uncertain, stop and ask for clarification before advancing.
