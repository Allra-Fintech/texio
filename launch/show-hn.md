# Show HN launch sheet

Use this sheet to write the submission in your own words. Do not paste or adapt
generated prose into Hacker News: its current guidelines prohibit AI-generated
and AI-edited submission text.

## Posting rules
Published on 2026-09-17: [Show HN: Texio, reliable Markdown operations for shell scripts and AI agents](https://news.ycombinator.com/item?id=49736484). The submission links directly to the repository and was posted by the maintainer as `yuzong`. Monitor the thread and answer questions in the maintainer's own words; do not solicit votes or booster comments.

- The [Show HN guidelines](https://news.ycombinator.com/showhn.html) and
  [site guidelines](https://news.ycombinator.com/newsguidelines.html) were
  rechecked immediately before posting.
- The title begins with `Show HN:` and links directly to the
  [Texio repository](https://github.com/Allra-Fintech/texio).
- The public `texio-cli` 0.1.2 install and launch-sheet demo were reverified
  immediately before posting.
- Keep follow-up conversation human-authored and stay available to answer
  questions without asking for votes.
## Verified facts

- Texio is an MIT-licensed CLI for structural Markdown inspection, extraction,
  and section-body replacement.
- It parses headings, ignores heading-like text inside fenced code blocks,
  refuses missing or duplicate matches, previews a unified diff, and writes
  atomically while preserving bytes outside the selected body.
- Public version: `0.1.2` on
  [crates.io](https://crates.io/crates/texio-cli), GitHub Releases, and the
  `Allra-Fintech/tap/texio` Homebrew formula.
- The public `texio-markdown` agent skill is discoverable by the standard
  Skills installer. Fresh Claude Code and Codex trials selected it for named
  Markdown-section tasks and skipped it for a plain-text control. Read the
  [method and limits](https://github.com/Allra-Fintech/texio/blob/main/launch/agent-validation/skill-selection.md).
- In the checked-in four-fixture mechanics benchmark, Texio passed 4/4 cases,
  the idealized whole-file baseline passed 3/4, and the regex proxy passed 2/4.
  The reported 82.8% reduction is a deterministic context-size proxy, not
  model-token usage or billing. Inspect the
  [raw result](https://github.com/Allra-Fintech/texio/blob/main/launch/evidence/benchmark-v0.1.2.json).

## Reproducible try-it path

```sh
cargo install texio-cli --version 0.1.2 --locked
printf '# Demo\n\n## Installation\nold\n\n## Usage\nkeep\n' > demo.md
texio headings demo.md --json
texio replace demo.md --section Installation --text 'new' --dry-run
texio replace demo.md --section Installation --text 'new' --write
```

Agent skill:

```sh
npx --yes skills@1.5.26 add https://github.com/Allra-Fintech/texio/tree/2141d66531ad10a748e11c566428fba3e80c7e4e/skills/texio-markdown --skill texio-markdown
```

## Points worth discussing

- Why agents rewriting an entire README for one section is hard to review.
- Why parsing Markdown structure is safer than matching heading text with a
  generated regular expression.
- Whether a narrow CLI is more useful to agents than a broader document server.
- Which Markdown constructs or agent hosts should be tested next.

Keep the final submission comment under 300 words so it takes less than three
minutes to read. State that Texio is an early preview and Markdown-only.
