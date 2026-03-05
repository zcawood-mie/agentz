#!/bin/bash
# Scan for sensitive content before git push.
# Blocks on secrets/credentials, warns on debug artifacts.
# Mirrors the scan from the git-workflow skill but enforced deterministically.

input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // empty')
[[ -z "$command" ]] && exit 0

# Only intercept git push commands
echo "$command" | grep -qE 'git\s+push\b' || exit 0

cwd=$(echo "$input" | jq -r '.cwd // empty')
[[ -n "$cwd" ]] && cd "$cwd" 2>/dev/null

# Get diff of unpushed commits
diff_output=$(git diff '@{u}'..HEAD 2>/dev/null \
  || git diff origin/main..HEAD 2>/dev/null \
  || git diff origin/master..HEAD 2>/dev/null \
  || true)
[[ -z "$diff_output" ]] && exit 0

# --- Blocking patterns: secrets, credentials, keys ---
blocking=$(echo "$diff_output" | grep -inE \
  '(api[_-]?key|secret|token|password|credential|private[_-]?key|connection[_-]?string)\s*[:=]' \
  2>/dev/null | head -5 || true)

if [[ -n "$blocking" ]]; then
  echo "$blocking" | jq -Rs '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: ("Potential secrets detected in diff:\n" + .)
    }
  }'
  exit 0
fi

# --- Warning patterns: debug artifacts, localhost, absolute paths ---
warnings=$(echo "$diff_output" | grep -inE \
  '(console\.(log|debug)\()|(debugger;)|(localhost|127\.0\.0\.1)|(/Users/[a-zA-Z])' \
  2>/dev/null | head -5 || true)

if [[ -n "$warnings" ]]; then
  echo "$warnings" | jq -Rs '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "ask",
      permissionDecisionReason: ("Warning patterns found in diff (console.log, debugger, localhost, etc.):\n" + .)
    }
  }'
  exit 0
fi
