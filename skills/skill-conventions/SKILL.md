---
name: skill-conventions
description: 'Skill file conventions and templates. Use for: create skill, new skill, edit skill, skill template, skill frontmatter, skill guidelines.'
user-invokable: false
---
# Skill Conventions

## When to Use
- Creating a new skill (`SKILL.md`)
- Editing or reviewing an existing skill

## File Location
`~/.agents/skills/<skill-name>/SKILL.md`
- Folder: lowercase-hyphenated
- File: always `SKILL.md` (uppercase)

## Template

```markdown
---
name: skill-name
description: 'Brief sentence about the domain. Use for: keyword1, keyword2, keyword3.'
---
# Skill Title

[Domain knowledge — facts, patterns, how things work, why things are the way they are]

[Methodology — workflow phases, checklists, verification steps, reporting formats]

## Rules (optional)

**ALWAYS:**
- [Required behavior in this domain]

**NEVER:**
- [Prohibited behavior in this domain]
```

Skills are organized by **domain**. A single skill contains everything an agent needs for that domain:
- **Facts** use descriptive voice — "Blaze morphs `<i>` elements instead of replacing them"
- **Rules** use prescriptive voice — "ALWAYS wrap `<i>` in `<span>` inside conditionals"

Both belong together because the rule makes no sense without the context.

## Frontmatter Rules
- `name` — matches folder name, lowercase-hyphenated
- `description` — single-quoted, brief sentence + `Use for:` keywords (4-8)
- `user-invokable` — set to `false` for internal/background skills
- `disable-model-invocation` — set to `true` for manual-only skills

### Visibility

| Property | Effect |
|---|---|
| (defaults) | Shows in `/` menu + auto-loads when relevant |
| `user-invokable: false` | Hidden from `/` menu, still auto-loads |
| `disable-model-invocation: true` | Only manual `/` invocation, no auto-load |
| Both set | Effectively disabled |

Use `user-invokable: false` for internal skills (e.g., `subagent-dispatch`, `subagent-response`).

## Content Guidelines
- **Facts are descriptive** — describe how things work, what's true, why things are the way they are
- **Rules are prescriptive** — state requirements with ALWAYS/NEVER in a Rules section
- **Include concrete examples** — exact commands, code, format expected
- **Keep focused** — one domain per skill; split if it covers multiple topics
- **Reference other skills** — don't inline rules already covered elsewhere
- **No code fence wrapper** — file starts with `---`, not ` ```skill `

## Skill vs. Instruction Decision

| Characteristic | → Skill | → Instruction |
|---|---|---|
| Length | Any length | Short (rules, conventions) |
| Invocation | Manual `/skill-name` or auto-load | Always auto-injected |
| Scope | Situational, context-specific | Global or file-type-specific |
| Progressive loading | Yes (3-level) | No (always full) |
| Portability | Cross-agent (VS Code, CLI, coding agent) | VS Code only |
| Activation | Only when relevant | Every prompt |

**Heuristic:** If the rule is always relevant regardless of context → instruction. If it only matters in specific situations → skill.

## Checklist
- [ ] Starts with `---` on line 1
- [ ] Has `name` and `description` with `Use for:` keywords
- [ ] Has H1 title
- [ ] Facts use descriptive voice (observations, how things work)
- [ ] Rules use prescriptive voice (ALWAYS/NEVER in a Rules section)
- [ ] Includes concrete examples
- [ ] No wrapping code fence

---

## Skill Scripts

Skills can include executable scripts in a `scripts/` subdirectory. Scripts let agents perform actions — running checks, transforming data, automating multi-step processes — rather than just reading instructions.

### When to Add a Script

Add a script when a skill's workflow includes steps that are:
- **Tedious and error-prone** if done manually (searching across many files, parsing structured data)
- **Repetitive** across multiple invocations (same grep patterns, same file iteration)
- **Verifiable** — the script can produce a clear pass/fail or structured result

Don't add a script for steps that are inherently judgment calls or require context the agent already has.

### Design Principles

**Non-interactive.** Scripts run in automated pipelines with no human at the keyboard. Never prompt for input, use confirmation dialogs, or wait for keypresses. Accept all inputs via arguments or stdin.

**Structured output.** Write machine-parseable output (JSON) to stdout. Write human-readable progress, diagnostics, and warnings to stderr. This separation lets agents parse results while users can still read logs.

**Meaningful exit codes.** Use consistent exit codes so agents can branch on results without parsing output:
- `0` — success / clean / no issues
- `1` — actionable result (issues found, changes needed, migration incomplete)
- `2` — usage error, invalid arguments, or infrastructure failure

**Self-documenting.** Support `--help` with a description, argument list, and concrete usage examples. The help text is the script's API contract — agents read it to learn invocation syntax.

**Safe by default.** Destructive operations (writing files, modifying state) should support `--dry-run` to preview changes without side effects. Default to the safe path; require explicit flags to modify anything.

**Idempotent.** Running a script twice with the same inputs should produce the same result. Don't create duplicates, append repeatedly, or leave partial state on failure.

**Minimal dependencies.** Prefer standard library only so scripts run with just `python3` and no package manager. When external packages are necessary, declare them with inline metadata (e.g., PEP 723 for Python) so the script remains self-contained.

### File Structure

```
~/.agents/skills/<skill-name>/
  SKILL.md
  scripts/
    check-something.py
    do-something.sh
```

### Documenting Scripts in SKILL.md

Add an `## Available Scripts` section at the end of the SKILL.md with:
- Script name and one-line description
- Usage examples (copy-pasteable commands)
- Exit codes and their meanings
- Key output fields (for JSON output)

---

## Cached User Context

Some skills need user-specific inputs (GitHub username, team workflow, org name, etc.) that don't change between invocations. Rather than asking every time or requiring upfront configuration, skills should **ask once and remember**.

### The Pattern

1. **Check** the memory files named in the skill for previously cached answers
2. **If found** — use cached values as defaults and proceed without asking
3. **If not found** — ask the user, then **save answers** to the named memory file
4. **Conversation overrides** always win — if the user provides a value in the current conversation, use it (and optionally update the cache)

### Naming Memory Files

Name memory files by **topic**, not by skill. Multiple skills can reference the same memory file when they share context. Every memory file a skill reads or writes must be **explicitly named in that skill** — agents should never invent new memory file names at runtime.

Examples:
- `/memories/github-identity.md` — username, org, team workflow (referenced by `pr-dashboard`, `pr-workflow`, etc.)
- `/memories/pr-dashboard.md` — dashboard-specific preferences referenced only by that skill

Memory files are known configuration files with defined contents. A skill may reference several, and a memory file may be referenced by several skills.

### Adding to a Skill

List the memory files the skill uses and what it expects to find in each. Add a brief section before any user-question phase:

```markdown
**Cached context:** Before asking, check `/memories/<topic>.md` for previously saved
answers. If found, use them and proceed — only re-ask if something looks stale or the user
requests changes. If not found, ask the questions below, then save the answers to
`/memories/<topic>.md` for future runs.
```

### Rules

- Every memory file a skill uses must be **named explicitly in that skill** — agents must not create ad-hoc memory files
- Use the `memory-access` skill's helper scripts (`read-memory.sh`, `write-memory.sh`) for all reads and writes
- Name memory files by topic — shared context lives in a single file, not duplicated per skill
- Only cache **stable inputs** — things that rarely change (username, org, team workflow). Don't cache volatile state (current PR list, branch names)
- Keep the format simple — key: value pairs or short bullet points
- Never cache secrets or tokens
- The user can always override cached values in conversation
