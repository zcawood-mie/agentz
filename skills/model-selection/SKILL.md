---
name: model-selection
description: 'AI model selection and optimization for agents. Use for: model comparison, model tuning, rate limits, premium requests, model assignment, agent model config.'
---
# Model Selection

## When to Use
- Reviewing or updating model assignments for agents
- Comparing model capabilities for a specific task type
- Optimizing for speed, quality, or rate limit headroom

## Model Tiers (as of Mar 2026)

### Included Models (0x multiplier on paid plans)
| Model | Strengths |
|---|---|
| GPT-5 mini | Reliable default, fast, multimodal, works across languages |
| GPT-4.1 | General-purpose coding |
| GPT-4o | General-purpose, multimodal |

### Budget Models (< 1x multiplier)
| Model | Multiplier | Strengths |
|---|---|---|
| Grok Code Fast 1 | 0.25x | Fast code generation, multi-language |
| Claude Haiku 4.5 | 0.33x | Fast responses with quality output, small tasks |
| Gemini 3 Flash | 0.33x | Fast, lightweight coding questions |
| GPT-5.1-Codex-Mini | 0.33x | Multi-step problem solving, budget tier |

### Mid-Tier Models (1x multiplier)
| Model | Strengths |
|---|---|
| Claude Sonnet 4 | Reliable completions, smart reasoning under pressure |
| Claude Sonnet 4.5 | Multi-file refactoring, hybrid reasoning, agent tasks, architectural planning |
| Claude Sonnet 4.6 | Latest Sonnet — improved quality over 4.5, multiplier may change |
| GPT-5.1 / GPT-5.2 / GPT-5.4 | Complex reasoning, code analysis, technical decisions |
| GPT-5.1-Codex / GPT-5.2-Codex / GPT-5.3-Codex | Agentic software development |
| Gemini 2.5 Pro / Gemini 3 Pro / Gemini 3.1 Pro | Advanced reasoning, long contexts, scientific analysis |

### Premium Models (3x+ multiplier)
| Model | Multiplier | Strengths |
|---|---|---|
| Claude Opus 4.5 | 3x | Complex problem-solving, sophisticated reasoning |
| Claude Opus 4.6 | 3x | Anthropic's most powerful, deep reasoning, complex architecture |
| Claude Opus 4.6 (fast mode) | 30x | Same quality, extreme speed |

### Auto Model Selection
- Available in VS Code via the model picker
- Chooses between Claude Sonnet 4, GPT-5, GPT-5 mini and others
- 10% multiplier discount on paid plans (e.g., Sonnet 4 at 0.9x)
- Falls back to 0x model if rate-limited

## Task-to-Model Mapping

### Deep Reasoning & Debugging
Best for: multi-file debugging, large refactors, architecture planning, trade-off analysis, log/perf analysis.
**Recommended:** Claude Opus 4.6, GPT-5.4, GPT-5.2, Claude Sonnet 4.6, Gemini 3 Pro

### General-Purpose Coding & Agent Tasks
Best for: writing/reviewing functions, code diffs, documentation, error explanation.
**Recommended:** Claude Sonnet 4.6, GPT-5.1-Codex, GPT-5 mini, Grok Code Fast 1

### Fast/Simple/Repetitive Tasks
Best for: small functions, syntax questions, prototyping, quick feedback.
**Recommended:** Claude Haiku 4.5, Gemini 3 Flash, GPT-5 mini (free)

### Agentic Software Development
Best for: multi-step autonomous coding sessions, tool calling, agent mode.
**Recommended:** Claude Sonnet 4.6, GPT-5.2-Codex, GPT-5.3-Codex, GPT-5.1-Codex-Max

### Visual/Multimodal Tasks
Best for: screenshots, diagrams, UI components.
**Recommended:** GPT-5 mini, Claude Sonnet 4.6, Gemini 3 Pro

## Agent Model Assignment Strategy

Match model to the **complexity ceiling** of each agent's typical task. Be vendor-agnostic — pick the best model for the job regardless of provider.

### Current Assignments

| Agent | Model | Multiplier | Rationale |
|---|---|---|---|
| Implementation | `['Claude Opus 4.6', 'GPT-5.4', 'GPT-5.2-Codex']` | 3x → 1x → 1x fallback | Orchestrator — plans, dispatches, verifies |
| Research | `Claude Sonnet 4.6` | 1x | Orchestrator — decomposes, dispatches, synthesizes |
| SourceWriter | `['Claude Opus 4.6', 'GPT-5.4', 'GPT-5.2-Codex']` | 3x → 1x → 1x fallback | Code quality (production + tests) — same reasoning as Implementation |
| CodeScanner | `Claude Sonnet 4.6` | 1x | Critical analysis, pattern recognition |
| CodeExplorer | `Claude Sonnet 4.6` | 1x | Investigative reasoning, same as Research |
| DocFetcher | `GPT-5 mini` | 0x | Structured context7 tool calls — mechanical |
| WebSearcher | `GPT-5 mini` | 0x | Structured web fetch tool calls — lightweight summarization |
| BrowserTest | `GPT-5 mini` | 0x | DOM clicks, screenshots — mechanical |
| DatabaseOps | `GPT-5 mini` | 0x | Structured MCP tool calls — mechanical |
| GitHubOps | `GPT-5 mini` | 0x | API wrapper operations — mechanical |

### Prompt-Level Overrides

Prompts can set `model:` to override their agent's default for specific tasks:

| Prompt | Model Override | Multiplier | Rationale |
|---|---|---|---|
| `commitCurrentChanges` | `GPT-5 mini` | 0x | git add + commit message — trivial |
| `resetProject` | `GPT-5 mini` | 0x | git checkout + pull — trivial |
| `cleanupBranch` | `Claude Sonnet 4.6` | 1x | Diff review needs judgment, not deep reasoning |
| `testCurrentBranch` | `Claude Sonnet 4.6` | 1x | Test execution needs some judgment |
| `reviewMyBranch` | `Claude Sonnet 4.6` | 1x | Self-review needs judgment |
| `reviewPR` | `Claude Sonnet 4.6` | 1x | Code review needs judgment |
| `scanBranch` | `Claude Sonnet 4.6` | 1x | Scan analysis needs pattern recognition |
| `implementTicketAuto` | (inherits Opus 4.6) | 3x | Full feature implementation — needs deep reasoning |
| `implementTicketManual` | (inherits Opus 4.6) | 3x | Full feature implementation — needs deep reasoning |
| `fixPRFeedback` | (inherits Opus 4.6) | 3x | Addressing review comments — needs deep reasoning |
| `tuneModels` | (inherits Sonnet 4.6) | 1x | Model comparison — Research agent task |

### Assignment Principles

1. **Subagents that call MCP tools → 0x models (GPT-5 mini)**. These are structured tool calls, not reasoning tasks.
2. **Mechanical prompts → 0x models**. Committing, resetting, staging — no reasoning needed.
3. **Judgment prompts → 1x models (Sonnet 4.6)**. Diff review, test planning — needs pattern matching.
4. **Implementation prompts → premium model**. Feature work, debugging, refactoring — needs deep reasoning.
5. **Use ordered fallback lists** for critical agents so rate limits don't block work.

### Model Property in Agent Files

Set in YAML frontmatter:
```yaml
model: 'Claude Opus 4.6'           # Single model
model: ['Claude Sonnet 4.6', 'Claude Opus 4.6']  # Ordered fallback
```

If omitted, the model picker selection is used.

## Comparison Methodology

When evaluating whether to change model assignments:

1. **Check the latest docs:** Fetch `https://docs.github.com/en/copilot/reference/ai-models/model-comparison` for current task recommendations
2. **Check multiplier changes:** Fetch `https://docs.github.com/en/copilot/concepts/billing/copilot-requests` for current multiplier table
3. **Match agent to task tier:** Map each agent's typical workload to the task categories above
4. **Optimize for the bottleneck:** If rate limits are the issue, shift support agents down. If quality is the issue, shift up.
5. **Update agent `model:` properties** in `~/.agents/agents/`

## Rules

**ALWAYS:**
- Be vendor-agnostic — pick the best model for each task regardless of provider
- Keep Implementation agent on the highest-quality reasoning model available
- Use 0x (included) models for subagents and mechanical prompts — they're free and fast
- Use ordered fallback lists on critical agents to survive rate limits
- Check GitHub docs for multiplier and model changes before recommending swaps
- Present a before/after comparison table when recommending changes
- Update prompt-level `model:` overrides alongside agent-level changes

**NEVER:**
- Put all agents on the same premium model (wastes rate limit headroom)
- Recommend a model without stating its multiplier
- Use premium models for subagents that just call MCP tools
- Default to a single vendor without comparing alternatives
- Ignore prompt-level overrides when auditing model assignments
