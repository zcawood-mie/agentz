#!/bin/bash
# Auto-format files after edits using the project's prettier config.
# No-op if prettier isn't installed or the file type isn't supported.

input=$(cat)

# Extract file path (single-file tools like replace_string_in_file)
file_path=$(echo "$input" | jq -r '.tool_input.filePath // empty')
[[ -z "$file_path" || ! -f "$file_path" ]] && exit 0

# Skip files that shouldn't be auto-formatted
case "$file_path" in
  *.lock|*.min.js|*.min.css|*.map) exit 0 ;;
  */.agents/*) exit 0 ;;
esac

# Navigate to workspace
cwd=$(echo "$input" | jq -r '.cwd // empty')
[[ -n "$cwd" ]] && cd "$cwd" 2>/dev/null

# Run prettier if installed in the project (don't download via npx)
if command -v npx &>/dev/null && [[ -f "node_modules/.bin/prettier" ]]; then
  if npx prettier --write "$file_path" 2>/dev/null; then
    jq -n --arg file "$file_path" '{
      hookSpecificOutput: {
        hookEventName: "PostToolUse",
        additionalContext: ("Auto-formatted with prettier: " + $file)
      }
    }'
  fi
fi
