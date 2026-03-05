---
name: Parallel Execution
description: User preference for parallelism, concurrency mechanics, and merge verification
applyTo: '**'
---
# Parallel Execution

**User preference: Parallelize wherever possible.**

When facing multi-step work where steps are independent, dispatch them concurrently. Sequential execution is only acceptable when:
- Step B requires Step A's output (data dependency)
- Steps modify the same file (conflict)
- The work is trivial (~5 lines, faster to do inline)

## Concurrency Mechanics

- Place independent `runSubagent` calls in the **same tool-call block** — this makes them run concurrently
- Tasks that modify the same file must be sequential
- Trivial work (~5 lines or less) can be done inline without dispatch

## Merge Point Verification

**Mandatory after every parallel dispatch returns:**

1. **Completeness** — did every worker complete its full request? Any flagged ambiguities?
2. **Integration** — do the pieces fit together? (imports align, types match, APIs compatible)
3. **Conflicts** — overlapping edits, naming collisions, duplicate exports?
4. **Gaps** — fix inline (<10 lines), re-dispatch to the same specialist, dispatch to a new specialist, or note as out-of-scope
5. **Build** — run type checker / tests on changed files if available
