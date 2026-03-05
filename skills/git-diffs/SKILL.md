---
name: git-diffs
description: 'Git diff analysis and minimization. Use for: git diff, diff review, diff audit, code changes, moved code detection, PR diff, diff minimization.'
---
# Git Diffs

## When to Use
- Reviewing what changed before pushing or opening a PR
- Auditing a diff for unnecessary changes
- Comparing branches

---

## Core Principle
**The cleanest PR is the smallest PR that accomplishes the goal.** Every line in the diff should exist for a reason.

## Essential Commands
```bash
# Full diff against base branch
git diff $(git merge-base <BASE> HEAD) HEAD

# Just file names
git diff $(git merge-base <BASE> HEAD) HEAD --name-only

# Stats (lines added/removed)
git diff $(git merge-base <BASE> HEAD) HEAD --stat

# Detect moved code (vs actual changes)
git diff $(git merge-base <BASE> HEAD) HEAD --color-moved=zebra

# More aggressive move detection
git diff $(git merge-base <BASE> HEAD) HEAD --color-moved=zebra --color-moved-ws=ignore-all-space
```

## Diff Minimization Audit
Unnecessary changes to identify:
- Whitespace-only changes to lines not otherwise modified
- Import/export reordering without clear benefit
- Moving code blocks without modification
- Style changes in lines unrelated to the feature
- Adding/removing blank lines in untouched sections

Questions to ask:
- Does every changed line contribute to the feature/fix?
- Would this change make sense to a reviewer who only knows the ticket?
- If code was moved, is the new location meaningfully better?
- Could any of these changes be a separate PR?

When in doubt, revert. A smaller, focused diff is easier to review, less likely to conflict, and creates cleaner history.

---

## Available Scripts

### analyze-diff.py
Categorizes each changed file as substantive, whitespace-only, import-reorder, or trivial. Flags diff bloat.

```bash
# Analyze current branch diff (auto-detects upstream)
python3 scripts/analyze-diff.py

# Analyze against specific base
python3 scripts/analyze-diff.py --base origin/master

# Human-readable output
python3 scripts/analyze-diff.py --format text

# Custom threshold for flagging whitespace changes
python3 scripts/analyze-diff.py --threshold 3
```

**Exit codes:** 0 = no bloat, 1 = bloat detected (files flagged), 2 = error

**JSON output fields:** `bloat_detected`, `summary.substantive_files`, `summary.whitespace_only_files`, `flagged[]`
