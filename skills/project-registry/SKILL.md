---
name: project-registry
user-invokable: false
description: 'Project inventory and per-project configuration. Use for: project list, default branch, submodules, install command, build artifacts, dev config, workspace layout, project lookup.'
---
# Project Registry

Domain knowledge about all projects in the workspace. All master repo paths follow the pattern `~/bhDev/masterRepos/<project>`.

## Project Table

| Project | Default Branch | Has Submodules | Install Cmd | Needs Build Artifacts | Needs Dev Config Copy | Dev Stash Needed |
|---------|---------------|----------------|-------------|----------------------|----------------------|-----------------|
| `bluehive` | `master` | Yes | `meteor npm install` | Yes (`build_info/` + `packages`) | No | Yes |
| `bluehive-ai` | `main` | No | `meteor npm install` | No | No | No |
| `bluehive-api` | `main` | No | `pnpm install` | No | Yes (`.env`) | No |
| `bluehive-employer` | `master` | Yes | `meteor npm install` | Yes (`build_info/`) | No (configs tracked) | Yes |
| `bluehive-opsdesk` | `main` | No | `npm install` | No | No | No |
| `bluehive-provider` | `master` | Yes | `meteor npm install` | Yes (`build_info/`) | No | Yes |
| `bluehive-ui` | `master` | No | `npm install` | No | No | No |
| `waggleline` | `main` | No | `npm install` | No | No | No |

**Has Submodules** means the project has `switch-branches.sh` and `update-packages.sh` scripts in its root.

**Dev Stash Needed** means the project requires a developer configuration stash to be applied after reset (contains login credentials, local config, etc.).

## Per-Project Setup Details

After creating a worktree and initializing submodules, some projects need additional developer-specific files that are **gitignored** and won't come with the worktree.

### `bluehive` (Meteor)
- **Build artifacts**: Generate `private/build_info/head`, `time`, and `packages`:
  ```bash
  mkdir -p private/build_info
  git rev-parse --short HEAD > private/build_info/head
  date +%s000 > private/build_info/time
  git submodule foreach -q 'echo "$name $sha1"' > private/build_info/packages
  ```
- **Tracked configs**: `.env`, `.npmrc`, `settings.json` — come with the worktree automatically

### `bluehive-ai` (Meteor + Docker)
- **No special setup needed** — `.env` and configs are tracked

### `bluehive-api` (Node/pnpm)
- **Must create `.env`**: Copy from master repo or create from `.env.example`
  ```bash
  cp ~/bhDev/masterRepos/bluehive-api/.env ~/bhDev/worktrees/<worktree-dir>/.env
  ```
  The `.env` contains MongoDB URI, RingCentral credentials, fax webhook config, and encryption keys. The `.env.example` is tracked and shows the required variables, but the actual `.env` with secrets is gitignored.

### `bluehive-employer` (Meteor)
- **Build artifacts**: Generate `private/build_info/head` and `time`:
  ```bash
  mkdir -p private/build_info
  git rev-parse --short HEAD > private/build_info/head
  date +%s000 > private/build_info/time
  ```
- **Tracked configs**: `.env`, `.npmrc`, `settings.json`, `settings.local.json` — all tracked, come automatically

### `bluehive-opsdesk` (Node)
- **No special setup needed**

### `bluehive-provider` (Meteor)
- **Build artifacts**: Generate `private/build_info/head` and `time`:
  ```bash
  mkdir -p private/build_info
  git rev-parse --short HEAD > private/build_info/head
  date +%s000 > private/build_info/time
  ```
- **Tracked configs**: `.npmrc` — tracked, comes automatically
- **Optional**: If `cypress.env.json` exists in master and tests are needed, copy it manually

### `bluehive-ui` (Node)
- **No special setup needed**

### `waggleline` (Meteor)
- **No special setup needed** — no local config files exist in master currently

## Test Commands

### `bluehive-api` (Node test runner)

**Template:**
```bash
cd ~/bhDev/worktrees/bluehive-api--<branch> && MONGODB_DATABASE=bluehive_test_$(date +%s)_$RANDOM NODE_ENV=test node --test --test-force-exit --test-concurrency=20 --experimental-test-module-mocks --import tsx --import ./test/setup-mongo-env.ts test/<specific-file>.test.ts
```

Or use the skill script:
```bash
cd ~/bhDev/worktrees/bluehive-api--<branch> && ~/.agents/skills/project-registry/scripts/run-api-test.sh test/<specific-file>.test.ts
```

**Rules:**
- **ALWAYS** set `MONGODB_DATABASE` to a unique test database name (e.g. `bluehive_test_$(date +%s)_$RANDOM`). All bluehive projects share the same local MongoDB database. Without this override, tests will `deleteMany({})` collections in the shared development database, destroying real data (e.g. brands, employees).
- **ALWAYS** target individual test files (e.g. `test/deals.test.ts`, `test/search.test.ts`)
- **NEVER** use wildcards (`test/*.test.ts`) — run only the file(s) relevant to the current change
- **NEVER** run tests without `MONGODB_DATABASE` set to a test-specific name
- If multiple test files are relevant, list them explicitly: `test/foo.test.ts test/bar.test.ts`
- The flags `--test-force-exit --test-concurrency=20 --experimental-test-module-mocks` are required
- The imports `--import tsx --import ./test/setup-mongo-env.ts` are required (sets up the test MongoDB)
- `NODE_ENV=test` is required

### Test Database Isolation

All bluehive projects (`bluehive-employer`, `bluehive-provider`, `bluehive-api`, etc.) share a single MongoDB database locally (`bluehive_zcawood`). Many bluehive-api test files use `mockMongo: false` and perform destructive operations like `collection.deleteMany({})` against real MongoDB — these will wipe production data if pointed at the shared database.

**Prevention:**
- package.json test scripts include `MONGODB_DATABASE=bluehive-test` via `cross-env`
- When running tests manually (outside `pnpm test`), always prepend `MONGODB_DATABASE=bluehive_test_<unique>` to the command
- The `run-api-test.sh` script handles this automatically

## Available Scripts

### `scripts/run-api-test.sh`

Run bluehive-api tests with an automatically isolated database. Generates a unique `MONGODB_DATABASE` name per invocation.

**Usage:**
```bash
cd ~/bhDev/worktrees/bluehive-api--<branch>
~/.agents/skills/project-registry/scripts/run-api-test.sh test/brands.test.ts
~/.agents/skills/project-registry/scripts/run-api-test.sh test/brands.test.ts test/integrations.test.ts
```

**Exit codes:**
- `0` — all tests passed
- `1` — test failure(s)
- `2` — usage error (no args, invalid file)

## Build Artifact Context

Some Meteor projects require generated files that are gitignored but needed at runtime. These are normally created by the start script (`bin/start.js`) but must exist before the app can boot. The files are read by the server at startup via `Assets.getTextAsync()`. Without them, the app crashes with `Error: Unknown asset: build_info/head`.
