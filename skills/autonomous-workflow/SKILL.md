---
name: autonomous-workflow
user-invokable: false
description: 'Full ticket-to-PR autonomous workflow. Use for: ticket, autonomous, end-to-end, feature implementation, ticket URL, full workflow.'
---
# Autonomous Workflow

## When to Use
- Given a ticket/issue URL to implement autonomously
- Running the full research → plan → implement → PR pipeline

## Pipeline

### Phase 1: Ticket Ingestion
1. Delegate to GitHubOps subagent to fetch the issue/ticket content from the provided URL
2. Extract: title, description, acceptance criteria, labels, linked issues
3. Determine the target repository and default branch

### Phase 2: Research
You need enough context to plan. Available research specialists:
- **CodeExplorer**: codebase patterns, data flow, registration points, existing implementations
- **DocFetcher**: library APIs relevant to the feature
- **WebSearcher**: error messages, framework-specific guidance, unfamiliar concepts
- **GitHubOps**: linked issues, related PRs, prior attempts

Provide each specialist with the ticket context (title, description, acceptance criteria) and its specific question.

After research completes, synthesize findings into a unified picture. Identify gaps and re-investigate if any question wasn't fully answered.

### Phase 3: Plan
Follow the `planning` skill methodology:
1. Break the ticket into implementable steps
2. Create a diagram showing the implementation flow
3. Identify parallelizable work
4. Note external dependencies

**Skip user review** — proceed directly to implementation.
(The user opted into autonomous mode by using this workflow.)

### Phase 4: Worktree Creation
Follow the `worktree-management` skill to create a worktree for active development.

1. Identify the target project and its master repo path from the `project-registry` skill
2. Sync the master repo:
   ```bash
   cd <master-repos>/<repo>
   git fetch origin && git pull
   ```
3. Create a worktree with the feature branch:
   ```bash
   BRANCH="feature/issue-<number>-<short-description>"
   DIR_NAME="<repo>--$(echo "$BRANCH" | tr '/' '-')"
   git worktree add <worktrees>/"$DIR_NAME" -b "$BRANCH" origin/<default-branch>
   ```
4. Switch into the worktree for all subsequent work:
   ```bash
   cd <worktrees>/"$DIR_NAME"
   ```
5. Branch naming: `feature/<ticket-id>-<short-description>`
   - For GitHub issues: `feature/issue-<number>-<short-description>`
   - Keep `<short-description>` to 3-4 hyphenated words max

**All remaining phases happen inside the worktree directory.** Never go back to the master repo to make changes.

### Phase 5: Incremental Implementation
Follow the `implementation-workflow` skill for change discipline and available specialists.

**Commit rhythm:**
- Commit after each logical unit of work is complete and verified
- Each commit should compile independently
- Use conventional commit messages
- Follow the `git-commits` skill for commit format

### Phase 6: Test & Iterate
1. Run tests after each significant change
2. Fix failures before proceeding
3. Commit fixes separately from feature work
4. If a test failure reveals a design issue, fix the design — don't hack around the test

### Phase 7: Self-Review Loop
Follow the `pr-review` skill priorities:
1. Run `git diff origin/<default-branch>..HEAD --stat` to see the full scope
2. Run `git diff origin/<default-branch>..HEAD` to review the complete diff
3. Check for: stray changes, debug artifacts, missing edge cases, style violations
4. Fix any issues found, commit as `chore: cleanup` or `fix: <specific>`
5. If fixes were made, re-review the updated diff from step 1
6. Repeat until no more substantive findings remain

### Phase 8: Push & Draft PR
1. Push to origin: `git push -u origin HEAD`
2. Delegate to GitHubOps subagent to create a **draft** PR with:
   - Title matching the ticket title (prefixed with conventional type)
   - Body including: what changed, why, testing done, ticket link
   - The ticket/issue linked via `Closes #<number>` or `Fixes #<number>`

### Phase 9: Copilot Review & Address Feedback
1. Delegate to GitHubOps subagent to request Copilot's review on the draft PR
2. Wait briefly, then fetch the review comments
3. For each piece of feedback:
   - If actionable: fix the issue and commit as `fix: <specific from review>`
   - If not applicable: add a reply comment explaining why the suggestion doesn't apply
4. Push any fixes: `git push`
5. Report completion to the user with the PR URL

## Context Management
- Use todo lists to track progress through phases
- If context gets large, summarize completed phases before continuing
- Keep the plan diagram as the north star throughout
- If a phase reveals the plan was wrong, update the plan before continuing

## Error Recovery
- If tests fail repeatedly (3+ attempts), stop and report the issue
- If a required dependency is missing (external service, migration, etc.), note it and skip that part
- If the ticket is ambiguous and you can't make a reasonable assumption, stop and ask

## Rules

**ALWAYS:**
- Run tests before pushing
- Self-review the full diff before creating the PR — loop until clean
- Request Copilot review on the draft PR and address all feedback

**NEVER:**
- Skip the research phase — understand before you build
- Push without running tests
- Switch to other branches — stay on your feature branch
- Delete branches or manipulate remotes
