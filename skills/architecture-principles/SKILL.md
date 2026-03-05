---
name: architecture-principles
user-invokable: false
description: 'Software architecture and design principles. Use for: architecture, design patterns, single responsibility, decoupling, modularity, composition, code organization, refactoring.'
---
# Architecture Principles

## Function Design

### Single Responsibility
- ONE function = ONE job
- If explaining requires "and", consider extraction
- When a function feels too long, look for natural boundaries

### Naming
- Name functions for what they RETURN or EFFECT, not internals
- Use descriptive, action-oriented names
- Include context: `validateUserEmail` not `validate`

### Purity
- Prefer pure functions: same inputs → same outputs
- Minimize side effects
- When side effects are needed, make them explicit

## Module/File Design

### Single Responsibility
- ONE file = ONE responsibility
- Ask: "What is the ONE reason this file would change?"
- Group by responsibility, not by type

### API Surface
- Export a small, focused public API
- Keep helpers private
- When a file feels unwieldy, extract cohesive pieces

### Naming
- Avoid "utils" or "helpers" junk drawers
- Name modules for their domain purpose

## Decoupling Patterns

### Dependency Injection
- Pass dependencies as arguments when it improves testability
- Depend on abstractions, not concrete implementations

### Circular Dependencies
- If A needs B and B needs A, extract shared logic to C
- Keep dependency graphs acyclic

### State Management
- Keep state localized
- Global/shared state should be rare and explicit
- Export shared state rather than duplicating it

## Composition Over Complexity

### Building Behavior
- Build complex behavior by combining simple functions
- Avoid adding conditionals; prefer composition
- Prefer `processUsers(users.filter(isActive).map(normalize))` over a single function with internal filtering

### Reusability
- Prefer general purpose functions over highly specific ones
- Extract repeated patterns into reusable functions when duplication becomes a burden

## Entity-Relationship First

When planning:
- Identify entities (nouns) before operations (verbs)
- Map relationships before designing functions
- Entities change less often than operations

## Parameter Independence

- Only include parameters that are truly independent
- If a parameter can be derived from another, derive it inside the function
- Don't pass both `employer` and `brand` if brand comes from employer

## Data Transformation Over Configuration

- Prefer transforming data to the desired shape over passing options
- The receiving function shouldn't need to know how to transform
- Data should arrive in the right shape

## File Organization

- Plan for small, focused files over large multi-purpose ones
- Group by feature/domain, not by technical layer
- Prefer `user/` over `controllers/`, `services/`, `models/`

## AI-Readability

These principles optimize code for AI-assisted editing and navigation:

### Locality Over Abstraction
- A 100-line file with one cohesive concern is better than 4 files of 25 lines that require cross-file navigation
- Don't split files just for size — split when responsibilities are genuinely unrelated
- When related code lives together, AI needs less context to make correct edits

### Predictability Over Cleverness
- Consistent patterns across the codebase are more valuable than locally optimal solutions
- When adding a new instance of an existing pattern, match the structure of existing instances exactly
- AI pattern-matches against existing code — inconsistency is the #1 source of AI errors

### Explicitness Over Brevity
- Explicit imports, literal strings, and direct references are searchable; dynamic keys, magic re-exports, and deep aliases are invisible
- Fully typed function signatures at boundaries serve as contracts AI can read without tracing implementations
- Name functions and variables for what they do, not for internal mechanisms — names are the cheapest form of documentation for AI

### Composition Depth
- Method chains ≤3 deep are fine; beyond that, break into named intermediate steps for safe mid-chain editing
- Prefer flat, linear code over deeply nested abstractions that require reading N files to understand one operation
