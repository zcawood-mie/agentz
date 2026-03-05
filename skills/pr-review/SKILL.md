---
name: pr-review
user-invokable: false
description: 'PR review priorities, workflow, and comment drafting. Use for: PR review, code review, review priorities, review workflow, self-review, colleague review, AI-optimized code.'
---
# PR Review

## When to Use
- Reviewing a pull request (own or colleague's)
- Self-reviewing implementation before pushing
- Analyzing code changes for quality improvements
- Drafting review comments

## Review Mode Selection

Before reviewing, determine single-agent vs multi-agent approach:

### Use Multi-Agent Review (Default) When:
- **Self-reviewing** AND any of:
  - Changes touch security, auth, or payment code
  - Changes span 5+ files OR 200+ lines
  - Architectural changes (new patterns, abstractions, cross-cutting concerns)
  - Critical paths (order processing, user data, billing)
- **Reviewing colleague code** AND:
  - They explicitly request comprehensive review
  - High-risk changes in production-critical paths

### Use Single-Agent Review When:
- Simple bug fix (<3 files, obvious change)
- Typo/style/formatting changes
- Test-only changes
- Documentation updates
- Quick colleague review where code is straightforward

**If multi-agent review applies, follow the `multi-agent-review` skill for orchestration.** The priorities, workflow, and comment standards below still apply — each specialist reviewer uses them within their domain.

---

## Context Selection

Before reviewing, determine where to read the code AND whose code it is:

| Situation | Source |
|-----------|--------|
| Colleague's PR | GitHub (they own the branch) |
| Own PR, already pushed | GitHub for PR metadata + local for latest code |
| Own changes, not yet pushed | Local diff only (`git diff`) |
| Cross-repo context needed | Check workspace folders first, fall back to GitHub |

**Steps:**
1. Is there a PR on GitHub? → Fetch PR metadata (description, comments, checks)
2. Are changes pushed? → Compare local HEAD with remote to check for drift
3. No PR yet? → Review local diff only, skip GitHub entirely
4. Need context from another repo? → Check if it's in the workspace before hitting GitHub
5. **Determine review mode** → Is this your own code or a colleague's? This controls which priority list applies.

---

## Review Mode: Colleague

**Philosophy:** If the code works and isn't a hazard, it ships. Don't do their job for them.

### Priorities

| Priority | Category | What to Look For |
|----------|----------|-----------------|
| P1 | **Bugs / Correctness** | Logic errors, edge cases, race conditions, off-by-ones, missing error handling |
| P2 | **Security** | Auth gaps, data exposure, injection, unsafe inputs |
| P3 | **Comprehensibility** | Can you follow the intent? Does the behavior make sense to someone unfamiliar? |
| — | **Common Sense** | Egregiously misleading names, obvious easy optimizations, reinvented built-ins that would simplify AND improve the code simultaneously. Flag only if the fix is clear and low-effort. |

### DO NOT Flag (Colleague)
- Style or naming preferences (unless a name is actively misleading)
- Architecture choices
- Missing tests (unless change is high-risk AND untested)
- "I would have done it differently"
- AI-readability concerns
- Code reduction / DRY beyond obvious source-of-truth issues
- Performance (unless it's a clear scaling problem on real data)
- Hardcoded values (unless environment-specific and likely to break)
- Refactoring suggestions
- Alternative approaches

---

## Review Mode: Self-Review

**Philosophy:** No stone unturned. Be your own harshest critic. Code should be optimized for both human and AI audiences, with AI-readability taking slight precedence.

**Key lens:** "Can an AI reliably find, understand, and correctly edit this code?" Explicitness and predictability trump brevity and elegance.

### Priorities

| Priority | Category | What to Look For |
|----------|----------|-----------------|
| P1 | **Bugs / Security** | Logic errors, edge cases, race conditions, auth gaps, data exposure, injection |
| P2 | **Pattern Consistency** | Does this follow the same structure as similar existing code? If an AI searched for examples of this pattern, would this instance look like the others? Inconsistency is the #1 source of AI errors. |
| P3 | **Single Source of Truth** | Is any logic duplicated where drift could occur? Would an AI updating one copy miss the other? Flag duplication only when copies could meaningfully diverge. |
| P4 | **Naming Clarity** | Would an AI (or new human) understand intent from names alone? A function called `process()` forces reading the body; `calculateOrderTotals()` doesn't. Follow `code-style-rules` fully. |
| P5 | **Type Completeness** | Are boundary types explicit? Any `any` or untyped parameters that could be narrowed? Explicit types are contracts AI can read without tracing implementations. |
| P6 | **Searchability / Greppability** | Can this code be found via text search? No dynamic keys, magic re-exports, deeply aliased imports. Prefer explicit imports, literal strings, direct references. |
| P7 | **Locality / Colocation** | Does an AI need to read 6 files to understand this edit? Is related code colocated? A 50-line file with everything relevant beats a 15-line file importing from 5 others. |
| P8 | **Accidental Inclusions** | Debug code, console logs, commented-out blocks, TODO remnants |
| P9 | **Hardcoded Environment Values** | URLs, connection strings, feature flags that should be configurable. Single-use constants like `timeout: 5000` are fine — they're explicit, searchable, and local. |
| P10 | **Dead Code** | Unused variables, imports, unreachable branches. Not "could be shorter" — just "is this actually used?" |

### DO NOT Flag (Self-Review)
- Function length (unless it mixes unrelated responsibilities)
- Nesting depth (unless control flow is genuinely unclear)
- "Could use existing utility X" (unless it's a source-of-truth risk)
- "Could be simplified to fewer lines" (unless current version is confusing)
- Missing docs on internal/private functions (only flag for exported APIs and module boundaries)
- Alternative approaches / "could be more elegant"

---

## Workflow

### Phase 1: Determine Context and Mode
1. Parse user input for PR identifier (URL, repo#number, "current", description) or local diff intent
2. If PR exists: fetch PR title, description, metadata, and full diff from GitHub
3. If no PR: get local diff with `git diff` or `git diff main...HEAD`
4. Fetch linked issues/tickets if referenced
5. **Select review mode:** Colleague or Self-Review based on whose code it is

### Phase 2: Analyze
Go through the diff using the priority list for the active mode. For each finding, note:
- Priority category
- Specific file and line(s)
- What the issue is
- Suggested improvement

### Phase 3: Iterative Presentation
Present ONE finding at a time, highest priority first.

Format:
```
## [Priority Category]

**File:** [path/to/file.js#L45-L52]
**Current Code:** [snippet]
**Observation:** [what you noticed]
**Suggestion:** [specific recommendation]
**Rationale:** [why this improves the code]
```

After presenting, use `ask_questions` for the response (Agree / Skip / Edit / Question). Do NOT put finding details in the question tool.

### Phase 4: Draft Comments
Group approved findings into line-specific, file-specific, and general comments.

**Comment style:**
- Direct and specific
- Lead with the suggestion
- Use code snippets when helpful
- Frame as suggestions, not demands
- No fluff ("Great work!", "Just a thought...")
- Combine general feedback into ONE comment

### Phase 5: Post Comments (only for GitHub PRs, only with approval)
1. Present all drafted comments for user review
2. Get final confirmation before posting
3. Use GitHub review API for line comments, issue comment API for general
4. Confirm what was posted

## Self-Review Fix Mode

When an Implementation agent self-reviews its own changes:
- **Switch mindset** — critique the code as if you didn't write it
- **Use the full self-review priority list** — no shortcuts
- **Check for accidental inclusions** — debug code, console logs, commented-out blocks
- **Skip Phase 5** — just fix the issues directly instead of drafting comments

### Fix-One-Commit-One Cycle
Follow the `git-commits` skill — one fix per commit, commit immediately, then move to the next issue. After all fixes, re-review the full diff.

## Rules

**ALWAYS:**
- Determine context source AND review mode before starting
- Present findings one at a time, highest priority first
- Get explicit approval before posting any comment to GitHub
- In self-review fix mode: fix one issue, commit, then move to the next

**NEVER:**
- Auto-post comments without approval
- Apply self-review standards to colleague code
- Dump all findings at once
- Post multiple general comments
