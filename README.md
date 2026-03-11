# agentz

A modular AI agent configuration system for GitHub Copilot Chat in VS Code. Clone it, customize it, make it yours.

## Quick Start

1. **Clone the repo** anywhere you like:
   ```bash
   git clone https://github.com/<your-fork>/agentz.git ~/path/to/agentz
   ```

2. **Tell VS Code where to find it** — open Settings (JSON) and add these five entries, pointing to your clone location:
   ```jsonc
   // Prompts — shows up when you type "/" in chat
   "chat.promptFilesLocations": {
       "~/path/to/agentz/prompts": true
   },
   // Agents — shows up in the agent selector dropdown
   "chat.agentFilesLocations": {
       "~/path/to/agentz/agents": true
   },
   // Skills — domain knowledge loaded by agents on demand
   "chat.agentSkillsLocations": {
       "~/path/to/agentz/skills": true
   },
   // Instructions — injected into every conversation automatically
   "chat.instructionsFilesLocations": {
       "~/path/to/agentz/instructions": true
   },
   // Hooks — lifecycle scripts that run before/after tool calls
   "chat.hookFilesLocations": {
       "~/path/to/agentz/hooks": true
   },
   ```

3. **Try a prompt** — open the chat panel, type `/` and pick one (e.g., `planFeature`, `commitCurrentChanges`)

4. **Pick an agent** — click the agent selector in chat and choose `Implementation` or `Research`

No build step, no package install, no dependencies — just markdown and shell scripts.

## How It Works

The system has five primitives. Each plays a distinct role, and the agent's approach to any task **emerges** from their combination:

```
User
  ↓ (goal via prompt or direct message)
Agent (values + tool access + constraints)
  ↓ (loads relevant context)
Skills (domain knowledge, methodology, contextual rules)
  ↓ (operates within)
Instructions (user preferences, mandatory policies — always active)
  ↓ (at lifecycle points)
Hooks (deterministic behavior — scripts triggered by agent operations)
```

No single primitive dictates step-by-step how to accomplish work. The approach is emergent from the goal, the agent's values, domain knowledge from skills, and user preferences from instructions.

## Directory Structure

```
~/.agents/
├── agents/          Agent definitions — who does what, with which tools
├── prompts/         Reusable task templates — one-click workflows
├── skills/          Domain knowledge — facts, methodology, rules per domain
├── instructions/    Always-on rules — injected into every conversation
├── hooks/           Lifecycle scripts — deterministic enforcement
│   ├── global.json  Hook configuration
│   └── scripts/     Shell scripts that run at lifecycle events
└── memories/        User-specific config, managed by agents (gitignored)
```

## The Primitives

### Agents — Values + Tool Access + Constraints

Agents define **who** does the work: what tools they can use, what they care about, and what's out of bounds. There are two user-facing agents and many specialized subagents.

| Agent | Role | Tools |
|-------|------|-------|
| **Implementation** | Read-write. Implements, tests, debugs, commits, pushes. | Edit, terminal, search, subagent delegation |
| **Research** | Read-only. Investigates, plans, reviews PRs, creates diagrams. | Search, terminal (read-only), subagent delegation |

Specialized subagents handle narrowly scoped work:

| Subagent | Purpose |
|----------|---------|
| SourceWriter | Write code within file boundaries set by orchestrator |
| CodeExplorer | Deep codebase investigation — patterns, data flow |
| CodeScanner | Dead code, security, and refactoring scanning |
| GitHubOps | PR creation, issue linking, GitHub API operations |
| BrowserTest | Chrome DevTools, UI testing, visual verification |
| DatabaseOps | MongoDB queries, data inspection |
| DocFetcher | Library documentation lookup (via Context7) |
| WebSearcher | General web search for technical info |

Review and planning subagents provide **multi-perspective** analysis:

| Category | Subagents |
|----------|-----------|
| **Reviewers** | SecurityReviewer, ArchitectureReviewer, PerformanceReviewer, MaintainabilityReviewer |
| **Planners** | PragmatistPlanner, CraftspersonPlanner, AdvocatePlanner, SecurityPlanner, ScalabilityPlanner, ConceptualistPlanner |
| **Investigators** | DataIntegrityInvestigator, ControlFlowInvestigator, ConcurrencyInvestigator, EnvironmentInvestigator |

**File format:** `agents/AgentName.agent.md` (PascalCase)

### Prompts — Reusable Task Templates

Prompts are pre-written task definitions you invoke with `/` in the chat panel. Each prompt targets an agent and describes the goal — the agent and skills handle the how.

| Prompt | Agent | What It Does |
|--------|-------|-------------|
| `implementTicketAuto` | Implementation | Full autonomous ticket-to-PR pipeline from a GitHub issue URL |
| `implementTicketManual` | Implementation | Same pipeline but pauses for plan approval before coding |
| `planFeature` | Research | Research codebase and create a diagram-first implementation plan |
| `reviewMyBranch` | Research | Self-review current branch diff using priority checklist (P1-P10) |
| `reviewPR` | Research | Review a colleague's PR with colleague-mode priorities |
| `commitCurrentChanges` | Implementation | Stage, generate conventional commit message, commit |
| `cleanupBranch` | Implementation | Polish committed changes — diff bloat, naming, style |
| `scanBranch` | Implementation | Scan branch diff for dead code, security issues, refactoring |
| `testCurrentBranch` | Implementation | Create test plan and manually test current changes |
| `fixPRFeedback` | Implementation | Fetch PR review comments and address them one by one |
| `resetProject` | Implementation | Reset to clean state on default branch |
| `reviewSession` | Research | Analyze current session to extract agent/skill improvements |
| `tuneModels` | Research | Compare AI models and update agent model assignments |

**File format:** `prompts/promptName.prompt.md` (camelCase)

### Skills — Domain Knowledge

Skills contain everything an agent needs for a specific domain: facts, patterns, methodology, and rules. They're loaded on demand — only when the task is relevant.

Skills cover areas like:
- **Workflow methodology** — `autonomous-workflow`, `implementation-workflow`, `planning`, `testing-workflow`
- **Git operations** — `git-commits`, `git-diffs`, `git-push`, `git-sync`
- **Code quality** — `code-style-rules`, `architecture-principles`, `code-cleanup`, `code-migration`
- **PR lifecycle** — `pr-review`, `pr-workflow`, `pr-comment-drafting`
- **Multi-agent orchestration** — `multi-agent-review`, `multi-agent-planning`, `multi-agent-debugging`
- **Meta** — `agent-management`, `agent-conventions`, `skill-conventions`, `prompt-conventions`, `hook-conventions`, `instruction-conventions`
- **Project-specific** — `project-registry`, `project-reset`, `worktree-management`
- **Tech-specific** — `blaze-gotchas`, `i18n-text`, `mermaid-diagrams`
- **Agent operations** — `subagent-dispatch`, `subagent-response`, `model-selection`, `session-review`
- **Investigation** — `research`, `debugging`
- **Memory infrastructure** — `memory-access` (read/write helpers for user config)

Skills can also include executable scripts in a `scripts/` subdirectory for automated checks and transformations.

**File format:** `skills/skill-name/SKILL.md` (folder is lowercase-hyphenated, file is always `SKILL.md`)

### Instructions — Always-On Rules

Instructions are injected into every conversation automatically. They represent non-negotiable user preferences.

| Instruction | Purpose |
|-------------|---------|
| `agent-autonomy` | When to ask the user vs proceed independently |
| `no-command-chaining` | Only allow `cd && command`, no arbitrary shell chaining |
| `no-terminal-edits` | Never use `sed`, `cat >`, heredocs to edit files — use built-in tools |
| `parallel-execution` | Parallelize independent work whenever possible |
| `response-formatting` | Output structure, diagrams, tables, file link format |

**File format:** `instructions/name.instructions.md` (lowercase-hyphenated)

### Memories — User-Specific Configuration

The `memories/` directory stores user-specific information that skills need to function — things like your GitHub username, project table, workspace layout, team review pipeline, and i18n configuration. This directory is **gitignored** so your personal data never enters version control.

Memories exist because skills need to be generic while still working with your specific setup. Instead of hardcoding project names, org details, or workflow preferences into skills, the system uses a **cache-or-ask pattern:**

1. When a skill runs and needs user-specific info, it checks for a cached memory file
2. If no cache exists, it asks you the relevant questions and saves your answers
3. On subsequent runs, it reads from cache — no repeated questioning

This means a fresh clone works immediately. The first time you invoke a workflow that needs project info, the agent asks you; after that, it remembers.

**What belongs in memory:**
- Your projects, workspace layout, build commands, and test configurations
- Your GitHub identity, org, and team review pipeline
- Your i18n system, language files, and template syntax
- Project-specific scripts, setup steps, and operational knowledge that's specific to your environment
- Any stable information that skills need but shouldn't be in the public repo

**What does NOT belong in memory:**
- Domain knowledge, methodology, or rules — that's skill content
- Volatile state like current branch names or PR lists
- Secrets or tokens

See the `skill-conventions` skill for how to add memory-backed config to a new skill.

**File format:** `memories/topic-name.md` (gitignored, managed by agents via the `memory-access` skill)

### Hooks — Deterministic Enforcement

Hooks run shell scripts at agent lifecycle events. Unlike instructions and skills (which are advisory), hooks are **deterministic** — they execute regardless of what the agent decides.

**Pre-tool hooks** (run before a tool executes):

| Hook | Purpose |
|------|---------|
| `block-hooks-edit.sh` | Require approval before editing hook files |
| `block-force-push.sh` | Block `git push --force` (require `--force-with-lease`) |
| `scan-before-push.sh` | Scan diff for secrets/debug artifacts before push |
| `sandbox-git.sh` | Auto-approve safe git ops, block dangerous ones |
| `auto-approve-simple.sh` | Auto-approve non-destructive terminal commands |

**Post-tool hooks** (run after a tool completes):

| Hook | Purpose |
|------|---------|
| `auto-format.sh` | Auto-format edited files with Prettier |

**File format:** `hooks/global.json` (config) + `hooks/scripts/name.sh` (scripts)

## Common Workflows

### "I have a GitHub issue to implement"

1. Open chat, type `/implementTicketAuto` and paste the issue URL
2. The Implementation agent fetches the issue, researches the codebase, plans, creates a worktree, implements, self-reviews, pushes, and opens a draft PR — all autonomously

Or use `/implementTicketManual` if you want to approve the plan before coding starts.

### "I want to plan a feature before building it"

1. Type `/planFeature` and describe what you want to build
2. The Research agent investigates the codebase, creates a diagram-first plan, and presents it
3. Click the "Implement" handoff button to pass the plan to the Implementation agent

### "I want to review my changes before pushing"

1. Type `/reviewMyBranch`
2. The Research agent diffs your branch, runs through the self-review priority checklist (P1-P10), and presents findings one at a time
3. Fix issues, then `/commitCurrentChanges` and push

### "I need to review a colleague's PR"

1. Type `/reviewPR` and paste the PR URL
2. The Research agent fetches the PR and reviews with colleague-mode priorities
3. Approve drafted comments before they're posted

### "I want multiple perspectives on my code"

The Research agent can orchestrate multi-perspective reviews, plans, and debugging sessions using specialized subagents in parallel:
- **Review:** SecurityReviewer + ArchitectureReviewer + PerformanceReviewer + MaintainabilityReviewer all analyze your code independently, findings are merged
- **Plan:** 6 planners (Pragmatist, Craftsperson, Advocate, Security, Scalability, Conceptualist) each propose an approach, then they're synthesized
- **Debug:** DataIntegrity + ControlFlow + Concurrency + Environment investigators each pursue different hypotheses in parallel

### "I need to commit my changes"

1. Type `/commitCurrentChanges`
2. The agent reviews your diff, filters out sensitive files, generates a conventional commit message, and commits

### "I want to clean up before opening a PR"

1. `/cleanupBranch` — polish naming, style, diff quality
2. `/scanBranch` — scan for dead code, security issues, refactoring opportunities
3. `/reviewMyBranch` — final self-review

### "I want to improve the agents themselves"

1. Type `/reviewSession` after a work session
2. The Research agent analyzes the conversation for improvement signals
3. Approved changes are handed off to Implementation to apply

## Customization Guide

### Adding a New Prompt

Create `prompts/myPrompt.prompt.md`:

```markdown
---
name: myPrompt
description: What this prompt does
argument-hint: What optional input the user provides
agent: Implementation
---
One-sentence task summary.

## Steps

1. **Step name**
   Instructions with clear success criteria.
```

### Adding a New Skill

Create `skills/my-skill/SKILL.md`:

```markdown
---
name: my-skill
description: 'Brief description. Use for: keyword1, keyword2, keyword3.'
---
# My Skill

Domain knowledge — facts, patterns, how things work.

## Rules

**ALWAYS:**
- Required behavior

**NEVER:**
- Prohibited behavior
```

Then reference it in an agent's `<skills>` section: `Follow the 'my-skill' skill for [domain].`

### Adding a New Instruction

Create `instructions/my-rule.instructions.md`:

```markdown
---
name: My Rule
description: What this enforces
applyTo: '**'
---
# My Rule

Short, prescriptive rules. Keep concise — this is always injected.
```

### Adding a New Hook

1. Create the script in `hooks/scripts/my-hook.sh`
2. Add an entry in `hooks/global.json` under the appropriate lifecycle event
3. Review carefully — hooks execute with full system permissions

### Adding a New Agent

Only create a new agent when it has **unique tool access, constraints, or values**. If the difference is just the task type, create a prompt instead.

See the `agent-conventions` skill for the full template and architecture guide.

## Key Design Principles

- **Emergent behavior** — no single primitive prescribes the full approach. The agent synthesizes from goal + values + domain knowledge + user preferences.
- **Skills are contextual, instructions are global** — if a rule always matters, it's an instruction. If it only matters in a specific domain, it's a skill.
- **Hooks are deterministic** — when a rule MUST be enforced without exception, use a hook. Instructions and skills are advisory.
- **Lean orchestrators** — user-facing agents delegate specialized work to subagents with narrowly scoped tools.
- **Facts are descriptive, rules are prescriptive** — skills describe how things work and prescribe behavior in separate sections.

## What to Customize First

1. **Instructions** — these shape every interaction. Adjust `agent-autonomy`, `response-formatting`, and `parallel-execution` to match your preferences.
2. **Prompts** — add prompts for your common workflows. Start by copying an existing one.
3. **Skills** — add domain knowledge for your tech stack, project structure, and conventions.
4. **Hooks** — adjust safety rails. You may want different auto-approve patterns or additional pre-push checks.
5. **Agents** — the defaults work well for most use cases. Only add agents when you have genuinely different tool/value needs.

## Requirements

- VS Code with GitHub Copilot Chat extension
- Five VS Code settings configured to point at the repo subdirectories (see [Quick Start](#quick-start))
- No other dependencies — everything is markdown and shell scripts
