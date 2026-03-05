---
name: scanBranch
description: Scan the current branch diff for dead code, security issues, and refactoring opportunities
argument-hint: Optionally specify which scan types to run (dead-code, security, refactoring, diff-quality) or leave blank for all
agent: Implementation
model: 'Claude Sonnet 4.5'
---
Scan all changes on the current branch for quality issues.

## Goal

Review the diff between the current branch and its base branch. Identify dead code, security issues, refactoring opportunities, and diff quality problems. If the user specified scan types, limit to those; otherwise run all four.

## Context

- Get the list of changed files: `git diff origin/<default-branch>..HEAD --name-only`
- CodeScanner subagents are available for delegating scan work
- Each CodeScanner can handle a subset of files or scan types

## Output

Present findings grouped by category, sorted by severity (high → medium → low). For each finding include: file:line, description, and suggested fix. Deduplicate if multiple scans cover overlapping files.
