#!/usr/bin/env python3
"""Fail unless a benchmark result is structurally valid and Texio passes."""

import json
from pathlib import Path
import sys


result = json.loads(Path(sys.argv[1]).read_text())
assert result["schema_version"] == 1
texio = result["methods"]["texio"]
assert texio["passed"] == texio["total"]
assert all(row["repeatable"] for row in result["results"])
