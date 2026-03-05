#!/bin/bash
# Block git push --force without --force-with-lease.
# --force-with-lease is safer — it fails if the remote has commits you haven't fetched.

input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // empty')
[[ -z "$command" ]] && exit 0

# Only check commands that include git push
echo "$command" | grep -qE 'git\s+push\b' || exit 0

# Block --force or -f unless --force-with-lease is present
if echo "$command" | grep -qE '(\s|^)(--force|-f)(\s|$)' && \
   ! echo "$command" | grep -q -- '--force-with-lease'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "git push --force is blocked. Use --force-with-lease instead."
    }
  }'
  exit 0
fi
