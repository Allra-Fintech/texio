#!/usr/bin/env python3
"""Execute the documented binary installation block on a disposable CI runner."""
import argparse
from pathlib import Path
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--texio", required=True)
parser.add_argument("--target", required=True, choices=["aarch64-apple-darwin", "x86_64-apple-darwin", "x86_64-unknown-linux-gnu", "x86_64-pc-windows-msvc"])
args = parser.parse_args()
windows = args.target.endswith("windows-msvc")
section = "Windows binary installation" if windows else "macOS and Linux binary installation"
document = Path(__file__).resolve().parents[1] / "docs/installation.md"
body = subprocess.check_output([args.texio, "section", str(document), section, "--body-only"], text=True)
fence = "```powershell\n" if windows else "```sh\n"
script = body.split(fence, 1)[1].split("```", 1)[0]
with tempfile.TemporaryDirectory(prefix="texio-doc-install-") as directory:
    path = Path(directory) / ("install.ps1" if windows else "install.sh")
    if windows:
        path.write_text("$ErrorActionPreference = 'Stop'\n" + script)
        subprocess.run(["pwsh", "-NoProfile", "-File", str(path)], cwd=directory, check=True)
    else:
        # Select the matching target exactly as the documentation instructs.
        script = script.replace("target=aarch64-apple-darwin", "target=" + args.target)
        path.write_text("set -eu\n" + script)
        subprocess.run(["bash", str(path)], cwd=directory, check=True)
print("Documented installation commands passed for", args.target)
