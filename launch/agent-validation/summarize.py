#!/usr/bin/env python3
"""Export task-relevant trial evidence; omit thinking, authentication and session metadata."""
import argparse
from datetime import datetime, timezone
import getpass
import hashlib
import json
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--work-dir", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()
root = Path(args.work_dir).resolve()
manifest = json.loads((root / "manifest.json").read_text())


def scrub(value):
    if isinstance(value, str):
        return value.replace(str(root), "TRIAL_ROOT").replace(str(root).replace("/private/tmp/", "/tmp/"), "TRIAL_ROOT").replace("/tmp/texio-launch-47/binary-v0.1.2", "TEXIO_BIN").replace(getpass.getuser(), "LOCAL_USER")
    if isinstance(value, list):
        return [scrub(item) for item in value]
    if isinstance(value, dict):
        return {key: scrub(item) for key, item in value.items()}
    return value


report = {"schema_version": 1, "exported_at": datetime.now(timezone.utc).isoformat(),
          "setup": manifest, "trials": []}
for context in ("agents", "claude"):
    for scenario in ("valid", "missing", "duplicate"):
        name = context + "-" + scenario
        work = root / name
        events = [json.loads(line) for line in (root / (name + ".raw.jsonl")).read_text().splitlines() if line]
        final = next((event for event in reversed(events) if event.get("type") == "result"), None)
        if final is None:
            raise SystemExit("Incomplete trial: " + name)
        calls, by_id, statements, models = [], {}, [], set()
        for event in events:
            if event.get("type") == "assistant":
                message = event.get("message", {})
                if message.get("model"):
                    models.add(message["model"])
                for block in message.get("content", []):
                    if block.get("type") == "text":
                        statements.append(block["text"])
                    elif block.get("type") == "tool_use":
                        call = {"tool": block["name"], "input": block["input"]}
                        calls.append(call)
                        by_id[block["id"]] = call
            elif event.get("type") == "user":
                for block in event.get("message", {}).get("content", []):
                    if block.get("type") == "tool_result" and block.get("tool_use_id") in by_id:
                        call = by_id[block["tool_use_id"]]
                        call["is_error"] = block.get("is_error", False)
                        # Directory listings add local account metadata, not validation evidence.
                        if not call["input"].get("command", "").startswith("ls "):
                            call["output"] = block.get("content")
        before = subprocess.check_output(["git", "-C", str(work), "show", "HEAD:document.md"])
        after = (work / "document.md").read_bytes()
        expected = before
        if scenario == "valid":
            boundary = before.index(b"## Installation\n") + len(b"## Installation\n")
            expected = before[:boundary] + b"Install Texio with Cargo.\n" + before[before.index(b"## Usage\n"):]
        previews = [i for i, c in enumerate(calls) if "texio replace" in c["input"].get("command", "") and "--dry-run" in c["input"]["command"] and c.get("is_error") is False]
        writes = [i for i, c in enumerate(calls) if "--write" in c["input"].get("command", "")]
        headings = [i for i, c in enumerate(calls) if "texio headings" in c["input"].get("command", "") and c.get("is_error") is False]
        sections = [i for i, c in enumerate(calls) if "texio section" in c["input"].get("command", "")]
        report["trials"].append({"name": name, "models": sorted(models), "prompt": (work / "prompt.txt").read_text(),
            "before": before.decode(), "after": after.decode(), "expected": expected.decode(),
            "before_sha256": hashlib.sha256(before).hexdigest(), "after_sha256": hashlib.sha256(after).hexdigest(),
            "exact_expected_bytes": after == expected, "write_calls": len(writes),
            "headings_inspected": bool(headings), "section_inspected": bool(sections),
            "preview_before_write": bool(previews and writes and min(previews) < min(writes)),
            "generic_edit_calls": sum(c["tool"] in ("Edit", "Write") for c in calls),
            "permission_denials": final.get("permission_denials", []), "session_result": final.get("subtype"),
            "assistant_statements": statements, "final_response": final.get("result"), "tool_calls": calls})
output = Path(args.output)
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(scrub(report), indent=2) + "\n")
for trial in report["trials"]:
    print(trial["name"], "exact=" + str(trial["exact_expected_bytes"]),
          "headings=" + str(trial["headings_inspected"]), "denials=" + str(len(trial["permission_denials"])))
