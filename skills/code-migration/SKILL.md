---
name: code-migration
user-invokable: false
description: 'Code migration and refactoring cleanup. Use for: moving code, migrating functions, refactoring files, removing dead code, orphaned imports, file deletion, code consolidation, function signature changes.'
---
# Code Migration

## Migration Verification Workflow

When code is moved from one location to another (e.g., `utils/emails.ts` → `services/email-triggers.ts`):

### 1. Identify all imports of the old location
```bash
grep -rn "from.*old/path" src/ test/ --include="*.ts"
grep -rn "import.*OldModule" src/ test/ --include="*.ts"
```

### 2. Update all consumers to use new location
- Update import paths
- Handle any function signature changes
- Update type imports if moved

### 3. Search for orphaned files
After migration, check if the source file has any remaining exports that are still used:
```bash
# Find all exports from the old file
grep -E "^export" src/old/path.ts

# For each export, verify no imports remain
grep -rn "exportName" src/ --include="*.ts" | grep -v "old/path"
```

### 4. Delete orphaned files
If no imports remain:
- Delete the source file
- Delete associated test files
- Verify build still passes: `pnpm tsc --noEmit`

## Function Signature Changes

When changing a function's signature during migration:

### Create a comparison script
For critical functions, create a script to verify behavior equivalence:
```typescript
// scripts/compare-migration.ts
// 1. Copy both OLD and NEW implementations
// 2. Create mock inputs
// 3. Capture outputs from both
// 4. Compare and report differences
```

### Document intentional changes
If the migration intentionally changes behavior (e.g., fixing a bug):
- Note it in the PR description
- Add a test case covering the fix
- Example: "Fixed hardcoded URL bug - now correctly uses brand domain"

## Cleanup Checklist

After completing a migration:

- [ ] All imports updated to new location
- [ ] Old file deleted (if fully migrated)
- [ ] Old test files deleted or updated
- [ ] TypeScript compilation passes
- [ ] All tests pass
- [ ] No orphaned imports remain

## Common Migration Patterns

### File consolidation
Multiple files → single service:
```
utils/email-helpers.ts  ─┐
utils/email-sender.ts   ─┼──► services/email.ts
utils/email-templates.ts─┘
```

### Layer separation
Monolithic file → routes + services:
```
routes/orders.ts (with business logic)
    ↓
routes/orders.ts (thin HTTP layer)
services/orders.ts (business logic)
```

### Type extraction
Inline types → shared types:
```
services/foo.ts (inline interfaces)
    ↓
types/foo.ts (exported interfaces)
services/foo.ts (imports from types)
```

## Rollback Strategy

If migration causes issues:
1. Keep old file until new code is verified in production
2. Use feature flags for gradual migration
3. Add deprecation warnings to old code before removal

---

## Available Scripts

### find-orphaned-imports.py
Finds all files that still import from a given source path. Verifies migration completeness.

```bash
# Check for remaining imports
python3 scripts/find-orphaned-imports.py src/utils/emails.ts

# Also list exports and cross-reference
python3 scripts/find-orphaned-imports.py src/old-module.ts --check-exports

# Custom search directories
python3 scripts/find-orphaned-imports.py lib/helpers.js --search-dirs src,test,lib

# Human-readable output
python3 scripts/find-orphaned-imports.py src/utils/emails.ts --format text
```

**Exit codes:** 0 = no imports remain (safe to delete), 1 = imports still exist, 2 = error

**JSON output fields:** `safe_to_delete`, `import_count`, `importing_files[]`, `references[]`, `exports[]` (with --check-exports)
