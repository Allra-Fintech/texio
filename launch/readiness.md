# Launch readiness evidence

## Installation audit

Tracked by #47, #29, #30, #28, and release issue #48. The initial audit found
an unsupported `brew install texio` example and an unpublished crate. The
example was replaced with a copyable inspect, preview, and write quickstart.
The crate's owner verified their email and the
[v0.1.1 publication succeeded](https://github.com/Allra-Fintech/texio/actions/runs/34331033440).

All four v0.1.1 release archives were downloaded and matched their adjacent
SHA-256 sidecars. The Apple Silicon archive reports `texio 0.1.1` and passes the
[recorded launch demonstration](evidence/demo-v0.1.1.txt). The public-install
workflow verifies crate, downloaded archive, and checkout installation on
Linux, Windows, Intel macOS, and Apple Silicon macOS; final run evidence will
be recorded after it completes.

## Quickstart and demonstration

The README's first example now provides installation, heading discovery,
section extraction, a dry run, an explicit write, and links to the agent policy
and benchmark caveat. Binary installation avoids a potentially long Rust build.
The five-minute target is a usability target, not a guarantee of network speed.

Reproduce the terminal demonstration with:

```sh
python3 scripts/launch-demo.py --texio /absolute/path/to/texio
```

The script starts Texio and the disclosed regex baseline with the same fixture.
The regex mistakes a fenced heading for a boundary; Texio preserves the entire
unrelated suffix. Missing and duplicate target scenarios refuse without writes.
The recording contains the released executable's hash. This transcript is a
reproducible terminal demo, not an edited video.

## Agent policy validation

The current Codex session followed the repository's AGENTS.md policy by
inspecting headings, reviewing dry-run output, and applying the same section
replacement. The demo repeats missing and ambiguous target scenarios for the
same vendor-neutral policy in AGENTS.md and CLAUDE.md contexts. These scripted
scenarios validate CLI behavior; they do not prove independent agent adherence.
No Claude runtime is available in this environment, so cross-agent behavior
remains unverified and #32 must stay open until actual agent trials are recorded.

## Adoption baseline

The [pre-promotion snapshot](metrics/2026-09-09-pre-promotion.json) captures
public API counters and collection timestamps. See the
[metric definitions and evidence rules](metrics/README.md). Maintainer and CI
downloads are included in public counters and must not be claimed as external
installs. Public promotion has not been performed by this task.
