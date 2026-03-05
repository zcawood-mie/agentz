---
name: No Terminal File Edits
description: Never use terminal commands to create or modify files — always use built-in editing tools
applyTo: '**'
---
# No Terminal File Edits

**Never** use terminal commands to create, modify, or overwrite files. This includes:

- `sed`, `awk`, `perl -pi` (substitution)
- `cat >`, `cat >>`, heredocs (`<< EOF`) (file writing)
- `echo >`, `printf >`, `tee` (redirection)
- Any other shell command that writes file content

These approaches bypass tool safeguards, corrupt files (especially heredocs), and require unnecessary user approval.

**Instead, always use the built-in file tools:**
- `replace_string_in_file` or `multi_replace_string_in_file` for edits
- `create_file` for new files

If an editing tool is unavailable or disabled in your current mode, **tell the user or hand off to an agent that has edit access**. Never fall back to terminal-based file writing.
