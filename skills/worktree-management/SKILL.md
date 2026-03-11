---
name: worktree-management
description: 'Git worktree lifecycle and workspace layout rules. Use for: worktree, branch, new feature, workspace structure, active development, create worktree.'
user-invokable: false
---
# Worktree Management

Git worktrees let you have multiple branches checked out simultaneously in separate directories. This skill covers worktree creation, setup, and lifecycle — the mechanics are universal, but workspace paths and project config come from memory.

## When to Use
- Starting active development on a new branch
- Creating a feature branch for a ticket
- Cleaning up after a branch is merged

## Workspace Context

Read the project-index memory for workspace layout, and the project's setup file for install/build config:
```bash
~/.agents/skills/memory-access/scripts/read-memory.sh project-index
~/.agents/skills/memory-access/scripts/read-memory.sh projects/<project>/setup
```

The index defines where repos live and (optionally) a dedicated worktree directory. If the user doesn't use a separate worktree directory, worktrees are created as siblings of the source repo or wherever the user specifies.

## Creating a Worktree

### Step 1: Ensure the source repo is up to date

```bash
cd <repo-path>
git fetch origin
git pull
```

### Step 2: Create the worktree

```bash
BRANCH="feature/issue-42-add-endpoint"
DIR_NAME="<repo>--$(echo "$BRANCH" | tr '/' '-')"

# If using a dedicated worktree directory:
git worktree add <worktree-dir>/"$DIR_NAME" -b "$BRANCH" origin/<default-branch>

# Otherwise, create alongside the repo:
git worktree add ../"$DIR_NAME" -b "$BRANCH" origin/<default-branch>
```

Branch naming convention: `<repo-name>--<branch-name>` (slashes become hyphens).

### Step 3: Initialize submodules (if applicable)

**`git worktree add` does NOT initialize submodules.** For projects with submodules, you must do this explicitly.

**Important:** Initialize submodules **one at a time**, not with `git submodule update --init --recursive`. Parallel clones can overwhelm SSH connections and cause timeouts. The source repo's `.git/modules/` already has cached clones, so individual updates are instant.

```bash
cd <worktree-path>
git submodule init
git submodule foreach --quiet 'echo $sm_path' | while read sm; do
  git submodule update --init "$sm"
done
```

**Verify submodules are populated:**
```bash
git submodule foreach 'echo $sm_path: $(ls | head -1)'
```

> **Gotcha:** Submodules may live outside `packages/` (e.g. `cypress` at the repo root). Always check `.gitmodules` for the complete list.

### Step 4: Generate build artifacts and copy dev config (if needed)

Refer to the project's setup file (`/memories/projects/<project>/setup.md`) for per-project setup details — build artifacts, config file copies, etc.

### Step 5: Install dependencies

Run the project's install command from the setup file:
- Meteor projects: `meteor npm install`
- pnpm projects: `pnpm install`
- Node projects: `npm install`

## Listing Worktrees

```bash
cd <repo-path>
git worktree list
```

## Removing a Worktree (After Branch Is Merged)

```bash
cd <repo-path>
git worktree remove <worktree-path>
# Optionally delete the branch if fully merged:
git branch -d <branch-name>
```

## Syncing a Worktree with Upstream

```bash
cd <worktree-path>
git pull --rebase origin <default-branch>
```

Follow the `git-sync` skill for conflict resolution and post-sync verification.

## Rules

**ALWAYS:**
- Clean up worktrees after branches are merged

**NEVER:**
- Delete worktrees for branches that haven't been merged yet
- Run `git submodule update --init --recursive` (parallel clones timeout) — init submodules one at a time

## Troubleshooting

### Module not found errors for submodule paths
Submodules were not initialized. Run:
```bash
git submodule init
git submodule foreach --quiet 'echo $sm_path' | while read sm; do
  git submodule update --init "$sm"
done
```

### SSH timeout during submodule clone
Too many parallel SSH connections. Init submodules one at a time (see above). The source repo's `.git/modules/` cache means most updates are instant local checkouts.

### Submodule directories exist but are empty
`git worktree add` creates the directories from the tree but doesn't populate submodule content. You must explicitly initialize them.

---

## Available Scripts

### create-worktree.sh
Automates worktree creation: fetch, branch, submodules, build artifacts, config copy, and dependency install. All project-specific configuration is passed as arguments — read the project-index memory for workspace paths and the project's setup memory for config flags.

```bash
# Read workspace paths and project config from memory first
~/.agents/skills/memory-access/scripts/read-memory.sh project-index
~/.agents/skills/memory-access/scripts/read-memory.sh projects/<repo>/setup

# Basic usage — worktrees go alongside the repo by default
bash scripts/create-worktree.sh my-api feature/new-endpoint \
  --repo-dir /path/to/my-api \
  --base main --install-cmd "pnpm install" --env-copy

# With dedicated worktree directory
bash scripts/create-worktree.sh my-app feature/big-change \
  --repo-dir /path/to/my-app --worktree-dir /path/to/worktrees \
  --base master --install-cmd "meteor npm install" \
  --submodules --build-info --build-packages

# Preview what would happen
bash scripts/create-worktree.sh my-api fix/typo \
  --repo-dir /path/to/my-api --base main --dry-run
```

**Required options:** `--repo-dir`
**Optional:** `--worktree-dir` (defaults to parent of repo-dir)
**Project config flags:** `--base`, `--install-cmd`, `--submodules`, `--build-info`, `--build-packages`, `--env-copy`
**Execution flags:** `--no-install`, `--dry-run`

**Exit codes:** 0 = success, 1 = creation error, 2 = invalid arguments

**Output:** JSON to stdout with `status`, `repo`, `branch`, `worktree_path`, `base`. Human-readable progress to stderr.
