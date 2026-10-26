#!/usr/bin/env python3
"""Recompute benchmark grades from immutable fixtures and every raw trial."""

import hashlib
import json
from pathlib import Path
import re
import statistics
import sys


def require(condition, message):
    """Reject inconsistent evidence even when Python runs with -O."""
    if not condition:
        raise ValueError(message)


def check(path):
    """Check provenance, coverage, raw grades, preservation and runtime summaries."""
    root = Path(__file__).resolve().parent
    data = (root / "cases.json").read_bytes()
    cases = {c["id"]: c for c in json.loads(data)}
    report = json.loads(path.read_text(encoding="utf-8"))
    require(report["schema_version"] == 1, "unsupported schema")
    require(report["manifest_sha256"] == hashlib.sha256(data).hexdigest(), "fixture mismatch")
    for name in ("structural/run.py", "structural/baseline.py", "run.py"):
        require(report["source_sha256"][name] == hashlib.sha256((root.parent / name).read_bytes()).hexdigest(), "source mismatch")
    require(re.fullmatch(r"[a-f0-9]{64}", report["binary_sha256"]), "invalid binary hash")
    require(report["agent_model"] is None and report["agent_tokens"] is None, "no agent measurement performed")
    require(type(report["runs_per_case"]) is int and report["runs_per_case"] > 0, "invalid runs")
    methods = {"texio", "regex", "whole-document"}
    seen = set()
    passed = dict.fromkeys(methods, 0)
    for row in report["results"]:
        key = (row["case"], row["method"])
        require(key not in seen and key[0] in cases and key[1] in methods, "duplicate or unknown row")
        seen.add(key)
        case = cases[key[0]]
        require(row["expected"] == case["expected"] and row["expected_exit"] == case["expected_exit"], "oracle changed")
        trials = row["trials"]
        require(len(trials) == report["runs_per_case"], "missing raw trials")
        for t in trials:
            require(type(t["runtime_ns"]) is int and t["runtime_ns"] >= 0, "invalid runtime")
            require(t["input_unchanged"] == (t["actual"] == case["input"]), "false unchanged flag")
        success = all(t["exit"] == case["expected_exit"] and t["actual"] == case["expected"] and
                      (key[1] != "texio" or t["preview_exit"] == case["expected_exit"]) for t in trials)
        require(row["success"] == success, "false pass grade")
        repeatable = len({(t["exit"], t["actual"]) for t in trials}) == 1
        require(row["repeatable"] == repeatable and repeatable, "nonrepeatable result")
        for side in ("prefix", "suffix"):
            region = case["protected_" + side]
            preserved = all((t["actual"].startswith(region) if side == "prefix" else t["actual"].endswith(region)) for t in trials)
            require(row["protected_" + side + "_unchanged"] == preserved, "false preservation grade")
        times = [t["runtime_ns"] for t in trials]
        require(row["runtime_ns"] == {"min": min(times), "median": int(statistics.median(times)), "max": max(times)}, "false timing summary")
        passed[key[1]] += success
    require(len(cases) >= 20 and len(seen) == len(cases) * 3, "incomplete coverage")
    for method in methods:
        require(report["methods"][method] == {"passed": passed[method], "total": len(cases)}, "false aggregate")
    require(passed["texio"] == len(cases), "Texio regression")
    print(json.dumps(report["methods"], indent=2))


if __name__ == "__main__":
    check(Path(sys.argv[1]))
