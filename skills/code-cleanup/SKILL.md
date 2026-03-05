---
name: code-cleanup
user-invokable: false
description: 'Code cleanup and refinement for committed changes. Use for: cleanup, polish, code style, clean code, diff review, PR polish, pre-review cleanup, pattern consistency.'
---
# Code Cleanup

## When to Use
- Polishing committed changes before opening a PR
- Reviewing a branch's diff for unnecessary changes, naming issues, or style problems
- Minimizing diff size by removing unrelated changes

This skill is always applied to your own code (pre-PR polish). The self-review priorities from `pr-review` apply here.

## Scope

**Only review code that was ADDED or CHANGED in the diff.** Do not suggest changes to existing code that wasn't touched in this branch.

Focus on these areas in order:

### 1. Diff Minimization (Check First)
Before any other cleanup, look for ways to reduce diff size:
- Unnecessary whitespace changes to lines that didn't need to change
- Moved code blocks without modification (use `git diff --color-moved` to detect)
- Reordered imports/exports without clear organizational benefit
- Style-only changes to untouched code

Goal: every line in the diff should exist for a reason tied to the feature/fix.

### 2. Pattern Consistency
- Does the new/changed code follow the same structure as existing similar code?
- If an AI searched for examples of this pattern, would this instance match the others?
- Are naming conventions consistent with the surrounding codebase?

### 3. Naming Clarity
Follow the `code-style-rules` skill for naming conventions. Focus on whether names communicate intent — would an AI or new developer understand purpose from the name alone?

### 4. Linting
- Run the project's linter on changed files
- Fix lint errors/warnings in new/changed code only
- Do not fix pre-existing lint issues in unchanged code

### 5. Type Completeness
- Are new function signatures fully typed at boundaries?
- Any `any` types that could be narrowed?
- Are exported APIs and interfaces explicitly typed?
- Internal/private function types are nice-to-have, not required

### 6. Searchability
- Can this code be found via text search?
- No dynamic key construction, magic re-exports, or deeply aliased imports
- Prefer explicit imports, literal strings, direct references

## Diff Minimization Questions

Follow the `git-diffs` skill for diff commands and minimization.

- Does every changed line contribute to the feature/fix?
- Would this change make sense to a reviewer who only knows the ticket?
- If code was moved, is the new location meaningfully better?
- Could any of these changes be a separate PR?

## Workflow

### Phase 1: Gather Context

1. Get the committed diff — follow the `git-diffs` skill for commands.

2. Check for diff bloat FIRST using `git diff --color-moved`

3. Run the project's linter on changed files

4. Analyze changed code against the checks above

### Phase 2: Present One Issue at a Time

Present ONLY one issue, starting with diff minimization issues first:

1. Explain the issue with specific file/line references
2. Show the current code
3. Propose a specific fix
4. Wait for the user to approve, skip, or modify

Example format:
```
## Cleanup: [Category]

**Issue:** [Description]
**Location:** [file#lines]
**Current Code:** [snippet]
**Proposed Fix:** [specific change]
**How to proceed?** (approve / skip / modify)
```

### Phase 3: Implement or Skip

- **Approved:** Make the change, then find the next issue
- **Skipped:** Move to the next issue
- **Modified:** Adjust approach per feedback, then implement

### Phase 4: Iterate

Repeat Phase 2-3 until all cleanup is done or user is satisfied.

### Phase 5: Complete

1. Summarize what was cleaned up
2. Report final diff stats (`git diff --stat`)
3. Confirm linting passes

## Rules

**ALWAYS:**
- Check for diff bloat BEFORE other cleanup
- Present only ONE issue at a time
- Wait for user response before proceeding
- Re-run linter after making changes

**NEVER:**
- Remove comments without showing them to the user first
- Make changes without user approval
- Flag function length or nesting depth as standalone issues
- Flag missing JSDoc on internal/private functions
