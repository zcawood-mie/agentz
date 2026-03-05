#!/bin/bash
# Auto-approve simple, non-destructive terminal commands that autonomous
# workflows need to run without user approval.
#
# Approved categories:
#   - Package managers: npm, pnpm, npx (run, test, install, exec)
#   - Meteor: meteor npm, meteor test, npx meteor
#   - Read-only: ls, cat, head, tail, wc, echo, pwd, which, type
#   - Build/test: tsc, eslint, prettier
#
# Security:
#   - Destructive commands (rm, mv, chmod, etc.) are explicitly denied
#   - Commands with chaining operators (&&, ||, ;, |) fall through to user approval
#
# Everything else falls through to VS Code's default behavior (ask user).

input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // empty')
[[ -z "$command" ]] && exit 0

# Strip a leading "cd <path> &&" — the tool prepends this when cwd doesn't
# match, but it's just a directory change and shouldn't block auto-approval.
command=$(echo "$command" | sed -E 's/^[[:space:]]*cd[[:space:]]+[^&]+&&[[:space:]]*//')

# Strip leading environment variable assignments (e.g. NODE_ENV=test FOO=bar)
# so "NODE_ENV=test node --test ..." still matches the "node" rule.
bare_command=$(echo "$command" | sed 's/^[[:space:]]*\([A-Za-z_][A-Za-z_0-9]*=[^ ]*[[:space:]]*\)*//')

# Skip if it's a git command — sandbox-git.sh handles those
echo "$command" | grep -qE '\bgit\b' && exit 0

# ── FALL THROUGH: Destructive commands ──
# Commands like rm, mv, chmod, kill require user approval — never auto-approve.
if echo "$bare_command" | grep -qE '^\s*(rm|rmdir|mv|chmod|chown|dd|mkfs|fdisk|kill|killall|pkill)\b'; then
  exit 0
fi

# ── FALL THROUGH: Command chaining ──
# Commands with &&, ||, ;, or | require user approval. Agents should run
# one command per terminal call (see no-command-chaining instruction).
if echo "$command" | grep -qE '&&|[;|]'; then
  exit 0
fi

# ── APPROVE: Package manager commands ──
if echo "$bare_command" | grep -qE '^\s*(npm|pnpm|npx|meteor)\s'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "allow",
      permissionDecisionReason: "Package manager / Meteor command — auto-approved."
    }
  }'
  exit 0
fi

# ── APPROVE: Read-only inspection commands ──
if echo "$bare_command" | grep -qE '^\s*(ls|cat|head|tail|wc|echo|pwd|which|type|file|stat|cd)\b'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "allow",
      permissionDecisionReason: "Read-only command — auto-approved."
    }
  }'
  exit 0
fi

# ── APPROVE: Build/lint tools ──
if echo "$bare_command" | grep -qE '^\s*(tsc|eslint|prettier|node)\b'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "allow",
      permissionDecisionReason: "Build/lint tool — auto-approved."
    }
  }'
  exit 0
fi

# Everything else: no opinion — VS Code will ask the user
