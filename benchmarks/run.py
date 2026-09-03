#!/usr/bin/env python3
"""Deterministic Markdown editing benchmark; standard library only."""

import argparse
import difflib
import hashlib
import json
from pathlib import Path
import re
import statistics
import subprocess
import tempfile
import time


ROOT = Path(__file__).resolve().parent
TOKEN_PATTERN = re.compile(r"\w+|[^\w\s]", re.UNICODE)


def token_count(value):
    """A fixed lexical token proxy, not a model tokenizer."""
    return len(TOKEN_PATTERN.findall(value))


def naive_replace(document, heading, replacement):
    """Replace after the first matching ATX heading using line regexes."""
    pattern = re.compile(rf"(?m)^(#{{1,6}})[ \t]+{re.escape(heading)}[ \t]*#*[ \t]*\r?$" )
    match = pattern.search(document)
    if not match:
        return 4, document
    level = len(match.group(1))
    body_start = document.find("\n", match.end())
    body_start = len(document) if body_start < 0 else body_start + 1
    boundary = re.compile(rf"(?m)^#{{1,{level}}}[ \t]+")
    next_heading = boundary.search(document, body_start)
    body_end = next_heading.start() if next_heading else len(document)
    normalized = replacement.rstrip("\r\n") + "\n"
    return 0, document[:body_start] + normalized + document[body_end:]


def naive_extract(document, heading):
    pattern = re.compile(rf"(?m)^(#{{1,6}})[ \t]+{re.escape(heading)}[ \t]*#*[ \t]*\r?$")
    match = pattern.search(document)
    if not match:
        return 4, ""
    level = len(match.group(1))
    boundary = re.compile(rf"(?m)^#{{1,{level}}}[ \t]+")
    next_heading = boundary.search(document, match.end())
    end = next_heading.start() if next_heading else len(document)
    return 0, document[match.start():end]


def run_texio(binary, case, document):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "input.md"
        path.write_bytes(document.encode())
        command = [str(binary)]
        if case["operation"] == "extract":
            command += ["section", str(path), case["heading"]]
        else:
            command += [
                "replace", str(path), "--section", case["heading"],
                "--text", case["replacement"], "--write",
            ]
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
        actual = completed.stdout if case["operation"] == "extract" else path.read_text()
        return completed.returncode, actual, completed.stdout


def changed_lines(actual, expected):
    return sum(
        line.startswith(("+ ", "- "))
        for line in difflib.ndiff(expected.splitlines(), actual.splitlines())
    )


def unrelated_changes(document, actual, protected):
    return sum(document.count(line) != actual.count(line) for line in protected)


def execute(method, case, document, expected, binary):
    started = time.perf_counter_ns()
    if method == "whole-file":
        if case["expected_exit"] == 0:
            exit_code, actual, stdout = 0, expected, expected
        else:
            exit_code, actual = naive_replace(document, case["heading"], case["replacement"])
            stdout = actual
    elif method == "regex":
        if case["operation"] == "extract":
            exit_code, actual = naive_extract(document, case["heading"])
            stdout = actual
        else:
            exit_code, actual = naive_replace(document, case["heading"], case["replacement"])
            stdout = ""
    else:
        exit_code, actual, stdout = run_texio(binary, case, document)
    elapsed = time.perf_counter_ns() - started
    return exit_code, actual, stdout, elapsed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--texio", required=True, type=Path)
    parser.add_argument("--release", required=True)
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.runs < 1:
        parser.error("--runs must be positive")

    binary = args.texio.resolve()
    digest = hashlib.sha256(binary.read_bytes()).hexdigest()
    cases = json.loads((ROOT / "cases.json").read_text())
    rows = []
    for case in cases:
        document = (ROOT / case["input"]).read_text()
        expected = (ROOT / case["expected"]).read_text()
        request = (
            f"extract section {case['heading']}"
            if case["operation"] == "extract"
            else f"replace section {case['heading']} with {case['replacement']}"
        )
        for method in ("whole-file", "regex", "texio"):
            trials = [execute(method, case, document, expected, binary) for _ in range(args.runs)]
            exit_code, actual, stdout, _ = trials[-1]
            expected_exit = case["expected_exit"]
            repeatable = all(
                trial[0] == trials[0][0] and trial[1] == trials[0][1]
                for trial in trials
            )
            success = exit_code == expected_exit and (
                actual == expected
                if expected_exit == 0
                else actual == document
            )
            rows.append({
                "case": case["id"],
                "method": method,
                "success": success,
                "exit_code": exit_code,
                "unrelated_lines_changed": (
                    0 if case["operation"] == "extract"
                    else unrelated_changes(document, actual, case["protected"])
                ),
                "lines_different_from_expected": changed_lines(actual, expected),
                "markdown_preserved": actual == expected,
                "repeatable": repeatable,
                "input_tokens": token_count(request) + (token_count(document) if method == "whole-file" else 0),
                "output_tokens": token_count(stdout),
                "median_runtime_ns": int(statistics.median(trial[3] for trial in trials)),
            })

    methods = {}
    for method in ("whole-file", "regex", "texio"):
        selected = [row for row in rows if row["method"] == method]
        methods[method] = {
            "passed": sum(row["success"] for row in selected),
            "total": len(selected),
            "success_rate": sum(row["success"] for row in selected) / len(selected),
            "input_tokens": sum(row["input_tokens"] for row in selected),
            "output_tokens": sum(row["output_tokens"] for row in selected),
            "unrelated_lines_changed": sum(row["unrelated_lines_changed"] for row in selected),
        }
    result = {
        "schema_version": 1,
        "release": args.release,
        "binary_sha256": digest,
        "runs_per_case": args.runs,
        "token_metric": "Unicode words and punctuation; deterministic proxy, not model tokens",
        "methods": methods,
        "results": rows,
    }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
