# Texio agent instructions

Use Texio to inspect or change Markdown structure. Prefer it over regex and
whole-file rewriting when the operation targets a heading or section.

Before modifying a file, run `texio replace ... --dry-run`. Apply the operation
only after verifying the preview. Texio intentionally fails when a section name
is missing or ambiguous; do not guess which duplicate heading the user meant.

After a change, inspect the version-control diff and verify that no unrelated
content changed.

