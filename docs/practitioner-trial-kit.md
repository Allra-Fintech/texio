# Try Texio on a real Markdown task

This kit is for an opted-in practitioner evaluating Texio 0.1.3, not a claim
that a trial has happened. Choose one task matching an actual workflow.
[Request assistance](https://github.com/Allra-Fintech/texio/issues/new?template=workflow-review.yml&source=practitioner-kit)
or use [the no-install review discussion](https://github.com/Allra-Fintech/texio/discussions/175).
Share public/minimal Markdown, never private data or credentials.

## Setup and evidence

Use the [verified installation paths](installation.md). Binary archives and the
macOS Homebrew tap avoid compiling; a Cargo source build may exceed five minutes.
Record OS, `texio --version`, installation path and setup start time. Ask for a
prepared diff first if installing another dependency is not justified.

Work on a disposable copy of your own document. Inspect headings before selecting
an exact target. Record task, command, expected result, actual result, setup time
(measured/approximate/unknown) and how much assistance was needed. Reviewing a
maintainer's diff is feedback; only your confirmed execution on your own workflow
counts as an external first use. A synthetic fixture alone does not.

## Task 1: refresh generated README content

Use a README section that your real generator refreshes, such as installation
instructions or a generated table. Keep the generator; evaluate only the final
section replacement. Put its complete desired body in `generated-body.md`, without
the selected heading. Retain wanted nested subsections, prose and separators.

```sh
texio headings README-trial.md --json
texio section README-trial.md Installation
texio replace README-trial.md --section Installation --from generated-body.md --dry-run
```

Replace the example file/heading with those from your task. Check the preview and
confirm the trial copy did not change. If you choose to apply, repeat with
`--write` on the disposable copy, inspect `git diff --no-index` against its original,
and compare content outside the target body byte-for-byte. Missing or ambiguous
headings stop the operation. Multiple replacements are independent operations, not one transaction.

Success: the actual generated body is correct and all unrelated bytes remain.
Record objections too: improving your existing selector or rebuilding a template
may be simpler than adding Texio. Do not propose production CI adoption merely
because this small trial worked.

## Task 2: provide an agent with one design section

Choose a real design/review task requiring one section and its nested subsections.

```sh
texio headings DESIGN-trial.md --json
texio section DESIGN-trial.md Authentication --body-only
```

Inspect the extracted text and confirm required context is present and unrelated
sections are excluded. If using an agent, provide this context for the actual task
and record which agent/session was used, whether it needed more context, and the
task result. The CLI check alone is not a fresh-agent-session validation or a
measurement of agent tokens, quality or billing savings.

Success: the practitioner confirms the scoped context was sufficient for their
actual task, or records what extra context was needed. No file should be changed.

## Task 3: test an unsafe target without writing

On a disposable copy, deliberately create two real headings with the target
name, then separately test a missing name:

```sh
texio replace README-duplicate.md --section Target --text proposed --dry-run
texio replace README-duplicate.md --section Missing --text proposed --dry-run
```

These commands are expected to fail: exit 5 for ambiguous target, exit 4 for a
missing target. Save status/output and compare each input before/after; both
must be byte-identical. Do not bypass the refusal by choosing a guessed match.
Record whether this failure mode helps or disrupts your actual automation.

## Optional result template

Post in your public request, omitting anything private:

```text
First discovery / assisting method:
Public workflow or minimal task:
Version / OS / installation path:
What I personally executed (or only reviewed):
Expected result / actual output or public run link:
Outside-section comparison / input unchanged check:
Setup minutes and measured/approximate/unknown:
Assistance minutes if known:
Failure, friction or reason to keep the existing approach:
Would I use this again? What remains uncertain?
May you ask me once after seven days? yes/no
Interested in a case study discussion? yes/no
```

Case-study interest is not publication consent. A finished story, attributed
quote, name or logo needs explicit approval of the exact artifact. Repeat use
requires actual later confirmation, not intent. Declines and failed attempts
remain in experiment denominators.

## Reproduce the kit mechanics

From a checkout after installation:

```sh
python3 scripts/check-practitioner-kit.py --texio /path/to/texio
```

This runs disposable synthetic examples of the three task types and checks
exact bytes, scoped extraction and both refusals. It does not run an agent or
count as a practitioner trial. The [experiment plan](../launch/promotion-experiments.md)
defines actual activation and repeat-use evidence. Run the product-direction
review in #122 after the first three external trials before expanding toward
the later five-trial target in #177; do not silently extend the pilot.
