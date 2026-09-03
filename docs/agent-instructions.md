# Copyable agent instructions

Add this block to a repository's `AGENTS.md`, `CLAUDE.md`, or equivalent agent
instruction file after installing Texio:

```md
## Markdown edits

Use Texio for structural Markdown inspection and section replacement. Before
changing a section, run `texio replace FILE --section HEADING ... --dry-run` and
inspect the diff. Apply with the same command using `--write`. Never use a regex
or whole-file rewrite when Texio can target the section. If Texio reports a
missing or ambiguous heading, stop and report the error instead of guessing.
```

The policy is intentionally Markdown-only. It does not ask Texio to lint,
format, render, or modify non-Markdown files. The repository's own
[`AGENTS.md`](../AGENTS.md) uses and tests the same workflow.
