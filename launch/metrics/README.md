# Public launch adoption metrics

## Baseline and daily snapshots

The [2026-09-09 baseline](2026-09-09-pre-promotion.json) was collected before
this task published any promotion, during release preparation. Each snapshot
records UTC start/end times and endpoint URLs. Counters include earlier public
availability and maintainer testing; this is not a zero-traffic baseline.

Run from a checkout with Python 3 and an authenticated GitHub CLI:

```sh
python3 scripts/capture-adoption.py --output "launch/metrics/$(date -u +%Y-%m-%dT%H%M%SZ).json"
```

Run once per day during launch week. This is a manual repeatable procedure;
no scheduled task is installed. The collector refuses to overwrite a snapshot.
Compare the same counter and release asset between snapshots. Missing metrics
are `null`, never zero; a missing crate is explicitly marked unavailable. A
negative delta requires investigation rather than being treated as adoption.

## Definitions

| Metric | Source and interpretation |
| --- | --- |
| Binary downloads | Sum `binary_archive` assets across public releases; excludes checksum assets and GitHub-generated source archives. Counts requests, including bots, CI, and repeat downloads. |
| Checksum downloads | Separate checksum asset counters; never add them to binary downloads. |
| Crate downloads | crates.io aggregate and per-version counts; not unique users or successful installations. |
| Stars and forks | GitHub repository counters; interest signals only. |
| Issues and PRs | Separate open/closed GitHub search counts; include maintainer work and are not bug totals. |
| Discussions | GitHub discussion count; does not measure substantive conversation. |
| Verified installs | Evidence of successful installation and reported version; count unique external trials, not downloads. |
| Independent agent trials | An external agent trial with a reproducible task and outcome; exclude this project's own scripted checks. |
| External adoption | A linked merged change in a non-Texio repository using Texio; deduplicate repositories. |
| Substantive feedback | Linked reproducible bug report, workflow evaluation, or meaningful question; exclude bot and administrative traffic. |
| Critical defects | Confirmed data loss or incorrect-target reports with reproduction and disposition; do not infer zero from issue counts. |

## Evidence ledger

Record external evidence in `evidence.jsonl`, one JSON object per event:

```json
{"observed_at":"UTC timestamp","kind":"verified_install|agent_trial|adoption|feedback|defect","source_url":"public evidence URL","repository":"owner/repo when relevant","version":"observed version","outcome":"concrete result","independent":true}
```

The ledger starts empty because no external evidence has been verified by this
task. Empty means unmeasured, not zero adoption. Do not record email addresses,
IP addresses, access tokens, private conversations, or personal identifiers.
Use public repository/source links only where needed to substantiate an event.

## Interpretation and launch targets

Prior launch decisions proposed 20 verified installs/downloads, three independent
trials, five substantive conversations, and zero critical data-loss reports.
Report downloads and verified installs separately rather than combining them.
Compare observed evidence with these targets in the seven-day retrospective
(#39); public counter growth alone cannot establish success.

Record known testing activity in snapshot notes. This task downloaded each
v0.1.1 archive and checksum once and installed the crate while preparing the
baseline. Later release verification will add more maintainer/CI downloads.
Do not subtract guessed bot or CI counts from public totals.
