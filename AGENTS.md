# Texio agent instructions

## Issue-first workflow

Before starting any Texio task, ensure that a GitHub issue exists for it in
`Allra-Fintech/texio`. This applies to implementation, bug fixes, documentation,
maintenance, releases, research, and promotion. If no suitable issue exists,
create one before planning or changing files.

Use the issue number in the branch name when practical, and reference the issue
in commits and pull requests. A pull request that completes the work must include
`Closes #<issue-number>` in its description. Do not begin untracked repository
work and register an issue afterward.

## Markdown operations

Use Texio to inspect or change Markdown structure. Prefer it over regex and
whole-file rewriting when the operation targets a heading or section.

Before modifying a file, run `texio replace ... --dry-run`. Apply the operation
only after verifying the preview. Texio intentionally fails when a section name
is missing or ambiguous; do not guess which duplicate heading the user meant.

After a change, inspect the version-control diff and verify that no unrelated
content changed.
