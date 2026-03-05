---
name: blaze-gotchas
user-invokable: false
description: 'Blaze template rendering pitfalls and workarounds. Use for: Blaze, templates, {{#if}}, {{#each}}, Font Awesome, icons, reactive rendering, Meteor UI, HTML templates, Blaze reactivity.'
---
# Blaze Gotchas

## When to Use
- Writing or editing Blaze templates (`.html` files with `<template>`)
- Adding icons (Font Awesome, etc.) inside reactive blocks (`{{#if}}`, `{{#unless}}`, `{{#each}}`)
- Debugging visual glitches where elements briefly show incorrect state during reactive re-renders
- Working with `{{#if}}` / `{{else}}` blocks that swap between similar DOM elements

## Attribute Helpers Must Use Single Quotes

When passing arguments to helpers inside HTML attributes, use **single quotes** around the helper arguments:

```html
<div class="my-class {{myHelper 'test'}}" title="{{__ 'session_title'}}"></div>
```

## No Logic Blocks Inside HTML Tags

Blaze does not support `{{#if}}` or other block helpers that split an HTML tag's attributes:

❌ Incorrect:

```html
<div {{#if addClass}}class="my-class"{{/if}}></div>
```

✅ Correct — use helpers or conditionals inside attribute values:

```html
<div class="{{#if addClass}}my-class{{/if}}"></div>
```

## Font Awesome Icons in Reactive Blocks

**ALWAYS wrap `<i>` icon tags in a `<span>` when they appear inside `{{#if}}` / `{{else}}` blocks.**

Blaze has a compatibility issue with Font Awesome `<i>` tags inside conditional blocks. When Blaze swaps between `{{#if}}` and `{{else}}` branches, bare `<i>` elements can briefly render both branches simultaneously, causing visual artifacts (e.g., both a "sent" and "read" icon appearing at once).

### Problem

```html
{{#if hasBeenRead order}}
  <i class="fa fa-check-double text-primary"></i>
  <span>Read</span>
{{else}}
  <i class="fa fa-check"></i>
  <span>Sent</span>
{{/if}}
```

When `hasBeenRead` changes from `false` to `true`, both the single-check and double-check icons may briefly appear together.

### Fix

Wrap the `<i>` tags in `<span>` elements:

```html
{{#if hasBeenRead order}}
  <span><i class="fa fa-check-double text-primary"></i></span>
  <span>Read</span>
{{else}}
  <span><i class="fa fa-check"></i></span>
  <span>Sent</span>
{{/if}}
```

This gives Blaze a distinct container element to diff against, preventing the rendering overlap.

### Why This Happens

Blaze's DOM diffing algorithm treats `<i>` elements inside conditional branches as "same element, different attributes" rather than distinct elements. It tries to morph one into the other (updating classes) instead of removing one and inserting the other. Wrapping in `<span>` forces distinct DOM nodes for each branch.

## Reactive Cursor Field Exclusion

When a `{{#each}}` block iterates over a cursor and a helper inside the loop also queries the same collection reactively, exclude the helper's field from the cursor to prevent the `{{#each}}` from tearing down and rebuilding items when that field changes.

### Problem

```js
// Cursor observes ALL fields including readReceipts
orderLog: function () {
  return OrderItemLog.find({ orderId: id });
},
// Helper also queries readReceipts independently
hasBeenRead: function (order) {
  const doc = OrderItemLog.findOne(order._id, { fields: { readReceipts: 1 } });
  return doc?.readReceipts?.length > 0;
},
```

When `readReceipts` changes, BOTH the cursor and the helper fire — the cursor triggers a full item teardown/rebuild while the helper tries to update the `{{#if}}` block, causing a visual glitch.

### Fix

Exclude the field from the cursor:

```js
orderLog: function () {
  return OrderItemLog.find({ orderId: id }, {
    fields: { readReceipts: 0 }
  });
},
```

Now only the `hasBeenRead` helper reacts to `readReceipts` changes, producing a clean `{{#if}}` branch swap without the `{{#each}}` item being torn down.

## Meteor Template Error Debugging

### "Cannot find module './template.html'" Errors

This error has TWO distinct causes. Check both:

1. **Actual missing file** — The import path is wrong or the file doesn't exist. Check the path first.
2. **Blaze parsing error** — Template syntax errors (malformed HTML, inline conditionals in attributes) cause this same error even when the file exists.

If the file exists and imports look correct, investigate template syntax:
- Count opening and closing HTML tags — mismatched or extra closing tags cause this error
- Look for inline Blaze conditionals inside HTML tag attributes (see "No Logic Blocks Inside HTML Tags" above)
- Check for unclosed elements or duplicate closing tags

Always validate HTML structure when editing Blaze templates.

## Rules

**ALWAYS:**
- Use single quotes for helper arguments inside HTML attributes: `{{myHelper 'value'}}`
- Wrap `<i>` tags in `<span>` when inside `{{#if}}` / `{{else}}` / `{{#unless}}` blocks
- Exclude fields from `{{#each}}` cursors when those fields are handled by separate reactive helpers inside the loop
- Test reactive transitions visually, not just the end state
- Validate HTML tag balance when editing templates (count opening/closing tags)

**NEVER:**
- Put logic blocks (`{{#if}}`, `{{#each}}`) that split HTML tag attributes
- Put bare `<i>` elements directly inside `{{#if}}` / `{{else}}` branches — wrap them
- Let a `{{#each}}` cursor and an inner helper both observe the same field on the same collection
