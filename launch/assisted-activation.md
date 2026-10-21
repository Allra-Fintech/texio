# Assisted workflow activation

Status checked on 2026-10-21 for [#128](https://github.com/Allra-Fintech/texio/issues/128).
The current objective in [#8](https://github.com/Allra-Fintech/texio/issues/8)
is three assisted external workflow trials before new feature work or renewed
broad promotion. Internal demonstrations, invitations, and submitted PRs are
not completed external trials or merged adoption.

## Public outreach status

| Repository | Public proposal | Current disposition |
| --- | --- | --- |
| CVE | [#7](https://github.com/0x5t4l1n/CVE/issues/7) | Submitted October 6; open, no maintainer response at this check |
| CleanTube | [#9](https://github.com/revolunet/cleantube/issues/9) | Submitted October 21; open, no maintainer response at this check |
| Tekton Catalog | [#285](https://github.com/open-toolchain/tekton-catalog/issues/285) | Declined October 7; closed because the maintainer will not use an external tool |
| SQuADDS | [#68](https://github.com/LFL-Lab/SQuADDS/issues/68) | Open, no maintainer response at this check |
| dbt MCP | [#887](https://github.com/dbt-labs/dbt-mcp/issues/887) | Declined and closed; dependency cost was not justified by the current workflow |

The current assisted-activation cycle has two invitations, no evidenced
accepted external trials, no completed external dry runs, and no merged
external adoption. Tekton, SQuADDS, and dbt MCP were contacted in the earlier
launch cycle. Do not add those proposals to the new-cycle invitation total.
An unanswered proposal is not an attributable rejection or a trial outcome.

The [public evidence ledger](metrics/evidence.jsonl) records the new invitations
as project-authored outreach and Tekton's response as external feedback.
The [launch retrospective](retrospective.md) remains the historical launch-window
report; this status does not rewrite its original measurement window.

## CleanTube boundary comparison

The [current updater](https://github.com/revolunet/cleantube/blob/7d16523d45d1f265b36a1bd3b7208845c6a4a454/src/update-readme.ts)
recognizes the next section only when its title starts with uppercase ASCII:

```ts
const chainesRegex = /## Chaines\n[\s\S]*?\n(?=## [A-Z])/;
newReadme = readme.replace(chainesRegex, channelsSection + "\n");
```

The replacement expression was executed in isolation against a copy of the
pinned README with only `## Setup` changed to `## setup`. It removed that
following section before reaching `## Usage`. The live document uses `Setup`;
this is a synthetic layout-change case, not a production incident.

With the existing generator producing the complete `Chaines` body, excluding
its own heading but retaining nested headings, the preview is:

```sh
texio replace README.md --section Chaines \
  --from channels-body.md --dry-run
```

Texio 0.1.2 left the input unchanged during preview. After reviewing the diff,
applying to a disposable copy preserved all bytes outside `Chaines`, including
the lowercase `setup` section. This internal check used the existing body plus
an explicitly synthetic comment, not newly fetched channel data. No channel
fetcher, API, or upstream workflow was run. The public invitation describes
the additional binary dependency and the alternative of fixing the selector
within the existing Node toolchain.

## CLIO extraction comparison

The [current selector](https://github.com/iowarp/clio-kit/blob/93e41d70d6c25ea22c82a39c25c510816e67e8ef/scripts/generate_docs.py)
still matches a requested word anywhere in a heading and does not track code
fences while selecting the section. Against the
[pinned hdf5 README](https://github.com/iowarp/clio-kit/blob/93e41d70d6c25ea22c82a39c25c510816e67e8ef/clio-kit-mcp-servers/hdf5/README.md):

- The selector treats `### Verify Installation` as another match and drops
  that subheading from its output.
- In a synthetic fenced shell example, `# shell comment` stops extraction
  before the remaining example and following section body.
- Texio's exact `Installation` selection retains both. Applying CLIO's same
  existing cleanup after extraction preserves these differences.

```sh
texio section clio-kit-mcp-servers/hdf5/README.md \
  Installation --body-only
```

The comparison isolated only the inspected selector and cleanup methods from
the pinned source. It did not import or execute the generator module, build
the website, invoke server backends, or run CI. The
[machine-readable result](evidence/clio-extraction-2026-10-21.json) records the
revision, document hash, and assertions. This is internal technical-fit
evidence, not an external trial. Other server heading names need separate
qualification; retain downstream MDX cleanup and rendering. Texio does not
edit MDX as part of this proposal.

## Next steps and decision gates

**Correctness gate:** An internal audit on October 21 reproduced four heading
preservation defects in the published v0.1.2 behavior: [multiline Setext title
loss](https://github.com/Allra-Fintech/texio/issues/135), [final-heading/body
concatenation](https://github.com/Allra-Fintech/texio/issues/136), [following
heading prefix loss](https://github.com/Allra-Fintech/texio/issues/139), and
[following Setext title merging](https://github.com/Allra-Fintech/texio/issues/141).
Fixes in PRs #137, #138, #140 and #142 pass their checks but still require
review. Do not send new trial offers or propose a v0.1.2 integration until the
relevant repairs have been reviewed and published in a corrected release.
These are project-authored reproductions, not independent user reports.

Correctness corrections were posted to the existing
[CVE invitation](https://github.com/0x5t4l1n/CVE/issues/7#issuecomment-6308490097)
and [CleanTube invitation](https://github.com/revolunet/cleantube/issues/9#issuecomment-6308490657).
These are disclosures about the tool, not new offers or external trial results.
The cycle invitation total remains two.

Wait for the CleanTube response before the next outbound offer. Do not repeat
the declined Tekton or dbt proposals without materially new evidence. CLIO
remains a technically revalidated reserve, not a submitted invitation.

For an accepted trial, record installation path, setup time, external
participant, time to first successful dry run, exact task outcome, outside-byte
preservation, portability/correctness failures, and adoption or attributable
rejection in [#121](https://github.com/Allra-Fintech/texio/issues/121).
After three externally participated trial outcomes, stop for the decision in
[#122](https://github.com/Allra-Fintech/texio/issues/122), even if adoption targets
are missed. Broad promotion and directory expansion remain deferred.

The user authorized autonomous continuation on October 21, including relevant
targeted offers and replies. The daily chat check monitors current evidence,
continues eligible work, and escalates decisions that require the user.
It is separate from the manual aggregate metrics collector and is not a
repository CI workflow. Its schedule lives in the app, not in this repository.
