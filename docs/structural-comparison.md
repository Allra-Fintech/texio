# What 24 Markdown editing tasks show—and what they do not

I maintain Texio, a Markdown CLI for inspecting and replacing named sections.
This is internal engineering evidence, not an external customer story. Source
and results were reviewed in [PR #179](https://github.com/Allra-Fintech/texio/pull/179).

## Start with one task

You generated a new body for `Installation` and want to inspect a proposed
change while keeping the rest of a README intact:

```sh
texio headings README.md --json
texio section README.md Installation
texio replace README.md --section Installation --from installation-body.md --dry-run
```

The replacement file contains the complete desired body without its target
heading. Nested subsections belong to the selected section. Review the preview
before repeating with `--write` on a disposable copy; inspect the repository
diff afterward. Missing or duplicate matching headings stop rather than guess.
Separate replacements are not one transaction. A binary dependency also has a
cost; improving an existing selector or regenerating a template may fit better.

## Compare implementations, not an answer oracle

The historical four-fixture benchmark gave its idealized whole-file method
the expected file. That was disclosed but was not a runnable editing
implementation. The [new suite](../benchmarks/structural/README.md) preserves
that historical record and uses two actual deterministic text implementations:

- An existing first-match ATX regex without fence parsing or duplicate checks.
- An independent whole-document ATX scanner with fence tracking and duplicate
  validation, rebuilding the document with LF endings. It does not implement
  Setext, containers, inline title rendering or full CommonMark.

All methods receive identical documents, headings and replacement inputs.
Expected outputs stay in the grader. The [manifest](../benchmarks/structural/cases.json)
contains every input and expected result. Cases deliberately stress nested and
fenced headings, duplicate/missing targets, Unicode, CRLF, Setext titles,
following prefixes, final headings and empty replacements. This is a selected
stress suite, not a representative sample of all Markdown workflows.

## Observed results

The [raw result](../benchmarks/structural/results/v0.1.3-macos-arm64.json) records
24 tasks repeated five times per method using the checksum-verified published
Texio 0.1.3 Apple Silicon binary:

| Method | Exact task passes | Required refusals correct |
| --- | ---: | ---: |
| Texio 0.1.3 | 24/24 | 2/2 |
| Disclosed ATX regex | 9/24 | 1/2 |
| Limited whole-document scanner | 15/24 | 2/2 |

Every method's output and exit status repeated identically across those runs.
A pass requires the complete expected UTF-8 output and status. Refusals must
leave the input untouched. The report retains protected-prefix/suffix checks,
actual outputs/errors, all runtime samples and provenance hashes.

Regex failures include fenced boundaries, duplicates and unsupported heading
forms. The scanner safely refuses some unsupported targets but also normalizes
line endings or mishandles following structural boundaries. A refusal and a
wrong write are both task failures here but have different consequences:
inspect raw status and `input_unchanged` fields, not just the table. Individual
failures remain visible in the result.

The [checker](../benchmarks/structural/check.py) recomputes grades and totals.
[Fault checks](../benchmarks/structural/test-check.py) reject six forms of altered
evidence, including with Python optimization enabled. Linux CI repeats the
suite against the current source build, not the Mac binary's timings.

## Reproduce and inspect a failure

[Install a matching verified binary](installation.md), then from a checkout:

```sh
python3 benchmarks/structural/run.py --texio /path/to/texio --runs 5 --output /tmp/structural.json
python3 benchmarks/structural/check.py /tmp/structural.json
python3 -O benchmarks/structural/test-check.py /tmp/structural.json
```

Use a new output path. Compare a failed row's `expected`, `trials[].actual`,
status and protected-region flags. The [short terminal demo](../launch/demos/section-workflow.html)
shows actual inspection, preview, write, diff verification and ambiguity
refusal on a disposable example. Download the HTML to play locally; GitHub's
file view does not execute it. Playback pacing is not execution time.

## What we still need to learn

These counts do not establish superiority over every text program or coding
agent. Both baselines have explicit limits. Timings include Python interpreter
startup versus a compiled CLI, so there is no cross-method speed ranking.
No agent/model session or token measurement was performed; `agent_model` and
`agent_tokens` remain null. No billing-savings claim follows.

Passing fixtures does not demonstrate useful external adoption. The next test
is a participant's actual task, setup friction and later repeat use.
[Request a no-install diff review](https://github.com/Allra-Fintech/texio/issues/new?template=workflow-review.yml&source=benchmark-article)
or use [discussion #175](https://github.com/Allra-Fintech/texio/discussions/175).
Share public/minimal Markdown and an exact heading, not private data. An
attributed case study or quote requires approval of the finished artifact.
