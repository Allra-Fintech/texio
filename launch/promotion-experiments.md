# Promotion experiments

Owner: #168. This plan is registered before the first publication. The user
authorized all five methods on 2026-10-23. Version 0.1.3 public installations
are verified; historical demonstrations remain internal evidence.

## What counts

Primary outcome: a unique external participant confirms a successful no-write
dry run on their own Markdown workflow, with version, task and result evidence.
Activation time runs from starting setup to that first successful preview;
record the participant's measured or approximate time and distinguish them.
Secondary outcome: the participant confirms a second useful use at least seven
days later, or links a merged external integration. A maintainer-run preview,
request, star, download, impression or unanswered offer is not activation.

Count people once across methods using a participant's public request issue as
the record. Do not collect email, IP addresses or private file contents. Record
first discovery and the method that helped them run the task separately. Allow
multiple assisted methods; do not assign full credit to every method. Unknown
attribution stays unknown. Ask participants; links alone do not prove exposure.

## Registered methods and decisions

| Method / issue | Attribution and denominator | Initial effort cap | Continue signal | Change or stop signal |
| --- | --- | --- | --- | --- |
| README comparison / #169 | `readme-comparison`; ask up to five opted-in readers whether they can identify the task, preview and next step | 2 hours preparation, 1 hour follow-up | At least 4/5 explain the preview correctly and two confirm their own first dry run | Revise once if fewer than 4/5 understand; no reach or fewer than five responses is inconclusive |
| Workflow review offer / #170 | `workflow-review`; count qualified opt-in requests, completed diff reviews and externally run previews | 3 requests or 3 hours assistance | At least 2/3 qualified requests reach an external first dry run | After three requests, zero activations or median assistance over 45 minutes: revise scope/setup before more recruitment |
| Agent and CI recipes / #171 | `agent-recipe` or `ci-recipe`; count external attempts, failures and successful previews separately | 2 hours preparation, 3 external attempts | At least 2/3 attempts succeed, with one reported repeat use after seven days | Two attempts hit the same blocker: repair instructions before increasing distribution |
| Consented case study / #172 | `case-study`; evidence from a completed external task, then qualified requests attributable to its publication | One participant, 2 hours editing after trial | Participant approves exact public artifact; later at least one attributable external activation | No participant/consent: remain blocked, never publish a synthetic story as a customer result |
| Targeted distribution / #173 | `github-tutorial` and `cli-listing` separately; count eligible publications, qualified requests and confirmed activations | One owned tutorial and one suitable listing; 2 hours each | At least two qualified requests and one external activation within 14 days of each publication | Zero qualified requests after 14 days: stop that channel for this cycle; unknown reach limits conclusions |

These are small-sample operating rules, not statistically significant conversion
estimates. They can tell us what to try next, not prove a method causes adoption.
Do not manufacture denominators from repository views. No click tracking or
runtime telemetry is installed. Public traffic counts are contextual only.

## Recording and allocation

Record public request URL, discovery source, assisted methods, version, task,
external confirmation URL, setup time, maintainer minutes, failure/objection,
repeat-use evidence and consent in the [outcome sheet](promotion-outcomes.csv).
Empty cells mean unmeasured. Keep declined and failed attempts in denominators.
Use `not-measured` rather than estimated time if nobody timed the setup.
Never overwrite historical results or turn unknowns into zero.

For each publication, record UTC publication time and exact URL in its issue.
Review at publication + 7 days for blockers, and + 14 days for allocation.
The daily monitor checks the due dates; no daily follow-up messages to users.
Ask once about seven-day repeat use only if the participant opts into follow-up.

At the 14-day review, report raw counts and confirmed activations per maintainer
hour, including preparation and support. Give 60% of the next cycle's effort to
the best supported method, 30% to the runner-up and 10% to a new test. Apply this
only after at least three external attempts per compared method; otherwise
retain the caps and gather evidence. If all methods fail, inspect objections
before more promotion. If a critical correctness defect appears, stop write
recommendations and repair/disclose it first. The existing three-trial product
direction review in #122 still takes precedence.

## Launch order and publication gates

1. Merge the reviewed README comparison, request form and recipes to develop.
2. Open the public workflow-review offer with a visible source tag; keep the
   default-branch assets accessible without requiring a release.
3. Publish one focused tutorial on the owned GitHub repository with affiliation, a synthetic runnable example,
   setup/dependency cost, and one source-tagged request link. This tutorial is
   not an external case study. Inspect existing posts for duplicates first.
4. Submit one suitable CLI listing only after checking current submission rules
   and duplicates. The user authorizes this bounded experiment despite the
   earlier blanket directory pause; no bulk submissions or paid promotion.
5. Assist opted-in requests, obtain exact-artifact consent for a real case
   study, then publish/distribute it. This step waits for actual participation.

Historical unanswered CVE/CleanTube proposals are not a new invitation pool.
Do not repeat declined offers. Further direct outreach needs a current concrete
workflow fit and a fresh rule/duplicate check, one maintainer at a time.

DEV is excluded from this AI-assisted promotional experiment: its [current guidelines](https://dev.to/guidelines-for-ai-assisted-articles-on-dev) prohibit AI-assisted promotion of a program, including the author's own. Do not publish AI-generated comments there. The existing DEV post is not treated as a fresh experiment publication.

