---
name: debugging
description: 'Bug investigation methodology and root cause analysis. Use for: debug, bug, fix, broken, regression, error, root cause, investigate bug, troubleshoot.'
user-invokable: false
---
# Debugging

## When to Use
- Investigating a bug or unexpected behavior
- Tracing a regression
- Diagnosing an error message or failure
- Any "why is X broken?" question

## Investigation Mode Selection

Before investigating, determine single-agent vs multi-agent approach:

### Use Multi-Agent Debugging (Default) When:
- Root cause is unclear after initial investigation
- Bug is intermittent or timing-dependent
- Symptoms could have multiple explanations (data vs logic vs race condition)
- Bug spans multiple domains (UI + API + database)
- Production-only bugs that can't be reproduced locally
- Regressions where "it used to work"

### Use Single-Agent Investigation When:
- Clear error message pointing to specific code
- Obvious typo or logic error
- Narrowly scoped issue (definitely data / definitely logic / definitely config)
- Stack trace leads directly to the problem

**If multi-agent debugging applies, follow the `multi-agent-debugging` skill for orchestration.** The investigation methodology below still applies — each specialist investigator uses it within their hypothesis domain.

---

## Methodology

### Phase 1: Characterize

Before touching code, establish:

1. **Symptoms** — what exactly is wrong (error message, wrong behavior, visual glitch)
2. **Reproduction** — steps to reproduce, frequency (always, intermittent, specific conditions)
3. **Scope** — one user, all users, one environment, all environments
4. **Timeline** — when it started, what changed recently (deploys, config, data)

### Phase 2: Form a Hypothesis

Based on the symptoms, pick the most likely category:

| Category | Signals |
|----------|---------|
| **Data** | Wrong values displayed, missing records, inconsistent state |
| **Logic** | Wrong behavior on specific inputs, unhandled edge cases, off-by-ones |
| **Timing** | Intermittent failures, works-on-refresh, race conditions |
| **Config** | Works locally / fails deployed, post-deploy regression, version mismatch |

Commit to one hypothesis at a time. Investigate it thoroughly before moving to the next.

### Phase 3: Trace the Code Path

1. **Start at the symptom** — find the exact code that produces the wrong output
2. **Work backwards** — trace the data/control flow toward the source
3. **Find the divergence point** — where does actual behavior split from expected behavior?
4. **Check boundaries** — function inputs/outputs, API request/response, database read/write

Use the `research` skill methodology for codebase exploration (find examples, trace data flow, identify registration points).

### Phase 4: Verify the Root Cause

Before declaring a root cause, confirm:

- **Explains all symptoms** — not just some of them
- **Explains the timeline** — why it started when it did
- **Explains the scope** — why it affects what it affects
- **A fix is obvious** — if the root cause is correct, the fix should follow naturally

If verification fails, return to Phase 2 with the next hypothesis.

### Phase 5: Report or Fix

**If you have edit access (Implementation agent):**
- Fix the root cause directly
- Verify the fix resolves the symptoms
- Check for similar patterns elsewhere that may have the same bug

**If you are read-only (Research agent):**
- Report the root cause with file:line references
- Describe the fix direction (what needs to change, not full implementation)
- Flag related code that may have the same issue

## Rules

**ALWAYS:**
- Characterize before investigating — don't jump to code without understanding symptoms
- One hypothesis at a time — scattered investigation finds nothing
- Verify root cause explains ALL symptoms — partial explanations are wrong explanations
- Include file:line references in findings

**NEVER:**
- Skip straight to "try random fixes" — understand before changing
- Investigate for more than two hypothesis cycles in single-agent mode — escalate to multi-agent debugging
- Assume the first suspicious code you find is the root cause — verify it explains the symptoms
