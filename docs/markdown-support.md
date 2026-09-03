# Markdown support

Texio is a Markdown-only tool. It parses documents using `pulldown-cmark` with
CommonMark behavior and the GitHub Flavored Markdown extensions needed for
tables, task lists, footnotes, and strikethrough.

## Supported section syntax

- ATX headings from `#` through `######`
- Setext level-one and level-two headings
- Nested sections bounded by the next heading at the same or a higher level
- Inline Markdown inside heading titles
- LF and CRLF line endings
- Documents with or without a final newline

Heading-like text inside fenced code blocks and HTML blocks is not treated as a
section boundary. YAML front matter is preserved as ordinary source content and
is never rewritten by section operations.

## Editing guarantees

- Section lookup is case-insensitive for ASCII text.
- A missing heading fails instead of creating a new section.
- Duplicate matching headings fail as ambiguous.
- Replacement changes only the selected section body.
- Line endings follow the target document.
- Writes replace the file atomically, retain its permissions, and preserve
  symlinks by updating their targets.

## Current limitations

- Section selection is by visible heading text; path-like selectors for
  duplicate headings are not implemented yet.
- Unicode case folding is not implemented.
- Markdown embedded in MDX or other templating languages is outside scope.
- Front matter fields are preserved but are not independently queryable.
- Texio does not format, render, or lint Markdown.
