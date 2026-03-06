---
name: reviewMyBranch
description: Self-review your current branch changes
argument-hint: Optionally provide additional review focus or context
agent: Research
model: 'Claude Sonnet 4.6'
---
Self-review the changes on the current branch using the self-review priority list.

## Steps

1. **Determine diff source**
   Check if a PR exists for the current branch (delegate GitHub lookups per the agent's delegation rules).
   - If a PR exists: fetch PR metadata, review comments, AND local diff (check for drift)
   - If no PR: use local diff only (`git diff main...HEAD` or appropriate base)

2. **Set review mode to Self-Review**
   Follow the `pr-review` skill with **self-review mode** explicitly. Use the full self-review priority list (P1-P10).

3. **Present findings one at a time, highest priority first.**
