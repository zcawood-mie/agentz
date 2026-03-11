---
name: project-registry
user-invokable: false
description: 'Project inventory and workspace layout. Use for: project list, default branch, submodules, workspace layout, project lookup, GitHub org.'
---
# Project Registry

Thin registry for project identity and workspace layout. Answers: "does this project exist, what's its default branch, and where does it live." Operational details (setup, testing, etc.) live in domain-specific memory files owned by other skills.

## Data Layout

```
memories/
  project-index.md              # Workspace layout, org, project list, default DB
  projects/
    <key>/
      setup.md                  # Owned by: worktree-management, project-reset
      test.md                   # Owned by: testing-workflow
```

Each skill reads only its own slice. This skill owns the index.

### Layer 1 — Project-Committed (in each project repo)
Team conventions committed to `.github/copilot-instructions.md` or project-level skills. Loaded automatically by VS Code when that workspace is open. This skill doesn't manage Layer 1.

### Layer 2 — User-Specific Domain Files (`$AGENTS_ROOT/memories/projects/<key>/<domain>.md`)
Per-project configuration split by domain. Each domain file is owned by the skill responsible for that concern — see the data layout above for ownership.

### Layer 3 — User-Specific Index (`$AGENTS_ROOT/memories/project-index.md`)
Workspace root, directory structure, GitHub org, project list with default branches, default database. Lightweight — never contains operational details.

## How to Load Context

### Index lookup (workspace paths, project list)
```bash
$AGENTS_ROOT/skills/memory-access/scripts/read-memory.sh project-index
```

### Determining the current project
Use the repository attachment context (`owner/repo-name`) to map to a project key. If no repo context is available, infer from `$PWD` or ask the user.

## First-Time Setup

If `$AGENTS_ROOT/memories/project-index.md` does not exist, ask the user these questions (together, not one at a time), then save using `write-memory.sh`:

1. Where is your workspace root? (e.g., `~/dev`)
2. Describe your workspace layout — where are your repos? Do you use worktrees? If so, where do they go?
3. What GitHub org do your projects belong to?
4. List all projects with their default branches and whether they have submodules
5. Default local database name (if applicable)

Save to `project-index` using the `## Workspace Layout`, `## Projects`, and `## Database` sections.

Then prompt the user for per-project setup details and save to `projects/<key>/setup` (see `worktree-management` skill). If the project has test infrastructure, save test config to `projects/<key>/test` (see `testing-workflow` skill).

## Placeholder Paths

Across this skill and others, these placeholders resolve from the project-index memory:
- `<workspace-root>` → the user's workspace root directory
- `<project>` → the specific project name

Workspace layout varies by user. The index stores whatever directory structure the user has — repos may be in a flat directory, nested org folders, or a master-clone + worktree setup. Always read paths from the index, never assume a particular layout.

## Column Definitions

**Has Submodules** means the project uses git submodules. See `worktree-management` for submodule initialization steps.
