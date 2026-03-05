---
name: code-style-rules
user-invokable: false
description: 'Code style and naming conventions. Use for: variable naming, code style, naming conventions, abbreviations, loop variables, renaming, refactoring names, descriptive names, clean code.'
---
# Code Style Rules

## Variable Naming

### Forbidden Short Names

These names are NOT acceptable, even in small scopes:

| Bad | Good Alternative |
|-----|------------------|
| `i`, `j`, `k` | `index`, `rowIndex`, `columnIndex`, `userIndex` |
| `e`, `err` | `error`, `validationError`, `networkError` |
| `cb` | `callback`, `onComplete`, `handleResult` |
| `fn` | `handler`, `processor`, `transformer` |
| `res`, `req` | `response`, `request`, `userResponse` |
| `el` | `element`, `listItem`, `buttonElement` |
| `acc` | `accumulator`, `result`, `total` |
| `val` | `value`, `currentValue`, `inputValue` |
| `obj` | `user`, `config`, `options` (use the actual type) |
| `arr` | `items`, `users`, `results` (use the actual contents) |
| `tmp`, `temp` | Name it for what it holds |

### Forbidden Abbreviations

Spell out words when the full version is short and more readable:

| Bad | Good |
|-----|------|
| `svc` | `service`, `faxService` |
| `mgr` | `manager`, `sessionManager` |
| `cfg` | `config` |
| `ctx` | `context` |
| `btn` | `button` |
| `msg` | `message` |
| `usr` | `user` |
| `idx` | `index` |

**The test:** If spelling it out adds only a few characters and improves clarity, use the full word.

### Loop Index Naming

Loop indices should reflect what they're iterating:

| Iterating | Use |
|-----------|-----|
| Users | `userIndex` |
| Rows | `rowIndex` |
| Items in group | `itemIndex` |
| Nested loops | `groupIndex`, `itemIndex` (not `i`, `j`) |

## Comment Rules

### Remove These Comments

```js
// Bad: Section dividers
// =====================================
// User Authentication Functions
// =====================================

// Bad: Restates the obvious
const count = 0; // Initialize count to zero

// Bad: Commented-out code
// const oldImplementation = doThingOldWay();

// Bad: Stale TODOs
// TODO: Add validation (already added below)
```

### Keep These Comments

```js
// Good: Explains WHY
// Using setTimeout(0) to defer execution until after the current 
// call stack clears, preventing race condition with auth state update
setTimeout(handleAuth, 0);

// Good: Documents non-obvious behavior
// The API returns dates in UTC but without timezone indicator,
// so we must explicitly parse as UTC
const date = parseAsUTC(apiDate);

// Good: Warns about gotchas
// WARNING: This array is mutated by processItems() - pass a copy
```

## Function Naming

- Use descriptive, action-oriented names conveying purpose
- Name functions for what they RETURN or EFFECT, not internals
- Include context: `validateUserEmail` not `validate`

## Code Style

- Extract magic numbers as named constants
- Prefer early returns to reduce nesting
- Group related logic together
- Keep functions focused on a single responsibility
- Prefer general purpose functions over highly specific ones
- Export shared state when needed rather than duplicating
