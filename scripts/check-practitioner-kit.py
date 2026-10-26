#!/usr/bin/env python3
"""Verify practitioner-kit mechanics with synthetic disposable inputs only."""

import argparse
import json
from pathlib import Path
import subprocess
import tempfile


def require(condition, message):
    """Retain checks under Python optimization."""
    if not condition:
        raise ValueError(message)


def main():
    """Exercise replacement, scoped context and safe refusal without user files."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--texio", type=Path, required=True)
    args = parser.parse_args()
    binary = args.texio.resolve()
    with tempfile.TemporaryDirectory(prefix="texio-practitioner-") as directory:
        root = Path(directory)
        path = root / "README.md"
        original = b"# Demo\n## Installation\nold\n## Usage\nkeep\n"
        expected = b"# Demo\n## Installation\ngenerated command\n## Usage\nkeep\n"
        path.write_bytes(original)
        body = root / "body.md"
        body.write_bytes(b"generated command\n")

        def run(*arguments, code=0):
            """Capture a real CLI command and enforce its expected exit status."""
            result = subprocess.run([str(binary), *map(str, arguments)], capture_output=True, timeout=30)
            require(result.returncode == code, "unexpected command status")
            return result

        headings = run("headings", path, "--json")
        require(json.loads(headings.stdout) == [
            {"level": 1, "title": "Demo"}, {"level": 2, "title": "Installation"},
            {"level": 2, "title": "Usage"}], "unexpected headings")
        replace = ("replace", path, "--section", "Installation", "--from", body)
        preview = run(*replace, "--dry-run")
        require(b"+generated command\n" in preview.stdout, "preview missing replacement")
        require(path.read_bytes() == original, "preview changed input")
        run(*replace, "--write")
        require(path.read_bytes() == expected, "replacement did not preserve expected bytes")
        print("PASS synthetic generated-body replacement and preservation")

        design = b"# Design\n## Authentication\nPolicy\n### Tokens\nExample only\n## Billing\nKeep\n"
        path.write_bytes(design)
        extracted = run("section", path, "Authentication", "--body-only")
        require(extracted.stdout == b"Policy\n### Tokens\nExample only\n", "incorrect scoped context")
        require(path.read_bytes() == design, "extraction modified input")
        print("PASS synthetic nested design context; no agent session performed")

        duplicate = b"## Target\none\n## Target\ntwo\n"
        path.write_bytes(duplicate)
        for heading, code in (("Target", 5), ("Missing", 4)):
            run("replace", path, "--section", heading, "--text", "proposed", "--dry-run", code=code)
            require(path.read_bytes() == duplicate, "refusal changed input")
        print("PASS synthetic missing/ambiguous refusal; no external trial claimed")


if __name__ == "__main__":
    main()
