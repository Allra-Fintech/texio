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
