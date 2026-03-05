#!/bin/bash
# Require approval before editing ~/.agents/hooks/ — these are deterministic guardrails.
# If agents can edit hook scripts unchecked, they can disable their own safety checks.

input=$(cat)
hooks_dir="$HOME/.agents/hooks"
tool_name=$(echo "$input" | jq -r '.tool_name // empty')

# Allow read-only tools without prompting
case "$tool_name" in
  *read*|*search*|*list*|*find*|*grep*|*get*) exit 0 ;;
esac

# Check if any path in tool_input targets the hooks directory
if echo "$input" | jq -r '.tool_input // {} | .. | strings' 2>/dev/null | grep -q "$hooks_dir"; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "ask",
      permissionDecisionReason: "This edit targets hook scripts (~/.agents/hooks/), which are used for safety checks. Approve to allow."
    }
  }'
  exit 0
fi
