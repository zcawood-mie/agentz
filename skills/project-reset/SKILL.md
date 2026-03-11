---
name: project-reset
user-invokable: false
description: 'Reset a project to a clean state on the default branch. Use for: reset project, clean start, new feature, initialize project, switch to main, switch to master, fresh start, project setup.'
---
# Project Reset

## When to Use
- Syncing a master repo to the latest default branch
- Preparing a master repo for research or reference
- Verifying the master repo is clean before creating a worktree

**NOTE:** This skill applies to master repos only (`<master-repos>/`). Master repos stay on their default branch at all times. For active development, follow the `worktree-management` skill to create a worktree in `<worktrees>/`.

Resolve `<master-repos>` and `<worktrees>` from the `project-registry` skill's cached memory.

## Project Lookup

Refer to the `project-registry` skill for each project's default branch, submodule scripts, dev stash requirements, and other configuration.

## Reset Workflow

### Phase 1: Identify and Validate

1. **Determine the project** from `$PWD` or user input
2. **Look up the project** in the `project-registry` skill
3. **Identify the default branch** from the registry
4. **Check for uncommitted changes:**
   ```bash
   git status --porcelain
   ```
   - If dirty, warn the user and ask how to proceed (discard, stash, or abort)
   - Do NOT proceed with uncommitted changes without user acknowledgment

### Phase 2: Switch to Default Branch

**For projects WITH submodule scripts** (`switch-branches.sh`):
```bash
./switch-branches.sh <default-branch>
```
This handles switching both the main repo and all submodules to the target branch.

**For projects WITHOUT submodule scripts:**
```bash
git switch <default-branch>
```

- If the switch fails (e.g., due to conflicts), report the error and ask the user how to proceed.

### Phase 3: Fetch and Pull

**Main repository:**
```bash
git fetch origin && git pull
```

**For projects WITH submodule scripts** (`update-packages.sh`):
```bash
./update-packages.sh
```
This fetches and pulls all submodules automatically.

**For projects WITHOUT submodule scripts:**
```bash
git fetch origin && git pull
```
Only the main repo needs updating.

- If pull fails (e.g., merge conflicts), report the error clearly and ask the user.

### Phase 4: Apply Developer Stash (conditional)

**Only for projects where Dev Stash Needed = Yes.**

1. **List available stashes:**
   ```bash
   git stash list
   ```

2. **Evaluate the stash list:**
   - Look for stashes that appear to contain developer configuration (keywords like "login", "config", "setup", "credentials", "dev", the user's name)
   - If a single obvious match exists on the default branch, apply the most recent one
   - If multiple candidates exist or none seem right, show the stash list to the user and ask which one to apply

3. **Apply the stash (NEVER pop):**
   ```bash
   git stash apply stash@{N}
   ```
   - **ALWAYS use `apply`** — the stash must remain in the stash list for future resets
   - **NEVER use `pop`** — this would remove the stash permanently

4. **Verify the apply succeeded:**
   ```bash
   git status --porcelain
   ```
   - If conflicts occurred during apply, report them and ask the user

### Phase 5: Verify

Confirm the reset completed successfully:

```bash
# Verify correct branch
git branch --show-current

# Verify clean state (except expected stash changes)
git status
```

Report a summary:
```
✓ Project: <project-name>
✓ Branch: <default-branch>
✓ Fetched and pulled latest
✓ Submodules updated
✓ Developer stash applied
```

If any step failed, list the failures clearly and ask the user how to proceed.

## Rules

**ALWAYS:**
- Use the `project-registry` skill to determine correct behavior
- Check for uncommitted changes before switching branches
- Use `switch-branches.sh` when available (it handles submodules)
- Use `update-packages.sh` when available (it handles submodule pulls)
- Use `git stash apply` for developer stashes (preserves the stash)
- Report failures clearly and ask the user for guidance
- Verify the final state after all steps complete
- Keep master repos on their default branch at all times

**NEVER:**
- Use `git stash pop` — always `apply` to keep the stash around
- Proceed past uncommitted changes without user acknowledgment
- Assume a stash index — always list and identify the correct one
- Skip submodule updates on projects that have submodule scripts
- Hard-code stash names — stash descriptions change over time
- Create feature branches in master repos — use `worktree-management` skill instead
- Switch master repos away from their default branch
