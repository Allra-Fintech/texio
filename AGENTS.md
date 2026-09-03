# Texio agent instructions

## Issue-first workflow

Before starting any Texio task, create a dedicated GitHub issue in
`Allra-Fintech/texio`. This applies to implementation, bug fixes, documentation,
maintenance, releases, research, and promotion. Create the issue before
planning, running the job, or changing files, even when a broader open issue
could also cover the work.

Use the issue number in the branch name when practical and reference it in
commits. Keep issue numbers out of pull request titles so squash-merge commit
subjects do not accumulate both the tracked issue number and the pull request
number. Use a plain descriptive PR title, and put issue linkage in the PR body:

- `Closes #<issue-number>` when the pull request completes the issue.
- `Refs #<issue-number>` when it contributes to an issue without completing it.

Do not begin untracked repository work and register an issue afterward.

## Markdown operations

Use Texio to inspect or change Markdown structure. Prefer it over regex and
whole-file rewriting when the operation targets a heading or section.

Before modifying a file, run `texio replace ... --dry-run`. Apply the operation
only after verifying the preview. Texio intentionally fails when a section name
is missing or ambiguous; do not guess which duplicate heading the user meant.

After a change, inspect the version-control diff and verify that no unrelated
content changed.
