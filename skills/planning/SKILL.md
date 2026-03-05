---
name: planning
user-invokable: false
description: 'Diagram-first implementation planning workflow. Use for: plan, design, architecture, implementation plan, feature planning, diagram-first, mermaid plan.'
---
# Planning

## When to Use
- Creating an implementation plan for a feature or task
- Designing architecture before coding
- Breaking down a complex task into implementable steps

## Planning Mode Selection

Before planning, determine single-agent vs multi-agent approach:

### Use Multi-Agent Planning (Default) When:
- Feature involves 2+ of: UI, API, database, external service, cron job
- User-facing changes with error handling or edge cases
- Security-sensitive features (auth, payments, PII)
- Architectural decisions (new patterns, data models, service boundaries)
- Features where tradeoffs matter (performance vs simplicity, speed vs quality)
- Anything tagged as "complex" or with ambiguous requirements

### Use Single-Agent Planning When:
- Simple CRUD operations following existing patterns
- Cosmetic UI changes (styling, layout adjustments)
- Adding fields to existing forms/displays
- Configuration changes
- Documentation tasks

**If multi-agent planning applies, follow the `multi-agent-planning` skill for orchestration.** The methodology, diagram standards, and workflow below still apply — each specialist planner uses them as the foundation for their proposal.

---

## Core Principle

**The diagram IS the plan.** It should be self-contained with all essential information. Text sections are supplementary.

## Workflow

### Phase 0: Clarifying Questions

MANDATORY before research. Ask the user:
- Scope boundaries (what IS and ISN'T included)
- Ambiguous requirements
- Preferences on implementation approach
- Constraints or dependencies

### Phase 1: Context Gathering

Follow the `research` skill for codebase investigation. Focus on:
- **Entities first** — identify data entities and attributes
- **Relationships second** — how entities relate
- **Patterns third** — find existing patterns for similar functionality

Additionally:
- Search for existing reusable modules
- Use provided artifacts (SQL, API specs, types) directly — adapt minimally
- Note external dependencies early (database migrations, other services)

Stop at 80% confidence you have enough context.

### Phase 2: Generate Diagram

MANDATORY: Use `renderMermaidDiagram` tool to create the plan visually.

Follow the `mermaid-diagrams` skill for styling.

**Required diagram elements:**
- Function names with parameters and return types: `functionName(param1, param2): ReturnType`
- Data flowing between nodes (labeled edges): `A -->|"userId: string"| B`
- Subgraphs for logical grouping
- Parallel task markers: `[PARALLEL]` annotations or `par` blocks

**Layout:**
- `flowchart LR` for data pipelines
- `flowchart TD` for process flows

### Phase 3: Present for Iteration

Present:
1. The rendered diagram (this IS the plan)
2. Brief entities summary
3. Parallelization opportunities
4. External dependencies or blockers
5. Open questions

MANDATORY: Pause for user feedback. Frame as a draft for review.

### Phase 4: Handle Feedback

When the user replies, restart from Phase 1 to gather additional context and refine.

**NEVER start implementation.** Plans describe steps for another agent to execute later.

## Rules

**ALWAYS:**
- Render diagrams with the tool — never output raw mermaid code blocks
- Include function signatures in diagram nodes
- Label edges with data being transferred
- Mark parallelizable tasks clearly
- Pause for user feedback before finalizing

**NEVER:**
- Start implementation or run edit tools
- Plan steps for yourself to execute
- Skip the diagram — text-only plans are not acceptable
