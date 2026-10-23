# Send a Markdown workflow for a no-install diff review

I maintain Texio, a Markdown CLI. Share one public Markdown document, its exact
target heading, and what should change. I can prepare a proposed diff before
you install anything. Start with [a workflow request](https://github.com/Allra-Fintech/texio/issues/new?template=workflow-review.yml&source=workflow-review).

This small pilot takes up to three qualified requests. A useful request has a
real named-section update, a public or minimal synthetic example and a desired
outcome. Do not post credentials, private documents or production data. If a
template generator or a small change to your existing updater fits better,
that is a valid outcome; another binary dependency has a cost.

## What happens

1. You share the task and expected preserved content. No installation needed.
2. I prepare a disposable-copy comparison and explain its limitations. No
   changes to your repository or CI happen without your request.
3. If useful, you try a no-write preview with verified Texio 0.1.3 and report
   version, result and measured or approximate setup time in your request.
4. We record blockers and whether a later second use helped. Seven-day
   follow-up and discussing a case study are optional; publishing a finished
   story or quote needs your explicit approval.

Reviewing my diff is useful feedback. Only your confirmed execution on your own
workflow counts as an external first use. A synthetic example alone does not.

## Try before asking

See the [command comparison](../README.md#extract-a-markdown-section),
[installation options](installation.md), and [agent/CI trial paths](trial-recipes.md).
Preview with `--dry-run` first. Texio refuses missing or ambiguous headings;
it does not make multiple section replacements a single transaction.

The [experiment plan](../launch/promotion-experiments.md) explains the public
outcome measures. No runtime telemetry or click tracking is installed.
