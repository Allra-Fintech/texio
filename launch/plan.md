# Texio launch execution

## Before public release

- Validate the name across developer ecosystems and the broader web.
- Add CommonMark and GitHub Flavored Markdown conformance fixtures.
- Publish benchmark results for targeted editing versus whole-file rewriting.
- Produce signed binaries for macOS, Linux, and Windows.
- Complete security and correctness review.

## Launch assets

- README with executable examples
- Agent integration instructions
- Ten tested problem-oriented recipes
- Terminal demonstration: regex versus Texio
- Terminal demonstration: whole-file rewrite versus surgical replacement
- Reproducible benchmark repository
- GitHub release notes and installation instructions

## Distribution

- GitHub Releases
- crates.io as `texio-cli`, exposing the `texio` executable
- Homebrew tap
- npm installer wrapper after binary releases stabilize
- Agent skill after the CLI contract stabilizes
- MCP adapter only if it adds value beyond shell invocation

## Promotion

- Show HN launch centered on safe Markdown editing for agents
- Technical article: “Stop letting AI agents rewrite your entire README”
- Short before/after demonstrations for developer communities
- Useful contributions to open-source documentation workflows
- Public adoption examples and benchmark updates

### AI Finderz directory submission

- Tracking issue: [#95](https://github.com/Allra-Fintech/texio/issues/95).
- Submitted via [AI Finderz](https://aifinderz.com/submit-ai-tool/) under **Developer Tools**.
- Project URL: https://github.com/Allra-Fintech/texio.
- Positioning: free, MIT-licensed Markdown CLI for shell scripts and AI agents;
  deterministic heading discovery, section extraction, and surgical replacement
  with dry-run previews and explicit errors for missing or ambiguous headings.
- Status (2026-09-22): submitted for review. The site confirmed:
  “Thanks! Your AI tool was submitted for review.”
  AI Finderz reviews submissions before publishing; no listing is confirmed.
- Follow-up (2026-09-29): check for review feedback or a public listing. Add the
  listing URL and any attributable referral/adoption evidence when available.

### Additional free directory submissions

Tracked in [#98](https://github.com/Allra-Fintech/texio/issues/98), following
[research #97](https://github.com/Allra-Fintech/texio/issues/97). Status checked
2026-09-22. Use free submission routes only; no paid placement or expedited review.

| Directory | Status | Next step |
| --- | --- | --- |
| [Future Tools](https://futuretools.io/submit-a-tool) | Submitted under Other / Open Source; page confirmed “Tool Submitted!” and editorial review. | Check for a listing on 2026-09-29; approval is not guaranteed. |
| [Console](https://console.dev/selection-criteria) | Email submission sent to hello@console.dev on 2026-09-22; verified in Mail’s Sent folder. | Await editorial response; check status on 2026-09-29. Publication is not confirmed. |
| [AlternativeTo](https://alternativeto.net/faq/#add-a-new-application) | Pending sign-in or account creation, including password, CAPTCHA, and email verification. | User completes account access; then submit via the standard free queue, without priority review. |
| [ToolScout](https://toolscout.ai/submit/repo) | Free GitHub-repository route accepts developer tools and CLIs; sign-in requires terms acceptance. | Await user approval of terms and complete sign-in, then submit the repository. |
| [Futurepedia](https://www.futurepedia.io/submit-tool) | Skipped: the free-listings FAQ explicitly says free submissions are no longer offered. | Revisit only if a free route becomes available. |
| [OpenSourceAlternative.to](https://opensourcealternative.to/submit) | Not submitted: requires a self-hosted alternative to a named proprietary product; no credible counterpart identified for Texio. | Reconsider only with an accurate eligibility match; do not invent a competitor to complete the form. |

Submission positioning: Texio is a free, MIT-licensed Markdown CLI for shell
scripts and AI-agent workflows, with heading discovery, section extraction,
surgical replacement, and dry-run previews. Clearly describe it as deterministic
tooling for agents rather than a generative AI model. Keep the contact email out
of public repository records. Record published listing URLs when available.
