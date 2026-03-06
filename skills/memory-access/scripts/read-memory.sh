#!/usr/bin/env bash
# read-memory.sh — Read an agent memory file by name
# Resolves paths relative to the .agents directory, avoiding external-file prompts.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENTS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
MEMORIES_DIR="$AGENTS_ROOT/memories"

usage() {
  cat >&2 <<'EOF'
Usage: read-memory.sh <memory-name>

Read an agent memory file and output its contents to stdout.

Arguments:
  memory-name   Name of the memory file without .md extension.
                Supports subdirectories (e.g., session/task-notes).

Exit codes:
  0  File found, contents on stdout
  1  File not found
  2  Usage error

Examples:
  read-memory.sh pr-dashboard
  read-memory.sh session/current-task
EOF
  exit 2
}

if [[ $# -lt 1 || "$1" == "--help" || "$1" == "-h" ]]; then
  usage
fi

MEMORY_NAME="$1"
MEMORY_FILE="$MEMORIES_DIR/$MEMORY_NAME.md"

if [[ ! -f "$MEMORY_FILE" ]]; then
  echo "Memory not found: $MEMORY_NAME ($MEMORY_FILE)" >&2
  exit 1
fi

cat "$MEMORY_FILE"
