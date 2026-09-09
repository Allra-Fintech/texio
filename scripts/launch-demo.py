#!/usr/bin/env python3
"""Reproduce the launch demonstration against any installed Texio binary."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--texio", required=True)
    args = parser.parse_args()
    binary = str(Path(args.texio).resolve())
    root = Path(__file__).resolve().parents[1]
    # Normalize checkout line endings so the demo fixture is identical on Windows.
    source = (root / "benchmarks/cases/complex/input.md").read_text().encode()
    replacement = "Updated safely.\n"
    expected = source[:source.index(b"## Target\n") + len(b"## Target\n")] + replacement.encode() + source[source.index(b"## After"):]
    print(subprocess.check_output([binary, "--version"], text=True).strip())
    print("binary_sha256=" + hashlib.sha256(Path(binary).read_bytes()).hexdigest())
    with tempfile.TemporaryDirectory(prefix="texio-demo-") as directory:
        path = Path(directory) / "document.md"
        path.write_bytes(source)
        def run(*arguments):
            shown = [str(a).replace(str(path), "document.md") for a in arguments]
            print("$ texio " + shlex.join(shown))
            result = subprocess.run([binary, *map(str, arguments)], capture_output=True, text=True)
            print((result.stdout + result.stderr).replace(str(path), "document.md"), end="")
            return result
        assert run("headings", path, "--json").returncode == 0
        preview = run("replace", path, "--section", "Target", "--text", replacement, "--dry-run")
        assert preview.returncode == 0 and path.read_bytes() == source
        assert run("replace", path, "--section", "Target", "--text", replacement, "--write").returncode == 0
        assert path.read_bytes() == expected, "Texio output changed unrelated bytes"
        print("PASS: preview did not write; applied edit preserved all unrelated bytes.")
        pattern = r"(?ms)(^## Target\n).*?(?=^## |\Z)"
        fragile = re.sub(pattern, lambda m: m.group(1) + "\n" + replacement + "\n", source.decode(), count=1)
        assert fragile.encode() != expected
        print("Regex baseline: " + pattern)
        print("".join(difflib.unified_diff(expected.decode().splitlines(True), fragile.splitlines(True), fromfile="expected", tofile="regex")))
        print("FAIL (expected): regex treats the heading inside the fence as a boundary.")
        duplicate = (root / "benchmarks/cases/duplicate/input.md").read_text().encode()
        for context in ("AGENTS.md", "CLAUDE.md"):
            print("Policy scenario: " + context)
            path.write_bytes(duplicate)
            for section, code in (("Repeated", 5), ("Missing", 4)):
                result = run("--error-format", "json", "replace", path, "--section", section, "--text", replacement, "--dry-run")
                assert result.returncode == code, result.returncode
                json.loads(result.stderr)
                assert path.read_bytes() == duplicate
                print("PASS: refused unsafe target; no write attempted.")
    print("All launch demonstration checks passed.")


if __name__ == "__main__":
    main()
