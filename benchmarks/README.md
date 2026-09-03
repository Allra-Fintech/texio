# Markdown agent-editing benchmark
This benchmark measures three deterministic editing strategies on public
Markdown fixtures: an idealized whole-file rewrite, a generated-regex proxy,
and Texio. It is a mechanics benchmark, not a claim about any model vendor or
agent's intelligence.

The whole-file baseline receives the complete document and, for valid tasks,
produces the checked-in expected file. This deliberately gives it perfect
editing knowledge while charging its full document input and output. On unsafe
duplicate-heading requests it uses the same first-match behavior as the regex
baseline. The regex baseline uses one documented ATX-heading expression and
edits the first match. Texio invokes the released binary with `--write` in an
isolated temporary directory.

Run each case five times from a clean checkout:

```sh
python3 benchmarks/run.py \
  --texio /path/to/released/texio \
  --release v0.1.1 \
  --runs 5 \
  --output benchmarks/results/v0.1.1.json
```

Verify the binary against the adjacent checksum on the
[v0.1.1 release](https://github.com/Allra-Fintech/texio/releases/tag/v0.1.1)
before running it. The checked-in [raw result](results/v0.1.1.json) records that
binary's SHA-256 digest.

`input_tokens` and `output_tokens` use a fixed Unicode word-and-punctuation
counter so runs do not depend on a proprietary tokenizer. They are a
transparent context-size proxy, not measured model billing tokens. Runtime is
the median wall-clock duration and is reported for transparency, not used for
cross-method performance claims. `repeatable` requires identical output and
exit status across all trials.

A case passes only when its exit code and bytes match the checked-in
expectation. For a required refusal, the input must also remain unchanged.
`unrelated_lines_changed` counts changed protected sentinel lines; the separate
`lines_different_from_expected` field captures all incorrect output.

The measured v0.1.1 result supports only these claims: Texio passed all four
fixtures; the idealized whole-file baseline passed three; and the regex proxy
passed two. Texio preserved every declared unrelated sentinel line. This small
sample does not establish general model quality. Promotional claims must cite
the raw result and retain these caveats.
