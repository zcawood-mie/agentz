#!/usr/bin/env bash
# create-worktree.sh — Create a git worktree with full project setup.
#
# Automates the multi-step worktree creation process:
# 1. Fetch latest from remote
# 2. Create branch and worktree
# 3. Initialize submodules (one at a time)
# 4. Generate build artifacts (build_info)
# 5. Copy developer-specific config files
# 6. Install dependencies
#
# All project-specific configuration is passed as arguments — the agent reads
# project memory files to determine the correct values.
#
# Usage:
#   bash scripts/create-worktree.sh <repo> <branch-name> [OPTIONS]
#
# Arguments:
#   <repo>         Repository name
#   <branch-name>  Branch name to create (e.g., feature/issue-42-add-endpoint)
#
# Options:
#   --repo-dir DIR        Path to the source repository (required)
#   --worktree-dir DIR    Directory for worktrees (default: parent of repo-dir)
#   --base REF            Base ref to branch from (default: main)
#   --install-cmd CMD     Dependency install command (e.g. "pnpm install")
#   --submodules          Initialize submodules after creation
#   --build-info          Generate private/build_info/head and time
#   --build-packages      Also generate build_info/packages from submodules
#   --env-copy            Copy .env from source repo to worktree
#   --no-install          Skip dependency installation
#   --dry-run             Show what would be done without executing
#   --help                Show this help message
#
# Exit codes:
#   0  Worktree created successfully
#   1  Error during creation
#   2  Invalid arguments
#
# Examples (paths come from the user's project-index memory):
#   bash scripts/create-worktree.sh my-api feature/new-endpoint \
#     --repo-dir /path/to/my-api \
#     --base main --install-cmd "pnpm install" --env-copy
#
#   bash scripts/create-worktree.sh my-app feature/big-change \
#     --repo-dir /path/to/my-app --worktree-dir /path/to/worktrees \
#     --base master --install-cmd "meteor npm install" \
#     --submodules --build-info --build-packages
#
#   bash scripts/create-worktree.sh my-api fix/typo \
#     --repo-dir /path/to/my-api --base main --dry-run

set -euo pipefail

REPO_DIR=""
WORKTREE_DIR=""

# --- Helpers ---
info()  { echo "  [INFO] $*" >&2; }
warn()  { echo "  [WARN] $*" >&2; }
error() { echo "  [ERROR] $*" >&2; }
step()  { echo "" >&2; echo "-> $*" >&2; }

usage() {
    cat >&2 <<'EOF'
Usage: bash scripts/create-worktree.sh <repo> <branch-name> [OPTIONS]

Arguments:
  <repo>                Repository name
  <branch-name>         Branch name to create

Options:
  --repo-dir DIR        Path to the source repository (required)
  --worktree-dir DIR    Directory for worktrees (default: parent of repo-dir)
  --base REF            Base ref to branch from (default: main)
  --install-cmd CMD     Dependency install command (e.g. "pnpm install")
  --submodules          Initialize submodules after creation
  --build-info          Generate private/build_info/head and time
  --build-packages      Also generate build_info/packages from submodules
  --env-copy            Copy .env from source repo to worktree
  --no-install          Skip dependency installation
  --dry-run             Show what would be done without executing
  --help                Show this help message
EOF
    exit 2
}

# --- Parse arguments ---
REPO=""
BRANCH=""
BASE_REF="main"
INSTALL_CMD=""
HAS_SUBMODULES=false
NEEDS_BUILD_INFO=false
NEEDS_BUILD_PACKAGES=false
NEEDS_ENV_COPY=false
NO_INSTALL=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --repo-dir)     REPO_DIR="$2"; shift 2 ;;
        --worktree-dir) WORKTREE_DIR="$2"; shift 2 ;;
        --base)         BASE_REF="$2"; shift 2 ;;
        --install-cmd)  INSTALL_CMD="$2"; shift 2 ;;
        --submodules)   HAS_SUBMODULES=true; shift ;;
        --build-info)   NEEDS_BUILD_INFO=true; shift ;;
        --build-packages) NEEDS_BUILD_PACKAGES=true; shift ;;
        --env-copy)     NEEDS_ENV_COPY=true; shift ;;
        --no-install)   NO_INSTALL=true; shift ;;
        --dry-run)      DRY_RUN=true; shift ;;
        --help|-h)      usage ;;
        -*)             error "Unknown option: $1"; usage ;;
        *)
            if [[ -z "$REPO" ]]; then
                REPO="$1"
            elif [[ -z "$BRANCH" ]]; then
                BRANCH="$1"
            else
                error "Unexpected argument: $1"; usage
            fi
            shift
            ;;
    esac
done

if [[ -z "$REPO" || -z "$BRANCH" ]]; then
    error "Both <repo> and <branch-name> are required."
    usage
fi

if [[ -z "$REPO_DIR" ]]; then
    error "--repo-dir is required."
    usage
fi

# Default worktree-dir to parent of repo-dir
if [[ -z "$WORKTREE_DIR" ]]; then
    WORKTREE_DIR="$(dirname "$REPO_DIR")"
fi

# --- Compute directory name ---
# feature/issue-42-add-endpoint -> feature-issue-42-add-endpoint
BRANCH_DIR_NAME="${BRANCH//\//-}"
DIR_NAME="${REPO}--${BRANCH_DIR_NAME}"
WORKTREE_PATH="$WORKTREE_DIR/$DIR_NAME"
REPO_PATH="$REPO_DIR"

# --- Validate source repo exists ---
if [[ ! -d "$REPO_PATH/.git" && ! -f "$REPO_PATH/.git" ]]; then
    error "Source repo not found: $REPO_PATH"
    exit 1
fi

# --- Dry run output ---
if [[ "$DRY_RUN" == true ]]; then
    echo "{"
    echo "  \"repo\": \"$REPO\","
    echo "  \"branch\": \"$BRANCH\","
    echo "  \"base\": \"$BASE_REF\","
    echo "  \"worktree_path\": \"$WORKTREE_PATH\","
    echo "  \"repo_path\": \"$REPO_PATH\","
    echo "  \"submodules\": $HAS_SUBMODULES,"
    echo "  \"install_cmd\": \"$INSTALL_CMD\","
    echo "  \"build_info\": $NEEDS_BUILD_INFO,"
    echo "  \"build_packages\": $NEEDS_BUILD_PACKAGES,"
    echo "  \"env_copy\": $NEEDS_ENV_COPY,"
    echo "  \"skip_install\": $NO_INSTALL,"
    echo "  \"dry_run\": true"
    echo "}"
    exit 0
fi

# --- Check if worktree already exists ---
if [[ -d "$WORKTREE_PATH" ]]; then
    error "Worktree already exists: $WORKTREE_PATH"
    exit 1
fi

# --- Step 1: Fetch latest ---
step "Step 1/6: Fetching latest from remote"
cd "$REPO_PATH"
git fetch origin

# --- Step 2: Create branch and worktree ---
step "Step 2/6: Creating worktree at $WORKTREE_PATH"
git worktree add -b "$BRANCH" "$WORKTREE_PATH" "origin/$BASE_REF"
cd "$WORKTREE_PATH"
info "Created worktree and branch '$BRANCH' from origin/$BASE_REF"

# --- Step 3: Initialize submodules ---
if [[ "$HAS_SUBMODULES" == true ]]; then
    step "Step 3/6: Initializing submodules (one at a time)"
    git submodule init
    git submodule foreach --quiet 'echo $sm_path' | while read -r sm; do
        info "Updating submodule: $sm"
        git submodule update --init "$sm"
    done
else
    step "Step 3/6: No submodules — skipping"
fi

# --- Step 4: Generate build artifacts ---
if [[ "$NEEDS_BUILD_INFO" == true ]]; then
    step "Step 4/6: Generating build artifacts"
    mkdir -p private/build_info
    git rev-parse --short HEAD > private/build_info/head
    date +%s000 > private/build_info/time
    info "Created private/build_info/head and time"

    if [[ "$NEEDS_BUILD_PACKAGES" == true && "$HAS_SUBMODULES" == true ]]; then
        git submodule foreach -q 'echo "$name $sha1"' > private/build_info/packages
        info "Created private/build_info/packages"
    fi
else
    step "Step 4/6: No build artifacts needed — skipping"
fi

# --- Step 5: Copy developer-specific config ---
if [[ "$NEEDS_ENV_COPY" == true ]]; then
    step "Step 5/6: Copying developer config files"
    if [[ -f "$REPO_PATH/.env" ]]; then
        cp "$REPO_PATH/.env" "$WORKTREE_PATH/.env"
        info "Copied .env from source repo"
    else
        warn ".env not found in source repo — create manually or from .env.example"
    fi
else
    step "Step 5/6: No config copy needed — skipping"
fi

# --- Step 6: Install dependencies ---
if [[ "$NO_INSTALL" == true || -z "$INSTALL_CMD" ]]; then
    step "Step 6/6: Skipping dependency installation"
else
    step "Step 6/6: Installing dependencies ($INSTALL_CMD)"
    eval "$INSTALL_CMD"
    info "Dependencies installed"
fi

# --- Summary ---
echo "" >&2
echo "============================================" >&2
echo "  Worktree ready: $WORKTREE_PATH" >&2
echo "  Branch: $BRANCH" >&2
echo "  Based on: origin/$BASE_REF" >&2
echo "============================================" >&2
echo "" >&2
echo "  cd $WORKTREE_PATH" >&2

# JSON output for agent consumption
echo "{"
echo "  \"status\": \"success\","
echo "  \"repo\": \"$REPO\","
echo "  \"branch\": \"$BRANCH\","
echo "  \"worktree_path\": \"$WORKTREE_PATH\","
echo "  \"base\": \"origin/$BASE_REF\""
echo "}"
