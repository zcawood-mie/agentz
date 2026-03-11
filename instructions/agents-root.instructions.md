---
name: Agents Root
description: Defines the $AGENTS_ROOT placeholder used in skill and instruction paths
applyTo: '**'
---
# $AGENTS_ROOT

`$AGENTS_ROOT` is the directory containing the `agents/`, `skills/`, `prompts/`, `instructions/`, `hooks/`, and `memories/` subdirectories. Derive it at runtime from the absolute path of **this file**: `$AGENTS_ROOT` is the parent of the `instructions/` directory that contains `agents-root.instructions.md`.

Other skills, agents, or prompts may be loaded from external locations with different parent directories — do not use those to derive `$AGENTS_ROOT`.

When you see `$AGENTS_ROOT/memories/...`, `$AGENTS_ROOT/skills/...`, etc. in skills, prompts, or agent files, resolve the placeholder to the actual directory before using the path.
