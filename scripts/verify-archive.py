#!/usr/bin/env python3
"""Check a downloaded release checksum and execute the extracted binary."""
import hashlib
from pathlib import Path
import subprocess
import sys
import tarfile
import zipfile

directory = Path(sys.argv[1])
version = sys.argv[2]
sidecars = list(directory.glob("*.sha256"))
assert len(sidecars) == 1, "Expected exactly one platform archive"
digest, name = sidecars[0].read_text().strip().split()
assert Path(name).name == name
archive = directory / name
assert hashlib.sha256(archive.read_bytes()).hexdigest() == digest, "Checksum mismatch"
destination = directory / "unpacked"
destination.mkdir()
if name.endswith(".zip"):
    with zipfile.ZipFile(archive) as package:
        binary = destination / "texio.exe"
        binary.write_bytes(package.read("texio.exe"))
else:
    with tarfile.open(archive) as package:
        member = next(m for m in package.getmembers() if m.name in ("texio", "./texio") and m.isfile())
        binary = destination / "texio"
        binary.write_bytes(package.extractfile(member).read())
    binary.chmod(0o755)
assert subprocess.check_output([str(binary), "--version"], text=True).strip() == "texio " + version
subprocess.run([sys.executable, str(Path(__file__).with_name("launch-demo.py")), "--texio", str(binary)], check=True)
print("Verified checksum, installed version, and safe-edit demonstration:", name)
