---
name: commitCurrentChanges
description: Stage and commit current branch changes with a conventional commit message
argument-hint: Optionally describe what the changes are for to help generate a better commit message
agent: Implementation
model: 'GPT-5 mini'
---
Review my current uncommitted changes, stage the relevant files, generate a conventional commit message, and commit.

## Steps

1. **Identify the workspace root(s)**
   Run `git status` (and `git status` inside any submodule/package directories that have their own repos) to see all uncommitted changes.

2. **Review the diff**
   Run `git diff` and `git diff --cached` to understand what changed. If there are changes across multiple repos (e.g., packages/ submodules), review each one separately.

3. **Filter out files that should NOT be staged**
   Follow the `git-push` skill's sensitive-content scan to identify files that should be excluded. Additionally exclude:
   - Agent, skill, and prompt files (`~/.agents/`) — these are personal tooling, not project source

   If any blocking issues are found (secrets, credentials), report them and do NOT commit those files.

4. **Stage the appropriate files**
   Use `git add` to stage only the safe, relevant files. Prefer staging specific files rather than `git add .` to avoid accidentally including unwanted changes.

5. **Generate a commit message**
   Follow the `git-commits` skill for commit message formatting and conventions.

6. **Commit**
   Run `git commit -m "<message>"` (or with body using multi-line format).

7. **If multiple repos have changes**, repeat steps 4-6 for each repo separately.

8. **Report back** with a summary of what was committed in each repo.
