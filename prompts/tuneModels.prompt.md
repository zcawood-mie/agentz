---
name: tuneModels
description: Compare latest AI models and update agent/prompt model assignments
argument-hint: Optional focus like 'optimize for speed' or 'check for new models'
agent: Research
---
Review the latest GitHub Copilot AI model landscape and update agent and prompt model assignments for optimal performance.

## Steps

1. **Gather current state**
   - Read all agent files in `$AGENTS_ROOT/agents/` and note their current `model:` property
   - Read all prompt files in `$AGENTS_ROOT/prompts/` and note any `model:` overrides
   - Follow the `model-selection` skill for the current model knowledge base

2. **Check for updates**
   - Use Context7 to fetch the latest from the GitHub Copilot docs library for current model comparison and task recommendations
   - Use Context7 to fetch the latest from the GitHub Copilot docs library for current multiplier rates and billing info
   - Note any new models, removed models, or multiplier changes since the skill was last updated

3. **Compare and recommend (vendor-agnostic)**
   Present two tables comparing current assignments against the latest recommendations.
   Be vendor-agnostic — recommend the best model for each slot regardless of provider.

   **Agent assignments:**
   | Agent | Current Model | Recommended Model | Multiplier | Rationale |
   |---|---|---|---|---|

   **Prompt overrides:**
   | Prompt | Current Override | Recommended Override | Multiplier | Rationale |
   |---|---|---|---|---|

   Flag any changes needed.

4. **Propose changes**
   If changes are needed, present the specific updates for each agent and prompt file.
   Also flag if the `model-selection` skill itself needs updating (new models, changed multipliers, new task categories).

   Get user approval before handing off.

5. **Hand off to Implementation**
   Use the handoff to have Implementation apply the approved changes to agent files, prompt files, and the `model-selection` skill.
