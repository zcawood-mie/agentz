---
name: multi-agent-debugging
description: 'Multi-perspective bug investigation orchestration. Use for: collaborative debugging, multi-agent debugging, parallel investigation, root cause analysis, debugging orchestration.'
user-invokable: false
---
# Multi-Agent Debugging

## When to Use
- A bug's root cause is unclear and could be in multiple domains
- The same symptom could have fundamentally different explanations
- Initial single-investigator debugging hasn't found the root cause

## How It Works

Multiple specialist investigators — each starting from a different hypothesis about what's wrong — investigate the same bug in parallel. The orchestrator evaluates which hypothesis best explains the evidence, and either identifies the root cause or dispatches a targeted follow-up.

The specialist investigators:

| Agent | Starting Hypothesis | Strongest Signals |
|-------|--------------------|--------------------|
| DataIntegrityInvestigator | "The data is wrong" | Wrong values displayed, missing records, inconsistent state |
| ControlFlowInvestigator | "The logic is wrong" | Wrong behavior on specific inputs, unhandled cases, state machine violations |
| ConcurrencyInvestigator | "The timing is wrong" | Intermittent failures, works-on-refresh, race conditions, stale data |
| EnvironmentInvestigator | "The config is wrong" | Works locally / fails deployed, post-deployment regressions, version sensitivity |

## Orchestration Workflow

### Phase 1: Characterize the Bug

Before dispatching investigators, the orchestrator should establish:

1. **Symptoms** — what the user observes (error message, wrong behavior, visual glitch)
2. **Reproduction** — steps to reproduce, frequency (always, intermittent, specific conditions)
3. **Context** — when it started, what changed recently, which environment
4. **Prior investigation** — what's already been ruled out

These signals help select which investigators to dispatch and what context to give them.

### Phase 2: Dispatch Investigators (Parallel)

Craft a prompt for each investigator with:

1. **Bug description** — full symptoms, reproduction steps, and context
2. **Relevant code** — file paths, recent changes, the area of the codebase involved
3. **Prior investigation** — what's already been checked and ruled out
4. **Return format specification:**

```
Return your investigation as:

1. **Hypothesis** — your specific theory about what's causing this bug
2. **Evidence For** — what you found in the code that supports your hypothesis (file:line references)
3. **Evidence Against** — anything you found that weakens your hypothesis
4. **Confidence** — high / medium / low, with reasoning
5. **Smoking Gun** — if you found the exact root cause, highlight it here; otherwise omit

If the bug is clearly outside your domain, return: "Status: ruled out — no [domain] explanation for these symptoms. Reasoning: [brief]"
```

Dispatch investigators in the same tool-call block so they run concurrently.

### Phase 3: Evaluate Hypotheses

When all investigators return:

1. **Rank by confidence and evidence quality:**
   - A hypothesis with a smoking gun (exact root cause identified with file:line) is the answer
   - Multiple investigators finding corroborating evidence for the same area is a strong signal
   - A ruled-out domain narrows the search space — that's valuable even without a positive finding

2. **Check for compound causes:**
   - Sometimes the bug requires two things to be true simultaneously (e.g., a concurrency issue that only manifests because of a data integrity gap)
   - If two investigators found medium-confidence evidence pointing to related areas, the compound explanation may be the real root cause

3. **Assess coverage:**
   - Did any investigator find the smoking gun? → Present the root cause
   - Is one hypothesis clearly strongest? → Present it as the likely root cause with caveats
   - Are multiple hypotheses plausible? → Proceed to Phase 4
   - Did all investigators rule out their domain? → The bug may be in a domain not covered; report the negative findings

### Phase 4: Targeted Follow-Up (if needed)

If Phase 3 doesn't produce a clear root cause:

1. Take the strongest hypothesis (or compound hypothesis)
2. Dispatch a single investigator from the most relevant domain with:
   - Their original findings
   - Findings from other investigators that may provide cross-domain context
   - A more specific question: "Given [evidence], investigate whether [specific mechanism] at [specific location] could cause [symptom]"

Cap at **one follow-up round** — if two passes don't find it, the remaining investigation likely needs human judgment or runtime debugging tools.

### Phase 5: Present Findings

Structure the output as:

```
## Bug: [brief description]

### Root Cause
[The identified root cause, or the strongest hypothesis if not definitive]
**Confidence:** [high/medium/low]
**Found by:** [which investigator(s)]

### Evidence
[Key evidence with file:line references]

### Ruled Out
[Domains/hypotheses that were investigated and eliminated, with reasoning]

### Suggested Fix
[Concrete fix direction — not implementation, but what needs to change]

---
**Investigators consulted:** [list]
```

## Selective Investigation

Not every bug needs all four investigators. Select based on symptoms:

| Symptom Pattern | Recommended Investigators |
|----------------|--------------------------|
| Wrong data displayed | Data Integrity, Control Flow |
| Feature broken for specific input | Control Flow, Data Integrity |
| Intermittent failure | Concurrency, Environment |
| Works locally, fails deployed | Environment, Concurrency |
| Regression after deploy (no code change) | Environment |
| Regression after code change | Control Flow, Data Integrity |
| Performance degradation | Concurrency, Data Integrity |
| Unknown / vague | All four |

## Rules

**ALWAYS:**
- Include full bug context in each investigator's prompt — they have no shared context
- Dispatch investigators in parallel — the whole point is competing hypotheses explored simultaneously
- Report ruled-out domains — negative findings narrow the search and are valuable
- Let investigators bring their own investigation strategy — don't tell them where to look

**NEVER:**
- Skip the hypothesis evaluation — raw investigator outputs need triage before presentation
- Ignore evidence-against that an investigator reports about their own hypothesis — self-doubt is the most honest signal
- Run more than one follow-up round — diminishing returns; escalate to human debugging instead
- Dispatch all four investigators for bugs with obvious symptoms pointing to one domain — match investigator count to ambiguity
