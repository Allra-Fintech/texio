# Try one Markdown task with an agent or CI

Use [verified 0.1.3 installation instructions](installation.md). A source build
can take more than five minutes; binary archives or the macOS Homebrew tap
avoid compiling. A new dependency may cost more than improving your existing
generator. Start with a disposable copy and inspect the diff.

For three task choices, setup and feedback guidance, use the
[practitioner trial kit](practitioner-trial-kit.md). Internal fixture checks do
not count as external use or a fresh agent session.

## Agent path

Copy the [Markdown agent policy](agent-instructions.md), then give your agent a
real task with an exact document and heading:

```text
Update only the Installation section of a disposable copy of our README.
Inspect its headings and current section with Texio. Prepare the replacement
body in a separate file, preserving any desired nested subsections. Run a
dry-run preview and show me the diff before any write. Stop on missing or
duplicate headings. Report Texio version and whether other sections changed.
```

The shell operations are:

```sh
texio --version
texio headings README.md --json
texio section README.md Installation
texio replace README.md --section Installation --from installation-body.md --dry-run
```

`installation-body.md` contains the complete desired body, without the target
heading. Supply it from your actual task, not an empty placeholder. The selected
section includes nested subsections. Applying a reviewed edit requires the
explicit `--write` flag; this trial only requests a preview.

[Report an agent-path result or request help](https://github.com/Allra-Fintech/texio/issues/new?template=workflow-review.yml&source=agent-recipe).
Include the actual task, version, OS, outcome and setup minutes if measured.
Do not share private agent transcripts or count an unexecuted suggestion as use.

## CI path

First exercise a no-write preview against a disposable fixture. These commands
run on a POSIX shell after installing Texio:

```sh
trial_dir=$(mktemp -d)
printf '# Demo\n\n## Installation\nold\n\n## Usage\nkeep\n' > "$trial_dir/README.md"
cp "$trial_dir/README.md" "$trial_dir/before.md"
texio replace "$trial_dir/README.md" --section Installation --text new --dry-run
cmp "$trial_dir/before.md" "$trial_dir/README.md"
```

A GitHub Actions job can run the same trial without repository write permission:

```yaml
name: Try a Markdown preview
on: workflow_dispatch
permissions:
  contents: read
jobs:
  preview:
    runs-on: ubuntu-latest
    steps:
      - uses: dtolnay/rust-toolchain@stable
      - name: Install pinned Texio (compiles from source)
        run: cargo install texio-cli --version 0.1.3 --locked
      - name: Preview a disposable example
        shell: bash
        run: |
          trial_dir=$(mktemp -d)
          printf '# Demo\n\n## Installation\nold\n\n## Usage\nkeep\n' > "$trial_dir/README.md"
          cp "$trial_dir/README.md" "$trial_dir/before.md"
          texio replace "$trial_dir/README.md" --section Installation --text new --dry-run
          cmp "$trial_dir/before.md" "$trial_dir/README.md"
```

That fixture proves setup, not workflow value. For an external activation trial,
use a checked-out copy of your actual document and an actual generated section
body, replace the example paths/heading, and review the preview. Keep generation,
credentials and publishing steps out of the initial boundary test. Two section
writes are independent operations, not a transaction.

[Report a CI-path result or request help](https://github.com/Allra-Fintech/texio/issues/new?template=workflow-review.yml&source=ci-recipe).
Link a public run if available, plus version, task, outcome and setup time.
