---
name: instruction-conventions
description: 'Instruction file conventions and templates. Use for: create instruction, new instruction, edit instruction, instruction template, applyTo glob.'
user-invokable: false
---
# Instruction Conventions

## When to Use
- Creating a new instruction (`.instructions.md`)
- Editing or reviewing an existing instruction

## File Location
`~/.agents/instructions/<name>.instructions.md`
- File: lowercase-hyphenated

## Template

```markdown
---
name: Instruction Name
description: Brief description of what rules this applies
applyTo: '**'
---
# Instruction Title

[Short, prescriptive rules. Keep concise — entire body is always injected into context.]
```

## Frontmatter Fields
- `name` — display name (title case)
- `description` — short description shown on hover
- `applyTo` — glob pattern: `**` for all files, `**/*.py` for Python, etc. If omitted, instruction won't auto-apply.

## Content Guidelines
- **Keep short** — instructions are always fully injected, no progressive loading
- **Rules, not workflows** — if it's a multi-step process, it belongs in a skill
- **No manual invocation** — instructions can't be `/` invoked; they're passive
- **Avoid overlap with skills** — if a skill covers the domain, don't duplicate as instruction

## Current Instructions

| Instruction | `applyTo` | Purpose |
|---|---|---|
| `agent-autonomy` | `**` | When to ask vs. proceed, decision-making defaults |
| `no-command-chaining` | `**` | Limit command chaining — only `cd &&` allowed |
| `no-terminal-edits` | `**` | Never use terminal commands to create/modify files |
| `parallel-execution` | `**` | Parallelize independent work |
| `response-formatting` | `**` | Output structure, diagrams, tables, file references |
