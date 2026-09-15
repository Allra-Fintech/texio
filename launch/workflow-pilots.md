# Open-source workflow pilots

Observed on 2026-09-15. These are technical-fit evaluations, not adoption
claims. No maintainer was contacted and no external pull request was opened.
The machine-readable [trial record](evidence/workflow-pilots-2026-09-15.json)
contains source commits, hashes, and safety results.

## Results

| Repository | Existing workflow | Texio result | Recommendation |
| --- | --- | --- | --- |
| [`dbt-labs/dbt-mcp`](https://github.com/dbt-labs/dbt-mcp) | [`generate_docs.py`](https://github.com/dbt-labs/dbt-mcp/blob/231970bc2658696a3eff228052e38a6208ff15a2/scripts/generate_docs.py) uses a multiline regular expression to replace the README `Tools` section; CI checks generated docs. | A representative `Tools` update produced a reviewable dry-run, changed the section, and preserved every byte outside it. | Strong problem fit. Open an issue before proposing a dependency change; the project requests issues for questions, signed commits, tests, and a changelog entry. |
| [`open-toolchain/tekton-catalog`](https://github.com/open-toolchain/tekton-catalog) | [`update_readme.py`](https://github.com/open-toolchain/tekton-catalog/blob/f7b166bc5556fc11ecbbae1e350153cf883af95d/.ci/update_readme.py) maintains `Available tasks` and `Details` across 12 README files with a custom line parser. A missing heading causes generated content to be appended. | A representative `Available tasks` update preserved outside bytes. The missing-heading trial exited 4 without writing instead of creating a new section. | Highest safety gain. Propose replacing the custom section parser after confirming maintainers accept a release-binary CI dependency. |
| [`LFL-Lab/SQuADDS`](https://github.com/LFL-Lab/SQuADDS) | A [push-triggered workflow](https://github.com/LFL-Lab/SQuADDS/blob/185f4e6cb013bb1e0421dc780e3df750b1befca7/.github/workflows/update_contributors.yml) runs [`update_contributors.py`](https://github.com/LFL-Lab/SQuADDS/blob/185f4e6cb013bb1e0421dc780e3df750b1befca7/scripts/update_contributors.py), whose regex spans the adjacent `Contributors` and `Developers` sections before writing directly to `master`. | A representative `Contributors` update preserved the following `Developers` section and all other bytes. Missing and duplicate targets were also confirmed write-safe. | Strong automation fit. Propose two explicit section replacements plus a checked Texio installation in the workflow. |

All three repositories were active and unarchived at observation time. The
trials used their public README files at the commits linked above and Texio
0.1.2. They did not run the projects' full generators, so maintainers still
need to weigh installation time and dependency policy against the safety gain.

## Reproduction pattern

For each repository, set `DOC` to the recorded file path, write the generated
section body to a temporary file, and apply it to a clean copy. The dbt MCP and
SQuADDS pilots use `README.md`; Tekton Catalog uses `git/README.md`.

```sh
DOC="${DOC:-README.md}"
texio headings "$DOC" --json
texio section "$DOC" "TARGET"
texio replace "$DOC" --section "TARGET" --from generated.md --dry-run
texio replace "$DOC" --section "TARGET" --from generated.md --write
git diff -- "$DOC"
```

The dry-run left the input unchanged. After the write, the bytes before and
after the selected section matched the original exactly. A separate missing
target returned exit 4 without writing; a duplicate target returned exit 5
without writing.

## Maintainer proposal outlines

### SQuADDS

The scheduled contributor updater currently matches two README headings with
one cross-section regular expression and then rewrites the file. Would the
maintainers accept a small trial that generates the two bodies as it does now,
previews each named-section replacement with Texio, and stops on missing or
duplicate headings? The proposal should include measured workflow installation
time and retain the existing `uv` checks.

### Open-Toolchain Tekton Catalog

The README generator duplicates Markdown section-boundary parsing and appends
content when an expected heading is missing. Would maintainers consider a
trial using Texio for `Available tasks` and `Details`, with a pinned verified
binary in CI? The key behavior change is deliberate refusal instead of silently
creating a misplaced section.

### dbt MCP

The generated `Tools` section is already validated in CI, but its boundary is
selected by a multiline regular expression. Before proposing code, ask whether
the project would accept a non-Python documentation-build dependency. Any pull
request must use signed commits, add a changelog entry, and retain
`task docs:generate CHECK_FLAG=1`.

Start with SQuADDS and Tekton because their current automation writes or
appends content. Treat dbt MCP as a discussion-only candidate until the
dependency tradeoff is accepted.
