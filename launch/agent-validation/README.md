# Cross-agent policy validation

## Result

Texio's revised copyable Markdown policy passed six fresh Claude Code sessions:
one valid replacement, one missing heading, and one duplicate heading in both
`AGENTS.md` and `CLAUDE.md` contexts.

Every revised-policy trial:

- inspected structural headings with `texio headings --json`;
- correctly excluded a heading-like line inside a fenced code block;
- used `texio section` to inspect an existing target;
- stopped without writing for missing and duplicate targets; and
- avoided generic edit and whole-file write tools.

Both valid trials inspected the target, previewed with `--dry-run`, applied the
same replacement with `--write`, and produced the exact expected bytes. All
content outside the selected section body was unchanged.

One AGENTS.md valid trial attempted a final `git -C ... diff` command that was
outside the deliberately narrow command allowlist. Claude then used an allowed
`git diff` form and completed the verification. The edit itself and all Texio
commands were allowed. This permission denial does not affect the outcome.

## Policy revision

The original policy kept all six fixtures safe, but its workflow was too vague.
Neither context ran `texio headings` before replacement, and several sessions
first invented an unsupported `--content` flag. One response also described a
heading-like line inside a fence as a real section.

The revised policy names the exact inspection and replacement commands, states
that fenced heading-like text is not a section, requires help rather than
invented flags, and requires a final version-control diff. Fresh trials showed
that these changes corrected all observed deviations.

## Evidence

- [`original-results.json`](original-results.json) records the original-policy
  tool calls, command results, final responses, byte hashes, and outcomes.
- [`revised-results.json`](revised-results.json) records the same evidence for
  the revised policy.
- [`reproduce.py`](reproduce.py) creates six isolated Git repositories and runs
  fresh Claude Code sessions with scoped local tools.
- [`summarize.py`](summarize.py) exports task-relevant evidence while excluding
  thinking, authentication, account, and session metadata.

The raw Claude event streams remain in the temporary validation directory and
are intentionally not committed because they can contain local account and
session metadata. The checked-in summaries retain prompts, model identifiers,
tool calls and outputs, final responses, file contents, byte hashes, permission
denials, and the exact invocation needed to audit the conclusions.

## Environment and limits

The trials used Claude Code 2.1.266 with its configured default model selection
and the released Texio v0.1.2 Apple Silicon binary. Each session was fresh and
non-persistent, with local file tools plus narrowly scoped Texio and Git command
access. Network-facing tools, plugins, skills, and MCP servers were disabled.

This evaluation establishes compliance for these six deterministic fixtures.
It does not establish behavior across every prompt, model version, repository,
or coding agent. The earlier Codex session independently followed the inspect,
dry-run, write, and diff workflow while preparing the launch documentation.
