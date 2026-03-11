---
name: implementation-workflow
user-invokable: false
description: 'Implementation execution cycle and discipline. Use for: implement, execute plan, coding workflow, change discipline, implementation phases.'
---
# Implementation Workflow

## When to Use
- Implementing a plan or feature
- Executing code changes from a task description
- Running the implement → test → debug cycle

## Workspace Location

**Ensure you're on a feature branch, not the default branch.** If the project uses worktrees, make sure you're in the worktree directory — see the `worktree-management` skill.

Read project paths from the `project-registry` skill's index (`/memories/project-index.md`).

## Change Discipline

**Every change must serve the plan. Nothing more, nothing less.**

Before making ANY edit, ask: "Is this required to accomplish the plan?"

**DO NOT make these unrelated changes:**
- Updating documentation or comments in code you're not otherwise modifying
- Reformatting or reorganizing code that isn't part of the feature
- "Improving" nearby code that caught your eye
- Adding JSDoc to existing functions you didn't change
- Fixing typos in unrelated files
- Reordering imports or exports for "consistency"
- Adding blank lines or adjusting whitespace in untouched sections

**The principle:** A reviewer should look at the diff and see that every changed line serves the ticket/plan.

If you notice something that should be fixed but isn't part of the plan, **note it in observations** — don't fix it.

## Workflow Phases

### Phase 1: Parse and Understand

MANDATORY: Break the plan into trackable tasks using the todo list.

Identify:
- All files, symbols, and changes required
- Which tasks can be done in parallel
- Dependencies between tasks

### Phase 2: Gather Context

Use **built-in search tools** (semantic_search, grep_search, file_search, read_file) for targeted lookups where you already know the exact file or symbol. For anything broader, delegate per the agent's delegation constraints.

**NEVER use complex shell commands for codebase exploration:**
- No `find ... -exec`, no `grep -r ... | xargs`, no multi-pipe chains
- No `awk`, `sed`, or `cut` for parsing code
- Keep terminal commands **simple and single-purpose** (e.g., `ls`, `cat`, `git status`)
- If you need to search code, use the search tools — that's what they're for

Before writing any code:
- Find existing patterns to match
- Use provided artifacts (SQL, API specs, types) directly — adapt minimally
- Note external dependencies early

### Phase 3: Execute

1. Mark todo as in-progress
2. Make code changes
3. Mark todo as completed
4. Verify changes compile/run

### Phase 4: Test and Debug (Autonomous)

Follow the `testing-workflow` skill for test methodology, project-specific test commands, and database isolation rules. Debug and fix issues autonomously before reporting back.

### Phase 5: Report Back

When complete, report:
1. Summary of what was implemented
2. Bugs found and fixed during debugging
3. Observations and suggestions for next steps
4. Out-of-scope issues noticed

## Implementation Style

- **Match existing code style** — copy indentation, naming conventions, comment style, file organization
- **Make minimal changes** — accomplish the plan's goals, nothing more
- **Use edit tools directly** — never output code blocks for the user to copy
- **Run validation** — tests or type-checking when available
- **Consistency > personal preference** — match the codebase, not your ideal

## Rules

**ALWAYS:**
- Break plan into tracked todos before starting
- Match existing codebase conventions exactly
- Debug and fix autonomously before reporting
- Note out-of-scope issues without fixing them

**NEVER:**
- Make drive-by improvements outside the plan
- Ask permission for each individual step
- Output code blocks instead of editing files
- Skip testing after implementation
- Edit files on the default branch — always work on a feature branch
