---
name: pr-comment-drafting
description: 'Draft natural PR comment replies. Use for: PR reply, review comment, draft response, GitHub comment, PR thread, code review reply.'
---
# PR Comment Drafting

## When to Use
- Drafting a reply to a PR review comment or thread
- Responding to reviewer questions about code changes

## Workflow

1. **Research first** — understand exactly why the code is the way it is before drafting anything
2. **Draft before posting** — always show the draft to the user for review before posting
3. **Iterate on feedback** — refine until the user says to post it
4. **Post via GitHubOps subagent** — never use `gh` CLI directly

## Writing Rules

**Tone:**
- Write like a normal developer typing a quick reply, not a formal explanation
- No corporate or technical-writing voice

**Content:**
- Include only the minimum information needed to answer the reviewer's question
- Lead with the reason, not a restatement of the observation ("both are needed" is implied if you explain why each exists)
- Drop filler opening sentences that just acknowledge what the reviewer said

**Formatting:**
- Use inline backticks for code references — that's normal in GitHub comments
- No bullet lists, tables, or headers unless the user asks for them
- No bold, no blockquotes, no horizontal rules

**Word choice:**
- No em-dashes (—), use commas or periods instead
- No "we/us/our" — use "the" when referring to the codebase or system
- No "essentially", "effectively", "notably", "specifically", "importantly"
- No "it's worth noting", "it should be noted", "as mentioned"

## Rules

**ALWAYS:**
- Research the actual code to back up the explanation
- Draft first and wait for user approval before posting
- Apply user feedback on each revision without re-introducing previous issues

**NEVER:**
- Post a comment without the user saying to post it
- Add explanatory filler the reviewer didn't ask about
- Use formatting that looks AI-generated
