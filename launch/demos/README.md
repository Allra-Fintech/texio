# Reproduce the short section-edit demo

Open `section-workflow.html` locally after downloading it, or serve this checkout
with `python3 -m http.server` and open the file's localhost URL. It has no remote
dependencies. GitHub's file view shows source rather than playing HTML.

The player has play/pause, restart and a keyboard-accessible timeline. Its
55-second duration is editorial pacing, not measured command execution time.
Adjacent JSON contains actual commands, output, exit codes, recording timestamp
and binary/recorder hashes. This is an internal synthetic demo, not a real
external user trial or an agent reasoning/token measurement.

To record a fresh copy, verify the published binary's archive checksum using
the [installation instructions](../../docs/installation.md), then from the
repository root:

```sh
python3 scripts/record-section-demo.py --texio /path/to/texio --output-dir /tmp/new-section-demo
```

Choose an unused output directory. Python 3.9+ and Git must be installed. The
recorder creates a disposable document, executes heading/section inspection,
preview and write, runs `git diff --no-index`, and checks the exact resulting
bytes. It adds a duplicate heading, requires exit 5 and verifies unchanged
input. Failed verification aborts before creating artifacts; no real repository
document is modified. CI executes the recorder with Python optimization enabled
against the Linux source build to keep these checks reproducible.

`git diff --no-index` returns 1 for the expected changed document. That is a
successful diff comparison here, not a failed Texio operation. The published
recording uses Texio 0.1.3; a future source-build recording may report another
version and must not be presented as the same binary or timing result.

## Verify published artifacts

The recorder also validates parsed headings, exact section text, expected
preview/diff changes and the ambiguous-target diagnostic. To compare a fresh
recording with the published JSON and HTML, run from the repository root:

```sh
python3 -O scripts/check-section-demo.py /tmp/new-section-demo
python3 -O scripts/test-section-demo.py --texio /path/to/texio --generated /tmp/new-section-demo
```

Only recording timestamp and binary hash may differ across recordings. Events,
exit codes, output, version, recorder hash and HTML template must match. Each
HTML payload must exactly match its own adjacent JSON, including metadata.
The current source version must match the published recording version; a
version or recorder change requires regenerating the committed artifacts.
Git output options are pinned for reproducibility. Fault checks reject altered
artifacts and successful-but-empty or incorrect CLI output before publication.
