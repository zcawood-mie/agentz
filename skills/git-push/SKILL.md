---
name: git-push
description: 'Git push workflow and pre-push checks. Use for: git push, push to remote, pre-push scan, sensitive content, secrets scan, push safety.'
---
# Git Push

## When to Use
- Pushing commits to a remote
- Running pre-push safety checks

---

## Pre-Push Workflow

### Step 1: Identify unpushed commits
```bash
git log --oneline @{u}..HEAD
# If no upstream:
git log --oneline origin/main..HEAD
```

### Step 2: Review the diff
```bash
git diff @{u}..HEAD --stat
git diff @{u}..HEAD
```

### Step 3: Scan for sensitive content
```bash
git diff @{u}..HEAD | grep -inE \
  '(api[_-]?key|secret|token|password|credential|private[_-]?key|connection[_-]?string)' \
  '|(console\.(log|debug|warn|error)\()' \
  '|(debugger;)' \
  '|(localhost|127\.0\.0\.1)' \
  '|(/Users/[a-zA-Z])' \
  '|(\.env\b)' || echo "No suspicious patterns found."
```

Categories:
- **Blocking** (never push): secrets, API keys, tokens, passwords, private keys, connection strings with credentials
- **Warning** (ask user): `console.log`, `debugger`, `localhost`, absolute paths, `.env` references

### Step 4: Push
```bash
git push
# If no upstream:
git push -u origin HEAD
```

---

## Rules

**ALWAYS:**
- Run the sensitive-content scan before every push
- Review unpushed commits before pushing

**NEVER (unless the user explicitly asks):**
- Use `git push --force` or `--force-with-lease`

**NEVER (no exceptions):**
- Push secrets/credentials (blocking — stop immediately)
- Skip the pre-push scan

---

## Available Scripts

### pre-push-scan.py
Scans unpushed commits for secrets, debug artifacts, and risky patterns. Returns structured JSON.

```bash
# Basic scan (auto-detects upstream)
python3 scripts/pre-push-scan.py

# Scan against specific base
python3 scripts/pre-push-scan.py --base origin/main

# Human-readable output
python3 scripts/pre-push-scan.py --format text
```

**Exit codes:** 0 = clean (warnings may exist), 1 = blocking issues found, 2 = error

**JSON output fields:** `has_blocking`, `blocking[]`, `warnings[]`, `summary.blocking_count`, `summary.warning_count`
