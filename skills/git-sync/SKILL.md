---
name: git-sync
description: 'Syncing with upstream and conflict resolution. Use for: git pull, git rebase, sync upstream, merge conflicts, conflict markers, pull rebase.'
---
# Git Sync

## When to Use
- Incorporating upstream changes into a feature branch
- Resolving merge conflicts
- Verifying branch integrity after a sync

---

## Syncing Strategy

Use `git pull --rebase` or merge — never interactive rebase.

```bash
git pull --rebase origin main
```

## Post-Sync Verification

### 1. Check for leftover conflict markers
```bash
grep -rn "^<<<<<<< " src/ test/ --include="*.ts" --include="*.js"
grep -rn "^=======" src/ test/ --include="*.ts" --include="*.js"
grep -rn "^>>>>>>> " src/ test/ --include="*.ts" --include="*.js"
```

### 2. TypeScript compilation
```bash
pnpm tsc --noEmit
```

### 3. Run tests
```bash
pnpm test
```

### After fixing post-sync issues
```bash
git add -A
git commit -m "fix: resolve merge conflict markers in imports"
git push
```

---

## Rules

**ALWAYS:**
- Verify after syncing (conflict markers, compilation, tests)
- Use `git pull --rebase` or merge to sync

**NEVER (unless the user explicitly asks):**
- Use `git rebase -i` — history rewriting is not your job
- Rebase to reorder or combine commits
