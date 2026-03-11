---
name: project-registry
user-invokable: false
description: 'Project inventory and per-project configuration. Use for: project list, default branch, submodules, install command, build artifacts, dev config, workspace layout, project lookup.'
---
# Project Registry

Domain knowledge about all projects in the workspace — workspace layout, project table, per-project setup details, test commands, and database configuration.

## Cached Context

All project-specific data lives in user memory (`/memories/project-registry.md`). Read it using the `memory-access` skill:
```bash
~/.agents/skills/memory-access/scripts/read-memory.sh project-registry
```

If the memory file does not exist, ask the user the following questions (together, not one at a time), then save the answers using `write-memory.sh`:

1. Where is your workspace root? (e.g., `~/mydev`)
2. What is the directory structure? (e.g., `masterRepos/` + `worktrees/`)
3. What GitHub org do your projects belong to?
4. For each project: name, default branch, submodule support, install command, build artifacts needed, dev config copy needed, dev stash needed
5. Per-project setup details (build artifact commands, config files, etc.)
6. Test commands and database isolation rules (if applicable)
7. Default local database name (if applicable)

Use the `## Workspace Layout`, `## Project Table`, `## Per-Project Setup Details`, `## Test Commands`, and `## Database` sections as the memory file structure — see the `pr-dashboard` skill for the cache pattern.

## How to Use the Registry

Once the memory file exists, all references in this skill use placeholder paths that resolve from the cached layout:
- `<workspace-root>` → the workspace root (e.g., `~/bhDev`)
- `<master-repos>` → `<workspace-root>/masterRepos/`
- `<worktrees>` → `<workspace-root>/worktrees/`
- `<project>` → the specific project name from the table

All master repo paths follow the pattern `<master-repos>/<project>`.

## Column Definitions

**Has Submodules** means the project has `switch-branches.sh` and `update-packages.sh` scripts in its root.

**Dev Stash Needed** means the project requires a developer configuration stash to be applied after reset (contains login credentials, local config, etc.).

## Test Command Rules

When test commands are defined in the memory file for a project, follow these rules:
- **ALWAYS** set `MONGODB_DATABASE` to a unique test database name when projects share a database. Without this override, tests performing `deleteMany({})` will destroy shared development data.
- **ALWAYS** target individual test files — never use wildcards
- If multiple test files are relevant, list them explicitly
- Use the skill's `run-api-test.sh` script when available — it handles database isolation automatically

## Available Scripts

### `scripts/run-api-test.sh`

Run tests for projects that have test database isolation configured. Generates a unique `MONGODB_DATABASE` name per invocation.

**Usage:**
```bash
cd <worktrees>/<project>--<branch>
~/.agents/skills/project-registry/scripts/run-api-test.sh test/brands.test.ts
~/.agents/skills/project-registry/scripts/run-api-test.sh test/brands.test.ts test/integrations.test.ts
```

**Exit codes:**
- `0` — all tests passed
- `1` — test failure(s)
- `2` — usage error (no args, invalid file)

## Build Artifact Context

Some Meteor projects require generated files that are gitignored but needed at runtime. These are normally created by the start script (`bin/start.js`) but must exist before the app can boot. The files are read by the server at startup via `Assets.getTextAsync()`. Without them, the app crashes with `Error: Unknown asset: build_info/head`.
