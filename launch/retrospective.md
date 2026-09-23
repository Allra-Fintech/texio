# Seven-day public launch retrospective

## Window and method

The launch window starts with the
[Show HN publication](https://news.ycombinator.com/item?id=49736484) at
2026-09-17 04:39:42 UTC and ends at 2026-09-24 04:39:42 UTC. The final public
counter snapshot will be collected immediately after the window closes. This
draft uses the [pre-retrospective snapshot](metrics/2026-09-23-pre-retrospective.json),
collected at 2026-09-23 01:59 UTC, and will replace it with the final snapshot
before publication.

Public counters are directional signals. crates.io and GitHub count requests,
not people or successful installations. GitHub traffic includes bots, retries,
maintainer activity, and CI. Verified installs, independent trials, adoption,
feedback, and defects require linked evidence in the
[evidence ledger](metrics/evidence.jsonl).

## Results against launch targets

| Signal | Seven-day result | Target | Result |
| --- | ---: | ---: | --- |
| crates.io downloads | 37 requests | 20 verified installs/downloads | Download threshold met; verification absent |
| GitHub v0.1.2 binary archives | 16 requests | Supporting distribution signal | Directional only |
| Verified external installs | 0 evidenced | 20 verified installs/downloads | Not met |
| Independent agent trials | 0 evidenced | 3 | Not met |
| Substantive conversations | 1 linked evaluation | 5 | Not met |
| External repository adoptions | 0 linked merges | Track public adoption | Not met |
| Confirmed critical data-loss defects | 0 | 0 | Met |

The download channels cannot be added into a unique-user total. The
[post-release baseline](metrics/2026-09-09-release-verified.json) had zero
v0.1.2 archive and crate downloads. By the pre-final capture, v0.1.2 had 16
binary-archive requests and the crate had 37 total requests. Four repository
stars were added from a zero-star baseline; forks and subscribers remained at
zero.

GitHub recorded 197 repository page views from September 17 through the latest
available daily bucket on September 21. Referrers attributed 21 views from
Hacker News, two from Reddit, and one from AI Finderz. Show HN finished the
pre-final observation with two points and no comments. The DEV article had two
reactions and no comments. These are discovery signals and do not establish an
installation or product fit.

## Adoption and feedback

No public code result showed a merged use of Texio outside repositories owned
by Allra-Fintech. GitHub code search found the crates.io index and automated
news or catalog copies, but no independent workflow integration. These results
are discovery, not adoption.

Three maintainers received proposals based on reproduced public workflows:

- [Open-Toolchain Tekton Catalog](https://github.com/open-toolchain/tekton-catalog/issues/285)
  had no response by the pre-final check.
- [SQuADDS](https://github.com/LFL-Lab/SQuADDS/issues/68) had no response by
  the pre-final check.
- [dbt MCP](https://github.com/dbt-labs/dbt-mcp/issues/887#issuecomment-5750484580)
  received the one substantive external evaluation. A collaborator judged that
  the extra binary was not justified for a non-production generator that
  already worked and was not hand-edited. No trial or adoption followed.

The dbt MCP response is useful product evidence: correctness improvements are
not sufficient when installation and dependency cost exceed the pain of the
current workflow. The outreach also tested three maintainer-selected cases,
but project-authored reproductions do not count as independent trials.

## Correctness, installation, and portability

No external report described data loss, an incorrect target, or another
critical or high-impact correctness failure. Issues created in the Texio
repository during the window were project-authored promotion or maintenance
work, plus one automation-authored repository setup issue; none reported a
user defect. Zero confirmed critical defects is therefore supported by the
public issue and evidence review, while the absence of independent trials
limits confidence in real-world correctness.

The published crate and four v0.1.2 release archives for Apple Silicon macOS,
Intel macOS, x86-64 Linux, and x86-64 Windows remained available. The public
download counters show that both distribution routes were reached. No external
user confirmed a successful installation or reported a portability failure,
so the launch cannot distinguish a smooth install from an abandoned attempt.

## What worked

- The launch assets made the safety claim reproducible through a small demo,
  benchmark, recipes, checksums, release archives, crates.io, Homebrew, and an
  Agent Skill.
- Show HN produced the clearest discovery spike: 162 page views arrived on
  September 17, compared with 35 across the following four available daily
  buckets.
- Public packaging counters moved from zero after v0.1.2 release verification
  to measurable crate and binary traffic.
- The outreach generated one candid evaluation with a concrete reason not to
  adopt, which is more useful than an unexplained click.

## What failed

- The campaign did not convert discovery into a verified install, independent
  trial, or merged external adoption.
- Promotion produced no public technical discussion on Show HN or DEV and only
  one of three workflow proposals received a response.
- The workflow proposals led with structural correctness where at least one
  maintainer saw no current failure worth a new dependency.
- Aggregate download and clone counters were too ambiguous to answer whether a
  person installed Texio and completed a task.

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

Issue [#8](https://github.com/Allra-Fintech/texio/issues/8) stays open. Its
campaign cannot be treated as complete while public adoption examples and the
launch metrics outcome remain unmet, even though the planned launch assets and
promotion channels were published.
