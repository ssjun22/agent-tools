---
name: opsx:audit-spec
description: Audit main specs to verify they accurately reflect actual codebase behavior
license: MIT
compatibility: Requires openspec CLI and codebase access.
metadata:
  author: openspec
  version: "1.0"
  generatedBy: "1.0.0"
---

Audit a main spec (`openspec/specs/<domain>/spec.md`) to verify it accurately reflects the actual codebase behavior.

**Input**: Optionally specify a domain name. If omitted, prompt for selection.

**Steps**

1. **If no domain provided, prompt for selection**

   List directories under `openspec/specs/` using Glob. Present the options and ask the user to select a domain.

   **IMPORTANT**: Do NOT guess or auto-select a domain. Always let the user choose.

2. **Load the main spec**

   Read `openspec/specs/<domain>/spec.md`. Parse its structure:
   - Requirements (sections marked with `### Requirement:` or similar heading patterns)
   - Scenarios (sections marked with `#### Scenario:` or similar)
   - API contracts (endpoints, request/response schemas)
   - Behavioral rules and constraints

3. **Initialize verification report structure**

   Create a report with three dimensions:
   - **Completeness**: Are all code behaviors documented in the spec?
   - **Correctness**: Does the spec accurately describe what the code does?
   - **Coherence**: Is the spec internally consistent and well-structured?

   Each dimension can have CRITICAL, WARNING, or SUGGESTION issues.

4. **Verify Completeness** (Code → Spec direction)

   Check that all significant code behaviors are captured in the spec:
   - Search the codebase for the domain's implementation files (agents, endpoints, schemas, services)
   - For each significant behavior found in code:
     - Check if a corresponding requirement or scenario exists in the spec
     - If code behavior is undocumented:
       - Add WARNING: "Undocumented behavior: <description> in `<file>:<line>`"
       - Recommendation: "Add requirement or scenario covering this behavior"

5. **Verify Correctness** (Spec → Code direction)

   Check that each spec requirement matches actual code behavior:
   - For each requirement in the spec:
     - Search the codebase for implementation evidence
     - If found, compare spec description with actual implementation
     - If requirement appears unimplemented:
       - Add CRITICAL: "Requirement not implemented: <requirement name>"
       - Recommendation: "Implement requirement or remove from spec"
     - If implementation diverges from spec:
       - Add WARNING: "Spec/code mismatch: <details>"
       - Recommendation: "Update spec to match code at `<file>:<line>` or fix code"

   - For each scenario in the spec:
     - Verify the described behavior matches code logic
     - If scenario is inaccurate:
       - Add WARNING: "Scenario does not match code: <scenario name>"
       - Recommendation: "Update scenario to reflect actual behavior"

   - For API contracts (if present):
     - Compare endpoint paths, methods, request/response schemas with actual route definitions and Pydantic models
     - If mismatch found:
       - Add CRITICAL: "API contract mismatch: <details>"
       - Recommendation: "Sync spec with actual endpoint definition at `<file>:<line>`"

6. **Verify Coherence** (Internal consistency)

   - Check for contradictions between requirements
   - Check for duplicate or overlapping scenarios
   - Check that terminology is used consistently
   - If issues found:
     - Add SUGGESTION: "Coherence issue: <details>"
     - Recommendation: specific fix suggestion

7. **Generate Verification Report**

   **Summary Scorecard**:
   ```
   ## Spec Audit Report: <domain>

   ### Summary
   | Dimension    | Status                    |
   |--------------|---------------------------|
   | Completeness | N undocumented behaviors   |
   | Correctness  | X/Y requirements verified  |
   | Coherence    | Clean / N issues           |
   ```

   **Issues by Priority**:

   1. **CRITICAL** (Spec is wrong or missing key behavior):
      - Unimplemented requirements still in spec
      - API contract mismatches
      - Each with specific, actionable recommendation

   2. **WARNING** (Spec is inaccurate or incomplete):
      - Spec/code divergences
      - Undocumented code behaviors
      - Inaccurate scenarios
      - Each with specific recommendation

   3. **SUGGESTION** (Spec quality improvements):
      - Coherence issues
      - Terminology inconsistencies
      - Each with specific recommendation

   **Final Assessment**:
   - If CRITICAL issues: "X critical issue(s) found. Spec needs update."
   - If only warnings: "No critical issues. Y warning(s) to consider. Spec is mostly accurate."
   - If all clear: "All checks passed. Spec accurately reflects codebase."

**Verification Heuristics**

- **Completeness**: Focus on significant behaviors (endpoints, business logic, error handling). Don't flag every utility function.
- **Correctness**: Use keyword search, file path analysis, schema comparison. Prefer concrete evidence over inference.
- **Coherence**: Look for contradictions and duplicates. Don't nitpick wording.
- **False Positives**: When uncertain, prefer SUGGESTION over WARNING, WARNING over CRITICAL.
- **Actionability**: Every issue must have a specific recommendation with file/line references where applicable.
- **Scope**: Only verify the spec for the selected domain. Don't cross-check other domains.

**Output Format**

Use clear markdown with:
- Table for summary scorecard
- Grouped lists for issues (CRITICAL/WARNING/SUGGESTION)
- Code references in format: `file.py:123`
- Specific, actionable recommendations
- No vague suggestions like "consider reviewing"
