---
name: resetProject
description: Reset the current project to a clean state on the default branch
argument-hint: Optionally specify the project name if not in a project directory
agent: Implementation
model: 'GPT-5 mini'
---
Reset the current project to a clean state on its default branch.

## Steps

1. **Follow the `project-reset` skill workflow**
   Identify the project from the current directory, switch to the default branch, fetch and pull latest, and apply any developer stash if needed.
