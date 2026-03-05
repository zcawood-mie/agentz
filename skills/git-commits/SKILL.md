---
name: git-commits
description: 'Git commit conventions and history rules. Use for: git commit, commit message, conventional commits, commit format, amend, squash, fixup, history rewriting.'
---
# Git Commits

## When to Use
- Committing code changes
- Writing commit messages
- Deciding whether to amend, squash, or create a new commit

---

## Conventional Commit Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation only
- **refactor**: Code refactoring (no functional change)
- **chore**: Maintenance, dependencies, tooling

## Format Rules
- Imperative mood ("Add feature" not "Added feature")
- Subject line max 50 characters
- No period at end of subject
- Blank line between subject and body (if body needed)
- Body wrap at 72 characters
- Only describe what changed — never reference PR feedback, reviews, or external context

## Atomic Commits
- One logical change per commit
- Each commit should pass tests independently
- Keep commits focused and reviewable
- **Prefer many small commits over few large ones** — small commits are easier to review, bisect, and revert
- Each fix, refactor, or cleanup step should be its own commit
- Even small fixes (typos, missing imports, lint) get their own commit

## Just Commit — No History Rewriting
- **Every change is a new `git commit`** — full stop
- Do NOT amend (`--amend`) unless the user explicitly asks
- Do NOT fixup (`--fixup`, `--squash`) unless the user explicitly asks
- Do NOT interactive rebase (`rebase -i`) unless the user explicitly asks
- Do NOT squash commits unless the user explicitly asks
- Do NOT rebase to reorder or combine commits unless the user explicitly asks
- The only acceptable use of rebase on your own is `git pull --rebase` to sync with upstream
- A clean trail of small commits is always preferred over a "polished" history
- **If the user asks** for amend, squash, rebase, or fixup — do it. Otherwise, never.

---

## Rules

**ALWAYS:**
- Use conventional commit format
- One logical change per commit
- Imperative mood in subject line

**NEVER (no exceptions):**
- Stage agent/skill files (`~/.agents/`)
- Stage or commit submodule reference (hash) changes — a bot manages these automatically
- Batch multiple unrelated fixes into a single commit
