---
name: No Command Chaining
description: Limit command chaining — allow cd && but forbid arbitrary chains
applyTo: '**'
---
# No Command Chaining

Limit chaining in terminal calls. Only `cd <dir> && <command>` is allowed — all other chaining is forbidden.

**Allowed:**
- `cd /path/to/dir && pnpm run dev` (directory change + single command)
- `cd ~/project && git status`

**Forbidden operators (except after `cd`):**
- `&&` between two non-cd commands
- `||` (OR chain)
- `;` (sequential)
- `|` (pipe)

**Instead:**
- Run each command in a separate `run_in_terminal` call
- If you need filtered output, use built-in search tools (`grep_search`, `read_file` with line ranges) instead of piping shell output

**Why:** Command chaining bypasses safety hooks that validate individual commands. A safe command chained with a destructive one gets auto-approved as a unit. The `cd &&` exception is necessary because background terminals always start at the workspace root.
