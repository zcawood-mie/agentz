---
name: reviewPR
description: Review a colleague's pull request
argument-hint: Provide a PR URL to review
agent: Research
model: 'Claude Sonnet 4.6'
---
Review the given pull request using the colleague review priority list.

## Steps

1. **Fetch PR content**
   Delegate to GitHubOps to fetch the PR diff, description, and metadata from the provided URL.

2. **Set review mode to Colleague**
   Follow the `pr-review` skill with **colleague review mode** explicitly. Use the colleague priority list (P1-P3 + common sense only).

3. **Present findings one at a time, highest priority first.**
   After all findings are presented and approved, draft comments and get confirmation before posting.
