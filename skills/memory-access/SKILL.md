---
name: memory-access
description: 'Read and write agent memory files without external-file prompts. Use for: memory, cache, read memory, write memory, skill cache, user context.'
user-invokable: false
---
# Memory Access

Global agent memory files live at `$AGENTS_ROOT/memories/` — **outside** the VS Code workspace. This skill provides prompt-free access to them.

## When to Use

Store data here when it **shouldn't be committed to the public agents repo** — either because it's user-specific or because it's project-specific operational knowledge that only applies to this user's environment:
- User configuration (GitHub username, team workflow, org name)
- Skill caches (PR dashboard context, saved preferences)
- Cross-project knowledge (things true regardless of which repo is open)
- Project-scoped setup, test config, and command templates (`projects/<key>/setup.md`, `projects/<key>/test.md`)

## When NOT to Use

- Domain knowledge, methodology, or rules — that belongs in skills
- Project-specific facts common to all developers (conventions, codebase structure) — Copilot's repo memory (`.copilot/memories/`) handles that automatically
- Volatile state like current branch names or PR lists
- Secrets or tokens

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
$AGENTS_ROOT/skills/memory-access/scripts/read-memory.sh <memory-name>
```

**Examples:**
```
$AGENTS_ROOT/skills/memory-access/scripts/read-memory.sh pr-dashboard
$AGENTS_ROOT/skills/memory-access/scripts/read-memory.sh session/current-task
```

### Writing

Pass the memory name and content as two arguments. This performs **atomic full-file replacement** — the entire file is overwritten, not patched.

```
$AGENTS_ROOT/skills/memory-access/scripts/write-memory.sh <memory-name> '<content>'
```

**Examples:**
```
$AGENTS_ROOT/skills/memory-access/scripts/write-memory.sh pr-dashboard '# PR Dashboard Context
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

## Project Memory Structure

Project-specific operational knowledge lives under `$AGENTS_ROOT/memories/projects/<key>/` in domain-scoped files:

```
memories/projects/<key>/
  setup.md          # Install command, build artifacts, dev config
  test.md           # Test command template, database isolation rules
```

Domain memory files are owned by the skill responsible for that domain (e.g., `test.md` is owned by `testing-workflow`). They contain **data and command templates** — not executable scripts. Scripts live in skills where they're discoverable; memories provide the project-specific values that parameterize those scripts.

## Available Scripts

### `read-memory.sh`

Reads a memory file and outputs its contents.

**Usage:**
```
$AGENTS_ROOT/skills/memory-access/scripts/read-memory.sh <memory-name>
$AGENTS_ROOT/skills/memory-access/scripts/read-memory.sh --help
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
$AGENTS_ROOT/skills/memory-access/scripts/write-memory.sh <memory-name> '<content>'
$AGENTS_ROOT/skills/memory-access/scripts/write-memory.sh --help
```

**Arguments:**
- `<memory-name>` — Name of the memory file without `.md` extension. Supports subdirectories (e.g., `session/task-notes`).
- `<content>` — The full content to write to the file.

**Exit codes:**
- `0` — File written successfully
- `2` — Usage error
