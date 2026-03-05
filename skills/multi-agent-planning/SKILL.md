---
name: multi-agent-planning
description: 'Multi-perspective feature planning orchestration. Use for: collaborative planning, multi-agent planning, parallel planning, comprehensive design, planning orchestration.'
user-invokable: false
---
# Multi-Agent Planning

## When to Use
- User asks to plan a feature with multiple perspectives
- A feature is complex enough to benefit from competing approaches
- The user wants to see tradeoffs surfaced explicitly before committing to an approach

## How It Works

Multiple specialist planners — each with distinct values — analyze the same feature request in parallel. Their proposals are synthesized into a unified plan that balances speed, quality, user experience, security, scalability, and conceptual integrity.

The specialist planners:

| Agent | Lens | Core Question |
|-------|------|---------------|
| PragmatistPlanner | Velocity | "What's the fastest path that doesn't create debt?" |
| CraftspersonPlanner | Quality | "What's the right way to build this so it lasts?" |
| AdvocatePlanner | User Experience | "What happens when things go wrong? What does the user experience?" |
| SecurityPlanner | Security | "What attack surface does this introduce and how do we close it?" |
| ScalabilityPlanner | Scale | "What happens when data grows 100x?" |
| ConceptualistPlanner | Conceptual Integrity | "Does the implementation structure truthfully represent the domain?" |

## Orchestration Workflow

### Phase 1: Frame the Feature

Before dispatching planners, the orchestrator should establish:

1. **Feature description** — what the user wants built (from their request, a ticket, or a conversation)
2. **Codebase context** — which repo, relevant existing code, current patterns (use CodeExplorer if needed)
3. **Constraints** — deadlines, dependencies, known limitations
4. **Scope** — what's in and out of scope for this planning exercise

### Phase 2: Dispatch Planners (Parallel)

Craft a prompt for each planner with:

1. **Feature description** — the full context of what needs to be built
2. **Codebase context** — relevant file paths, existing patterns, current architecture
3. **Constraints** — any timelines, dependencies, or limitations
4. **Return format specification:**

```
Return your plan as:

1. **Approach Summary** — 2-3 sentences describing your proposed approach
2. **Key Decisions** — numbered list of the important design choices you're making and why
3. **Tradeoffs** — what you're explicitly choosing NOT to do and the cost of that choice
4. **Risks** — what could go wrong with this approach
5. **Codebase References** — specific files:lines that are relevant to your plan
6. **Estimated Scope** — rough sizing (files touched, new files, complexity)

If the feature is outside your domain's concerns, return: "Status: no [domain] concerns — this feature is straightforward from a [domain] perspective."
```

Dispatch all planners in the same tool-call block so they run concurrently.

### Phase 3: Synthesize Draft Plan

When all planners return:

1. **Identify consensus** — where do multiple planners agree? These are high-confidence decisions.
2. **Surface tensions** — where do planners disagree? These are the real design decisions.
   - Pragmatist wants to reuse an existing pattern; Craftsperson wants a new abstraction
   - Advocate wants comprehensive error states; Pragmatist wants to ship the happy path first
   - Conceptualist says the domain model is wrong; Pragmatist says it works fine today
3. **Resolve tensions** — for each disagreement, present both sides and either:
   - Recommend a resolution with reasoning
   - Present it as an open question for the user to decide
4. **Merge into a draft unified plan** that incorporates the best of each perspective

This draft is NOT the final plan — it goes back to the planners for critique.

### Phase 4: Critique Round (Parallel)

Dispatch the same planners again, this time with the **draft plan** instead of the original feature request. Each planner reviews the synthesized plan through their own lens.

Craft a prompt for each planner with:

1. **The original feature description** — so they remember what's being built
2. **The full draft plan** — the synthesized output from Phase 3
3. **Their original proposal** — so they can see what was incorporated and what wasn't
4. **Return format specification:**

```
Review this draft plan through your lens. Return:

1. **Accepted** — parts of the plan that satisfy your concerns (brief)
2. **Objections** — specific parts of the plan that are problematic from your perspective, with concrete reasoning for why
3. **Gaps** — concerns from your domain that the plan doesn't address at all
4. **Suggestions** — specific changes that would resolve your objections without undermining the plan's other strengths

If the plan fully satisfies your concerns, return: "Status: approved — no [domain] objections."
```

Dispatch all planners in the same tool-call block so they run concurrently.

### Phase 5: Incorporate Feedback

When all critique responses return:

1. **Triage objections by weight:**
   - **Blocking** — the objection identifies a real flaw that would cause failure (bug, security hole, data loss, conceptual incoherence). These must be addressed.
   - **Strengthening** — the objection improves the plan but the plan would still work without it. Incorporate if the cost is low.
   - **Preference** — the planner wants the plan to look more like their original proposal. Acknowledge but don't change the plan unless the reasoning is compelling.

2. **Revise the draft plan** to address blocking objections and incorporate strengthening feedback.

3. **Assess convergence:**
   - If revisions are minor (no structural changes, just refinements) → the plan has converged. Proceed to Phase 6.
   - If revisions are substantial (structural changes that might introduce new concerns) → run another critique round (Phase 4) with the revised plan. Cap at **2 critique rounds** to prevent infinite loops.

### Phase 6: Present the Final Plan

Structure the output as:

```
## Feature: [name]

### Approach
[Unified approach that balances all perspectives]

### Key Decisions
[Numbered decisions, noting which planner(s) drove each one]

### Tensions Resolved
[For each disagreement that was resolved, explain the tradeoff and the chosen direction]

### Open Questions
[Tensions that need user input to resolve]

### Implementation Outline
[High-level steps, not a detailed implementation plan]

### Risks & Mitigations
[Merged from all planners, deduplicated]

---
**Planners consulted:** [list]
```

## Selective Planning

Not every plan needs all six planners. Select based on feature type:

| Feature Type | Recommended Planners |
|-------------|---------------------|
| New CRUD feature | Pragmatist, Craftsperson, Advocate |
| Auth/permissions change | Security, Conceptualist, Craftsperson |
| Data model change | Scalability, Conceptualist, Craftsperson |
| Performance fix | Pragmatist, Scalability |
| UI/UX feature | Advocate, Pragmatist, Craftsperson |
| Full-stack feature (complex) | All six |
| API endpoint | Security, Scalability, Craftsperson |
| Refactoring | Conceptualist, Craftsperson, Pragmatist |

## Rules

**ALWAYS:**
- Include full feature context in each planner's prompt — they have no shared context
- Dispatch planners in parallel — sequential dispatch wastes time
- Surface tensions explicitly — hiding disagreements between planners defeats the purpose
- Let planners bring their own values — don't tell them what to prioritize
- Run at least one critique round — a single-pass synthesis misses cross-cutting concerns that only emerge when planners see each other's influence on the plan
- Include each planner's original proposal in the critique prompt — they need to see what was kept, what was changed, and what was dropped to give meaningful feedback

**NEVER:**
- Force consensus where genuine tension exists — the point is to surface tradeoffs, not hide them
- Skip the synthesis phase — raw planner outputs without integration are noise, not a plan
- Use all six planners for trivial features — match planner count to feature complexity
- Run more than 2 critique rounds — diminishing returns set in fast; if 2 rounds don't converge, the remaining disagreements are genuine tradeoffs for the user to decide
- Dismiss an objection without reasoning — every blocking or strengthening objection gets a documented response in the final plan
