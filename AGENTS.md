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

## Branch strategy

`develop` is the integration branch. `main` is the release branch and must
always represent a publish-ready state.

For normal implementation, fixes, documentation, maintenance, research, and
promotion work:

1. Update local `develop` from `origin/develop`.
2. Create the issue branch from `develop`, not from `main`.
3. Open the pull request with `develop` as its base branch.
4. Merge only after required review and checks pass.

Do not merge normal feature branches directly into `main`. When the accumulated
changes on `develop` are ready to publish, create a dedicated release issue and
open one release pull request from `develop` to `main`. Use a merge commit for
the release pull request rather than squash or rebase merging, then fast-forward
`develop` to the resulting `main` commit before starting more work.

An urgent production hotfix may branch from `main` only when its dedicated issue
documents why it cannot wait for the normal release flow. Merge the hotfix into
`main`, then synchronize the same commit back into `develop` immediately.

## Markdown operations

Use Texio to inspect or change Markdown structure. Prefer it over regex and
whole-file rewriting when the operation targets a heading or section.

Before modifying a file, run `texio replace ... --dry-run`. Apply the operation
only after verifying the preview. Texio intentionally fails when a section name
is missing or ambiguous; do not guess which duplicate heading the user meant.

After a change, inspect the version-control diff and verify that no unrelated
content changed.
