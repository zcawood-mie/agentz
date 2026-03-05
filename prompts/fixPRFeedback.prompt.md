---
name: fixPRFeedback
description: Address review feedback on the current branch's pull request
argument-hint: Optionally provide additional personal feedback to address
agent: Implementation
---
Address the review feedback on the current branch's pull request.

## Steps

1. **Identify the current PR**
   Delegate to GitHubOps to get the current branch's open PR (repo, number, URL, and review comments).

2. **Follow the `pr-workflow` skill's feedback workflow**
   Categorize review comments by priority and address each item one at a time with user approval.
