# Launch readiness evidence

## Installation audit

Completed for v0.1.2 under #47, #29, #30, #28, and release issue #48.
The initial audit found an unsupported Homebrew example and an unpublished
crate. The README now uses a tested quickstart, and the crate was published
after the owner verified their account email.

- [Tagged release](https://github.com/Allra-Fintech/texio/actions/runs/34332607844): formatting, lint, 29 tests, packaging, publish dry run, security audit, and all four binary builds passed.
- [Public installation](https://github.com/Allra-Fintech/texio/actions/runs/34333101992): crates.io, downloaded archives, checkout installation, and the actual documented binary-install commands passed on Linux x86-64, Windows x86-64, Intel macOS, and Apple Silicon macOS.
- [Homebrew](https://github.com/Allra-Fintech/homebrew-tap/actions/runs/34333146721): the v0.1.2 formula installed and passed version, preview, and exact-edit tests on both macOS architectures, then merged into the public tap.
- [crates.io publication](https://github.com/Allra-Fintech/texio/actions/runs/34332614524): v0.1.2 published successfully; a separate local installation also passed the demo.

All four downloaded v0.1.2 archives matched their
[SHA-256 sidecars](evidence/checksums-v0.1.2.json). Machine-readable
[workflow results](evidence/verification-v0.1.2.json) retain run links and commit
identities. Archives are checksum-protected; they are not signed or notarized.
Release notes and installation examples identify the early-preview scope and
unverified platforms. The CLI implementation was unchanged by this release.

## Quickstart and demonstration

The README provides install, inspect, preview, write, and verify commands with
links to the agent policy and benchmark caveat. The
[automated quickstart record](evidence/quickstart-v0.1.1.json) verifies exact
output and an unchanged Usage section. Its timing is command-execution time,
not a novice usability study or a network-speed guarantee.

Reproduce the terminal demonstration with the released binary:

```sh
python3 scripts/launch-demo.py --texio /absolute/path/to/texio
```

The [v0.1.2 transcript](evidence/demo-v0.1.2.txt) records the binary's hash,
preview immutability, exact replacement, and missing/duplicate target refusal.
The disclosed regex baseline starts with the same fixture and fails at a
heading inside fenced code. This is a reproducible transcript, not an edited
video or evidence of a particular agent's intelligence.

The [v0.1.2 benchmark reproduction](evidence/benchmark-v0.1.2.json) passed the
checked-in benchmark verifier. It retains the four-fixture context-proxy
measurement and does not claim billing-token savings or general model quality.

## Agent policy validation

The current Codex session followed the repository's policy by inspecting
headings, reviewing dry-run output, applying the same replacement, and checking
the resulting diff. Six fresh Claude Code sessions then tested valid, missing,
and duplicate targets with the copyable policy in both `AGENTS.md` and
`CLAUDE.md` contexts.

The [cross-agent validation report](agent-validation/README.md) records the
policy revision, outcomes, evidence, reproduction procedure, and limitations.
All revised-policy trials inspected real headings. Both valid trials previewed
before writing and produced exact expected bytes; all missing and duplicate
trials stopped without writes. No trial used a generic edit tool.

This evidence covers six deterministic Claude Code fixtures and the observed
Codex workflow. It does not claim universal behavior across agents, models,
prompts, or repositories.

## Adoption baseline

The [initial baseline](metrics/2026-09-09-pre-promotion.json) and
[release-verified snapshot](metrics/2026-09-09-release-verified.json) record
public counters, source URLs, UTC timestamps, and testing-traffic limitations.
The [collection guide](metrics/README.md) defines each metric, daily collection,
comparison rules, and an evidence ledger for external trials and adoption.

Downloads include maintainer, CI, bot, and repeat traffic; counters may update
with delay. No independent adoption is inferred from these counts. Missing
external-install and trial evidence remains unmeasured rather than zero.
This task did not publish Show HN or community promotion posts.
