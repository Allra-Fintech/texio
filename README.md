# Texio

Reliable Markdown operations for shell scripts and AI agents.

Texio extracts and surgically edits Markdown by document structure. Use it when
regular expressions are unsafe and rewriting the complete file would create
unnecessary changes.

> `grep` finds text. `sed` changes text. Texio understands Markdown.

## Extract a Markdown section

```console
$ texio section README.md "Installation"
## Installation

brew install texio
```

## Replace one section safely

Preview the proposed change:

```sh
texio replace README.md \
  --section "Installation" \
  --from installation.md \
  --dry-run
```

Apply it by removing `--dry-run`. Texio preserves content outside the selected
section and refuses ambiguous heading matches.

## List headings for an agent

```sh
texio headings README.md --json
```

```json
[{"level":1,"title":"Texio"},{"level":2,"title":"Installation"}]
```

## Installation

Texio is currently built from source:

```sh
cargo install --path .
```

## Status

Texio is an early preview. The initial contract focuses on section extraction,
heading discovery, and surgical replacement. CommonMark and GitHub Flavored
Markdown compatibility work is ongoing.

## Why Texio?

AI agents frequently rewrite entire Markdown files to change one section. That
uses unnecessary context and can alter unrelated content. Texio provides a
small, deterministic operation that is easier to review and automate.

## License

MIT

