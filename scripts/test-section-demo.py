#!/usr/bin/env python3
"""Reject transcript and artifact regressions, including with Python -O."""

import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def update_pair(directory, mutate):
    """Change a JSON payload and its HTML copy while retaining the template."""
    path = directory / "section-workflow.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    mutate(data)
    path.write_text(json.dumps(data), encoding="utf-8")
    page = directory / "section-workflow.html"
    text = page.read_text(encoding="utf-8")
    marker = '<script id="recording" type="application/json">'
    start = text.index(marker) + len(marker)
    end = text.index("</script>", start)
    page.write_text(text[:start] + json.dumps(data).replace("<", "\\u003c") + text[end:], encoding="utf-8")


def main():
    """Exercise allowed metadata changes and rejected output/template failures."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--texio", type=Path, required=True)
    parser.add_argument("--generated", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location("demo_checker", root / "check-section-demo.py")
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    with tempfile.TemporaryDirectory(prefix="texio-demo-checks-") as temporary:
        base = Path(temporary)
        for name, mutate in {
            "events": lambda d: d["events"][0].update(stdout="wrong"),
            "exit": lambda d: d["events"][0].update(exit=9),
            "recorder": lambda d: d.update(recorder_sha256="0" * 64),
            "missing-timestamp": lambda d: d.pop("recorded_at"),
            "missing-binary-hash": lambda d: d.pop("binary_sha256"),
        }.items():
            copy = base / name
            shutil.copytree(args.generated, copy)
            update_pair(copy, mutate)
            try:
                checker.check(copy, args.generated)
            except ValueError:
                print("Rejected altered", name)
            else:
                raise ValueError("accepted altered " + name)
        copy = base / "template"
        shutil.copytree(args.generated, copy)
        page = copy / "section-workflow.html"
        page.write_text(page.read_text(encoding="utf-8").replace("<title>", "<title>Changed "), encoding="utf-8")
        try:
            checker.check(copy, args.generated)
        except ValueError:
            print("Rejected altered template")
        else:
            raise ValueError("accepted altered template")
        copy = base / "metadata"
        shutil.copytree(args.generated, copy)
        update_pair(copy, lambda d: d.update(recorded_at="different timestamp", binary_sha256="1" * 64))
        checker.check(copy, args.generated)

        wrapper = base / "texio"
        wrapper.write_text("#!" + sys.executable + "\n" + '''import os, pathlib, sys
args = sys.argv[1:]
mode = os.environ['TEXIO_DEMO_FAULT']
if mode == 'headings' and args[0] == 'headings': raise SystemExit(0)
if mode == 'section' and args[0] == 'section': print('wrong'); raise SystemExit(0)
if mode == 'preview' and '--dry-run' in args: raise SystemExit(0)
if mode == 'refusal' and '--dry-run' in args and pathlib.Path(args[1]).read_text().count('## Installation') > 1: raise SystemExit(5)
os.execv(''' + repr(str(args.texio.resolve())) + ''', [''' + repr(str(args.texio.resolve())) + '''] + args)
''', encoding="utf-8")
        wrapper.chmod(0o755)
        for mode in ("headings", "section", "preview", "refusal"):
            output = base / ("rejected-" + mode)
            result = subprocess.run([sys.executable, "-O", str(root / "record-section-demo.py"),
                                     "--texio", str(wrapper), "--output-dir", str(output)],
                                    capture_output=True, env=dict(os.environ, TEXIO_DEMO_FAULT=mode), timeout=30)
            if result.returncode == 0 or output.exists():
                raise ValueError("accepted bad transcript: " + mode)
            print("Rejected bad transcript:", mode)


if __name__ == "__main__":
    main()
