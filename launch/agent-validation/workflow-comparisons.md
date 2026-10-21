# Reproduce assisted workflow comparisons

These six small fixtures let a maintainer inspect the proposed section
operations before considering a dependency. They compare selected behavior
from pinned public updater code with an existing Texio executable. The
fixtures are synthetic and offline; they are not independent trials, current
production incident reports, full generator runs, or adoption evidence.

## Run locally

With Python 3 and the existing Texio 0.1.2 release installed:

```sh
python3 scripts/reproduce-assisted-cases.py --texio texio
```

Or use a built binary directly and save the machine-readable result:

```sh
cargo build --locked
python3 scripts/reproduce-assisted-cases.py \
  --texio target/debug/texio --output /tmp/texio-assisted-cases.json
```

On Windows use `target/debug/texio.exe` and a new writable output path, such as
`assisted-cases.json`. The result path must not already exist. The script does
not download or install anything, contact GitHub or external APIs, import
upstream generator modules, or modify repository documents. All CLI inputs
are disposable copies. It only invokes section extraction, dry-run previews
and stdout replacement, never `--write`. Temporary inputs are removed after
the run; only a requested new result file persists.

Every case must reproduce its recorded baseline and expected Texio output or
refusal. Any mismatch or command failure produces a nonzero script exit.
The JSON records the executable version/hash, fixture hashes, pinned source
URLs, actual baseline/CLI outputs, refusal codes and unchanged-input checks.
Existing output files are refused, even on a successful rerun.

## Cases and scope

| Case | Selected baseline behavior | Texio operation |
| --- | --- | --- |
| CVE reordered tables | Assigns generated tables by occurrence, putting Reported data under Patched after reordering | Two named body replacements retain the correct mapping and the footer |
| CleanTube lowercase boundary | Its next-heading expression skips lowercase `setup` and consumes that following section | Replaces only `Chaines` and preserves `setup` and `Usage` |
| CLIO nested heading | A substring match treats `Verify Installation` as a new target and drops its heading | Exact section extraction retains the nested heading |
| CLIO fenced comment | A shell comment beginning with `#` is treated as a real section boundary | The comment and the rest of the fenced example remain in the extracted body |
| Missing target | The isolated existing-section regex has no match | Preview exits 4 and leaves the input unchanged |
| Duplicate target | The isolated regex replaces its first match | Preview exits 5 and leaves the input unchanged |

The missing-target baseline only exercises CleanTube's isolated replacement
expression. The full updater has separate insertion/append fallback branches;
this package does not run or characterize those branches. The duplicate case
likewise exercises only that expression. Neither refusal case attempts a
write, and neither replaces full integration validation.

The CVE baseline models its positional assignment with generated sample
tables; no vulnerability records are copied. CleanTube's JavaScript regex is
transcribed into Python for these ASCII/LF fixtures, so Node is not required.
Its outputs were checked against the published JavaScript expression for the
three included fixtures. This is not a claim of general regex equivalence.
Both CLIO extraction paths use the same adapted upstream cleanup. The
transcribed selector/cleanup outputs were checked against the two inspected
pure upstream methods for these fixtures; MDX rendering remains out of scope.

## Inspect the comparisons

The inputs, replacements, complete expected outputs, baseline outputs and
commit-specific source links are in [workflow-cases.json](workflow-cases.json).
The small local baseline adapters are in
[the reproduction script](../../scripts/reproduce-assisted-cases.py).
CLIO's adapted helpers retain their [BSD notice](workflow-baselines.NOTICE).

A write comparison previews each named body before computing the updated
document with `--stdout`. The second CVE replacement operates on a fresh
temporary copy of the first result. These are sequential operations, not a
transaction across both sections. Expected complete documents include the
unchanged neighboring content. A maintainer considering real integration
still needs their generated bodies, platform setup measurement, existing
checks and an explicit decision about dependency cost.

CI runs this package on Linux, macOS and Windows using the binary it just
built. Passing this package verifies the checked-in fixtures only. Do not
count it toward the three assisted external trial outcomes in
[#121](https://github.com/Allra-Fintech/texio/issues/121).
