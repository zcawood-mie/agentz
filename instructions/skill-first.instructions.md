---
name: Skill First
description: Skills are first-class context — load relevant skill files before starting any task
applyTo: '**'
---
# Skill First

Skills encode tested, domain-specific best practices. They are **first-class context**, not optional enrichment.

## MANDATORY: Load Skills Before Starting Work

Before taking any action on a task, scan the available skills list and load relevant skills using `read_file`. Do this silently — no need to announce it.

## Two-Pass Loading

**Pass 1 — Load the definite skills first.**
Any skill whose description clearly matches the task domain gets loaded immediately.

**Pass 2 — Use those skills to resolve ambiguous ones.**
If a skill might apply but you're unsure, let the content of the already-loaded skills inform the decision. A loaded skill may clarify scope, reference other skills, or rule out the ambiguous candidate.

Only skip a skill if you can confidently say it doesn't apply after this process.

## This Applies to ALL Tasks

Simple or obvious tasks are not exempt. Skipping skill loading because the path to completion seems clear is the most common failure mode — skills frequently contain output format requirements, edge case handling, and workflow nuances that aren't apparent from the task description alone.
