---
name: testCurrentBranch
description: Manually test the changes on the current branch
argument-hint: Optionally describe specific areas to focus testing on
agent: Implementation
model: 'Claude Sonnet 4.6'
---
Manually test the changes on the current branch.

## Steps

1. **Identify what changed**
   Run `git diff main...HEAD --stat` (or the appropriate base branch) to understand the scope of changes.

2. **Follow the `testing-workflow` skill**
   Create a test plan, run the app, execute test scenarios, and produce a final report with pass/fail results.
