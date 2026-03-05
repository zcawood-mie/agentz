---
name: prompt-conventions
description: 'Prompt file conventions and templates. Use for: create prompt, new prompt, edit prompt, prompt template, prompt frontmatter.'
user-invokable: false
---
# Prompt Conventions

## When to Use
- Creating a new prompt (`.prompt.md`)
- Editing or reviewing an existing prompt

## File Location
`~/.agents/prompts/<promptName>.prompt.md`
- File: camelCase

## Template

```markdown
---
name: promptName
description: Brief description
argument-hint: What optional input the user can provide
agent: AgentName
---
[One-sentence task summary]

## Steps

1. **[Step name]**
   [Concise instructions with clear success criteria]

2. **[Step name]**
   Follow the `skill-name` skill for [domain].
```

## Frontmatter Fields
- `name` — matches filename (camelCase)
- `description` — concise purpose
- `argument-hint` — what optional user input enhances the prompt
- `agent` — which agent executes (e.g., `Implementation`, `Research`)

## Content Guidelines
- **Reference skills, don't inline rules** — skills are the single source of truth
- **Keep focused** — one logical task per prompt
- **Describe what, not how** — the agent and skills handle the how
- **Be explicit about multi-repo** — if task might span repos, handle each separately
