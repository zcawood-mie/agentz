#!/bin/bash
# Sandbox git operations for autonomous agent workflows.
# Agents can create branches, add, commit, push to origin — but cannot
# switch branches, delete branches, manipulate remotes, or hard reset.
#
# Security:
#   - Commands with chaining operators (&&, ||, ;, |) fall through to user approval
#
# Decision matrix:
#   ALLOW: add, commit, status, diff, log, show, fetch, branch (list),
#          checkout -b, switch -c, checkout --, restore, push origin
#   DENY:  reset --hard, clean -f, branch -d/-D, remote add/remove/set-url
#   ASK:   checkout (switch), switch (without -c), rebase, merge, stash drop

input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // empty')
[[ -z "$command" ]] && exit 0

# Only intercept git commands
echo "$command" | grep -qE '\bgit\b' || exit 0

# Strip a leading "cd <path> &&" — the tool prepends this when cwd doesn't
# match, but it's just a directory change and shouldn't block auto-approval.
command=$(echo "$command" | sed -E 's/^[[:space:]]*cd[[:space:]]+[^&]+&&[[:space:]]*//')

# ── FALL THROUGH: Command chaining ──
# If the command still contains chaining operators after stripping cd, don't auto-approve.
# Agents should run one command per terminal call.
if echo "$command" | grep -qE '&&|[;|]'; then
  exit 0
fi

# ── DENY: Hard reset ──
if echo "$command" | grep -qE 'git\s+reset\s+--hard'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "git reset --hard is blocked. Use git checkout -- <file> to restore individual files."
    }
  }'
  exit 0
fi

# ── DENY: Clean with force ──
if echo "$command" | grep -qE 'git\s+clean\s+-[a-zA-Z]*f'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "git clean -f is blocked. It permanently deletes untracked files."
    }
  }'
  exit 0
fi

# ── DENY: Branch deletion ──
if echo "$command" | grep -qE 'git\s+branch\s+-[dD]'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "Branch deletion is blocked. Only the repository owner should delete branches."
    }
  }'
  exit 0
fi

# ── DENY: Remote manipulation ──
if echo "$command" | grep -qE 'git\s+remote\s+(add|remove|rm|set-url|rename)'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "Remote manipulation is blocked. Agents must only use the existing origin remote."
    }
  }'
  exit 0
fi

# ── DENY: Push to non-origin remote ──
# Allow: git push, git push origin, git push -u origin, git push --set-upstream origin
# Deny: git push <other-remote>
if echo "$command" | grep -qE 'git\s+push\s+[a-zA-Z]'; then
  if ! echo "$command" | grep -qE 'git\s+push\s+(origin\b|-u\s+origin\b|--set-upstream\s+origin\b)'; then
    jq -n '{
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: "Pushing to non-origin remotes is blocked. Use git push origin <branch>."
      }
    }'
    exit 0
  fi
fi

# ── ASK: Branch switching via git checkout ──
# Allow: checkout -b (create), checkout -B (force create), checkout -- (file restore)
# Ask: everything else (likely a branch switch)
if echo "$command" | grep -qE 'git\s+checkout\s' && \
   ! echo "$command" | grep -qE 'git\s+checkout\s+-[bB]\b' && \
   ! echo "$command" | grep -qE 'git\s+checkout\s+--\s'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "ask",
      permissionDecisionReason: "Branch switching detected. Approve if this is intentional — agents should typically stay on their feature branch."
    }
  }'
  exit 0
fi

# ── ASK: Branch switching via git switch ──
# Allow: switch -c (create)
# Ask: everything else
if echo "$command" | grep -qE 'git\s+switch\s' && \
   ! echo "$command" | grep -qE 'git\s+switch\s+-c\b'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "ask",
      permissionDecisionReason: "Branch switching detected. Approve if this is intentional — agents should typically stay on their feature branch."
    }
  }'
  exit 0
fi

# ── ASK: Rebase and merge ──
# Exclude merge-base (used in diff comparisons, not an actual merge)
if echo "$command" | grep -qE 'git\s+(rebase|merge)\b' && \
   ! echo "$command" | grep -qE 'git\s+merge-base\b'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "ask",
      permissionDecisionReason: "Rebase/merge detected. Approve if this is intentional."
    }
  }'
  exit 0
fi

# ── ASK: Stash drop (destructive stash op) ──
if echo "$command" | grep -qE 'git\s+stash\s+(drop|clear)'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "ask",
      permissionDecisionReason: "Stash drop/clear detected. This permanently discards stashed changes. Approve if intentional."
    }
  }'
  exit 0
fi

# All other git commands are allowed (add, commit, status, diff, log, show,
# fetch, branch --list, stash push/pop, checkout -b, push origin, etc.)
# Explicitly approve so VS Code doesn't prompt the user.
jq -n '{
  hookSpecificOutput: {
    hookEventName: "PreToolUse",
    permissionDecision: "allow",
    permissionDecisionReason: "Safe git operation — auto-approved by sandbox-git hook."
  }
}'
