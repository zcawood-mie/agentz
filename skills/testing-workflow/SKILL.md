---
name: testing-workflow
user-invokable: false
description: 'Testing methodology — running, verifying, and reporting test results. Use for: run tests, test, unit test, integration test, automated test, manual test, test suite, QA, verify, browser test, smoke test, regression test, validate, test plan.'
---
# Testing Workflow

## When to Use
- Running automated tests (unit, integration, test suites)
- Manually testing a feature or fix
- Verifying changes on the current branch
- Running through test scenarios with browser/terminal/database tools

## Core Principle

**Show, don't tell.** Screenshots > descriptions. Console output > "no errors found." Response bodies > "the API returned success."

## Scope Determination

### If given a description:
1. Parse what functionality to test
2. Search codebase to understand the feature
3. Identify key behaviors, edge cases, and failure modes

### If no input (test current branch):
1. Run `git diff $(git merge-base HEAD master 2>/dev/null || git merge-base HEAD main)..HEAD --stat` for changed files
2. Run the full diff to understand actual changes
3. Design tests around those changes

## Test Plan

MANDATORY: Create a visible test plan using the todo list.

Structure as specific scenarios:
```
1. [Feature Area] - [Scenario] - [Expected Result]
2. [Feature Area] - [Edge Case] - [Expected Result]
3. [Feature Area] - [Error Case] - [Expected Result]
```

Categories to cover:
- **Happy path** — normal usage flows
- **Edge cases** — boundary values, empty inputs, large data
- **Error cases** — invalid inputs, missing data, failures
- **Permissions** — unauthorized access, role-based behavior
- **UI/UX** — visual correctness, responsive behavior, loading states

Present the plan before executing. Ask if the user wants to add, remove, or modify scenarios.

## Environment Check

Before testing, verify:
1. Is the app running? (`curl localhost:3000` or similar)
2. If not, start it with the project's standard command
3. Wait for startup to complete
4. Check for build errors — if the app won't start, that's the first failure

## Execution

For each scenario:

1. Mark todo as in-progress
2. **Record the action** — what you're doing and why
3. **Execute** — use the appropriate tool (terminal, Chrome DevTools, browser, database)
4. **Record the result** — what actually happened (with evidence)
5. **Record the verdict** — PASS, FAIL, or BLOCKED
6. Mark todo as completed

### Recording Format
```
### Test [N]: [Scenario Name]
**Action:** [What you did]
**Tool Used:** [Terminal / Chrome DevTools / Browser / Database]
**Command/Steps:** [Exact command or steps]
**Expected:** [What should happen]
**Actual:** [What happened]
**Evidence:** [Screenshot, console output, response body]
**Verdict:** PASS / FAIL / BLOCKED
```

## Failure Investigation

For each FAIL:
1. **Reproduce** — confirm it's consistent
2. **Isolate** — narrow to UI, API, database, or logic
3. **Trace** — read relevant code to find root cause
4. **Document:**
```
### Failure Investigation: [Test N]
**Symptom:** [What the user sees]
**Root Cause:** [Why — with file:line references]
**Impact:** [Severity and scope]
**Suggested Fix:** [Specific change needed]
**Reproduction Steps:** [Numbered steps]
```

Do NOT fix code during testing. Report only.

## Final Report

```markdown
## Manual Test Report

### Summary
- **Feature Tested:** [Description]
- **Total Scenarios:** [N]
- **Passed:** [N] | **Failed:** [N] | **Blocked:** [N]

### Test Results
| # | Scenario | Verdict | Notes |
|---|----------|---------|-------|
| 1 | [Name]   | PASS    |       |

### Issues Found
#### Issue 1: [Title]
**Severity:** Critical / High / Medium / Low
**Root Cause:** [file:line references]
**Suggested Fix:** [Specific change]

### Observations
- [Fragile areas, performance concerns, UX issues]

### Recommendations
- [Priority-ordered fixes and additional coverage]
```

## Per-Project Test Configuration

Test commands and database isolation rules live in per-project memory files at `$AGENTS_ROOT/memories/projects/<key>/test.md`. Read the current project's test config before running any tests:
```bash
$AGENTS_ROOT/skills/memory-access/scripts/read-memory.sh projects/<project>/test
```

If the test memory file doesn't exist, the project either doesn't have automated tests or hasn't been configured yet. Ask the user.

## Project Test Commands

Each project's `test.md` memory contains a **command template** — the exact command to run with placeholder arguments. The agent reads the template, substitutes the specific test file paths, and runs it directly. No wrapper scripts needed — the memory is the documentation and the template in one.

## Testing Tools

| Category | Tools | Use For |
|----------|-------|---------|
| Terminal | Commands, curl, logs | API endpoints, server state, process checks |
| Chrome DevTools | Screenshots, console, network, DOM | UI state, JS errors, requests, element inspection |
| Browser | Navigate, click, fill forms | User workflow simulation |
| Database | MCP queries (when available) | Data integrity, business rule validation |

## Rules

**ALWAYS:**
- Verify the app is running before testing
- Create and present test plan before executing
- Investigate failures to root cause
- Use todo list for progress visibility
- When running tests that share a database with other projects, set `MONGODB_DATABASE` to a unique test database name — shared databases mean destructive test operations (`deleteMany`, etc.) will destroy real data without isolation (read the project's `$AGENTS_ROOT/memories/projects/<key>/test.md` for the template command and test scripts)

**NEVER:**
- Edit, create, or delete source files
- Skip recording a test result
- Assume something works without verifying
- Run tests against a shared database without `MONGODB_DATABASE` set to a test-specific name
