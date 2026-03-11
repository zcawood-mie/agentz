---
name: i18n-text
user-invokable: false
description: 'Internationalization rules for user-facing text. Use for: labels, buttons, placeholders, headings, titles, toasts, alerts, error messages, confirmation dialogs, tooltips, UI text, templates, modals, user-facing strings, hard-coded text.'
---
# i18n Text Rules

## Core Rule

**Never hardcode user-facing strings.** All text visible to users must use i18n translation keys.

This applies to:
- Labels, headings, titles
- Button text
- Placeholder text
- Toast / alert / confirmation messages
- Error messages shown to users
- Tooltip text
- Modal titles and body text
- Empty state messages
- Form validation messages

## How It Works

The i18n system, syntax, and language files are project-specific. Read the cached config from memory:
```bash
~/.agents/skills/memory-access/scripts/read-memory.sh i18n-config
```

If the memory file does not exist, ask the user the following questions (together, not one at a time), then save the answers using `write-memory.sh`:

1. What i18n package/library does your project use? (e.g., `universe:i18n`, `react-intl`, `next-intl`)
2. How are translation keys used in templates/JSX? (provide syntax example)
3. How are translation keys used in JavaScript/TypeScript? (provide syntax example)
4. What is the interpolation syntax? (e.g., `{$var}`, `{var}`, `{{var}}`)
5. Where are the language files located? (e.g., `packages/my-i18n/i18n/`)
6. What language files exist and what languages do they cover?
7. What is the key naming convention? (e.g., `snake_case`, `camelCase`, `dot.separated`)

Use the cached config for all template/JS syntax examples, language file locations, and key naming conventions below.

### In Templates

Use the template syntax from the cached i18n config. Example patterns:
- Simple key: `{{_ 'key_name'}}` or `<FormattedMessage id="key_name" />`
- With interpolation: follows the project's interpolation syntax

### In JavaScript

Use the JS import/call pattern from the cached i18n config.

## Key Naming Convention

Follow the key naming convention from the cached i18n config. General guidelines:
- Be descriptive — the key should convey meaning
- Keep keys consistent with the project's existing style
- Use the English text as a guide for the key name

| English Text | Example Key |
|---|---|
| "Save Changes" | `save_changes` |
| "No results found" | `no_results_found` |
| "Are you sure you want to delete this?" | `are_you_sure_you_want_to_delete_this` |

## Interpolation Syntax

Use the interpolation syntax defined in the cached i18n config.

## Required Workflow

When adding user-facing text:

### 1. Check for Existing Keys

Before creating a new key, search **all** language files for an existing key that matches. Open each language file listed in the cached i18n config and search for the key or a substring of it.

Reuse existing keys whenever the meaning matches exactly. Verify the key exists in **every** language file — if it's missing from any, add it.

### 2. Add to ALL Language Files

New keys must be added to **every** language file listed in the cached i18n config.

- The primary language file gets the source value
- All other language files get the **properly translated** value for that language
- Keys are sorted **alphabetically** within each file
- Maintain valid JSON — watch for trailing commas
- After adding, verify the key appears in every language file

### 3. Use the Key in Code

Use the template and JS syntax from the cached i18n config.

## Anti-Patterns

### Never Do This

```html
<!-- BAD: Hardcoded string -->
<button>Save Changes</button>
<h2>No results found</h2>

<!-- GOOD: Use your project's i18n helper -->
<button>{{translate 'save_changes'}}</button>
<h2>{{translate 'no_results_found'}}</h2>
```

```js
// BAD: Hardcoded string in JS
showToast('Order sent successfully', 'Success');

// GOOD: Use the i18n function
showToast(t('order_sent_successfully'), t('success'));
```

### Never Add Keys to Only One Language

Every new key requires entries in **all** language files listed in the cached i18n config.

### Never Redefine Existing Keys

If a key already exists, reuse it. Don't create duplicates like `save_button` when `save` already exists with the same meaning.
