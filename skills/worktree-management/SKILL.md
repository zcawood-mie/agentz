---
name: worktree-management
description: 'Git worktree lifecycle and workspace layout rules. Use for: worktree, branch, new feature, workspace structure, master repo, active development, create worktree.'
user-invokable: false
---
# Worktree Management

## When to Use
- Starting active development on any branch
- Creating a feature branch for a ticket
- Determining where to make code changes
- Cleaning up after a branch is merged

## Workspace Layout

Refer to the `project-registry` skill for the full project table (default branches, submodules, install commands, build artifacts, dev config, and per-project setup details).

```
~/bhDev/
  masterRepos/          # Reference copies on default branch
    bluehive/
    bluehive-ai/
    bluehive-api/
    bluehive-employer/
    bluehive-opsdesk/
    bluehive-provider/
    bluehive-ui/
    waggleline/
  worktrees/            # Active development — one worktree per branch
    <repo>--<branch>/   # e.g. bluehive-api--feature-issue-42-add-endpoint
```

### Master Repos (`masterRepos/`)
- Always stay on the default branch (`master` or `main`)
- **Never** create feature branches here
- **Never** make code changes here
- Used for: fetching, pulling latest, creating worktrees, research/reference
- May be used for running/testing the app on the default branch

### Worktrees (`worktrees/`)
- One directory per active branch
- Naming convention: `<repo-name>--<branch-name>`
  - Branch slashes become hyphens in the directory name: `feature/issue-42-add-endpoint` → `bluehive-api--feature-issue-42-add-endpoint`
- All active development happens here
- Delete the worktree directory when the branch is merged

## Creating a Worktree

### Step 1: Ensure master repo is up to date

```bash
cd ~/bhDev/masterRepos/<repo>
git fetch origin
git pull
```

### Step 2: Create the worktree

```bash
# Sanitize branch name for directory: replace / with -
BRANCH="feature/issue-42-add-endpoint"
DIR_NAME="<repo>--$(echo "$BRANCH" | tr '/' '-')"

git worktree add ~/bhDev/worktrees/"$DIR_NAME" -b "$BRANCH" origin/<default-branch>
```

This creates a new branch tracking the default branch and checks it out in the worktree directory.

### Step 3: Initialize submodules (if applicable)

**`git worktree add` does NOT initialize submodules.** For projects with submodules, you must do this explicitly.

**Important:** Initialize submodules **one at a time**, not with a blanket `git submodule update --init --recursive`. The parallel clones can overwhelm SSH connections and cause timeouts. The master repo's `.git/modules/` already has cached clones, so individual updates are instant (no network needed).

```bash
cd ~/bhDev/worktrees/"$DIR_NAME"

# List all submodules from .gitmodules
git submodule init

# Update each submodule individually (avoids SSH connection limits)
git submodule foreach --quiet 'echo $sm_path' | while read sm; do
  git submodule update --init "$sm"
done
```

**Verify all submodules are populated:**
```bash
git submodule foreach 'echo $sm_path: $(ls | head -1)'
```

If any submodule directory is empty, run `git submodule update --init <path>` for that specific submodule.

> **Gotcha:** Submodules may live outside `packages/` (e.g. `cypress` at the repo root). Always check `.gitmodules` for the complete list — don't assume all submodules are under `packages/`.

### Step 4: Generate build artifacts and copy dev config (if needed)

Refer to the `project-registry` skill for per-project setup details. Projects that need build artifacts or dev config copies are listed there with exact commands.

### Step 5: Switch to the worktree

```bash
cd ~/bhDev/worktrees/"$DIR_NAME"
```

**All subsequent work happens in this directory.**

### Step 6: Install dependencies

Run the project's install command from the `project-registry` skill:
- Meteor projects: `meteor npm install`
- pnpm projects: `pnpm install`
- Node projects: `npm install`

## Listing Worktrees

```bash
cd ~/bhDev/masterRepos/<repo>
git worktree list
```

Or simply:
```bash
ls ~/bhDev/worktrees/ | grep "^<repo>--"
```

## Removing a Worktree (After Branch Is Merged)

```bash
cd ~/bhDev/masterRepos/<repo>
git worktree remove ~/bhDev/worktrees/<repo>--<branch-dir>
# Optionally delete the branch if fully merged:
git branch -d <branch-name>
```

## Syncing a Worktree with Upstream

```bash
cd ~/bhDev/worktrees/<repo>--<branch-dir>
git pull --rebase origin <default-branch>
```

Follow the `git-sync` skill for conflict resolution and post-sync verification.

## Determining Where You Are

When starting any task, check whether you're in:
1. **A worktree** (`~/bhDev/worktrees/...`) → Good, proceed with development
2. **A master repo** (`~/bhDev/masterRepos/...`) → **Stop.** Create or switch to a worktree first.

To check programmatically:
```bash
[[ "$PWD" == */worktrees/* ]] && echo "worktree" || echo "master repo"
```

## Rules

**ALWAYS:**
- Clean up worktrees after branches are merged

**NEVER:**
- Delete worktrees for branches that haven't been merged yet
- Run `git submodule update --init --recursive` (parallel clones timeout) — init submodules one at a time

## Troubleshooting

### App crashes with "Unknown asset: build_info/head"
The `private/build_info/` directory and files are gitignored and generated by `bin/start.js`. Create them manually:
```bash
mkdir -p private/build_info
git rev-parse --short HEAD > private/build_info/head
date +%s000 > private/build_info/time
```

### Module not found errors for submodule paths
Submodules were not initialized. Run:
```bash
git submodule init
git submodule foreach --quiet 'echo $sm_path' | while read sm; do
  git submodule update --init "$sm"
done
```

### SSH timeout during submodule clone
Too many parallel SSH connections to GitHub. Init submodules one at a time (see above). The master repo's `.git/modules/` cache means most updates are instant local checkouts, not network clones.

### Submodule directories exist but are empty
Same as above — `git worktree add` creates the directories from the tree but doesn't populate submodule content. You must explicitly initialize them.

---

## Available Scripts

### create-worktree.sh
Automates the full 6-step worktree creation process: fetch, branch, submodules, build_info, config copy, and dependency install. Embeds the project registry.

```bash
# Create a worktree for bluehive-employer
bash scripts/create-worktree.sh bluehive-employer feature/issue-42-fix

# Branch from a specific base
bash scripts/create-worktree.sh bluehive-api feature/new-endpoint --base main

# Skip dependency installation
bash scripts/create-worktree.sh bluehive feature/big-change --no-install

# Preview what would happen
bash scripts/create-worktree.sh bluehive-employer fix/typo --dry-run
```

**Exit codes:** 0 = success, 1 = creation error, 2 = invalid arguments

**Output:** JSON to stdout with `status`, `repo`, `branch`, `worktree_path`, `base`. Human-readable progress to stderr.
