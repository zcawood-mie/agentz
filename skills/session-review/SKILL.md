---
name: session-review
description: 'Session evaluation methodology for extracting agent improvements. Use for: session review, conversation review, self-evaluation, agent improvement, learning, retrospective.'
user-invokable: false
---
# Session Review

## When to Use
- Reviewing a completed or in-progress session to extract improvements
- Evaluating agent performance after a task
- Identifying patterns in user corrections or frustrations

## Signal Classification

Scan the session and classify every meaningful interaction into one of three categories:

### Positive Signals
User approved, moved forward, expressed satisfaction, or accepted output without modification.

### Negative Signals
User corrected output, re-prompted with different wording, expressed frustration, manually edited agent output, or abandoned an approach.

### Implicit Preferences
Patterns in how the user modifies agent output that reveal unstated rules — formatting choices, naming conventions, level of detail, communication style, tool preferences.

## Evaluation Dimensions

Score each dimension as **strong**, **adequate**, or **needs improvement** based on session evidence:

| Dimension | What to Evaluate |
|---|---|
| **Efficiency** | Did the agent minimize unnecessary steps, tool calls, and user interactions? |
| **Accuracy** | Were outputs correct on the first attempt? How many corrections were needed? |
| **Autonomy** | Did the agent proceed without unnecessary permission-seeking? Did it ask when it should have? |
| **Convention adherence** | Did the agent follow existing skills, instructions, and codebase patterns? |
| **Scope discipline** | Did the agent stay on task without drive-by fixes or tangents? |
| **Communication** | Was output concise, well-formatted, and at the right level of detail? |

## Finding Presentation Format

Present each finding as:

- **Signal:** What happened in the session (quote or summarize the interaction)
- **Dimension:** Which evaluation dimension it relates to
- **Primitive:** Which file should change (agent / skill / prompt / instruction / hook)
- **Change:** Specific proposed edit or new content
- **Impact:** Why this improvement matters (frequency, severity, or user friction)

Present findings **one at a time**, highest impact first. Wait for user response before presenting the next.

## Improvement Categorization

Map each finding to the correct primitive:

| Finding Type | Primitive |
|---|---|
| Agent used wrong tools or too many tools | **Agent** (tool restrictions) |
| Missing workflow or methodology | **Skill** (new or updated) |
| Always-on rule that was violated | **Instruction** (new or updated) |
| Repetitive task that should be one-click | **Prompt** (new) |
| Rule that was ignored despite existing | **Hook** (deterministic enforcement) |
| Implicit preference that should be codified | **Instruction** or **Skill** depending on scope |

## Rules

**ALWAYS:**
- Ground every finding in specific session evidence (quote or reference the interaction)
- Score all six evaluation dimensions, even if some are "strong"
- Categorize improvements by primitive type before proposing changes
- Present findings one at a time, highest impact first

**NEVER:**
- Invent findings not supported by session evidence
- Propose changes to primitives without identifying the specific file to modify
- Batch all findings into a single wall of text
- Skip dimensions where the agent performed well — acknowledge strengths too
