---
name: pr-dashboard
description: 'Fetch all open PRs for a GitHub user, classify by action needed vs waiting on others, and render a status diagram. Use for: PR dashboard, PR status report, what PRs do I have, PR overview, review status, open pull requests, PR triage, PR health.'
---
# PR Dashboard

## When to Use
- User asks for a summary of their open PRs
- User wants to know what they need to act on vs. what they're waiting on
- User wants a visual overview of PR pipeline health
- PR triage / end-of-day review

---

## Phase 1: Brief the Workflow

Before fetching, you need enough context about the user and their team to classify PRs accurately.

**Cached context:** Check user memory (`$AGENTS_ROOT/memories/pr-dashboard.md`) for previously saved answers. If found, use them and proceed — only re-ask if something looks stale or the user requests changes. If not found, ask the questions below, then save the answers to `$AGENTS_ROOT/memories/pr-dashboard.md` for future runs.

**Key questions** (ask together, not one at a time):
1. What is your GitHub username?
2. Which GitHub org/repos should be searched? (or "all repos in org X")
3. What does your team's review pipeline look like? (e.g., "2 code reviewers then a QA reviewer", "1 reviewer, then merge", "just me self-reviewing")
4. Are there any blocking conditions before requesting review? (e.g., "CI must pass", "no unresolved Copilot comments", "linked issue required")

If the user has already answered these in the conversation, use those values (and update the cache).

> **Note:** If workflow details are unknown, default to the most common pattern and note your assumptions: "Assuming 1+ approval = ready for next stage."

---

## Phase 2: Fetch PR Data

Delegate to GitHubOps subagent. Request **all open PRs** (including drafts) authored by the user.

For EACH PR, collect:
- Title, number, URL, repo
- Draft status
- Head branch
- PR body (for linked issue extraction)
- Requested reviewers + their review states (`approved`, `changes_requested`, `commented`, `pending`)
- CI/check status (passing, failing, pending)
- Unresolved review threads — distinguish resolved vs unresolved, outdated vs current
- Mergeable state (`clean`, `dirty`, `behind`, `blocked`)
- Created date (for staleness detection)

---

## Phase 3: Classify Each PR

Apply the user's stated workflow to classify every PR. The classification has two axes:

### Axis 1: Who Needs to Act?

| Category | Condition |
|---|---|
| **Author action required** | Something blocks progress and only the author can fix it |
| **Waiting on others** | PR is in a valid intermediate state; only reviewer/CI action moves it forward |

### Axis 2: What Kind of Action / Wait?

**Author action sub-categories:**

| Sub-category | Examples |
|---|---|
| **Fix merge conflicts** | `mergeable_state: dirty` |
| **Rebase / sync** | `mergeable_state: behind` |
| **Resolve code comments** | Unresolved non-outdated review threads, `changes_requested` review |
| **Fix failing CI** | Check status is failed |
| **Add reviewers** | Non-draft PR with no reviewers assigned |
| **Address Copilot comments** | Unresolved non-outdated threads from `copilot-pull-request-reviewer[bot]` |
| **Draft still in progress** | Draft PR with open Copilot threads or other blockers worth noting |
| **Audit / consider closing** | Stale PRs (typically 2+ months old, dirty, no activity) |

**Waiting sub-categories** — derive these from the user's stated pipeline stages. Examples:
- Waiting for 1st code reviewer
- Waiting for 2nd code reviewer
- Waiting for QA sign-off
- Waiting for CI to finish
- Draft (no action expected from anyone yet)

> **Key insight:** A PR can appear in *both* columns — e.g., it needs a rebase (author action) AND once that's done it will be waiting on a reviewer. Call this out explicitly.

### Staleness Heuristic
Flag PRs created more than ~6-8 weeks ago with `dirty` state and no recent activity as stale candidates. Don't auto-close — surface them for the user to decide.

---

## Phase 4: Render the Report

Produce **two outputs**:

### A. Mermaid Diagram (via `mermaid-diagrams` skill)

Use `flowchart TD`. Structure:
```
Root node → "You Need to Act" branch + "Waiting on Others" branch
Each branch → sub-category nodes → individual PR nodes
```

Color scheme:
- **Author action nodes**: warm/red tones (`#A07060`)
- **Waiting nodes**: teal/blue tones (`#4D7A7A`)  
- **Category headers**: deeper versions of each (`#7A5050`, `#3a6060`)
- **Draft WIP nodes**: dark with blue border (`#2D3748`, border `#5C7C9A`)
- **Stale nodes**: muted gray-brown (`#4a4438`)
- **Conflict/blocker nodes**: muted coral (`#A07060`)

Keep PR node labels short: `repo #num · Short Title\nKey status line`

### B. Prioritized Text Summary

After the diagram, output a short priority table:

```
## Your Action Items (Priority Order)
| Priority | Action | PRs |
|---|---|---|
| 1 | [Highest urgency action] | [link list] |
...

## Waiting On Others
| What | Who | PRs |
|---|---|---|
| [Stage name] | [Reviewer(s)] | [link list] |
```

---

## Rules

**ALWAYS:**
- Include draft PRs — they provide pipeline visibility even when no review is expected
- Distinguish outdated review threads from current ones — outdated threads on superseded code don't block the PR
- Show count of unresolved threads, not just presence
- Note when a PR appears on both sides (needs rebase AND needs reviewer)
- Group sister PRs that belong to the same feature together in notes

**NEVER:**
- Filter out stale PRs silently — surface them even if just to confirm they should be closed
- Assume the user's workflow without asking or noting your assumption
- Flag Copilot bot overview comments (the summary at the top of a review) as unresolved — only flag actual inline suggestion/code threads
- Conflate `outdated` threads with blocking threads — outdated = code has changed, comment may no longer apply

---

## Variation: Repo-scoped or Team Dashboard

If the user wants a team dashboard instead of personal PRs:
- Change the search to `is:pr is:open repo:owner/repo` (no author filter)
- Group by author instead of action category
- Same classification logic applies per PR