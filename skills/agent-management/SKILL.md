---
name: agent-management
description: 'Create, edit, and improve agents, skills, prompts, instructions, and hooks. Use for: create agent, edit agent, new agent, create skill, new skill, create prompt, new prompt, create instruction, create hook, agent management, skill conventions, prompt conventions, instruction conventions, hook conventions.'
---
# Agent Management

## When to Use
- Creating a new agent, skill, prompt, instruction, or hook
- Editing or improving an existing agent/skill/prompt/instruction/hook
- Reviewing a conversation to extract agent improvements
- Deciding which primitive to use for a new rule or workflow

## File Locations

**IMPORTANT:** As a first step, always `list_dir` on `~/.agents/` to establish directory access upfront. This ensures a single approval covers all subdirectory reads/edits for the session.

| Primitive | Location | Naming |
|-----------|----------|--------|
| Agents | `~/.agents/agents/[AgentName].agent.md` | PascalCase |
| Skills | `~/.agents/skills/[skill-name]/SKILL.md` | lowercase-hyphenated |
| Prompts | `~/.agents/prompts/[promptName].prompt.md` | camelCase |
| Instructions | `~/.agents/instructions/[name].instructions.md` | lowercase-hyphenated |
| Hooks | `~/.agents/hooks/global.json` + `scripts/[name].sh` | lowercase-hyphenated |
| Tool Sets | `~/.agents/toolsets/[name].toolsets.jsonc` | lowercase |

Agent, skill, prompt, and instruction files are user-local configuration — never stage or commit them.

---

## Architecture

### How It All Fits Together

The system has five primitives, each with a distinct role:

```
User
  ↓ (goal via prompt or direct message)
Agent (values + tool access + constraints)
  ↓ (loads relevant context)
Skills (domain knowledge, methodology, and contextual rules)
  ↓ (operates within)
Instructions (user preferences, mandatory policies — always active)
  ↓ (at lifecycle points)
Hooks (deterministic behavior — scripts triggered by agent operations)
```

**The approach to any task is emergent.** It is not prescribed by any single primitive. It emerges from:
- The **goal** (provided by the user or prompt)
- The agent's **values** (what it cares about, embedded in the agent)
- **Domain knowledge** (facts the agent can't derive, provided by skills)
- **User preferences** (mandatory approaches the user requires, provided by instructions)

No primitive should dictate step-by-step HOW to accomplish work. Instead, each primitive contributes its piece, and the agent synthesizes an approach.

### Each Primitive's Role

#### Agents — Values + Tool Access + Constraints

Agents encode three layers:

1. **Tool access** — what capabilities exist (read vs edit vs execute vs GitHub vs browser)
2. **Hard constraints** — scope boundaries and never-do rules
3. **Values** — what the agent cares about across all tasks (quality, thoroughness, correctness, security, etc.)

Agents do NOT contain workflows, domain knowledge, or approach prescriptions. Orchestrators provide the **goal**. Agents bring **values**. The approach emerges from values applied to the goal within the constraints of instructions and available domain knowledge.

#### Skills — Domain Knowledge & Contextual Rules

Skills are organized by **domain**. Each skill contains everything an agent needs for that domain — facts, methodology, and rules — in one place.

| Valid Skill Content | Description |
|---|---|
| Environmental facts | Where things live, how the workspace is structured |
| Codebase conventions | Testing frameworks, template engines, schema patterns |
| Reference patterns | How existing code is structured as a model to follow |
| Available tools/specialists | What subagents exist, their tool access, their values |
| Format/reporting standards | Commit message format, report structure, diagram conventions |
| Technical mechanics | How concurrency works, how tool calls behave |
| Workflow methodology | Phases, checklists, verification steps for standardized workflows |
| Contextual standards | Naming rules, code style, commit format — rules for this domain |
| Domain-specific requirements | i18n rules, testing patterns, review priorities — things that only apply in this context |

Within a skill, **voice follows content type**:
- Facts → descriptive: "This codebase uses X", "The pattern is Y", "Z causes W"
- Rules → prescriptive: "ALWAYS X", "NEVER Y" (in a `## Rules` section)

Both live together because the rule makes no sense without its context.

Skills live in skills (rather than instructions) because they should only be loaded when relevant, not injected into every prompt.

| Invalid Skill Content | Why |
|---|---|
| Implementation approach prescriptions | Tells the agent HOW to solve a specific problem — should emerge from values + goal |
| Dispatch recipes | Overrides agent judgment on how to sequence work |
| Reasoning instructions | Belongs in agent values or the user's prompt |

**Note:** Workflow methodology IS valid domain knowledge. A skill can describe a standardized workflow (phases, checklists, verification steps) without prescribing how to solve the underlying problem. The distinction: "Phase 1: Research, Phase 2: Implement, Phase 3: Verify" is methodology. "Use grep to find X, then open file Y, then edit line Z" is implementation prescription.

#### Prompts — Goals (The WHAT)

Prompts define what the user wants done — the task and desired outcome, plus relevant context. Priorities are NOT defined in prompts; they come from the agent's values or are provided directly by the user at invocation time.

Prompts should NOT prescribe step-by-step approaches. They describe the destination, not the route.

#### Instructions — User Preferences & Mandatory Policies

Instructions are always-on rules that apply globally (or to files matching an `applyTo` glob). They represent things the user requires regardless of agent values:

| Instruction Type | Description |
|---|---|
| **User style preferences** | Communication tone, verbosity, formatting |
| **User-mandated approaches** | Strategies the user requires even if an agent's values might suggest otherwise |
| **Safety policies** | Preventing dangerous or destructive operations |
| **Correctness policies** | Mandatory verification steps |
| **Tool restrictions** | Limiting how certain tools may be used |

Instructions override agent autonomy. An agent whose values might suggest a different approach must still comply with instructions. The agent's values then shape HOW it satisfies that constraint.

#### Hooks — Deterministic Behavior at Lifecycle Points

Hooks add deterministic behavior at specific points in an agent's operation (before/after tool calls, etc.). They run scripts that can block, modify, or augment tool calls. Currently used primarily for rule enforcement, but the framework supports any deterministic behavior tied to agent lifecycle events.

### Choosing the Right Primitive

| Need | Primitive | Convention Skill |
|---|---|---|
| Distinct tool access, values, or constraints | **Agent** | `agent-conventions` |
| Domain knowledge, methodology, or contextual rules | **Skill** | `skill-conventions` |
| User preference or mandatory policy (always-on) | **Instruction** | `instruction-conventions` |
| Reusable tool profile | **Tool Set** | `agent-conventions` |
| Pre-written task definition | **Prompt** | `prompt-conventions` |
| Rules tied to file types | **Instruction** | `instruction-conventions` |
| Deterministic behavior at lifecycle points | **Hook** | `hook-conventions` |

**The key boundary:** Skills are contextual (loaded when relevant). Instructions are always-on (injected into every prompt). If a rule always matters regardless of what the agent is doing → instruction. If it only matters when working in a specific domain → skill.

**After choosing the primitive, follow the corresponding convention skill for templates, rules, and examples.**

### Valid vs Invalid Agent Differentiators

**Create a new agent when it has unique:**
- **Tool access** — different capabilities than existing agents
- **Values spanning multiple task types** — a distinct perspective that applies across varied work

**Do NOT create a new agent when the only difference is:**
- **Task type** — use the same agent with different prompts
- **Reasoning style for one task** — provide it as context in the prompt
