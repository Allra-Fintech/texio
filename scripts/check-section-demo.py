#!/usr/bin/env python3
"""Check generated and published demo data and HTML template equivalence."""

import json
from pathlib import Path
import sys


def require(condition, message):
    """Never disable evidence checks with Python optimization."""
    if not condition:
        raise ValueError(message)


def normalize(value):
    """Only timestamp and binary build hash may differ between recordings."""
    return {k: v for k, v in value.items() if k not in {"recorded_at", "binary_sha256"}}


def read_artifacts(directory):
    """Validate the full embedded payload against its adjacent JSON."""
    data = json.loads((directory / "section-workflow.json").read_text(encoding="utf-8"))
    require(isinstance(data, dict) and {"recorded_at", "binary_sha256"} <= data.keys(),
            "recording timestamp and binary hash are required")
    page = (directory / "section-workflow.html").read_text(encoding="utf-8")
    marker = '<script id="recording" type="application/json">'
    require(page.count(marker) == 1, "expected exactly one recording payload")
    start = page.index(marker) + len(marker)
    end = page.find("</script>", start)
    require(end >= 0, "unterminated recording payload")
    require(json.loads(page[start:end]) == data, "HTML payload differs from JSON")
    return data, page[:start], page[end:]


def check(generated, published):
    """Compare raw events, exits, recorder hash and complete HTML template."""
    actual, before, after = read_artifacts(generated)
    expected, old_before, old_after = read_artifacts(published)
    require(normalize(actual) == normalize(expected), "recording events/provenance changed")
    require((before, after) == (old_before, old_after), "HTML template changed")
    print("Published and regenerated section demo artifacts match")


if __name__ == "__main__":
    check(Path(sys.argv[1]), Path(sys.argv[2]) if len(sys.argv) > 2 else Path("launch/demos"))
