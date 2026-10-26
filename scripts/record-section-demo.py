#!/usr/bin/env python3
"""Record real disposable-file CLI output as an offline paced terminal replay."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import tempfile


def require(condition, message):
    """Keep the recorder's correctness checks active with Python -O."""
    if not condition:
        raise ValueError(message)


def main():
    """Execute the workflow before writing any demo artifacts."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--texio", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    binary = args.texio.resolve()
    out = args.output_dir
    require(not out.exists(), "choose a new output directory")
    events = []
    original = b"# Demo\n\n## Installation\nold\n\n## Usage\nkeep\n"
    expected = b"# Demo\n\n## Installation\nnew\n## Usage\nkeep\n"
    with tempfile.TemporaryDirectory(prefix="texio-demo-") as directory:
        root = Path(directory)
        document = root / "document.md"
        document.write_bytes(original)
        (root / "before.md").write_bytes(original)

        def run(at, argv, code=0):
            shown = ["texio" if i == 0 and arg == str(binary) else arg
                     for i, arg in enumerate(argv)]
            result = subprocess.run(argv, cwd=root, capture_output=True, text=True, timeout=30)
            require(result.returncode == code, f"unexpected exit: {shown}: {result.stderr}")
            events.append({"at": at, "command": shlex.join(shown), "exit": result.returncode,
                           "stdout": result.stdout, "stderr": result.stderr})
            return result

        version = run(0, [str(binary), "--version"]).stdout.strip()
        require(re.fullmatch(r"texio \S+", version), "invalid version response")
        run(5, [str(binary), "headings", "document.md", "--json"])
        run(11, [str(binary), "section", "document.md", "Installation"])
        replace = [str(binary), "replace", "document.md", "--section", "Installation", "--text", "new"]
        run(18, replace + ["--dry-run"])
        require(document.read_bytes() == original, "preview changed input")
        run(27, replace + ["--write"])
        require(document.read_bytes() == expected, "write changed unexpected bytes")
        run(32, ["git", "diff", "--no-index", "--", "before.md", "document.md"], code=1)
        events.append({"at": 39, "command": None, "exit": None,
                       "stdout": "PASS: preview did not write; actual output matches every expected byte, including Usage.\n", "stderr": ""})
        document.write_bytes(expected + b"\n## Installation\nsecond\n")
        duplicate = document.read_bytes()
        events.append({"at": 42, "command": None, "exit": None,
                       "stdout": "Recorder adds a second real Installation heading to test ambiguity.\n", "stderr": ""})
        run(44, replace + ["--dry-run"], code=5)
        require(document.read_bytes() == duplicate, "ambiguous preview changed input")
        events.append({"at": 50, "command": None, "exit": None,
                       "stdout": "PASS: ambiguous target refused with exit 5; input unchanged.\nSynthetic internal demo. Playback is paced, not a speed measurement.\n", "stderr": ""})
    report = {"schema_version": 1, "recorded_at": datetime.now(timezone.utc).isoformat(),
              "version": version, "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
              "recorder_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "duration_seconds": 55, "timing": "editorial pacing, not command runtime", "events": events}
    payload = json.dumps(report, ensure_ascii=False).replace("<", "\\u003c")
    page = '''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Texio: inspect, preview, apply, verify</title>
<style>body{font:16px system-ui;max-width:960px;margin:2rem auto;padding:0 1rem;background:#111827;color:#e5e7eb}button,input{font:inherit}button{padding:.5rem;margin-right:.5rem}pre{background:#030712;padding:1rem;height:28rem;overflow:auto;white-space:pre-wrap}input{width:70%}a{color:#93c5fd}</style>
<h1>Inspect → preview → apply → verify</h1>
<p>Real output from disposable files. A 55-second paced replay, not an execution-speed measurement or external trial.</p>
<button id="play">Play</button><button id="restart">Restart</button>
<label>Playback <input id="timeline" aria-label="Playback time" type="range" min="0" max="55" step="0.1" value="0"></label>
<span id="time"></span><pre id="terminal" aria-label="Recorded terminal output"></pre>
<p id="provenance"></p><p>Read the adjacent <code>section-workflow.json</code> for all commands, exits and output. No network dependencies or telemetry.</p>
<script id="recording" type="application/json">PAYLOAD</script>
<script>
const data=JSON.parse(document.getElementById('recording').textContent);
const terminal=document.getElementById('terminal'), slider=document.getElementById('timeline'), play=document.getElementById('play');
let current=0, running=false, previous=0;
function render(){terminal.textContent=data.events.filter(e=>e.at<=current).map(e=>(e.command?'$ '+e.command+'\\n':'')+e.stdout+e.stderr+(e.exit!==null?'[exit '+e.exit+']\\n':'')).join('\\n');terminal.scrollTop=terminal.scrollHeight;slider.value=current;document.getElementById('time').textContent=current.toFixed(1)+' / 55s';}
function stop(){running=false;play.textContent='Play';}
play.onclick=()=>{if(running){stop();return;}if(current>=55)current=0;running=true;previous=0;play.textContent='Pause';requestAnimationFrame(tick);};
function tick(t){if(!running)return;if(previous)current=Math.min(55,current+(t-previous)/1000);previous=t;render();if(current>=55)stop();else requestAnimationFrame(tick);}
slider.oninput=()=>{stop();current=Number(slider.value);render();};
document.getElementById('restart').onclick=()=>{stop();current=0;render();};
document.getElementById('provenance').textContent=data.version+' · binary SHA256 '+data.binary_sha256;
render();
</script></html>'''.replace("PAYLOAD", payload)
    out.mkdir(parents=True)
    (out / "section-workflow.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "section-workflow.html").write_text(page, encoding="utf-8")
    print(f"Recorded {len(events)} verified events; 55-second editorial playback")


if __name__ == "__main__":
    main()
