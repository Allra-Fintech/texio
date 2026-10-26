#!/usr/bin/env python3
"""Run identical byte-level replacement tasks without giving methods the oracle."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import re
import statistics
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parent
METHODS = ("texio", "regex", "whole-document")


def require(condition, message):
    """Keep validation active with Python optimization enabled."""
    if not condition:
        raise ValueError(message)


def trial(binary, method, case):
    """Use a fresh byte-identical file and include process startup plus edit I/O."""
    with tempfile.TemporaryDirectory(prefix="texio-structural-") as directory:
        path = Path(directory) / "input.md"
        original = case["input"].encode("utf-8")
        path.write_bytes(original)
        if method == "texio":
            command = [str(binary), "replace", str(path), "--section", case["heading"],
                       "--text", case["replacement"], "--write"]
            preview = subprocess.run(command[:-1] + ["--dry-run"], capture_output=True, timeout=30)
            require(path.read_bytes() == original, "dry-run changed input")
            preview_code = preview.returncode
        else:
            command = [sys.executable, str(ROOT / "baseline.py"), method, str(path),
                       case["heading"], case["replacement"]]
            preview_code = None
        started = time.perf_counter_ns()
        result = subprocess.run(command, capture_output=True, timeout=30)
        elapsed = time.perf_counter_ns() - started
        actual = path.read_bytes()
        return {
            "exit": result.returncode,
            "runtime_ns": elapsed,
            "actual": actual.decode("utf-8"),
            "stdout": result.stdout.decode("utf-8").replace(str(path), "input.md"),
            "stderr": result.stderr.decode("utf-8").replace(str(path), "input.md"),
            "input_unchanged": actual == original,
            "preview_exit": preview_code,
        }


def main():
    """Save immutable raw trials, exact expectations, provenance and summaries."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--texio", type=Path, required=True)
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.runs < 1 or args.output.exists():
        parser.error("runs must be positive and output must not already exist")
    binary = args.texio.resolve()
    version = subprocess.run([str(binary), "--version"], capture_output=True, text=True, timeout=30)
    require(version.returncode == 0 and re.fullmatch(r"texio \S+", version.stdout.strip()), "invalid binary version")
    manifest_bytes = (ROOT / "cases.json").read_bytes()
    cases = json.loads(manifest_bytes)
    require(len(cases) >= 20 and len({c["id"] for c in cases}) == len(cases), "need 20 unique cases")
    rows = []
    for case in cases:
        require(case["input"].startswith(case["protected_prefix"]) and
                case["input"].endswith(case["protected_suffix"]), "invalid protected regions")
        for method in METHODS:
            attempts = [trial(binary, method, case) for _ in range(args.runs)]
            success = all(t["exit"] == case["expected_exit"] and t["actual"] == case["expected"]
                          and (method != "texio" or t["preview_exit"] == case["expected_exit"])
                          for t in attempts)
            times = [t["runtime_ns"] for t in attempts]
            rows.append({
                "case": case["id"], "category": case["category"], "method": method,
                "success": success,
                "expected_exit": case["expected_exit"], "expected": case["expected"],
                "repeatable": len({(t["exit"], t["actual"]) for t in attempts}) == 1,
                "protected_prefix_unchanged": all(t["actual"].startswith(case["protected_prefix"]) for t in attempts),
                "protected_suffix_unchanged": all(t["actual"].endswith(case["protected_suffix"]) for t in attempts),
                "runtime_ns": {"min": min(times), "median": int(statistics.median(times)), "max": max(times)},
                "trials": attempts,
            })
    report = {
        "schema_version": 1,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "scope": "synthetic replacement fixtures; deterministic baselines, no agent or external trial",
        "version": version.stdout.strip(), "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        "python": platform.python_version(), "platform": platform.platform(),
        "runs_per_case": args.runs, "agent_model": None, "agent_tokens": None,
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "source_sha256": {str(p.relative_to(ROOT.parent)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in [ROOT / "run.py", ROOT / "baseline.py", ROOT.parent / "run.py"]},
        "methods": {m: {"passed": sum(r["success"] for r in rows if r["method"] == m),
                        "total": len(cases)} for m in METHODS},
        "results": rows,
    }
    with args.output.open("x", encoding="utf-8", newline="\n") as output:
        output.write(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report["methods"], indent=2))
    return 0 if report["methods"]["texio"]["passed"] == len(cases) else 1


if __name__ == "__main__":
    raise SystemExit(main())
