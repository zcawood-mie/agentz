#!/usr/bin/env bash
# Run bluehive-api tests with an isolated test database.
#
# Generates a unique MONGODB_DATABASE name per invocation to prevent
# tests from mutating the shared development database.
#
# Usage:
#   run-api-test.sh <test-file> [test-file...]
#   run-api-test.sh test/brands.test.ts
#   run-api-test.sh test/brands.test.ts test/integrations.test.ts
#   run-api-test.sh --help
#
# Exit codes:
#   0 — all tests passed
#   1 — test failure(s)
#   2 — usage error

set -euo pipefail

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" || $# -eq 0 ]]; then
  cat >&2 <<'EOF'
Usage: run-api-test.sh <test-file> [test-file...]

Run bluehive-api tests with an isolated database.

Arguments:
  test-file   One or more test file paths (e.g. test/brands.test.ts)

Options:
  --help, -h  Show this help message

Environment:
  MONGODB_DATABASE is overridden with a unique name per run.
  NODE_ENV is set to 'test'.

Examples:
  run-api-test.sh test/brands.test.ts
  run-api-test.sh test/integrations.test.ts test/orders-routes.test.ts
EOF
  [[ $# -eq 0 ]] && exit 2
  exit 0
fi

# Validate that all arguments look like test files
for file in "$@"; do
  if [[ ! "$file" == *.test.ts ]]; then
    echo "Error: '$file' does not look like a test file (expected *.test.ts)" >&2
    exit 2
  fi
  if [[ ! -f "$file" ]]; then
    echo "Error: '$file' not found" >&2
    exit 2
  fi
done

# Generate a unique database name to isolate this test run
DB_NAME="bluehive_test_$(date +%s)_${RANDOM}_$$"
echo "[run-api-test] Using isolated database: $DB_NAME" >&2

export NODE_ENV=test
export MONGODB_DATABASE="$DB_NAME"

exec node \
  --test \
  --test-force-exit \
  --test-concurrency=20 \
  --experimental-test-module-mocks \
  --import tsx \
  --import ./test/setup-mongo-env.ts \
  "$@"
