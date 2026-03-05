---
name: implementTicketAuto
description: Autonomously implement a ticket from URL to PR
argument-hint: GitHub issue or ticket URL
agent: Implementation
---
Implement the ticket at the provided URL autonomously, from research through to PR creation.

## Steps

1. **Ingest the ticket**
   Delegate to GitHubOps to fetch the issue content from the provided URL.
   Extract title, description, acceptance criteria, and target repository.

2. **Research the codebase**
   Follow the `autonomous-workflow` skill — complete Phase 2.
   Find existing patterns, registration points, and dependencies.

3. **Plan the implementation**
   Follow the `autonomous-workflow` skill — complete Phase 3.
   Break into implementable steps with a diagram.

4. **Create branch and implement**
   Follow the `autonomous-workflow` skill — complete Phases 4-6.
   Commit incrementally with conventional commit messages after each logical change.

5. **Self-review loop**
   Follow the `autonomous-workflow` skill — complete Phase 7.
   Review the full diff, fix any issues found, then re-review the updated diff.
   Repeat until no more substantive findings remain.

6. **Push and open draft PR**
   Follow the `autonomous-workflow` skill — complete Phase 8.
   Push the branch and delegate to GitHubOps to create a **draft** PR.

7. **Request Copilot review and address feedback**
   Follow the `autonomous-workflow` skill — complete Phase 9.
   Request Copilot's review on the draft PR, then fix issues or document why they don't apply.
