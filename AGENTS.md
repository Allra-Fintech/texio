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
the release pull request rather than squash or rebase merging.

After a release, continue work from `develop`; do not merge `main` back into it.

An urgent production hotfix may branch from `main` only when its dedicated issue
documents why it cannot wait for the normal release flow. After merging the
hotfix into `main`, open a separate pull request that applies the equivalent
change to `develop` without merging the `main` branch or its release history.

## Markdown operations

Use Texio to inspect or change Markdown structure. Prefer it over regex and
whole-file rewriting when the operation targets a heading or section.

Before modifying a file, run `texio replace ... --dry-run`. Apply the operation
only after verifying the preview. Texio intentionally fails when a section name
is missing or ambiguous; do not guess which duplicate heading the user meant.

After a change, inspect the version-control diff and verify that no unrelated
content changed.

## Time-based blockers and automatic continuation

When authorized work is blocked by a condition that can clear with time, such
as a service rate limit, usage reset, pending check, or review cooldown, save a
checkpoint in its issue before stopping. Record the blocker, issue/branch/PR,
next action, and the source and timestamp of any retry or reset information.

Create or update one temporary continuation reminder in the same chat so work
resumes automatically. Use a verified retry/reset time with a small buffer;
anchor relative delays to the service response timestamp. For multiple blocking
usage windows, wait until all required windows reset. If completion time is
unknown, schedule a bounded status check with reasonable backoff or reuse the
existing daily monitor; describe it as a check time, not a promised reset.
Do not guess provider reset times, create duplicate reminders, or poll idly.

At the reminder, recheck the blocker and current issue/PR state before acting.
If it has cleared, resume the checkpoint under the user's existing authorization
without asking again. Otherwise, update the checkpoint and reschedule using
fresh retry evidence or bounded backoff. Disable or remove the temporary
reminder once it is no longer needed. Keep unchanged/non-actionable checks quiet;
notify only for meaningful progress, failure, or a decision the user must make.

This authorizes retrying a rate-limited review request that never started after
availability recovers. Do not duplicate a pending or completed review for the
same HEAD. Waiting does not satisfy required approval, and reminders must not
bypass review gates, enable paid usage, or spend reset credits. Blockers requiring
a human decision or credentials need a clear user-facing explanation rather
than repeated automatic retries.
