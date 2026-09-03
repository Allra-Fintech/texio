# Stop letting agents rewrite your entire README

An agent needs to update one installation paragraph. A whole-file edit sends
the complete README through the model and asks it to reproduce every unrelated
byte. A generated regex is smaller, but Markdown headings inside fenced code,
nested sections, and duplicate names make textual matching unsafe.

Texio gives the agent a narrower operation:

```sh
texio replace README.md \
  --section Installation \
  --from proposed-installation.md \
  --dry-run
```

The preview is a normal unified diff. After inspection, the agent changes only
the mode:

```sh
texio replace README.md \
  --section Installation \
  --from proposed-installation.md \
  --write
```

Texio parses Markdown structure, refuses missing or duplicate matches, performs
an atomic write, and preserves bytes outside the selected body. It remains a
small Markdown utility rather than a formatter or general document platform.

## What the benchmark shows

The public [v0.1.1 benchmark](../benchmarks/results/v0.1.1.json) has four
fixtures. Texio passed 4/4, an idealized whole-file baseline passed 3/4, and a
first-match regex proxy passed 2/4. Texio changed zero protected unrelated
sentinels. These results demonstrate the tested mechanics only; four fixtures
do not establish general agent or model quality.

## Reproduce it

Download the [v0.1.1 release](https://github.com/Allra-Fintech/texio/releases/tag/v0.1.1),
verify its adjacent SHA-256 file, and follow the
[benchmark instructions](../benchmarks/README.md). The raw result records the
exact binary digest and the runner is also exercised in CI.
