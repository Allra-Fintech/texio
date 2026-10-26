# Structural replacement comparison

This separate suite contains **24 synthetic replacement tasks**, each repeated
five times against the checksum-verified published Texio 0.1.3 Apple Silicon
binary. It does not modify the historical four-case benchmark or its results.
All methods receive the same input, heading and replacement body. Expected
outputs are used only by the grader, never by an editing method.

## Reproduce

Use Python 3.9+ and an installed Texio binary. Download the matching public
[0.1.3 archive and SHA256 sidecar](https://github.com/Allra-Fintech/texio/releases/tag/v0.1.3)
and verify it before running. From the repository root:

```sh
python3 benchmarks/structural/run.py --texio /path/to/texio --runs 5 --output /tmp/structural.json
python3 benchmarks/structural/check.py /tmp/structural.json
python3 -O benchmarks/structural/test-check.py /tmp/structural.json
```

Choose a new output filename each time; existing results are never overwritten.
CI repeats the suite against the current release-mode source build on Linux.
That checks regressions, not reproduction of this Mac binary's runtime.

## Methods and contract

- **Texio:** actual `replace --write` on a fresh temporary file, preceded by a
  separate untimed `--dry-run` that must leave all bytes unchanged and return
  the expected status. Uses the published binary for the checked-in result.
- **Regex:** reuses `naive_replace` from the existing benchmark: first-match
  ATX selector, next ATX heading boundary, no fenced-code parsing or duplicate
  validation. It writes only on success. No oracle or special-case fixture IDs.
- **Whole-document:** a real independent ATX line scanner, with fence tracking
  and missing/duplicate validation. It reconstructs the complete file with LF
  line endings and a final newline. It deliberately does not implement Setext,
  inline title rendering, containers or full CommonMark. Its implementation is
  disclosed in [baseline.py](baseline.py). It is neither a model nor an oracle.

Each trial must match the entire UTF-8 output and exit status. Refusals must
return 4 (missing) or 5 (ambiguous) with the file unchanged. The replacement
contract uses the document's line endings and terminates the body with one
newline if needed, including an empty body. A following Setext title needs a
separating blank line. These expectations follow the documented Texio editing
contract and are explicit in [cases.json](cases.json). Two initially drafted
expectations (CRLF replacement and empty body) were corrected against the
existing normalization contract before freezing this result; they were not
new product failures.

Protected prefixes and suffixes are compared byte-for-byte (empty regions are
vacuously preserved); complete expected-output comparison determines success.
The suite covers ordinary/nested ATX, fenced headings, missing/duplicate targets,
Unicode, CRLF, indentation, closing hashes, Setext and multiline titles, final
headings without newline, following block/list prefixes, empty bodies, inline
formatting and parent boundaries. It exercises replacement, not every CLI mode.

## Observed result

[Raw five-run result](results/v0.1.3-macos-arm64.json), including exact outputs,
errors, grades, source/fixture/binary hashes and all runtime samples:

| Method | Exact task passes | Failures |
| --- | ---: | ---: |
| Texio 0.1.3 | 24/24 | 0 |
| Disclosed ATX regex | 9/24 | 15 |
| Limited whole-document scanner | 15/24 | 9 |

Every method's exit status and output repeated identically across five runs.
The grader recomputes every grade, preservation flag, timing summary and total
from raw trials, checks coverage and source/fixture hashes, and rejects Texio
regressions. Fault checks reject altered raw output, grades, expectations,
counts, missing rows and fabricated timing summaries even under Python `-O`.

Regex failures include fenced boundaries, duplicate targets, CRLF and unsupported
heading forms. Whole-document failures include line-ending normalization and
unsupported Setext/container/inline titles. See individual raw rows rather than
inferring that every failure loses unrelated bytes. Explicit safe refusal of an
unsupported form is still a task failure here, but differs from writing a wrong
result; each raw exit/output/unchanged flag preserves that distinction.

## Limits on interpretation

This is an intentionally selected structural stress suite, not a random sample
of real workflows. The partial text baselines have documented limitations; the
results do not represent every regex program, whole-file editor or coding agent.
No claim of general superiority, external adoption or measured time savings is
supported. A template generator can still be a better fit for a whole document.

Runtime measures process startup plus edit I/O, excludes fixture setup and the
Texio preview, and records per-case min/median/max and every sample. The Python
baselines start an interpreter while Texio is a compiled CLI. These are cold
process timings on one host, not comparable algorithm-speed measurements or
agent reasoning time; no cross-method speed ranking is claimed.

No model or agent session was run. `agent_model` and `agent_tokens` are null;
these results contain no token proxy, billing savings or model-quality claim.
Actual agent-token and repeated-session evidence require a separately specified
agent experiment. This suite is internal engineering evidence, not a completed
external practitioner trial or permission to publish a customer story.
