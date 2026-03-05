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
# Usage:
#   bash scripts/create-worktree.sh <repo> <branch-name> [OPTIONS]
#
# Arguments:
#   <repo>         Repository name (e.g., bluehive-employer, bluehive-api)
#   <branch-name>  Branch name to create (e.g., feature/issue-42-add-endpoint)
#
# Options:
#   --base REF        Base ref to branch from (default: project's default branch)
#   --no-install      Skip dependency installation
#   --dry-run         Show what would be done without executing
#   --help            Show this help message
#
# Exit codes:
#   0  Worktree created successfully
#   1  Error during creation
#   2  Invalid arguments
#
# Examples:
#   bash scripts/create-worktree.sh bluehive-employer feature/issue-42-fix
#   bash scripts/create-worktree.sh bluehive-api feature/new-endpoint --base main
#   bash scripts/create-worktree.sh bluehive feature/big-change --no-install
#   bash scripts/create-worktree.sh bluehive-employer fix/typo --dry-run

set -euo pipefail

BHDEV="$HOME/bhDev"
MASTER_DIR="$BHDEV/masterRepos"
WORKTREE_DIR="$BHDEV/worktrees"

# --- Project Registry ---
# Format: "default_branch|has_submodules|install_cmd|needs_build_info|needs_env_copy"
# Using a function instead of associative arrays for bash 3.x (macOS) compatibility.
AVAILABLE_REPOS="bluehive bluehive-ai bluehive-api bluehive-employer bluehive-opsdesk bluehive-provider bluehive-ui waggleline"

get_registry() {
    case "$1" in
        bluehive)          echo "master|yes|meteor npm install|yes|no" ;;
        bluehive-ai)       echo "main|no|meteor npm install|no|no" ;;
        bluehive-api)      echo "main|no|pnpm install|no|yes" ;;
        bluehive-employer)  echo "master|yes|meteor npm install|yes|no" ;;
        bluehive-opsdesk)  echo "main|no|npm install|no|no" ;;
        bluehive-provider) echo "master|yes|meteor npm install|yes|no" ;;
        bluehive-ui)       echo "master|no|npm install|no|no" ;;
        waggleline)        echo "main|no|npm install|no|no" ;;
        *)                 return 1 ;;
    esac
}

# --- Helpers ---
info()  { echo "  [INFO] $*" >&2; }
warn()  { echo "  [WARN] $*" >&2; }
error() { echo "  [ERROR] $*" >&2; }
step()  { echo "" >&2; echo "-> $*" >&2; }

usage() {
    echo "Usage: bash scripts/create-worktree.sh <repo> <branch-name> [OPTIONS]"
    echo ""
    echo "Arguments:"
    echo "  <repo>         Repository name"
    echo "  <branch-name>  Branch name to create"
    echo ""
    echo "Options:"
    echo "  --base REF     Base ref to branch from (default: project's default branch)"
    echo "  --no-install   Skip dependency installation"
    echo "  --dry-run      Show what would be done without executing"
    echo "  --help         Show this help message"
    echo ""
    echo "Available repos: $AVAILABLE_REPOS"
    exit 2
}

# --- Parse arguments ---
REPO=""
BRANCH=""
BASE_REF=""
NO_INSTALL=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --base)     BASE_REF="$2"; shift 2 ;;
        --no-install) NO_INSTALL=true; shift ;;
        --dry-run)  DRY_RUN=true; shift ;;
        --help|-h)  usage ;;
        -*)         error "Unknown option: $1"; usage ;;
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

# --- Validate repo ---
REGISTRY_ENTRY=$(get_registry "$REPO" 2>/dev/null) || true
if [[ -z "$REGISTRY_ENTRY" ]]; then
    error "Unknown repo: $REPO"
    echo "Available repos: $AVAILABLE_REPOS" >&2
    exit 2
fi

# --- Parse registry entry ---
IFS='|' read -r DEFAULT_BRANCH HAS_SUBMODULES INSTALL_CMD NEEDS_BUILD_INFO NEEDS_ENV_COPY <<< "$REGISTRY_ENTRY"
BASE_REF="${BASE_REF:-$DEFAULT_BRANCH}"

# --- Compute directory name ---
# feature/issue-42-add-endpoint -> feature-issue-42-add-endpoint
BRANCH_DIR_NAME="${BRANCH//\//-}"
DIR_NAME="${REPO}--${BRANCH_DIR_NAME}"
WORKTREE_PATH="$WORKTREE_DIR/$DIR_NAME"
MASTER_PATH="$MASTER_DIR/$REPO"

# --- Validate master repo exists ---
if [[ ! -d "$MASTER_PATH/.git" && ! -f "$MASTER_PATH/.git" ]]; then
    error "Master repo not found: $MASTER_PATH"
    exit 1
fi

# --- Dry run output ---
if [[ "$DRY_RUN" == true ]]; then
    echo "{"
    echo "  \"repo\": \"$REPO\","
    echo "  \"branch\": \"$BRANCH\","
    echo "  \"base\": \"$BASE_REF\","
    echo "  \"default_branch\": \"$DEFAULT_BRANCH\","
    echo "  \"worktree_path\": \"$WORKTREE_PATH\","
    echo "  \"master_path\": \"$MASTER_PATH\","
    echo "  \"has_submodules\": \"$HAS_SUBMODULES\","
    echo "  \"install_cmd\": \"$INSTALL_CMD\","
    echo "  \"needs_build_info\": \"$NEEDS_BUILD_INFO\","
    echo "  \"needs_env_copy\": \"$NEEDS_ENV_COPY\","
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
cd "$MASTER_PATH"
git fetch origin

# --- Step 2: Create branch and worktree ---
step "Step 2/6: Creating worktree at $WORKTREE_PATH"
git worktree add -b "$BRANCH" "$WORKTREE_PATH" "origin/$BASE_REF"
cd "$WORKTREE_PATH"
info "Created worktree and branch '$BRANCH' from origin/$BASE_REF"

# --- Step 3: Initialize submodules ---
if [[ "$HAS_SUBMODULES" == "yes" ]]; then
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
if [[ "$NEEDS_BUILD_INFO" == "yes" ]]; then
    step "Step 4/6: Generating build artifacts"
    mkdir -p private/build_info
    git rev-parse --short HEAD > private/build_info/head
    date +%s000 > private/build_info/time
    info "Created private/build_info/head and time"

    # bluehive (main app) also needs packages file
    if [[ "$REPO" == "bluehive" && "$HAS_SUBMODULES" == "yes" ]]; then
        git submodule foreach -q 'echo "$name $sha1"' > private/build_info/packages
        info "Created private/build_info/packages"
    fi
else
    step "Step 4/6: No build artifacts needed — skipping"
fi

# --- Step 5: Copy developer-specific config ---
if [[ "$NEEDS_ENV_COPY" == "yes" ]]; then
    step "Step 5/6: Copying developer config files"
    if [[ -f "$MASTER_PATH/.env" ]]; then
        cp "$MASTER_PATH/.env" "$WORKTREE_PATH/.env"
        info "Copied .env from master repo"
    else
        warn ".env not found in master repo — create manually or from .env.example"
    fi
else
    step "Step 5/6: No config copy needed — skipping"
fi

# --- Step 6: Install dependencies ---
if [[ "$NO_INSTALL" == true ]]; then
    step "Step 6/6: Skipping dependency installation (--no-install)"
else
    step "Step 6/6: Installing dependencies ($INSTALL_CMD)"
    $INSTALL_CMD
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
