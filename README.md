# Texio

Reliable Markdown operations for shell scripts and AI agents.

Texio extracts and surgically edits Markdown by document structure. Use it when
regular expressions are unsafe and rewriting the complete file would create
unnecessary changes.

> `grep` finds text. `sed` changes text. Texio understands Markdown.

## Extract a Markdown section

Try a short comparison on a disposable file after [installing Texio 0.1.3](docs/installation.md):

| Whole-document editing | Named-section preview |
| --- | --- |
| Read or regenerate the document, then review the complete edit | Inspect the target, prepare its desired body and preview only that replacement |
| Your script owns boundary selection | Texio parses headings and refuses missing or ambiguous targets |

```sh
trial_dir=$(mktemp -d)
printf '# Demo\n\n## Installation\nold\n\n## Usage\nkeep\n' > "$trial_dir/README.md"
cp "$trial_dir/README.md" "$trial_dir/before.md"
texio replace "$trial_dir/README.md" --section Installation --text new --dry-run
cmp "$trial_dir/before.md" "$trial_dir/README.md"
```

The preview proposes `old` → `new` inside Installation. `cmp` verifies that the
file stayed unchanged. After reviewing, repeat the replacement with `--write`
instead of `--dry-run` on the disposable copy; Usage remains unchanged.

For a real generated body, use `--from section-body.md` instead of `--text new`.
Inspect with `texio headings FILE --json` and `texio section FILE "HEADING"`
first. The replacement covers the complete selected body, including nested
subsections; retain everything you want within that body. Separate section
writes are not a transaction.

This is a synthetic example, not external adoption evidence. A new binary
dependency must justify its setup cost; improving your current generator can
be preferable. A source build can take more than five minutes. See the
[platform-specific binary and Homebrew instructions](docs/installation.md).

**Try this on a copy of your Markdown file.** Want a diff before installing?
[Request a no-install workflow review](https://github.com/Allra-Fintech/texio/issues/new?template=workflow-review.yml&source=readme-comparison),
or use the [agent and CI trial recipes](docs/trial-recipes.md).
The [reproducible boundary comparison](scripts/launch-demo.py) also shows one
specific regex selector stopping at a fenced-code heading. That result does
not establish that every regex-based updater fails.

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
- Install the [agent skill](skills/texio-markdown/SKILL.md) and review its
  [automatic-selection evidence](launch/agent-validation/skill-selection.md).
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
