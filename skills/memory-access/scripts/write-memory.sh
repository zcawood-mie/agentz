#!/usr/bin/env bash
# write-memory.sh — Write content to an agent memory file
# Takes memory name and content as arguments. Creates parent directories as needed.
# Performs atomic full-file replacement — no incremental edits.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENTS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
MEMORIES_DIR="$AGENTS_ROOT/memories"

usage() {
  cat >&2 <<'EOF'
Usage: write-memory.sh <memory-name> <content>

Write content to a memory file, replacing it entirely.
Creates the file and parent directories if they don't exist.

Arguments:
  memory-name   Name of the memory file without .md extension.
                Supports subdirectories (e.g., session/task-notes).
  content       The full content to write to the file.

Exit codes:
  0  File written successfully
  2  Usage error

Examples:
  write-memory.sh pr-dashboard "# PR Dashboard Context
  - **GitHub username:** octocat"
  write-memory.sh session/current-task "Working on issue #42"
EOF
  exit 2
}

if [[ $# -lt 2 || "$1" == "--help" || "$1" == "-h" ]]; then
  usage
fi

MEMORY_NAME="$1"
CONTENT="$2"
MEMORY_FILE="$MEMORIES_DIR/$MEMORY_NAME.md"
MEMORY_DIR="$(dirname "$MEMORY_FILE")"

mkdir -p "$MEMORY_DIR"
printf '%s\n' "$CONTENT" > "$MEMORY_FILE"

echo "Written: $MEMORY_NAME ($MEMORY_FILE)" >&2
