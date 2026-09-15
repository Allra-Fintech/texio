# Agent skill selection validation

On 2026-09-14, fresh Claude Code and Codex sessions tested the installable
`texio-markdown` skill without naming Texio in their task prompts.

| Host | Markdown edit | Missing section | Plain-text control |
| --- | --- | --- | --- |
| Claude Code 2.1.267 (`claude-sonnet-5`) | Selected Texio; exact output | Selected Texio; zero writes | Did not select Texio; exact output |
| Codex CLI 0.149.1 | Selected Texio; exact output | Selected Texio; zero writes | Did not select Texio; exact output |

Each host received the same three prompts in isolated Git repositories. The
positive prompt requested a named Markdown section replacement while preserving
unrelated bytes. The refusal prompt targeted a missing Markdown section. The
control prompt edited a `.txt` file. The released Texio 0.1.2 binary was on
`PATH`; the skill was installed in each host's project skill directory.

Run [`scripts/evaluate-agent-skill.py`](../../scripts/evaluate-agent-skill.py)
to reproduce the trials and export sanitized JSON results. Raw agent event
streams stay outside the repository because they contain local session and
account metadata.

These six deterministic trials establish correct selection for the tested
prompts and host versions. They do not establish behavior across every model,
prompt, repository, or agent host. GitHub Copilot selection remains untested.
