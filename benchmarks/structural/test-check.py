#!/usr/bin/env python3
"""Ensure inconsistent raw comparison evidence fails validation, including -O."""

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile


def main():
    """Validate one real report, then reject six independently corrupted copies."""
    spec = importlib.util.spec_from_file_location("checker", Path(__file__).with_name("check.py"))
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    source = Path(sys.argv[1])
    with contextlib.redirect_stdout(io.StringIO()):
        checker.check(source)
    original = json.loads(source.read_text(encoding="utf-8"))
    mutations = {
        "grade": lambda r: r["results"][0].update(success=False),
        "raw-output": lambda r: r["results"][0]["trials"][0].update(actual="wrong"),
        "missing-row": lambda r: r["results"].pop(),
        "aggregate": lambda r: r["methods"]["texio"].update(passed=0),
        "timing": lambda r: r["results"][0]["runtime_ns"].update(median=-1),
        "oracle": lambda r: r["results"][0].update(expected="wrong"),
    }
    with tempfile.TemporaryDirectory() as directory:
        for name, mutate in mutations.items():
            report = json.loads(json.dumps(original))
            mutate(report)
            path = Path(directory) / (name + ".json")
            path.write_text(json.dumps(report), encoding="utf-8")
            try:
                checker.check(path)
            except ValueError:
                print("Rejected corrupted", name)
            else:
                raise ValueError("Accepted corrupted " + name)


if __name__ == "__main__":
    main()
