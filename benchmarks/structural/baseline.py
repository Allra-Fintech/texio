#!/usr/bin/env python3
"""Disclosed deterministic text baselines, never given expected benchmark output."""

import argparse
import importlib.util
from pathlib import Path
import re


def whole_document(document, heading, replacement):
    """Validate ATX targets outside fences, rebuild all lines with LF endings.

    Deliberately limited: no Setext, inline title rendering, containers or full
    CommonMark parser. This is a runnable text rewriter, not an AI agent.
    """
    lines = document.splitlines()
    headings = []
    fence = None
    for index, line in enumerate(lines):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
            continue
        if marker:
            fence = marker[1]
            continue
        match = re.match(r"^ {0,3}(#{1,6})[ \t]+(.+?)\s*$", line)
        if match:
            title = re.sub(r"[ \t]+#+[ \t]*$", "", match[2])
            headings.append((index, len(match[1]), title))
    matches = [h for h in headings if h[2] == heading]
    if len(matches) != 1:
        return (4 if not matches else 5), document
    start, level, _ = matches[0]
    end = next((i for i, depth, _ in headings if i > start and depth <= level), len(lines))
    result = lines[:start + 1] + replacement.rstrip("\r\n").splitlines() + lines[end:]
    return 0, "\n".join(result) + "\n"


def main():
    """Transform only the supplied input; errors leave its bytes untouched."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("method", choices=["regex", "whole-document"])
    parser.add_argument("input", type=Path)
    parser.add_argument("heading")
    parser.add_argument("replacement")
    args = parser.parse_args()
    document = args.input.read_bytes().decode("utf-8")
    if args.method == "regex":
        spec = importlib.util.spec_from_file_location("legacy", Path(__file__).parents[1] / "run.py")
        legacy = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(legacy)
        code, result = legacy.naive_replace(document, args.heading, args.replacement)
    else:
        code, result = whole_document(document, args.heading, args.replacement)
    if code == 0:
        args.input.write_bytes(result.encode("utf-8"))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
