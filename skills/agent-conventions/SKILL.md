---
name: agent-conventions
description: 'Agent conventions. Use for: create agent, edit agent, agent template, subagent, agent architecture, tool restrictions.'
user-invokable: false
---
# Agent Conventions

## When to Use
- Creating or editing an agent (`.agent.md`)
- Deciding agent vs. subagent architecture

## File Locations
- **Agents:** `~/.agents/agents/[AgentName].agent.md` (PascalCase)

---

## User-Facing Agent Template

```markdown
---
name: [Name]
description: '[Brief description. Use for: keywords.]'
argument-hint: '[Expected input format]'
tools: ['vscode/askQuestions', 'vscode.mermaid-chat-features/renderMermaidDiagram', 'todo', 'read', 'search', 'search/searchSubagent', 'agent', '[additional-tools]']
agents: ['SubagentName1', 'SubagentName2']
disable-model-invocation: true
handoffs:
  - label: [Next Step]
    agent: [AgentName]
    prompt: '[Context]'
    showContinueOn: true
    send: true
---
You are a [ROLE]. [One-sentence purpose].

<constraints>
**Boundaries:**
- [Capability/scope boundary as identity statement]
- [Capability/scope boundary as identity statement]
- [Capability/scope boundary as identity statement]
</constraints>

<skills>
Follow the `subagent-dispatch` skill when delegating to subagents.
Follow the `skill-name` skill for [domain].
Follow the `other-skill` skill for [domain].
</skills>
```

## Subagent Template

```markdown
---
name: [Name]
description: '[Brief description. Use for: keywords.]'
argument-hint: '[Expected input format]'
tools: ['read', 'search', 'search/searchSubagent', '[specialized-tools]']
user-invokable: false
---
You are a [ROLE] SUBAGENT. [One-sentence purpose].

**What you care about:** [Core values that apply across all tasks this agent handles — descriptive, explaining WHY each matters]
- [Value] — because [consequence/reason]
- [Value] — because [consequence/reason]

**Task-specific priorities** come from the orchestrator's prompt.

<constraints>
**Boundaries:**
- [Scope/capability boundary as identity statement]
- [Domain-specific boundary]
</constraints>

<skills>
Follow the `subagent-response` skill when returning results to the parent agent.
</skills>
```

## Architecture: Lean Orchestrators + Specialized Subagents

User-facing agents are lean orchestrators. They have core tools (questions, mermaid, todo), read/search, and subagent delegation. Specialized capabilities live in subagents with narrowly scoped tools.

**Current agents:**

| Agent | Capabilities | Subagents | User-Invokable |
|-------|-------------|-----------|----------------|
| Research | Read, search, terminal (read-only), subagent delegation | GitHubOps, CodeExplorer, DocFetcher, WebSearcher, CodeScanner, SecurityReviewer, ArchitectureReviewer, PerformanceReviewer, MaintainabilityReviewer | Yes |
| Implementation | Read, search, edit, terminal (full), subagent delegation | Research, GitHubOps, BrowserTest, DatabaseOps, SourceWriter, CodeScanner, CodeExplorer, DocFetcher, WebSearcher | Yes |
| SourceWriter | Read, search, edit, terminal — scoped to files specified by orchestrator | — | No |
| CodeScanner | Read, search (no edit) — scans for dead code, security, refactoring | — | No |
| CodeExplorer | Read, search — investigates specific codebase questions | — | No |
| DocFetcher | Read, search, context7 — library documentation lookup | — | No |
| WebSearcher | Read, search (web fetch pending) — general internet search | — | No |
| GitHubOps | Read, search, GitHub API (`github/*`), terminal (`gh api` only) | — | No |
| BrowserTest | Read, search, Chrome DevTools (`chrome-devtools/*`), terminal (read-only) | — | No |
| DatabaseOps | Read, search, MongoDB (`mongodb/*`) | — | No |
| SecurityReviewer | Read, search — security-focused code review | — | No |
| ArchitectureReviewer | Read, search — architecture-focused code review | — | No |
| PerformanceReviewer | Read, search — performance-focused code review | — | No |
| MaintainabilityReviewer | Read, search — maintainability-focused code review | — | No |
| PragmatistPlanner | Read, search — velocity-focused feature planning | — | No |
| CraftspersonPlanner | Read, search — quality-focused feature planning | — | No |
| AdvocatePlanner | Read, search — UX-focused feature planning | — | No |
| SecurityPlanner | Read, search — security-focused feature planning | — | No |
| ScalabilityPlanner | Read, search — scalability-focused feature planning | — | No |
| ConceptualistPlanner | Read, search — conceptual-integrity-focused feature planning | — | No |
| DataIntegrityInvestigator | Read, search — data-focused bug investigation | — | No |
| ControlFlowInvestigator | Read, search — logic-focused bug investigation | — | No |
| ConcurrencyInvestigator | Read, search — timing-focused bug investigation | — | No |
| EnvironmentInvestigator | Read, search — environment-focused bug investigation | — | No |

## Agent Design Rules
- **Agent body should be ~15-25 lines:** one-sentence role, priorities/values, `<constraints>` (3-5 rules), `<skills>` references
- **Three-layer test:** every agent must have unique tool access, constraints, OR priorities. If it only differs by task type, it should be a prompt, not an agent.
- User-facing agents should be lean — delegate specialized tools to subagents
- Subagents use `user-invokable: false` — they don't appear in the agent dropdown
- Keyword-rich descriptions for subagent discovery
- No inline workflows — reference skills instead
- **List tools explicitly** in the `tools:` frontmatter array — never reference tool set names
