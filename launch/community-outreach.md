# Community outreach review

Rules checked on 2026-09-15 and rechecked before the first publication. This
document now records published outreach as well as the remaining plan. Recheck
the linked rules immediately before each later post. The machine-readable
[rule record](evidence/community-rules-2026-09-15.json) captures the review.

## Recommended order
| Priority | Community | Why it fits | Publication condition |
| --- | --- | --- | --- |
| 1 | [`r/github` self-promotion thread](https://www.reddit.com/r/github/comments/1jy8rea/promote_your_projects_here_selfpromotion/) | The thread explicitly accepts GitHub-hosted tools and asks for a short description and repository link. | Published in the designated thread; monitor for substantive replies. |
| 2 | [DEV `#showdev`](https://dev.to/t/showdev) | A durable tutorial can be indexed and found later by developers and agents. | A human author must verify every claim, select the current AI-disclosure tier, and keep the article educational rather than promotional. |
| — | [`r/LLMDevs`](https://www.reddit.com/r/LLMDevs/) | The audience builds LLM and agent systems, and its policy explicitly permits free open-source projects. | Withdrawn after duplicate cleanup; both submitted copies now resolve as author-deleted. |

The `r/github` comment was published on 2026-09-17: [Texio in the self-promotion megathread](https://www.reddit.com/r/github/comments/1jy8rea/comment/pa9h13r/). It includes the tested install command, a dry-run example, the repository link, agent-client context, and maintainer/AI disclosures. Monitor it for substantive questions or workflow examples.

Two accidental `r/LLMDevs` copies were submitted on 2026-09-17. The older duplicate was deleted intentionally; the intended retained copy also became author-deleted during cleanup. Neither URL is active, so this channel is recorded as withdrawn rather than published outreach.

Publish one channel at a time and answer substantive questions before using the next channel. Do not ask for votes or reuse identical copy.
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
- **Proposed title:** I built Texio so coding agents can edit one Markdown section safely
- **Tags:** `showdev`, `rust`, `ai`, `markdown`
- **DEV disclosure tier:** AI-Assisted (Some AI)
- **Target reading time:** under three minutes

#### Article copy

Coding agents often need to change one section in a README. The usual shortcuts—regex replacement or regenerating the whole file—can silently cross a structural boundary.

I built [Texio](https://github.com/Allra-Fintech/texio), an MIT-licensed Rust CLI that gives agents a smaller, fail-closed interface for Markdown: list real headings, inspect one section, preview one replacement, then apply it explicitly.

Here is a small failure case. The second heading-shaped line is only example text inside a fence:

~~~markdown
# Demo

## Installation
old command

```md
## Installation
example only
```

## Usage
keep this
~~~

A text regex can mistake the fenced line for a section boundary. Texio parses the document structure instead:

~~~bash
cargo install texio-cli --version 0.1.2 --locked
texio headings demo.md --json
texio replace demo.md \
  --section Installation \
  --text 'cargo install texio-cli --locked' \
  --dry-run
~~~

The dry run prints a unified diff and leaves the file unchanged. Replace `--dry-run` with `--write` only after reviewing that diff. If `Installation` is missing or appears more than once as a real heading, Texio refuses to write instead of guessing.

I also packaged this workflow as an [Agent Skill](https://github.com/Allra-Fintech/texio/tree/main/skills/texio-markdown) for Codex, Claude Code, and compatible clients. The instructions make agents inspect headings, preview the exact edit, write it, and check the repository diff:

~~~bash
npx --yes skills@1.5.26 add \
  https://github.com/Allra-Fintech/texio/tree/2141d66531ad10a748e11c566428fba3e80c7e4e/skills/texio-markdown \
  --skill texio-markdown
~~~

The checked-in [four-fixture benchmark](https://github.com/Allra-Fintech/texio/blob/main/launch/evidence/benchmark-v0.1.2.json) passed 4/4 cases with Texio, 3/4 with an idealized whole-file baseline, and 2/4 with the disclosed regex proxy. That is a small mechanics benchmark, not a claim about every Markdown document, model, or token bill.

I maintain Texio. I would especially value examples of repository automation that currently rewrites a README or uses a multiline regex to replace one named section.

*Disclosure: I wrote and verified the project claims, commands, and results. AI tools assisted with development and editing this article; the DEV disclosure tier should be set to “AI-Assisted (Some AI).”*
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

After publication, write the documented compact public outcome fields to
`launch/metrics/evidence.jsonl`. Record the channel and substantive public
feedback in issue #8. Treat views and votes as attention signals, not proof of
adoption; never copy private replies or personal data into either public record.
