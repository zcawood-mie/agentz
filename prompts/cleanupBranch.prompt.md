---
name: cleanupBranch
description: Clean up committed changes on the current branch
argument-hint: Optionally provide the base branch name (defaults to auto-detect)
agent: Implementation
model: 'Claude Sonnet 4.5'
---
Clean up the committed changes on the current branch.

## Steps

1. **Determine the base branch**
   If the user provided a branch name, use it. Otherwise, detect it:
   ```
   git merge-base --fork-point master HEAD || git merge-base --fork-point main HEAD
   ```

2. **Follow the `code-cleanup` skill workflow**
   Review the committed diff against the base branch, checking for diff bloat first, then naming, linting, comments, and documentation issues. Present one issue at a time.
