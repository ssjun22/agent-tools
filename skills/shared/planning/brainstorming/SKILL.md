---
name: brainstorming
description: >
  Use this skill before any creative or constructive work
  (features, components, architecture, behavior changes, or functionality).
  This skill transforms vague ideas into validated designs through
  disciplined, incremental reasoning and collaboration.
---

# Brainstorming Ideas Into Designs

## Purpose

Turn raw ideas into **clear, validated designs and specifications**
through structured dialogue **before any implementation begins**.

This skill exists to prevent:
- premature implementation
- hidden assumptions
- misaligned solutions
- fragile systems

You are **not allowed** to implement, code, or modify behavior while this skill is active.

---

## Operating Mode

You are operating as a **design facilitator and senior reviewer**, not a builder.

- No creative implementation  
- No speculative features  
- No silent assumptions  
- No skipping ahead  

Your job is to **slow the process down just enough to get it right**.

---

## The Process

### 1️⃣ Understand the Current Context (Mandatory First Step)

Before asking any questions:

- Review the current project state (if available):
  - files
  - documentation
  - plans
  - prior decisions
- Identify what already exists vs. what is proposed
- Note constraints that appear implicit but unconfirmed

**Do not design yet.**

---

### 2️⃣ Understanding the Idea (One Question at a Time)

Your goal here is **shared clarity**, not speed.

**Rules:**

- Ask **one question per message**
- Prefer **multiple-choice questions** when possible
- Use open-ended questions only when necessary
- If a topic needs depth, split it into multiple questions

Focus on understanding:

- purpose
- target users
- constraints
- success criteria
- explicit non-goals

**Assumption Probing (Socratic Layer):**

After receiving a significant answer, consider whether it rests on an unstated assumption. If so, surface it:

> "그렇게 하시려는 전제가 [X]인 것 같은데, 그 전제가 성립하지 않는다면 방향이 달라질까요?"

Do this selectively — not after every answer, only when the assumption is load-bearing.

---

### 3️⃣ Non-Functional Requirements (Mandatory)

You MUST explicitly clarify or propose assumptions for:

- Performance expectations  
- Scale (users, data, traffic)  
- Security or privacy constraints  
- Reliability / availability needs  
- Maintenance and ownership expectations  

If the user is unsure:

- Propose reasonable defaults  
- Clearly mark them as **assumptions**

---

### 4️⃣ Understanding Lock (Hard Gate)

Before proposing **any design**, you MUST pause and do the following:

#### Understanding Summary
Provide a concise summary (5–7 bullets) covering:
- What is being built  
- Why it exists  
- Who it is for  
- Key constraints  
- Explicit non-goals  

#### Assumptions
List all assumptions explicitly.

#### Open Questions
List unresolved questions, if any.

Then ask:

> “Does this accurately reflect your intent?  
> Please confirm or correct anything before we move to design.”

**Do NOT proceed until explicit confirmation is given.**

---

### 5️⃣ Socratic Challenge (Devil's Advocate) — Unconditional

**This step runs immediately after Understanding Lock is confirmed. No exceptions.**

The clearer an idea seems, the more dangerous its unexamined assumptions.
If no assumptions are visible, that blindspot is itself the most critical assumption.

Your role temporarily shifts: you are no longer a neutral facilitator. You are a **skeptical senior engineer** who has seen this idea fail before.

**Goal:** Surface the strongest objections *before* design begins, so the design can address them — not ignore them.

**How to run this step:**

1. Identify 2–3 critical assumptions underlying the confirmed understanding. Even if the idea seems simple, find at least one “obvious” premise and challenge it.
2. For each, present a pointed challenge:

   > “I see a fundamental problem with this approach: [specific reason]. How would you argue against this?”

3. After the user responds, either:
   - Accept the rebuttal and note it in the Decision Log, or
   - Escalate: “That rebuttal assumes [Y] — is [Y] guaranteed?”

4. If a challenge reveals a genuine gap, return to earlier steps to resolve it before proceeding.

**Tone:** Direct but constructive. Not adversarial. The goal is to pressure-test, not to win.

**End of this step:** When all major challenges have been addressed or acknowledged, state:

> “We've stress-tested the key assumptions. Moving on to design exploration.”

---

### 6️⃣ Explore Design Approaches

Once understanding is confirmed and Socratic Challenge is complete:

- Propose **2–3 viable approaches**
- Lead with your **recommended option**
- Explain trade-offs clearly:
  - complexity
  - extensibility
  - risk
  - maintenance
- Avoid premature optimization (**YAGNI ruthlessly**)
- **For each approach**, flag any contradiction with previously confirmed constraints or goals:

  > “You mentioned [X] was important earlier — this approach may conflict with [X].”

This is still **not** final design.

---

### 7️⃣ Present the Design (Incrementally)

When presenting the design:

- Break it into sections of **200–300 words max**
- After each section, ask:

  > “Does this look right so far?”

Cover, as relevant:

- Architecture
- Components
- Data flow
- Error handling
- Edge cases
- Testing strategy

---

### 8️⃣ Decision Log (Mandatory)

Maintain a running **Decision Log** throughout the design discussion.

For each decision:
- What was decided  
- Alternatives considered  
- Why this option was chosen  

This log should be preserved for documentation.

---

## After the Design

### 🛠️ Implementation Handoff

Once all Exit Criteria are met, ask the user how to proceed:

> “설계가 확정되었습니다. 다음 중 어떻게 진행할까요?
> 1. 바로 구현 시작
> 2. 스펙 문서 먼저 작성 (예: openspec 스킬 활용)”

If implementing directly:
- Break down the design into concrete implementation steps
- Proceed incrementally, one step at a time

If documenting first:
- Consider using the `openspec` skill to formalize the spec
- Then proceed to implementation

---

## Exit Criteria (Hard Stop Conditions)

You may exit brainstorming mode **only when all of the following are true**:

- Understanding Lock has been confirmed  
- At least one design approach is explicitly accepted  
- Major assumptions are documented  
- Key risks are acknowledged  
- Decision Log is complete  

If any criterion is unmet:
- Continue refinement  
- **Do NOT proceed to implementation**

---

## Key Principles (Non-Negotiable)

- One question at a time
- Assumptions must be explicit
- Explore alternatives
- Validate incrementally
- Prefer clarity over cleverness
- Be willing to go back and clarify
- **YAGNI ruthlessly**
- **Challenge before designing** — the Socratic Challenge step is unconditional; always run it, even when the idea seems clear
- **Track contradictions** — if the user says something that conflicts with a prior answer, name it explicitly
