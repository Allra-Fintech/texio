# Maintainer outreach packages

Prepared on 2026-09-15 for issue #79 and parent issue #36. The three upstream
files still matched the exact commits used by the reproducible pilot. No
maintainer message or external pull request has been sent.

Send these proposals one at a time, starting with Tekton Catalog. Publish the
[pilot report](workflow-pilots.md) on Texio's `main` branch first so its links
are stable. Recheck the target repository and search its issues again
immediately before contact.

## Open-Toolchain Tekton Catalog

**Route:** Open a normal
[GitHub issue](https://github.com/open-toolchain/tekton-catalog/issues/new).
The repository has issues enabled and no contribution guide or issue template.

**Suggested title:** Fail closed when generated README headings are missing

**Draft body:**

> Your `.ci/update_readme.py` already has a useful `--dry-run`, but its
> custom heading parser appends generated documentation when an expected
> heading is missing. I reproduced the `git/README.md` “Available tasks”
> update at commit `f7b166b` with Texio 0.1.2. The named-section update
> preserved every byte outside that section; missing and duplicate headings
> stopped without writing.
>
> Would you be open to a small trial that keeps the existing Python generator
> and uses a pinned, checksum-verified Texio binary only for the two final
> “Available tasks” and “Details” replacements? The behavior change would be
> deliberate refusal instead of appending content under a missing anchor. I
> would measure installation time and keep the current dry-run and lint steps.
>
> Reproduction and source hashes: [Texio workflow
> pilot](https://github.com/Allra-Fintech/texio/blob/main/launch/workflow-pilots.md).
> Texio is an MIT-licensed early preview; I maintain it.

**Before/after:** missing heading can append a new section; proposed trial exits
without writing. **Tradeoff:** a Rust binary becomes a pinned CI dependency.

## SQuADDS

**Route:** Open a
[General Issue](https://github.com/LFL-Lab/SQuADDS/issues/new?template=GENERAL_ISSUE.md).
The template requires checking existing issues and retaining its fields.

**Suggested title:** Make the contributor README update section-scoped

**Draft body fields:**

> **Describe the issue**
>
> The push-triggered contributor updater at commit `185f4e6` replaces the
> “Contributors” and “Developers” areas with one cross-section regular
> expression, normalizes the file ending, and then pushes to `master`. A
> boundary mistake can therefore affect both sections before the bot commit.
>
> I reproduced a representative “Contributors” update with Texio 0.1.2. The
> explicit named-section operation preserved the following “Developers” section
> and all other bytes, while missing and duplicate headings stopped without
> writing. Would you accept a small
> workflow trial that keeps the current data collection and `uv` checks but
> previews and applies those two generated bodies separately?
>
> **Steps to Reproduce**
>
> The commands, pinned source, and hashes are in the [Texio workflow
> pilot](https://github.com/Allra-Fintech/texio/blob/main/launch/workflow-pilots.md).
>
> **Expected behavior**
>
> The workflow updates only the two named bodies and refuses an ambiguous or
> missing heading before committing.
>
> **Actual behavior**
>
> The current regex spans both headings and writes the complete README result.
>
> **Environment details**
>
> Reproduced on macOS with Texio 0.1.2 against the pinned public README; this is
> a structural trial, not a run of the full contributor fetch.
>
> **Additional context**
>
> Texio is an MIT-licensed early preview that I maintain. A trial would add a
> pinned, checksum-verified binary download to the workflow.

**Before/after:** one regex owns two adjacent sections; proposed trial gives
each body an explicit boundary. **Tradeoff:** installation time and a new CI
binary must justify the narrower write surface.

## dbt MCP

**Route:** Use the repository's
[feature request](https://github.com/dbt-labs/dbt-mcp/issues/new?template=feature_request.yml).
Its contribution guide explicitly directs questions and requests to GitHub
issues. Do not open an implementation pull request before maintainers accept
the non-Python dependency; later code would require signed commits, a changelog
entry, and the project's checks.

**Suggested title:** Consider a structural boundary for generated README tools

**Draft form fields:**

> **Is your feature request related to a problem?**
>
> `scripts/generate_docs.py` at commit `231970b` finds the generated README
> “Tools” boundary with a multiline regex. Its explicit missing-section failure
> is good, but a structural heading selector would also ignore heading-like
> strings inside fenced examples and reject duplicate targets.
>
> **Describe the solution you'd like**
>
> First, confirm whether the project would consider a pinned, verified
> non-Python documentation-build dependency. If yes, I can prepare a measured
> trial that keeps the existing generator and `task docs:generate CHECK_FLAG=1`
> behavior, then passes only the generated body to Texio for dry-run and write.
> Against the pinned README, Texio 0.1.2 changed only “Tools”; all outside bytes
> remained identical, and missing or duplicate headings caused no write.
>
> **Describe alternatives you've considered**
>
> Keep the current regex, or replace it with a Python Markdown parser. Either
> avoids a Rust binary download; the latter adds a Python library and needs its
> own byte-preservation contract.
>
> **Additional context**
>
> Reproduction and hashes: [Texio workflow
> pilot](https://github.com/Allra-Fintech/texio/blob/main/launch/workflow-pilots.md).
> Texio is an MIT-licensed early preview; I maintain it. I would include binary
> installation timing before proposing code.

**Before/after:** a regex identifies one generated section; proposed trial uses
the Markdown heading tree and preserves the existing check mode. **Tradeoff:**
this project is Python-first and already fails safely when “Tools” is absent,
so the dependency may cost more than the added ambiguity protection.

## Outcome recording

For each approved send, write one compact public event using the schema in
`launch/metrics/README.md` to `launch/metrics/evidence.jsonl`. Record the exact
public draft, channel, substantive public response, and disposition in issue #8.
Use `accepted`, `declined`, `no-response`, or `unsuitable`; do not count an
opened issue as adoption, and do not copy private replies or personal data into
public records. Convert a repeated product limitation into a Texio issue only
after the same need appears in more than one independent workflow.
