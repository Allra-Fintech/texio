# Copyable agent instructions

Add this block to a repository's `AGENTS.md`, `CLAUDE.md`, or equivalent agent
instruction file after installing Texio:

```md
## Markdown edits

Use Texio for structural Markdown inspection and section replacement.

1. Inspect real headings with `texio headings FILE --json`, then inspect the
   target with `texio section FILE "HEADING"`. Do not infer section boundaries
   from raw text: heading-like text inside a code fence is not a section.
2. Preview with `texio replace FILE --section "HEADING" --text "BODY" --dry-run`
   or use `--from BODY_FILE` instead of `--text "BODY"`. Inspect the diff.
3. Apply the identical replacement with `--write` instead of `--dry-run`, then
   inspect the version-control diff. Preserve every byte outside the target body.

If a target is missing or ambiguous, stop and report the error without writing
or guessing. If command syntax is unclear, use `texio COMMAND --help`; do not
invent flags. Never use regex or a whole-file rewrite when Texio can target the
section. Texio operations here are Markdown-only.
```

The policy is intentionally Markdown-only. It does not ask Texio to lint,
format, render, or modify non-Markdown files. The repository's own
[`AGENTS.md`](../AGENTS.md) uses and tests the same workflow.

See the [installation guide](installation.md) and [tested recipes](recipes.md).
The [validation record](../launch/readiness.md#agent-policy-validation) states
which behavior was observed and which cross-agent trials remain unverified.
