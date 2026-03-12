---
name: pr-workflow
user-invokable: false
description: 'Pull request lifecycle: opening, reviewing comments, responding, fixing feedback. Use for: open PR, create PR, PR comments, review comments, respond to reviewers, fix PR feedback, PR feedback priority, pull request template.'
---
# PR Workflow

## When to Use
- Opening a new pull request
- Responding to PR review comments
- Addressing PR feedback
- Understanding comment placement and tone

## Context Awareness

This skill works with both local and remote content:
- **Local workspace** is the primary source for code context, especially for cross-repo work
- **GitHub API** is used for PR metadata, comments, reviews, and posting
- **Check workspace first** before hitting GitHub for file contents — repos may be in the workspace
- **Compare local vs. remote** when reviewing pushed PRs — note any drift between the two

---

## Opening a PR

### Issue Discovery (before creating)
1. **Search the organization** — not just the current repo: `org:owner keyword1 keyword2 is:issue`
2. **Read top candidates** — compare against branch's actual changes
3. **Verify the match** — confirm same features, files, scope
4. **If uncertain, ask the user** — don't guess

### PR Body Format
```markdown
## Related PRs
- [ ] owner/repo#[pr_number]
- [ ] owner/repo#[pr_number]

## Related Issues
Relates to owner/repo#[issue_number]

## Summary
[1-2 sentences describing the goal/purpose — why this change exists, not what files changed]
```

**Rules:**
- **Related PRs goes FIRST** — it's referenced repeatedly during review and merge
- The Related PRs list includes the PR itself — every related PR has an identical list
- Always search for related issues across the **entire organization**
- Use `Relates to` — NEVER `Closes`, `Fixes`, `Resolves` (they auto-close)
- Omit Related Issues section if no issue found
- Omit Related PRs section if only one PR
- **NEVER list changed files** — GitHub's Files tab already shows this

### Multi-Repo PRs

When a feature spans multiple repos, create all PRs first, then backfill Related PRs:

1. **Create each PR** with Summary and Related Issues filled in, Related PRs empty
2. **Collect all PR numbers** from the created PRs
3. **Update every PR body** to add the full Related PRs list (including itself)

After backfill, every PR in the group should have an identical Related PRs section.

---

## Comment Style

### DO:
- "Consider using X instead of Y here"
- "This could be simplified to: [code]"
- "Looks like lines 45-50 might be removable since..."
- "Question: Is this intended to replace X or supplement it?"

### DON'T:
- "You should..." (too prescriptive)
- "Why didn't you..." (accusatory)
- "Great job but..." (false positivity)
- "Nitpick:" (if it's a nitpick, don't comment)
- "I think maybe possibly..." (be direct)

### Comment Placement
- **Line-specific**: Reference the START of relevant code block
- **File-level**: Place at top of file's diff
- **General**: Combine ALL non-line-specific feedback into ONE comment

---

## Responding to Reviewers

### Templates
- Fix implemented: "Fixed in [latest commit]. [brief explanation]"
- Acknowledged: "Good catch! Updated to [description]."
- Question answered: "[Direct answer]"
- Won't fix: "Keeping as-is because [reason]."

### Guidelines
- Be concise and professional
- Reference specific commits or code
- Never just "Done" — add brief context
- Never be defensive or argumentative

---

## Fixing PR Feedback

### Feedback Priority (address in this order)

1. **Architectural / Design** — fundamental design, code organization, data flow
2. **Security** — vulnerabilities, auth issues, data exposure
3. **Bugs / Correctness** — logic errors, edge cases, race conditions
4. **Performance** — inefficiency, unnecessary queries, memory leaks
5. **Code Quality** — duplication, missing error handling, inconsistent patterns
6. **Testing** — missing tests, coverage, test quality
7. **Documentation** — missing/incorrect docs, comments
8. **Style / Nitpicks** — formatting, naming suggestions
9. **Questions / Clarifications** — reviewer questions, discussion points

### Workflow
1. Fetch PR reviews and comments from GitHub
2. Categorize each item by priority
3. Present ONE item at a time (highest priority first):
   ```
   ## Priority [N]: [Category]
   **Reviewer:** @username
   **Comment:** > [quoted]
   **Location:** [file#lines]
   **Proposed Fix:** [specific solution]
   ```
4. Each fix = one separate commit (follow `git-commits` skill for commit format)
5. Offer to respond to reviewer after each fix
6. Iterate until all items addressed

### Response after fix
- "Fixed in [latest commit]. [brief explanation]"
- "Good catch! Updated to [description]."
- "Keeping as-is because [reason]."

---

## GitHub API Reference

### Fetching PR Content
```
mcp_github_pull_request_read(owner, repo, pullNumber)
mcp_github_get_file_contents(owner, repo, path, branch)
```

### Creating Reviews
```
mcp_github_pull_request_review_write(owner, repo, method='create', pullNumber)
mcp_github_add_comment_to_pending_review(owner, repo, pullNumber, path, line, body)
mcp_github_pull_request_review_write(owner, repo, method='submit_pending', pullNumber, event='COMMENT')
```

### General Comments
```
mcp_github_add_issue_comment(owner, repo, issue_number, body)
```

---

## Rules

**ALWAYS:**
- Search entire org for related issues before opening a PR
- Use `Relates to` for issue linking
- Present feedback items one at a time, highest priority first
- Commit each fix separately
- Get user approval before posting any comment

**NEVER:**
- Use `Closes`/`Fixes`/`Resolves` for issue linking
- Dump all feedback at once
- Post comments without user approval
- Bundle multiple fixes into one commit
- Skip security or architectural feedback
