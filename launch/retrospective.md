# Seven-day public launch retrospective

## Window and method

The launch window started with the
[Show HN publication](https://news.ycombinator.com/item?id=49736484) at
2026-09-17 04:39:42 UTC and ended at 2026-09-24 04:39:42 UTC. The
[final snapshot](metrics/2026-09-24-seven-day.json) was captured on September
27 after the cutoff. It combines the collector's cumulative public counters
with separately sourced GitHub traffic, launch-page counters, outreach status,
issue review, and public code searches.

The late capture limits precision. GitHub release and crates.io counters are
cumulative and can include activity after the seven-day cutoff. GitHub's
traffic API returned daily buckets only through September 23, while referrers
covered its rolling window rather than the exact launch window. Downloads,
clones, and views count requests and can include maintainers, CI, bots, retries,
and repeat visitors. They cannot establish a successful installation or a
unique person. Verified installs, independent trials, adoption, feedback, and
defects require linked public evidence in the
[evidence ledger](metrics/evidence.jsonl).

## Results against launch targets

| Signal | Seven-day result | Target | Result |
| --- | ---: | ---: | --- |
| crates.io downloads | 37 cumulative requests | 20 verified installs/downloads | Download threshold met; verification absent |
| GitHub v0.1.2 binary archives | 18 cumulative requests | Supporting distribution signal | Directional only |
| Verified external installs | No public evidence found | 20 verified installs/downloads | Not met |
| Independent agent trials | No public evidence found | 3 | Not met |
| Substantive conversations | 1 linked evaluation | 5 | Not met |
| External repository adoptions | No linked merge found | Track public adoption | Not met |
| Confirmed critical data-loss defects | 0 reported | 0 | Met, with limited external use |

The download channels cannot be added into a unique-user total. The
[post-release baseline](metrics/2026-09-09-release-verified.json) had zero
v0.1.2 archive and crate downloads. The final capture had 18 v0.1.2 binary
archive requests and 37 total crate requests, including 23 for v0.1.2. The
repository had four stars, zero forks, and zero subscribers.

GitHub returned 226 repository page views and 286 clone requests across the
available September 17-23 daily buckets. The September 17 Show HN day accounted
for 162 page views. The rolling referrer report attributed 26 views to Hacker
News, two to Reddit, and one to AI Finderz; those figures are not restricted to
the exact launch window. Clone traffic was especially affected by project and
automation activity and is not adoption evidence.

[Show HN](https://news.ycombinator.com/item?id=49736484) finished with two
points and no comments. The
[DEV article](https://dev.to/jonghunyu/i-built-texio-so-coding-agents-can-edit-one-markdown-section-safely-2n61)
had two reactions and no comments. These are discovery signals and do not
establish an installation or product fit.

## Adoption and feedback

Public GitHub code searches found six repository-URL mentions outside the
Allra-Fintech organization, one `texio-cli` match in the crates.io index, and
no external `cargo install texio-cli` match. The six URL mentions were an
automated catalog entry and RSS or news mirrors. None showed a repository
workflow using Texio, so no public external adoption was evidenced.

Three maintainers received proposals based on reproduced public workflows:

- [Open-Toolchain Tekton Catalog](https://github.com/open-toolchain/tekton-catalog/issues/285)
  remained open with no response.
- [SQuADDS](https://github.com/LFL-Lab/SQuADDS/issues/68) remained open with no
  response.
- [dbt MCP](https://github.com/dbt-labs/dbt-mcp/issues/887#issuecomment-5750484580)
  produced the one substantive external evaluation. A collaborator judged that
  the extra binary was not justified for a non-production generator that
  already worked and was not hand-edited. No trial or adoption followed.

The three Chinese-language directory submissions documented in
[Chinese-language promotion](chinese-promotion.md) remained pending. No public
listing URL or attributable editorial response was recorded for 爱自由 · AI
自由, AI旗页, or 拾品号导航, so these events remain outreach rather than adoption.

The dbt MCP response is useful product evidence: correctness improvements are
insufficient when installation and dependency cost exceed the pain of the
current workflow. The outreach tested three maintainer-selected cases, but
project-authored reproductions do not count as independent trials. No new
substantive public event beyond the existing dbt response qualified for the
evidence ledger during final review.

## Correctness, installation, and portability

No external report described data loss, an incorrect target, or another
critical or high-impact correctness failure. Nine Texio issues were created
during the window: six project-authored promotion or merge tasks and three
automation-authored repository setup tasks. None was an external user defect.
Zero confirmed critical defects is therefore supported by the public issue and
evidence review, while the absence of independent trials sharply limits
confidence in real-world correctness.

The published crate and four v0.1.2 release archives for Apple Silicon macOS,
Intel macOS, x86-64 Linux, and x86-64 Windows remained available. Public
counters show that both distribution routes received requests. No external
user confirmed a successful installation or reported a portability failure,
so the launch cannot distinguish a smooth install from an abandoned attempt.

## What worked

- The launch assets made the safety claim reproducible through a small demo,
  benchmark, recipes, checksums, release archives, crates.io, Homebrew, and an
  Agent Skill.
- Show HN produced the clearest discovery spike: 162 page views arrived on
  September 17, compared with 64 across the next six available daily buckets.
- Public packaging counters moved from zero after v0.1.2 release verification
  to measurable crate and binary traffic.
- The outreach generated one candid evaluation with a concrete reason not to
  adopt, which is more useful than an unexplained click.
- Chinese-language and free-directory submissions broadened discovery testing
  without paid placement, while their pending status was kept separate from
  confirmed listings and adoption.

## What failed

- The campaign did not convert discovery into a verified install, independent
  trial, or merged external adoption.
- Promotion produced no public technical discussion on Show HN or DEV and only
  one of three workflow proposals received a response.
- The workflow proposals led with structural correctness where at least one
  maintainer saw no current failure worth a new dependency.
- Three Chinese-language directory submissions had no confirmed public listing
  or attributable editorial response at final review.
- Aggregate download, clone, and view counters were too ambiguous to show
  whether a person installed Texio and completed a task; the late capture also
  prevents an exact cutoff comparison.

## Decision

The next product priority is **three assisted external workflow trials with a
no-install-or-one-command path, before any new feature work**. Preserve the
Markdown-only scope and the current fail-closed editing contract. For each
trial, record the installation path, time to first successful dry run, task
outcome, and any correctness or portability failure. Stop after three trials
and decide whether packaging friction or weak workflow value is the larger
barrier.

This decision follows the evidence: correctness has no confirmed critical
failure, distribution attracted requests, and the only substantive evaluator
rejected the dependency cost rather than the Markdown behavior. More features
or broader promotion would not resolve the missing proof of successful use.

Issue [#8](https://github.com/Allra-Fintech/texio/issues/8) stays open. Although
its launch assets and promotion channels were published, the campaign still
lacks verified adoption examples and did not meet the launch outcome targets.
