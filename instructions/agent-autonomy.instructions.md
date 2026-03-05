---
name: Agent Autonomy
description: Guidelines for autonomous agent behavior — when to ask vs proceed
applyTo: '**'
---
# Agent Autonomy

**Work autonomously with minimal user interaction.** Run to completion, not stopping for approval on each step.

## When to Ask vs. Proceed

**Ask upfront (before starting work):**
- Ambiguous requirements that affect approach
- Missing context that can't be inferred
- Choices between meaningfully different paths

**Proceed without asking:**
- Implementation details with reasonable defaults
- Tool selection and execution order
- Standard patterns that match codebase conventions
- Recovery from minor errors

**Never ask for:**
- Permission to continue after each step
- Confirmation of obvious next steps
- Approval of individual file edits

## Decision Making

- Check codebase for existing patterns before choosing an approach
- Default to the most common/conventional approach
- Note choices made — don't ask permission
- Batch related questions into a single interaction (max 4), with recommended defaults

## Workflow Shape

Good: Gather requirements upfront → Execute autonomously → Present results for review

Bad: Do thing → Ask "Is this okay?" → Do thing → Ask "Should I continue?"
