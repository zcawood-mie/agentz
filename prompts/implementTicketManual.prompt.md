---
name: implementTicketManual
description: Research, plan, implement, and self-review a ticket end-to-end (pauses for plan approval)
argument-hint: Provide a ticket URL, number, or description of what to implement
agent: Implementation
---
Implement the given ticket from research through to a polished PR.

## Steps

1. **Research the ticket**
   Understand the requirements — read the ticket, explore relevant code, identify affected files and cross-repo dependencies. Check workspace folders first for cross-repo context.

2. **Draft a plan**
   Follow the `planning` skill to create a diagram-first implementation plan. Present the plan for approval before proceeding.

3. **Implement**
   Follow the `implementation-workflow` skill. Commit incrementally using the `git-commits` skill.

4. **Self-review loop**
   After implementation is functionally complete:
   a. Review your own diff using the `pr-review` skill (self-review mode)
   b. Fix any findings directly
   c. Re-review the updated diff
   d. Repeat until no more substantive findings

5. **Push and create draft PR**
   Follow the `pr-workflow` skill to push the branch and open a **draft** PR with proper issue linking.

6. **Request Copilot review and address feedback**
   Follow the `autonomous-workflow` skill — complete Phase 9.
   Request Copilot's review on the draft PR, then fix pointed-out issues or document why they don't apply.

7. **Report**
   Summarize what was implemented, key decisions made, and any remaining concerns.
