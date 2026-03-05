---
name: multi-agent-review
description: 'Multi-perspective code review orchestration. Use for: collaborative review, multi-agent review, parallel review, comprehensive review, review orchestration.'
user-invokable: false
---
# Multi-Agent Review

## When to Use
- User requests a collaborative or multi-perspective review
- A PR or diff warrants comprehensive coverage across multiple domains
- Self-review where thoroughness matters more than speed

## How It Works

Multiple specialist reviewers — each with distinct values — review the same code in parallel. Their findings are merged into a single unified review that covers more ground than any single reviewer could.

The specialist reviewers:

| Agent | Domain | Looks For |
|-------|--------|-----------|
| SecurityReviewer | Security | Auth gaps, injection, data exposure, secrets, XSS/CSRF |
| ArchitectureReviewer | Architecture | Pattern violations, boundary crossings, coupling, dependency direction |
| PerformanceReviewer | Performance | N+1 queries, blocking I/O, memory leaks, scaling risks |
| MaintainabilityReviewer | Maintainability | Naming, dead code, AI-readability, searchability, source-of-truth drift |

## Orchestration Workflow

### Phase 1: Gather the Diff

Determine what to review and collect the code:

| Source | How to Get It |
|--------|--------------|
| GitHub PR | Dispatch to GitHubOps to fetch PR metadata and diff |
| Local changes (pushed) | `git diff master...HEAD` or equivalent |
| Local changes (unpushed) | `git diff` for staged/unstaged |

Collect:
- The full diff (file paths + changed lines)
- PR description and linked issues (if applicable)
- List of changed files with context on what each file does

### Phase 2: Dispatch Specialists (Parallel)

Craft a prompt for each reviewer with:

1. **The diff content** — paste the full diff or relevant sections
2. **File context** — for each changed file, include enough surrounding code for the reviewer to understand the change in context
3. **Scope contract** — "Review only the changed code and its immediate context. Report findings only in your domain."
4. **Return format specification:**

```
Return your findings as a structured list. For each finding:
- **File:** path/to/file.ext#L<line>
- **Severity:** critical / high / medium / low
- **Category:** [domain-specific category]
- **Finding:** [what you found]
- **Suggestion:** [concrete remediation]

If you find no issues in your domain, return: "Status: clean — no [domain] issues found."
```

5. **PR context** — include the PR description so reviewers understand intent

Dispatch all four reviewers in the same tool-call block so they run concurrently.

### Phase 3: Merge Results

When all reviewers return:

1. **Collect** all findings into a single list
2. **Deduplicate** — if two reviewers flag the same line for overlapping reasons (e.g., hardcoded URL flagged by both Security and Maintainability), merge into one finding noting both perspectives
3. **Sort by severity** — critical > high > medium > low, then by file order in the diff
4. **Tag each finding** with which reviewer(s) identified it

### Phase 4: Present Unified Review

Present the merged review organized by severity:

```
## Critical
[findings]

## High
[findings]

## Medium
[findings]

## Low
[findings]

---
**Summary:** X findings across Y files (N critical, N high, N medium, N low)
**Reviewers:** SecurityReviewer, ArchitectureReviewer, PerformanceReviewer, MaintainabilityReviewer
```

Each finding includes:
- File and line reference (as a link)
- Which reviewer(s) flagged it
- The observation and suggested remediation

### Phase 5: Act on Results

Depending on the review mode:

| Mode | Action |
|------|--------|
| Self-review (pre-push) | Fix issues directly, one commit per fix |
| Colleague review | Present findings iteratively, draft GitHub comments for approved ones |
| PR already on GitHub | Draft a GitHub review with line comments, post after user approval |

## Selective Review

Not every review needs all four specialists. The orchestrator should select reviewers based on the nature of the changes:

| Change Type | Recommended Reviewers |
|-------------|----------------------|
| Auth/API changes | Security, Architecture |
| Database/query changes | Performance, Security |
| UI/template changes | Maintainability, Security (XSS) |
| Refactoring | Architecture, Maintainability |
| New feature (full stack) | All four |
| Config/environment | Security, Maintainability |

## Rules

**ALWAYS:**
- Include the full diff in each reviewer's prompt — they have no shared context
- Dispatch reviewers in parallel — sequential dispatch wastes time for no benefit
- Deduplicate findings before presenting — redundant findings waste the reader's attention

**NEVER:**
- Tell reviewers what to find — they bring their own values; your job is to give them the code
- Skip a reviewer because "the change is small" — small changes can have outsized security or architectural impact
- Merge findings that are genuinely distinct even if they're on the same line — a security issue and an architecture issue on the same line are two findings
