---
name: hook-conventions
description: 'Hook file conventions, lifecycle events, and script guidelines. Use for: create hook, new hook, edit hook, hook lifecycle, hook scripts, PreToolUse, PostToolUse.'
user-invokable: false
---
# Hook Conventions

## When to Use
- Creating or editing a hook script
- Understanding hook lifecycle events
- Choosing between hooks, instructions, and skills for enforcement

## File Locations
- **Config:** `~/.agents/hooks/global.json` — defines which scripts run at which lifecycle events
- **Scripts:** `~/.agents/hooks/scripts/<name>.sh` — the actual shell scripts that execute

## Config Template

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "type": "command",
        "command": "~/.agents/hooks/scripts/script-name.sh",
        "timeout": 5
      }
    ],
    "PostToolUse": [
      {
        "type": "command",
        "command": "~/.agents/hooks/scripts/other-script.sh",
        "timeout": 30
      }
    ]
  }
}
```

## Lifecycle Events

| Event | Fires When | Common Uses |
|---|---|---|
| `PreToolUse` | Before any tool runs | Block dangerous ops, require approval |
| `PostToolUse` | After tool completes | Auto-format, log results |
| `SessionStart` | New agent session | Inject project context |
| `UserPromptSubmit` | User sends prompt | Audit requests |
| `SubagentStart` | Subagent spawned | Track nested usage |
| `SubagentStop` | Subagent completes | Aggregate results |
| `PreCompact` | Before context compaction | Save important state |
| `Stop` | Session ends | Generate reports, cleanup |

## Script Guidelines
- Read JSON input from stdin, write JSON output to stdout
- Exit 0 = success (parse stdout), exit 2 = blocking error, other = warning
- Use `jq` for JSON construction to handle escaping correctly
- Short-circuit early when the event is irrelevant (wrong tool name, no matching input)
- No `set -euo pipefail` — hooks should be fault-tolerant
- Keep scripts focused — one concern per script

## Hooks vs Instructions vs Skills

| Characteristic | Hook | Instruction | Skill |
|---|---|---|---|
| Enforcement | **Deterministic** — code runs regardless | Advisory — agent may ignore | Advisory — agent may ignore |
| Runs on | Lifecycle events | Every prompt | On-demand |
| Format | Shell script + JSON config | Markdown | Markdown |
| Can block actions | Yes (`permissionDecision: deny`) | No | No |
| Can modify behavior | Yes (modify input, inject context) | Influence only | Influence only |
| Portability | VS Code, Claude Code, Copilot CLI | VS Code only | Cross-agent |

**Heuristic:** If the rule MUST be enforced without exception → hook. If it's guidance that shapes behavior → instruction or skill.

## Current Hooks

| Script | Event | Purpose |
|---|---|---|
| `block-hooks-edit.sh` | PreToolUse | Require approval for edits to `~/.agents/hooks/` |
| `block-force-push.sh` | PreToolUse | Block `git push --force` (require `--force-with-lease`) |
| `scan-before-push.sh` | PreToolUse | Scan diff for secrets/debug artifacts before `git push` |
| `sandbox-git.sh` | PreToolUse | Auto-approve safe git ops, block dangerous ones (reset --hard, branch deletion, remote manipulation) |
| `auto-approve-simple.sh` | PreToolUse | Auto-approve non-destructive terminal commands (package managers, read-only, build tools) |
| `auto-format.sh` | PostToolUse | Auto-format edited files with prettier |

## Security Notes
- Hook scripts execute with the same permissions as VS Code
- Agents are prompted for approval before editing `~/.agents/hooks/` (enforced by `block-hooks-edit.sh` with `permissionDecision: "ask"`)
- Review hook scripts manually — never let agents create or modify them without explicit approval
