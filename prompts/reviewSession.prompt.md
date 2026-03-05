---
name: reviewSession
description: Review the current session to extract agent improvements
argument-hint: Optionally focus on a specific agent, skill, or issue area
agent: Research
---
Review this conversation to identify improvements to agents, skills, prompts, and instructions.

## Steps

1. **Scan the session**
   Identify which prompts were invoked, which agents ran, and what tasks were attempted.
   Note the overall arc: what was the goal, what happened, and what was the outcome.

2. **Classify signals and score dimensions**
   Follow the `session-review` skill.
   Classify every meaningful interaction as positive, negative, or implicit preference.
   Score all six evaluation dimensions.

3. **Propose improvements**
   Follow the `session-review` skill's finding presentation format and improvement categorization.
   Present findings one at a time, highest impact first. Wait for approval on each.

4. **Hand off approved changes**
   After the user approves specific changes, hand off to Implementation to apply them.
   Follow the `agent-management` skill for creating or editing primitives.
