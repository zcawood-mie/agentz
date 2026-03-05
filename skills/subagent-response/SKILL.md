---
name: subagent-response
description: 'How to structure subagent return summaries. Use for: subagent output, return format, response structure, reporting back to parent agent.'
user-invokable: false
---
# Subagent Response

## When to Use
- You are a subagent finishing your work and returning results to the parent agent

## Core Principle

**Your return summary is the ONLY context the parent agent receives.** It won't see your tool calls, file reads, or intermediate reasoning — just your final message. The parent agent will make decisions based solely on this summary.

## Response Structure

Every return summary must include:

1. **Status** — `success` / `failure` / `partial`
2. **What was done** — specific operations performed (e.g., "Created PR #142", "Queried orders collection with filter {status: 'pending'}")
3. **Key data** — identifiers, URLs, counts, sample data — anything the parent needs to reference or continue
4. **Issues** — warnings, errors, permission problems, unexpected results, or anything that might affect the parent's next step

## Guidelines

- **Be terse but complete** — no filler, no explanations of what tools you used, no methodology narrative
- **Lead with status** — the parent needs to know pass/fail before details
- **Include all actionable data** — if the parent might need a URL, number, or ID, include it
- **Flag anomalies** — empty results, unexpected shapes, rate limits, missing resources — the parent can't see what surprised you unless you say so
- **Don't recommend next steps** — you don't know the parent's plan. Report facts, not advice.

## Anti-Patterns

- **Narrative summaries** — "First I searched for X, then I found Y, and after that..." Just state the results.
- **Missing identifiers** — "The PR was created successfully" without the PR number or URL
- **Swallowed errors** — encountering a problem but not mentioning it because the main task succeeded
- **Unsolicited advice** — "You should also consider..." — the parent didn't ask for opinions
