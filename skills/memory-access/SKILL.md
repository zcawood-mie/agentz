---
name: memory-access
description: 'Read and write agent memory files without external-file prompts. Use for: memory, cache, read memory, write memory, skill cache, user context.'
user-invokable: false
---
# Memory Access

Global agent memory files live at `<agents-root>/memories/` — **outside** the VS Code workspace. This skill provides prompt-free access to them and clarifies when to use global memory vs repo memory.

## When to Use Global Memory (`~/.agents/memories/`)

Store data here when it is **stable across projects and sessions**:
- User configuration (GitHub username, team workflow, org name)
- Skill caches (PR dashboard context, saved preferences)
- Cross-project knowledge (things true regardless of which repo is open)

## When NOT to Use Global Memory

For **project-specific facts** — conventions, build commands, codebase structure — use **repo memory** (`.copilot/memories/` inside the workspace). Repo memory is managed by Copilot automatically and scoped to the current project.

| Question | Global (`~/.agents/memories/`) | Repo (`.copilot/memories/`) |
|---|---|---|
| Does this change if I switch projects? | No | Yes |
| Who manages it? | Skills explicitly (via this skill) | Copilot automatically |
| Scope | All workspaces | Current workspace only |
| Examples | GitHub username, review pipeline | "Uses Meteor", "Tests: `npm test`" |

## The Problem

| Operation | Tool | Prompts? | Visible in VS Code? |
|---|---|---|---|
| Write | `create_file` | No | **Yes** — shows as changed file |
| Read | `read_file` | **Yes** — external file dialog | N/A |
| Read/Write | `run_in_terminal` (scripts) | No | No |

## How to Access Memories

Both reads and writes use scripts via `run_in_terminal`. This keeps memory operations invisible to the editor and avoids external-file prompts.

### Reading

```
~/.agents/skills/memory-access/scripts/read-memory.sh <memory-name>
```

**Examples:**
```
~/.agents/skills/memory-access/scripts/read-memory.sh pr-dashboard
~/.agents/skills/memory-access/scripts/read-memory.sh session/current-task
```

### Writing

Pass the memory name and content as two arguments. This performs **atomic full-file replacement** — the entire file is overwritten, not patched.

```
~/.agents/skills/memory-access/scripts/write-memory.sh <memory-name> '<content>'
```

**Examples:**
```
~/.agents/skills/memory-access/scripts/write-memory.sh pr-dashboard '# PR Dashboard Context
- **GitHub username:** octocat
- **GitHub org:** my-org'
```

## Rules

**ALWAYS:**
- Use `read-memory.sh` and `write-memory.sh` (via `run_in_terminal`) for all memory operations
- Write complete file contents — memory writes are full replacements, not incremental edits

**NEVER:**
- Use `read_file` for memory files outside the workspace — it triggers an approval prompt
- Use `create_file` or `replace_string_in_file` for memory files — these show changes in VS Code
- Use incremental edits on memory files — always write the complete content

## Available Scripts

### `read-memory.sh`

Reads a memory file and outputs its contents.

**Usage:**
```
~/.agents/skills/memory-access/scripts/read-memory.sh <memory-name>
~/.agents/skills/memory-access/scripts/read-memory.sh --help
```

**Arguments:**
- `<memory-name>` — Name of the memory file without `.md` extension. Supports subdirectories (e.g., `session/task-notes`).

**Exit codes:**
- `0` — File found, contents written to stdout
- `1` — File not found (message on stderr)
- `2` — Usage error

### `write-memory.sh`

Writes content to a memory file, replacing it entirely. Creates the file and parent directories if they don't exist.

**Usage:**
```
~/.agents/skills/memory-access/scripts/write-memory.sh <memory-name> '<content>'
~/.agents/skills/memory-access/scripts/write-memory.sh --help
```

**Arguments:**
- `<memory-name>` — Name of the memory file without `.md` extension. Supports subdirectories (e.g., `session/task-notes`).
- `<content>` — The full content to write to the file.

**Exit codes:**
- `0` — File written successfully
- `2` — Usage error
