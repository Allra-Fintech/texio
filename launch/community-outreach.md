# Community outreach review

Rules checked on 2026-09-15. This is a publication plan, not a record of posts:
no community message has been sent. Recheck the linked rules immediately before
posting. The machine-readable [rule record](evidence/community-rules-2026-09-15.json)
captures the review.

## Recommended order

| Priority | Community | Why it fits | Publication condition |
| --- | --- | --- | --- |
| 1 | [`r/LLMDevs`](https://www.reddit.com/r/LLMDevs/) | The audience builds LLM and agent systems, and its policy explicitly permits free open-source projects. | Disclose the author relationship, avoid marketing language, and lead with the reproducible agent-editing failure. |
| 2 | [`r/github` self-promotion thread](https://www.reddit.com/r/github/comments/1jy8rea/promote_your_projects_here_selfpromotion/) | The thread explicitly accepts GitHub-hosted tools and asks for a short description and repository link. | Comment only in the designated thread; keep it short and include the install path and example. |
| 3 | [DEV `#showdev`](https://dev.to/t/showdev) | A durable tutorial can be indexed and found later by developers and agents. | A human author must verify every claim, select the current AI-disclosure tier, and keep the article educational rather than promotional. |

Publish one at a time and answer substantive questions before using the next
channel. Do not ask for votes or reuse identical copy.

## Community-specific author sheets

These are fact sheets for the human publisher. They deliberately avoid a
ready-to-paste personal story.

### `r/LLMDevs`: deterministic Markdown edits for coding agents

- Problem: an agent often reads or rewrites a whole README to update one named
  section; a heading-like line inside a code fence can break a regex approach.
- Demonstration: run `texio headings demo.md --json`, preview the `Installation`
  replacement, apply it, then show that `Usage` stayed byte-for-byte unchanged.
- Agent path: `npx --yes skills@1.5.26 add https://github.com/Allra-Fintech/texio/tree/2141d66531ad10a748e11c566428fba3e80c7e4e/skills/texio-markdown --skill texio-markdown`.
- Evidence: fresh Codex and Claude Code trials selected the skill for named
  Markdown-section work; the checked-in mechanics benchmark passed 4/4 fixtures.
- Ask: which agent hosts and Markdown failure cases should be tested next?
- Disclose: the poster is the project author; Texio is MIT-licensed, free,
  Markdown-only, and an early preview. The 82.8% figure is a deterministic
  context proxy, not model-token usage.

### `r/github` thread: a narrow repository-maintenance tool

- One-sentence description: Texio is a Rust CLI that previews and applies one
  named Markdown-section replacement while preserving the rest of the file.
- Repository: <https://github.com/Allra-Fintech/texio>.
- Install: `cargo install texio-cli --version 0.1.2 --locked`.
- Small example: `texio replace README.md --section Installation --text 'new' --dry-run`.
- Context: useful in repository scripts and agent instructions when a missing or
  duplicate heading should stop the edit instead of guessing.
- Ask: feedback on real README automation that currently uses regular expressions
  or whole-file generation.

### DEV `#showdev`: reproduce a fenced-heading failure

- Article goal: teach the failure mode, then let readers reproduce the fix.
- Start with a README containing a real `## Installation` heading and another
  `## Installation` string inside a fenced example.
- Compare a disclosed regex proxy with Texio's parsed heading list, dry-run, and
  exact write. Link the raw four-fixture benchmark and explain its limits.
- Include both discovery paths: `cargo install texio-cli --version 0.1.2 --locked` and
  `npx --yes skills@1.5.26 add https://github.com/Allra-Fintech/texio/tree/2141d66531ad10a748e11c566428fba3e80c7e4e/skills/texio-markdown --skill texio-markdown`.
- Use `#showdev`; do not use `#opensource` for a single-project announcement.
- The publisher must choose DEV's current AI-disclosure tier and personally
  verify the prose, commands, and results. Do not use generated comments.

## Hold or exclude

| Community | Decision | Reason |
| --- | --- | --- |
| `r/rust` | Human-authored option only | Texio is relevant because it is written in Rust, but project posts must be Rust-primary, self-promotion is limited, and low-effort submissions, including work produced mainly by AI with minimal human intervention, may be removed. Use only for a technically detailed Rust implementation story written by the maintainer. |
| Rust Users Forum | Hold | The Terms reject machine-generated or traffic-driving spam. The announcements category is valid, but moderators muted it by default on 2026-09-10 after declining quality, reducing likely visibility. |
| Lobsters | Hold | Self-promotion should be under one quarter of a member's activity, new accounts have submission limits, and content without meaningful human authorship is treated as spam. Use only through an established, participating account. |
| `r/commandline` | Exclude | Its current rules prohibit generative-AI-related projects except already-popular projects and prohibit AI-generated titles or post text. Texio's agent positioning makes it a poor fit. |

## Shared reproducible path

Every published item should include or link to this verified sequence:

```sh
cargo install texio-cli --version 0.1.2 --locked
printf '# Demo\n\n## Installation\nold\n\n## Usage\nkeep\n' > demo.md
texio headings demo.md --json
texio section demo.md Usage > usage.before
texio replace demo.md --section Installation --text 'new' --dry-run
texio replace demo.md --section Installation --text 'new' --write
texio section demo.md Usage > usage.after
cmp usage.before usage.after
```

After publication, record the URL, UTC timestamp, channel, exact version, and
substantive feedback in both `launch/metrics/evidence.jsonl` and issue #8. Treat
views and votes as attention signals, not proof of adoption.
