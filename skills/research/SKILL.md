---
name: research
user-invokable: false
description: 'Codebase investigation methodology and report formatting. Use for: code research, codebase investigation, finding patterns, trace data flow, code exploration, research reports, diagram selection, finding presentation.'
---
# Research

## When to Use
- Investigating how something works in the codebase
- Finding patterns, tracing data flow, understanding code
- Presenting codebase research findings

## Core Principles

Research methodically from broad to specific. Stop at 80% confidence you have enough context.

---

## Available Research Specialists

| Specialist | Values | Best for |
|-----------|--------|----------|
| **CodeExplorer** | Thoroughness, tracing connections | Codebase patterns, data flow, registration points, existing implementations |
| **DocFetcher** | Accurate reference | Library APIs, framework documentation, package behavior |
| **WebSearcher** | Broad technical knowledge | Error messages, Stack Overflow, general technical knowledge |
| **GitHubOps** | Precise retrieval | PR diffs, issue content, review comments |
| **CodeScanner** | Quality, waste elimination | Dead code, security issues, pattern violations (when reviewing) |

### Merge Point Verification

After specialists return, verify:
- Did every question get a complete answer?
- Are there contradictions between findings?
- Are there gaps that need a follow-up investigation?

---

## Methodology

Use this methodology yourself for narrow lookups, and include it in CodeExplorer prompts for delegated investigation.

### 1. Find 3-5 Examples of the Same Pattern
Search for existing code that does something similar. Multiple instances reveal the true pattern better than documentation.

### 2. Trace Data Flow Within Your Boundary
- Where does data come from?
- What transforms it?
- Where does it go?

In multi-repo/microservice setups, trace to the boundary (API route, message queue, shared contract).

### 3. Identify Extension vs Invention
Most tasks are "add another X like the existing Xs" — recognize this early.

### 4. Find Registration Points
Search for where similar things are registered, routed, or exported:
- Adding API endpoint → find the router file
- Adding component → find where similar components are exported
- Adding handler → find the dispatch/switch that routes to handlers

### 5. Note External Dependencies
If the task requires something outside your codebase, note it early.

## Process

1. **Start high-level** — code searches before reading specific files
2. **Map the area** — structure, dependencies, key files
3. **Identify key pieces** — classes, functions, modules involved
4. **Trace paths** — code paths and data flow as needed
5. **Note exact locations** — file:line for all findings
6. **Compare paths** — use tables for related code paths

---

## Reporting

### Diagram Selection

| Question Type | Diagram Type | When |
|---|---|---|
| "How does X work?" | **Flowchart** | Workflows, processes, decisions |
| "What calls what?" | **Sequence diagram** | Call chains, request/response |
| "How are these related?" | **ER diagram** | Data models, relationships |
| "What depends on what?" | **Flowchart + subgraphs** | Dependencies, imports |
| "What are the states?" | **State diagram** | Status transitions, lifecycle |
| "What's the data flow?" | **Sequence or flowchart** | Pipelines, transformations |

**Skip diagrams for:** narrow lookups, single-fact answers, simple lists (<4 items with no relationships).

**Diagrams mandatory for:** architecture questions, multi-step processes, data flow tracing, 3+ interacting components.

Always render with `renderMermaidDiagram` — never output raw mermaid code blocks.
Follow the `mermaid-diagrams` skill for styling.

### Report Formats

**Narrow Lookup** (single fact):
```
## {Direct answer}
{File reference and brief context.}
```

**Focused Question** (specific mechanism):
```
## {Direct answer}
{Rendered diagram}
{1-2 paragraphs with file references. Diagram carries the weight.}
```

**Broad Question** (architecture/overview):
```
## {Direct answer}
{Rendered diagram — architecture, flow, or relationship overview}
{Bullet points connecting diagram to code locations.}
### Detail (if needed)
{Additional diagram zooming in}
```

**Comparison:**

| Aspect | Path A | Path B |
|---|---|---|
| {criterion} | {finding with line ref} | {finding with line ref} |

---

## Output Rules

- ALWAYS include file paths and line numbers
- USE tables to compare implementations
- ANSWER only what was asked — no suggestions
- FORMAT code references as clickable links
- Lead with diagrams for anything beyond a narrow lookup

## When to Stop

Stop when you can:
- Answer the specific question asked
- Provide concrete file/line references
- Explain how pieces connect
- Identify patterns to follow
