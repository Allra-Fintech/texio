#!/usr/bin/env python3
"""Offline, source-attributed workflow comparisons; no upstream code imports."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "launch" / "agent-validation" / "workflow-cases.json"

# clio_cleanup and substring_extract adapt CLIO Kit's BSD-3-Clause helpers.
# Copyright (c) 2025, Gnosis Research Center, Illinois Institute of Technology.
# Full notice: launch/agent-validation/workflow-baselines.NOTICE.
# Pinned provenance for all baseline selectors is in workflow-cases.json.


def positional_tables(document, replacements):
    """CVE's occurrence-based table assignment, without file I/O."""
    pattern = r"(\| CVE \| Description \| Severity \|.*?)(?=\n---|\n##|\Z)"
    if len(re.findall(pattern, document, flags=re.DOTALL)) < 2:
        return None
    tables = {item["heading"]: item["body"].strip().split("\n---")[0].rstrip("\r\n") + "\n"
              for item in replacements}
    count = 0

    def replace(_match):
        nonlocal count
        count += 1
        return tables["Reported" if count == 1 else "Patched"]

    return re.sub(pattern, replace, document, flags=re.DOTALL)


def uppercase_boundary(document, replacements):
    """Equivalent of CleanTube's JS regex for these ASCII fixtures only."""
    body = replacements[0]["body"]
    return re.sub(
        r"## Chaines\n[\s\S]*?\n(?=## [A-Z])",
        lambda _match: "## Chaines\n" + body,
        document,
        count=1,
    )


def clio_cleanup(content):
    """The inspected CLIO cleanup, retained after both extraction methods."""
    cleaned = []
    in_code = False
    for line in content.split("\n"):
        if line.strip().startswith("```"):
            cleaned.append(line)
            in_code = not in_code
            continue
        if line.strip() == "---" and len(cleaned) > 10:
            break
        if "Screenshot" in line or "alt text" in line:
            continue
        if line.strip().startswith("![") and line.strip().endswith(">)"):
            continue
        cleaned.append(line)
    if in_code:
        cleaned.append("```")
    return "\n".join(cleaned).strip()


def substring_extract(document, heading):
    """CLIO's selector loop, followed by its existing cleanup."""
    in_section = False
    section_level = 0
    lines = []
    for line in document.split("\n"):
        match = re.match(r"^(#+)\s*", line)
        if match and heading.lower() in line.lower():
            in_section = True
            section_level = len(match.group(1))
            continue
        if in_section and match and len(match.group(1)) <= section_level:
            break
        if in_section:
            lines.append(line)
    return clio_cleanup("\n".join(lines).strip()) if lines else ""


def run(binary, arguments):
    return subprocess.run(
        [str(binary), *arguments], capture_output=True, text=True, check=False, timeout=15
    )


def require(condition, message):
    # Deliberately not an assert: validation must survive Python's -O flag.
    if not condition:
        raise ValueError(message)


def compare_case(binary, case, directory):
    """All CLI inputs are disposable copies; only preview/stdout modes run."""
    document = case["input"]
    path = directory / (case["id"] + ".md")
    path.write_bytes(document.encode("utf-8"))
    original_bytes = path.read_bytes()
    expected_exit = case.get("expected_exit", 0)
    dry_runs = []
    if case["operation"] == "extract":
        require(case["baseline"] == "substring_extract", "unknown extraction baseline")
        baseline = substring_extract(document, case["heading"])
        result = run(binary, ["section", str(path), case["heading"], "--body-only"])
        actual = clio_cleanup(result.stdout) if result.returncode == 0 else result.stdout
    elif case["operation"] == "replace":
        replacements = case["replacements"]
        baseline_function = {
            "positional_tables": positional_tables,
            "uppercase_boundary": uppercase_boundary,
        }.get(case["baseline"])
        require(baseline_function is not None, "unknown replacement baseline")
        baseline = baseline_function(document, replacements)
        actual = document
        result = None
        for index, replacement in enumerate(replacements):
            # A new temporary input for each stage avoids changing source files.
            stage = directory / f"{case['id']}-{index}.md"
            stage.write_bytes(actual.encode("utf-8"))
            body = directory / f"{case['id']}-{index}-body.md"
            body.write_bytes(replacement["body"].encode("utf-8"))
            arguments = ["replace", str(stage), "--section", replacement["heading"],
                         "--from", str(body)]
            before = stage.read_bytes()
            preview = run(binary, [*arguments, "--dry-run"])
            require(stage.read_bytes() == before, "dry-run modified its input")
            dry_runs.append(preview.returncode)
            if preview.returncode != 0:
                result = preview
                break
            result = run(binary, [*arguments, "--stdout"])
            require(stage.read_bytes() == before, "stdout mode modified its input")
            if result.returncode != 0:
                break
            actual = result.stdout
    else:
        raise ValueError("unknown operation")
    require(path.read_bytes() == original_bytes, "original fixture was modified")
    require(result is not None, "case did not run a command")
    require(result.returncode == expected_exit,
            f"expected exit {expected_exit}, got {result.returncode}: {result.stderr}")
    if expected_exit == 0:
        require(actual == case["expected"], "Texio output differs from expected content")
        require(baseline == case["baseline_expected"], "baseline reproduction changed")
        require(actual != baseline, "fixture no longer demonstrates a difference")
    else:
        require(result.stdout == "", "refused operation emitted updated content")
        require(baseline == case["baseline_expected"], "baseline reproduction changed")
    return {
        "id": case["id"],
        "source_url": case["source_url"],
        "fixture_sha256": hashlib.sha256(original_bytes).hexdigest(),
        "synthetic": True,
        "baseline": case["baseline"],
        "baseline_matches_recorded_output": True,
        "texio_exit": result.returncode,
        "dry_run_exits": dry_runs,
        "input_unchanged": True,
        "expected_output_matches": True if expected_exit == 0 else None,
        "refused_as_expected": expected_exit != 0,
        "baseline_output": baseline,
        "texio_output": actual if expected_exit == 0 else None,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--texio", default="texio", help="existing executable; never downloaded")
    parser.add_argument("--output", type=Path, help="new JSON result path; never overwritten")
    args = parser.parse_args()
    if args.output and args.output.exists():
        parser.error("output already exists; choose a new result path")
    executable = shutil.which(args.texio)
    if executable is None:
        parser.error("Texio executable not found; pass --texio /path/to/texio")
    binary = Path(executable).resolve()
    version = run(binary, ["--version"])
    if version.returncode != 0:
        parser.error("could not read Texio version")
    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory(prefix="texio-assisted-") as temporary:
            rows = []
            for case in manifest["cases"]:
                try:
                    rows.append(compare_case(binary, case, Path(temporary)))
                except ValueError as error:
                    raise ValueError(f"{case['id']}: {error}") from error
        report = {
            "schema_version": 1,
            "texio_version": version.stdout.strip(),
            "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
            "scope": "offline synthetic selector comparisons; no upstream generator execution",
            "independent": False,
            "external_trial": False,
            "cases": rows,
        }
        if args.output:
            with args.output.open("x", encoding="utf-8", newline="\n") as output:
                json.dump(report, output, indent=2)
                output.write("\n")
        print(json.dumps(report, indent=2))
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print(f"comparison failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
