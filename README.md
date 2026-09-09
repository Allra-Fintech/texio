# Texio

Reliable Markdown operations for shell scripts and AI agents.

Texio extracts and surgically edits Markdown by document structure. Use it when
regular expressions are unsafe and rewriting the complete file would create
unnecessary changes.

> `grep` finds text. `sed` changes text. Texio understands Markdown.

## Extract a Markdown section

Install from [crates.io](https://crates.io/crates/texio-cli) with a current stable
Rust toolchain, or use the [platform-specific binary instructions](docs/installation.md).

```sh
cargo install texio-cli --locked
texio --version
```

Create a small document and inspect its structure:

```sh
printf '# Demo\n\n## Installation\nold command\n\n## Usage\nkeep this\n' > demo.md
texio headings demo.md --json
texio section demo.md Installation
```

Preview one section change, then apply the same change after checking the diff:

```sh
texio replace demo.md --section Installation --text 'cargo install texio-cli --locked' --dry-run
texio replace demo.md --section Installation --text 'cargo install texio-cli --locked' --write
texio section demo.md Installation
```

The preview leaves the file unchanged; the write preserves the Usage section.
Copy the [agent policy](docs/agent-instructions.md) for future edits. Missing or
duplicate headings cause an error rather than selecting a guessed target.

The [four-fixture benchmark](benchmarks/README.md) measured 82.8% fewer
context-proxy tokens versus an idealized whole-file rewrite. This is not a
model-token or billing measurement. A source build can take longer than five
minutes; use a binary archive for the fastest first edit.

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

Install the published crate with a current stable Rust toolchain:

```sh
cargo install texio-cli --locked
texio --version
```

From a checkout, use `cargo install --path . --locked`.

For Linux x86-64, Windows x86-64, Intel macOS, and Apple Silicon macOS,
follow the [binary installation and checksum instructions](docs/installation.md).
The same page documents the organization Homebrew tap and platform limits.

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
