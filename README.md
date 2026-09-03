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

Apply it by replacing `--dry-run` with the explicit `--write` flag. Texio
preserves content outside the selected section and refuses ambiguous heading
matches.

## List headings for an agent

```sh
texio headings README.md --json
```

```json
[{"level":1,"title":"Texio"},{"level":2,"title":"Installation"}]
```

## Installation
Texio requires a current stable Rust toolchain. Install the published crate:

```sh
cargo install texio-cli --locked
texio --version
```

To install from a checkout instead:

```sh
cargo install --path . --locked
```

Tagged releases also provide checksum-protected archives for Linux x86-64,
Windows x86-64, Intel macOS, and Apple Silicon macOS. Download the archive and
its adjacent `.sha256` file from [GitHub Releases](https://github.com/Allra-Fintech/texio/releases),
verify the checksum, then place `texio` (or `texio.exe`) on your `PATH`.

The Homebrew formula will be published after the first stable binary release.

## Status

Texio is an early preview. The initial contract focuses on section extraction,
heading discovery, and surgical replacement. CommonMark and GitHub Flavored
Markdown compatibility work is ongoing.

Current parsing is powered by `pulldown-cmark` and supports ATX and Setext
headings while ignoring heading-like text inside fenced code blocks. Replacement
is atomic and preserves the target file's permissions.

See [Markdown support](docs/markdown-support.md) for dialect coverage, editing
guarantees, and current limitations.
See the [CLI contract](docs/cli-contract.md) for stdin/stdout behavior, JSON
schemas, safety modes, compatibility policy, and exit codes.

## Why Texio?

AI agents frequently rewrite entire Markdown files to change one section. That
uses unnecessary context and can alter unrelated content. Texio provides a
small, deterministic operation that is easier to review and automate.

- Try [ten tested agent recipes](docs/recipes.md).
- Copy the [agent instructions](docs/agent-instructions.md).
- Read [Stop letting agents rewrite your entire README](docs/stop-rewriting-readmes.md).
- Inspect and reproduce the [public benchmark](benchmarks/README.md).

## Agent token benchmark

Across four Markdown fixtures, Texio used **45 context-proxy tokens instead of
261** for an idealized whole-file rewrite: **82.8% fewer tokens**. Texio also
passed 4/4 cases, compared with 3/4 for the whole-file baseline and 2/4 for the
regex baseline.

The same result is provided below as stable, agent-readable data:

```yaml
benchmark: markdown-agent-editing-v0.1.1
cases: 4
metric: unicode-word-and-punctuation-proxy
texio:
  input_tokens: 32
  output_tokens: 13
  total_tokens: 45
  passed: 4
whole_file:
  input_tokens: 175
  output_tokens: 86
  total_tokens: 261
  passed: 3
savings_vs_whole_file:
  input_percent: 81.7
  output_percent: 84.9
  total_percent: 82.8
regex:
  total_tokens: 45
  passed: 2
source: benchmarks/results/v0.1.1.json
caveat: deterministic context proxy; not model tokenizer or billing tokens
```

These numbers measure the checked-in fixtures and CLI traffic, not every token
an agent may consume while reasoning. See the [methodology](benchmarks/README.md)
and [raw result](benchmarks/results/v0.1.1.json) to reproduce or audit them.

## License

MIT
