#!/usr/bin/env python3
"""Evaluate implicit Texio skill selection in isolated agent sessions."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess


MARKDOWN = """# Guide

## Installation

Old instructions.

```md
## Not a real section
```

## Usage

Keep this exactly.  
"""
UPDATED = """# Guide

## Installation
Install with Cargo.
## Usage

Keep this exactly.  
"""

CASES = (
    {
        "name": "markdown-update",
        "file": "guide.md",
        "before": MARKDOWN,
        "expected": UPDATED,
        "prompt": (
            "In guide.md, replace only the body of the Installation section "
            "with exactly `Install with Cargo.` followed by a newline. Preserve "
            "every other byte. Work only in this directory."
        ),
        "expect_texio": True,
    },
    {
        "name": "markdown-missing",
        "file": "guide.md",
        "before": MARKDOWN,
        "expected": MARKDOWN,
        "prompt": (
            "In guide.md, replace only the body of the Deployment section with "
            "exactly `Deploy safely.` followed by a newline. Preserve every "
            "other byte. Work only in this directory."
        ),
        "expect_texio": True,
    },
    {
        "name": "plain-text-update",
        "file": "notes.txt",
        "before": "alpha\n",
        "expected": "beta\n",
        "prompt": (
            "In notes.txt, replace the word alpha with beta. Preserve the final "
            "newline. Work only in this directory."
        ),
        "expect_texio": False,
    },
)


def sha256(data):
    """Return the SHA-256 digest of exact bytes."""
    return hashlib.sha256(data).hexdigest()


def successful_claude_tool_uses(events):
    """Return Claude tool requests that have a successful matching result."""
    requests = {}
    successful = set()
    for event in events:
        if event.get("type") == "assistant":
            for block in event.get("message", {}).get("content", []):
                if block.get("type") == "tool_use" and block.get("id"):
                    requests[block["id"]] = block
        elif event.get("type") == "user":
            for block in event.get("message", {}).get("content", []):
                tool_use_id = block.get("tool_use_id")
                if (
                    block.get("type") == "tool_result"
                    and tool_use_id in requests
                    and not block.get("is_error", False)
                ):
                    successful.add(tool_use_id)
    return [
        block
        for tool_use_id, block in requests.items()
        if tool_use_id in successful
    ]


def read_complete_jsonl(path):
    """Read JSONL while tolerating one truncated final event."""
    events = []
    lines = path.read_text().splitlines(keepends=True)
    truncated_final_event = False
    for index, raw_line in enumerate(lines):
        line = raw_line.rstrip("\r\n")
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            if (
                raw_line.endswith(("\n", "\r"))
                or any(remaining.strip() for remaining in lines[index + 1:])
            ):
                raise
            truncated_final_event = True
    return events, truncated_final_event


def positive_finite_float(value):
    """Parse a positive finite floating-point argument."""
    parsed = float(value)
    if not math.isfinite(parsed) or parsed <= 0:
        raise argparse.ArgumentTypeError("must be a positive finite number")
    return parsed


def command_calls(agent, events):
    """Extract successful shell commands from one agent event stream."""
    calls = []
    if agent == "claude":
        for block in successful_claude_tool_uses(events):
            if block.get("name") == "Bash":
                command = block.get("input", {}).get("command")
                if command:
                    calls.append(command)
    else:
        for event in events:
            if event.get("type") != "item.completed":
                continue
            item = event.get("item", {})
            if (
                item.get("type") == "command_execution"
                and item.get("status") == "completed"
                and item.get("exit_code") == 0
                and item.get("command")
            ):
                calls.append(item["command"])
    return calls


def skill_loaded(agent, events):
    """Report whether the agent loaded the Texio skill during the trial."""
    if agent == "claude":
        return any(
            block.get("name") == "Skill"
            and block.get("input", {}).get("skill") == "texio-markdown"
            for block in successful_claude_tool_uses(events)
        )
    return any("texio-markdown/SKILL.md" in command for command in command_calls(agent, events))


def model_names(events):
    """Collect model identifiers disclosed by agent events."""
    names = set()

    def visit(value):
        """Traverse nested event values looking for model fields."""
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "model" and isinstance(item, str):
                    names.add(item)
                else:
                    visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    visit(events)
    return sorted(names)


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--agent", required=True, choices=("claude", "codex"))
parser.add_argument("--agent-command", required=True)
parser.add_argument("--texio", required=True)
parser.add_argument("--skill", required=True)
parser.add_argument("--work-dir", required=True)
parser.add_argument("--output", required=True)
parser.add_argument("--timeout-seconds", type=positive_finite_float, default=240)
args = parser.parse_args()

root = Path(args.work_dir).resolve()
root.mkdir(parents=True, exist_ok=False)
agent_command = str(Path(args.agent_command).resolve())
texio = Path(args.texio).resolve()
skill = Path(args.skill).resolve()
environment = os.environ.copy()
environment["PATH"] = str(texio.parent) + os.pathsep + environment["PATH"]

report = {
    "schema_version": 1,
    "observed_at": datetime.now(timezone.utc).isoformat(),
    "agent": args.agent,
    "agent_version": subprocess.check_output(
        [agent_command, "--version"], text=True, timeout=30
    ).strip(),
    "texio_version": subprocess.check_output(
        [str(texio), "--version"], text=True, timeout=30
    ).strip(),
    "skill_sha256": sha256((skill / "SKILL.md").read_bytes()),
    "trials": [],
}

for case in CASES:
    work = root / case["name"]
    work.mkdir()
    installed = work / (".claude/skills" if args.agent == "claude" else ".agents/skills")
    installed.mkdir(parents=True)
    shutil.copytree(skill, installed / skill.name)
    target = work / case["file"]
    target.write_bytes(case["before"].encode())
    subprocess.run(["git", "init", "-q", str(work)], check=True)
    subprocess.run(["git", "-C", str(work), "add", "."], check=True)
    subprocess.run(
        [
            "git", "-C", str(work), "-c", "user.name=Texio validation",
            "-c", "user.email=validation@example.invalid", "commit", "-qm",
            "Initialize implicit-selection fixture",
        ],
        check=True,
    )
    raw = root / (case["name"] + ".raw.jsonl")
    error = root / (case["name"] + ".stderr.txt")
    if args.agent == "claude":
        command = [
            agent_command, "-p", "--verbose", "--output-format", "stream-json",
            "--no-session-persistence", "--setting-sources", "project",
            "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
            "--permission-mode", "dontAsk", "--tools", "Read,Bash,Edit,Write,Skill",
            "--allowedTools", "Read", "Edit", "Write", "Skill", "Bash(texio *)",
            "Bash(git diff*)", "--max-budget-usd", "2", case["prompt"],
        ]
    else:
        command = [
            agent_command, "exec", "--json", "--ephemeral", "--sandbox",
            "workspace-write", "--ignore-user-config", "--ignore-rules", "-C",
            str(work), case["prompt"],
        ]
    with raw.open("w") as output, error.open("w") as stderr:
        try:
            completed = subprocess.run(
                command, cwd=work, env=environment, stdout=output, stderr=stderr,
                timeout=args.timeout_seconds,
            )
            process_exit = completed.returncode
            timed_out = False
        except subprocess.TimeoutExpired:
            process_exit = 124
            timed_out = True
    events, truncated_final_event = read_complete_jsonl(raw)
    calls = command_calls(args.agent, events)
    calls = [
        command.replace(str(work), "TRIAL_ROOT").replace(
            str(work).replace("/tmp/", "/private/tmp/"), "TRIAL_ROOT"
        )
        for command in calls
    ]
    after = target.read_bytes()
    expected = case["expected"].encode()
    used_texio = any("texio " in command for command in calls)
    loaded_skill = skill_loaded(args.agent, events)
    report["trials"].append(
        {
            "name": case["name"],
            "prompt": case["prompt"],
            "expect_texio": case["expect_texio"],
            "skill_loaded": loaded_skill,
            "used_texio": used_texio,
            "selection_expected": (
                loaded_skill == case["expect_texio"]
                and used_texio == case["expect_texio"]
            ),
            "exact_expected_bytes": after == expected,
            "before_sha256": sha256(case["before"].encode()),
            "after_sha256": sha256(after),
            "expected_sha256": sha256(expected),
            "process_exit": process_exit,
            "timed_out": timed_out,
            "truncated_final_event": truncated_final_event,
            "models": model_names(events),
            "commands": calls,
        }
    )
    print(
        case["name"], "selected=" + str(used_texio),
        "exact=" + str(after == expected),
        "exit=" + str(process_exit),
        "timed_out=" + str(timed_out),
        "truncated_final_event=" + str(truncated_final_event), flush=True,
    )

Path(args.output).write_text(json.dumps(report, indent=2) + "\n")
if any(
    trial["process_exit"] != 0
    or not trial["selection_expected"]
    or not trial["exact_expected_bytes"]
    for trial in report["trials"]
):
    raise SystemExit("One or more skill-selection trials failed")
