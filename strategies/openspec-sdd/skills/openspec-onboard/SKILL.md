---
name: opsx:onboard
description: Onboard users to OpenSpec workflow and recommend the right next command.
license: MIT
compatibility: Requires openspec CLI.
metadata:
  author: openspec
  version: "1.0"
  customizedBy: openspec-sdd-strategy
---

Help users quickly understand and start the OpenSpec SDD workflow.

**Input**: Optional project context and user goal.

**Steps**

1. **Inspect project readiness**
   - Check whether `openspec/` exists and list active changes:
     ```bash
     openspec list --json
     ```
   - If no specs but existing code is present, recommend `/opsx:seed`.

2. **Classify current user intent**
   - New feature or behavior change -> `/opsx:new`
   - Existing code documentation -> `/opsx:seed`
   - Existing main spec elaboration (within current behavior scope) -> `/opsx:elaborate-spec`
   - Existing change progress -> `/opsx:continue` or `/opsx:ff`
   - Implementation step -> `/opsx:apply`
   - Pre-archive validation -> `/opsx:verify`
   - Main spec accuracy check -> `/opsx:audit-spec`

3. **Provide minimal starter path**
   - Present a concrete 3-5 step path tailored to the user.
   - Include one command to start immediately.

4. **Offer a short command cheat sheet**
   - `/opsx:new`, `/opsx:ff`, `/opsx:continue`, `/opsx:apply`, `/opsx:verify`, `/opsx:archive`
   - `/opsx:seed`, `/opsx:elaborate-spec`, `/opsx:audit-spec` for brownfield/spec-maintenance flows.

**Output**

- Current state summary
- Recommended path and first command
- Command cheat sheet

**Guardrails**

- Do not overwhelm with full documentation unless requested.
- Prefer explicit next action over generic explanation.
- Keep guidance aligned with SDD rules in this strategy.
