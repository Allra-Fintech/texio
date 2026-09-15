---
name: texio-markdown
description: Use Texio whenever a task asks to inspect, extract, replace, or update a named heading or section in a Markdown file while preserving unrelated content. Trigger for README and other Markdown section work; do not use for formatting, rendering, or non-Markdown files.
---

# Texio Markdown

Use the `texio` executable for structural Markdown inspection and section-body
replacement. If it is unavailable, report that Texio must be installed rather
than silently using a less precise replacement method.

1. Inspect real headings with `texio headings FILE --json`.
2. Inspect an existing target with `texio section FILE "HEADING"`.
3. For a requested edit, preview it with
   `texio replace FILE --section "HEADING" --text "BODY" --dry-run`, or use
   `--from BODY_FILE` for multiline content.
4. Check the preview. Apply the identical replacement with `--write` instead of
   `--dry-run`, then inspect the version-control diff when one is available.

Preserve every byte outside the target section body. Treat heading-like text
inside code fences as content. If a heading is missing or ambiguous, stop and
report the error without writing or guessing. Use `texio COMMAND --help` when
syntax is unclear. Texio operations are Markdown-only.
