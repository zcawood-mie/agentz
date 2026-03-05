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

The project uses `universe:i18n` via the `bluehive-i18n` package.

### In Blaze Templates (HTML)

Use the `{{_ 'key_name'}}` helper:

```html
<h2>{{_ 'available_services'}}</h2>
<button class="btn btn-primary">{{_ 'save'}}</button>
<input placeholder="{{_ 'search_by_name'}}" />
<p class="empty-state-title">{{_ 'no_results_found'}}</p>
```

With interpolation:

```html
<p>{{_ 'your_card_will_be_charged' total=formattedTotal}}</p>
```

### In JavaScript

Import and use `i18n.__()`:

```js
import { i18n } from 'meteor/universe:i18n';

// Simple key
BlueHive.functions.createToast(i18n.__('order_sent'), i18n.__('success'), 'success');

// With interpolation
i18n.__('you_do_not_have_the_correct_permissions_role_to_perform_this_action', { role: 'employer-admin' });

// In Meteor errors
throw new Meteor.Error(i18n.__('permission_not_granted'), i18n.__('access_denied'));
```

## Key Naming Convention

- Use `snake_case`
- Be descriptive — the key should convey meaning
- Keep keys lowercase
- Use the English text as a guide for the key name

| English Text | Key |
|---|---|
| "Save Changes" | `save_changes` |
| "No results found" | `no_results_found` |
| "Are you sure you want to delete this?" | `are_you_sure_you_want_to_delete_this` |
| "Order #{id} sent" | `order_n_sent` (with `{$id}` interpolation) |

## Interpolation Syntax

Use `{$variableName}` inside translation values:

```json
"your_email_n_has_not_been_verified": "Your email <strong>{$email}</strong> has not been verified.",
"account_linked_successfully": "{$service} account linked successfully!"
```

## Required Workflow

When adding user-facing text:

### 1. Check for Existing Keys

Before creating a new key, search `en.i18n.json` for an existing key that matches:

```bash
grep -i "search term" packages/bluehive-i18n/i18n/en.i18n.json
```

Reuse existing keys whenever the meaning matches exactly.

### 2. Add to ALL Language Files

New keys must be added to every language file in `packages/bluehive-i18n/i18n/`:

| File | Language |
|---|---|
| `en.i18n.json` | English |
| `ar.i18n.json` | Arabic |
| `de.i18n.json` | German |
| `es.i18n.json` | Spanish |
| `fr.i18n.json` | French |
| `ru.i18n.json` | Russian |
| `tl.i18n.json` | Tagalog |
| `vi.i18n.json` | Vietnamese |
| `zh.i18n.json` | Chinese (Simplified) |

- `en.i18n.json` gets the English value
- All other language files get the **properly translated** value for that language
- Keys in each file are sorted **alphabetically**
- Maintain valid JSON — watch for trailing commas

### 3. Use the Key in Code

Use `{{_ 'key_name'}}` in templates or `i18n.__('key_name')` in JavaScript.

## Anti-Patterns

### Never Do This

```html
<!-- BAD: Hardcoded string -->
<button>Save Changes</button>
<h2>No results found</h2>
<p>Are you sure?</p>

<!-- GOOD: i18n key -->
<button>{{_ 'save_changes'}}</button>
<h2>{{_ 'no_results_found'}}</h2>
<p>{{_ 'are_you_sure'}}</p>
```

```js
// BAD: Hardcoded string in JS
BlueHive.functions.createToast('Order sent successfully', 'Success', 'success');

// GOOD: i18n key
BlueHive.functions.createToast(i18n.__('order_sent_successfully'), i18n.__('success'), 'success');
```

```js
// BAD: Mixing hardcoded and i18n
throw new Meteor.Error('Permission denied', i18n.__('access_denied'));

// GOOD: Both use i18n
throw new Meteor.Error(i18n.__('permission_denied'), i18n.__('access_denied'));
```

### Never Add Keys to Only English

Every new key requires entries in **all 9 language files**. If you're unsure of a translation, add your best translation and note it in `packages/bluehive-i18n/i18n/needs-translated.txt`.

### Never Redefine Existing Keys

If a key already exists in `en.i18n.json`, reuse it. Don't create duplicates like `save_button` when `save` already exists with the same meaning.

---

## Available Scripts

### check-i18n-key.py
Check if a key exists across all 9 language files.

```bash
# Substring search
python3 scripts/check-i18n-key.py save_changes

# Exact match
python3 scripts/check-i18n-key.py save_changes --exact

# Human-readable output
python3 scripts/check-i18n-key.py save_changes --format text
```

**Exit codes:** 0 = found in all files, 1 = missing from some, 2 = not found anywhere

### add-i18n-key.py
Add a key to all language files atomically, maintaining alphabetical sort.

```bash
# Add with English value (other languages get English as fallback)
python3 scripts/add-i18n-key.py --key "save_changes" --en "Save Changes"

# Add with multiple translations
python3 scripts/add-i18n-key.py --key "hello" --en "Hello" --es "Hola" --fr "Bonjour"

# Preview without writing
python3 scripts/add-i18n-key.py --key "save" --en "Save" --dry-run

# Overwrite existing key
python3 scripts/add-i18n-key.py --key "save" --en "Save" --force
```

**Exit codes:** 0 = added, 1 = key already exists, 2 = error

**Note:** Languages without a provided translation receive the English value and are flagged in the `needs_translation` output field.
