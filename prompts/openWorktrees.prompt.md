---
name: openWorktrees
description: Open a labeled, interactive terminal for each worktree relevant to the current session
argument-hint: Optionally name specific worktrees or a feature/issue keyword to filter by (e.g. "issue-849")
agent: Implementation
model: GPT-4.1 mini
---
Open a labeled, interactive terminal for each worktree that is relevant to the current session, so the user can click "Focus Terminal" directly into the right project directory.

## Rules

- Run ALL terminal commands DIRECTLY — never delegate to a subagent. Terminals opened by subagents are not accessible to the user.
- Run one `run_in_terminal` call per worktree, sequentially (not batched).
- Do NOT open terminals for every worktree — only the ones relevant to the current session.

## Steps

1. **Identify relevant worktrees**
   Check session memory (if any exists) and the current conversation context to determine which worktrees have been touched, discussed, or worked in during this session. If the user provided an argument, use it to filter. If nothing can be determined from context, ask the user which worktrees to open before proceeding.

2. **Open a terminal per relevant worktree**
   For each identified worktree, run (with `isBackground=false`):
   ```
   cd /path/to/worktree && echo -ne "\033]0;WORKTREE-NAME\007"
   ```
   This navigates the terminal to the worktree root and sets the tab title to the worktree name.
   Resolve worktree paths from the `project-registry` skill's index (`/memories/project-index.md`).

3. **Summarize**
   List the terminals opened. One line each.
