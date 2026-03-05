---
name: Response Formatting
description: How to format responses — structure, diagrams, tables, file references
applyTo: '**'
---
# Response Formatting

- **Concise but complete** — say what's needed, nothing more
- **Structured over prose** — use formatting to aid scanning
- **One topic at a time** — don't overwhelm with everything at once
- **No emojis** — keep it professional and clean

## Mermaid Diagrams

Use for: complex workflows, architecture, data flow, state machines, dependency graphs, cross-service sequences.

Skip for: simple linear processes (≤3 steps), single-file changes, direct answers.

## Structured Presentation

When presenting findings, issues, or proposals:
- **Issue:** Clear description
- **Location:** File/line as a link
- **Impact:** Why it matters
- **Proposed Solution:** Specific suggestion

## Tables

Use tables for comparing options, before/after states, feature comparisons, priority lists.

## File References

Always link to files and lines — never backticks around file paths when linking:
- File: [src/config.ts](src/config.ts)
- Line: [config.ts](src/config.ts#L42)
- Range: [the handler](src/handler.ts#L15-L30)

## Length

| Response Type | Target |
|---|---|
| Direct answer | 1-3 sentences |
| Explanation | 1-2 paragraphs |
| Analysis | Structured sections |

Match depth to complexity.
