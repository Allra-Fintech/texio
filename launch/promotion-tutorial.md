# Preview one README section change before an agent writes it

Publication status: prepared for #173; owned GitHub tutorial; external case study still requires a participant.
Disclosure: I maintain Texio, the MIT-licensed Markdown CLI used below.

Suppose a generator updates an Installation section and the next Usage section
must stay unchanged. The smallest useful trial is a preview on a disposable
copy, not a new dependency added to production CI.

After [installing Texio 0.1.3](https://github.com/Allra-Fintech/texio/blob/develop/docs/installation.md),
try this POSIX-shell example:

```sh
trial_dir=$(mktemp -d)
printf '# Demo\n\n## Installation\nold\n\n## Usage\nkeep\n' > "$trial_dir/README.md"
cp "$trial_dir/README.md" "$trial_dir/before.md"
texio replace "$trial_dir/README.md" --section Installation --text new --dry-run
cmp "$trial_dir/before.md" "$trial_dir/README.md"
```

The diff proposes changing `old` to `new`. The `cmp` command verifies that the
preview left the file untouched. To apply after inspecting the preview, repeat
the replacement with `--write` instead of `--dry-run` on a disposable copy.

| Existing workflow | Texio trial |
| --- | --- |
| Read/regenerate a whole document, then review the full diff | Select one named section, prepare its complete desired body, preview that replacement |
| Maintain a selector in your script | Use Markdown heading boundaries; missing/ambiguous headings stop the operation |
| Keep existing generator dependencies | Add a verified binary or compile a Rust CLI; evaluate whether the setup cost is justified |

For generated content, pass `--from section-body.md` rather than `--text new`.
The body must retain wanted nested subsections and any other selected content.
A target section includes its nested subsections. Multiple section writes are
not one transaction. Texio is Markdown-only and remains an early preview.

This is a synthetic demonstration, not a customer result or a claim that all
regex-based updaters fail. Improving an existing selector or regenerating a
fully templated document may be the better option. Source builds can take more
than five minutes; release archives cover Linux x86-64, Windows x86-64 and both
Mac architectures, with Homebrew also available on macOS.

If you have a real workflow, [request a no-install diff review](https://github.com/Allra-Fintech/texio/issues/new?template=workflow-review.yml&source=github-tutorial).
Share a public document and exact heading, not secrets. I will prepare a diff
before you install anything. If you choose to try it, a version, outcome and
approximate setup time help us learn whether the tool is useful. Publication
of a participant story always needs approval of the finished artifact.
