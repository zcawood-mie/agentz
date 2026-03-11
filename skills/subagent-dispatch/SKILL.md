---
name: subagent-dispatch
description: 'How to delegate work to subagents. Use for: subagent prompt, delegation, context passing, subagent invocation, orchestration.'
user-invokable: false
---
# Subagent Dispatch

## When to Use
- Delegating a task to a subagent via `runSubagent`
- Crafting the prompt string for a subagent call

## Core Principle

**Your prompt is the ONLY context the subagent receives.** Subagents have no conversation history, no knowledge of what you've been doing, and no access to your findings unless you explicitly include them.

**Orchestrators provide the goal. Agents bring values.** Your prompt describes the goal, scope, context, and any task-specific priorities. The agent applies its own inherent values — the approach emerges from values meeting the goal. Do NOT tell the subagent what it already knows from its own design — don't restate its role, its priorities, or how to reason.

## Prompt Structure

Every subagent prompt must include:

1. **Exact operation** — what to do, stated as a specific action
   - Good: "Fetch PR #142 from my-org/my-repo including the diff and all review comments"
   - Bad: "Look at the PR we've been discussing"

2. **All necessary identifiers** — repo, branch, PR number, issue number, URLs, file paths
   - Good: "Create a PR from feature/auth-flow to main in my-org/my-repo"
   - Bad: "Create a PR for my current branch"

3. **What to return** — specify the shape of the response you need
   - Good: "Return the PR URL, PR number, and any merge conflicts"
   - Bad: "Let me know how it goes"

4. **Relevant context** — if the subagent needs data from your session, paste it in
   - Good: "The PR body should be: [full text here]"
   - Bad: "Use the PR body from earlier"

## Anti-Patterns

- **Assuming shared context** — the subagent knows nothing about your conversation
- **Vague operations** — "check the GitHub stuff" gives the subagent nothing to act on
- **Missing identifiers** — the subagent can't infer which repo, branch, or PR you mean
- **No return spec** — without knowing what you need back, the subagent guesses at what's useful

---

## Scope Contracts

When dispatching write agents or scoped investigations, include a scope contract to prevent overreach.

**For write agents (SourceWriter):**

```
Task: [one-sentence action verb + object]

Scope:
  MAY modify: [exact file paths]
  MUST change: [specific functions, sections, or line ranges]
  MUST NOT touch: [explicit exclusions — other workers' territory]

Deliverable:
  Return: [what the worker should produce]
  Do NOT: [common overreach for this type of task]

Context:
  [Minimal information needed — existing patterns, types, function signatures]
  [Paste relevant code snippets — the worker has no conversation history]
```

**For read agents (CodeExplorer, CodeScanner, DocFetcher, WebSearcher):**

```
Question: [specific, answerable question]

Scope:
  Search within: [file paths, directories, or repos to focus on]
  Do NOT explore: [explicit exclusions]

Return format:
  [What shape the answer should take — file:line refs, summary, comparison table]

Context:
  [Why you're asking — helps the worker focus its search]
```
