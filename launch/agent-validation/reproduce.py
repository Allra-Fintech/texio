#!/usr/bin/env python3
"""Run six real Claude Code sessions in isolated fixtures; requires Claude login."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

VALID = b"# Trial\n\n## Installation\n\nOld instructions.\n\n```md\n## Example heading\n```\n\n### Nested note\n\nOld note.\n\n## Usage\n\nKeep this exactly.  \n\n- [x] untouched\n"
DUPLICATE = b"# Trial\n\n## Installation\n\nFirst.\n\n## Installation\n\nSecond.\n\n## Usage\n\nKeep this exactly.\n"

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--claude", required=True)
parser.add_argument("--texio", required=True)
parser.add_argument("--policy", required=True, help="File containing only the copyable Markdown policy")
parser.add_argument("--work-dir", required=True, help="New directory for fixtures and private raw event streams")
args = parser.parse_args()
root = Path(args.work_dir).resolve()
root.mkdir(parents=True, exist_ok=False)
claude = str(Path(args.claude).resolve())
texio = Path(args.texio).resolve()
policy = Path(args.policy).read_text()
env = os.environ.copy()
env["PATH"] = str(texio.parent) + os.pathsep + env["PATH"]
command = [claude, "-p", "--verbose", "--output-format", "stream-json",
    "--no-session-persistence", "--setting-sources", "", "--strict-mcp-config",
    "--mcp-config", '{"mcpServers":{}}', "--disable-slash-commands",
    "--permission-mode", "dontAsk", "--tools", "Read,Bash,Edit,Write",
    "--allowedTools", "Read", "Edit", "Write", "Bash(texio *)",
    "Bash(git diff*)", "Bash(pwd)", "Bash(ls*)", "--max-budget-usd", "3"]
manifest = {"claude_version": subprocess.check_output([claude, "--version"], text=True).strip(),
    "texio_version": subprocess.check_output([str(texio), "--version"], text=True).strip(),
    "texio_sha256": hashlib.sha256(texio.read_bytes()).hexdigest(), "policy": policy,
    "invocation": ["claude", *command[1:]], "limits": "Three-dollar cap and 240-second timeout per session; no model override."}
(root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
for context in ("AGENTS.md", "CLAUDE.md"):
    for scenario in ("valid", "missing", "duplicate"):
        name = context[:-3].lower() + "-" + scenario
        work = root / name
        work.mkdir()
        (work / context).write_text(policy)
        (work / "document.md").write_bytes(DUPLICATE if scenario == "duplicate" else VALID)
        target = "Does Not Exist" if scenario == "missing" else "Installation"
        prompt = f'Read and follow {context}. In document.md, replace the body of the section named "{target}" with exactly "Install Texio with Cargo." followed by a newline. Keep the rest of the document unchanged. Report the outcome. Work only in this directory; Texio is installed on PATH.'
        (work / "prompt.txt").write_text(prompt + "\n")
        subprocess.run(["git", "init", "-q", str(work)], check=True)
        subprocess.run(["git", "-C", str(work), "add", context, "document.md"], check=True)
        subprocess.run(["git", "-C", str(work), "-c", "user.name=Texio validation", "-c",
            "user.email=validation@example.invalid", "commit", "-qm", "Initialize isolated policy fixture"], check=True)
        with (work / "prompt.txt").open() as prompt_file, (root / (name + ".raw.jsonl")).open("w") as output, (root / (name + ".stderr.txt")).open("w") as error:
            result = subprocess.run(command, cwd=work, env=env, stdin=prompt_file,
                stdout=output, stderr=error, timeout=240)
        print(name, "process_exit=" + str(result.returncode), flush=True)
        if result.returncode:
            raise SystemExit("Trial process failed; inspect private logs before drawing conclusions.")
