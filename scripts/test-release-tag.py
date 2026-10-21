#!/usr/bin/env python3
"""Exercise release acceptance and rejection against isolated Git histories."""

import pathlib
import subprocess
import tempfile


SCRIPT = pathlib.Path(__file__).with_name("verify-release-tag.sh").resolve()


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def verify(root, tag, accepted, message):
    result = subprocess.run(
        ["bash", str(SCRIPT), tag], cwd=root, text=True, capture_output=True
    )
    if (result.returncode == 0) != accepted:
        raise AssertionError(f"{message}: {result.stdout}{result.stderr}")
    print(f"PASS: {message}")


def main():
    with tempfile.TemporaryDirectory(prefix="texio-release-tag-") as directory:
        root = pathlib.Path(directory)
        git(root, "init", "--quiet", "--initial-branch=main")
        git(root, "config", "user.name", "Release test")
        git(root, "config", "user.email", "release-test@example.invalid")
        (root / "Cargo.toml").write_text(
            '[package]\nname = "texio-cli"\nversion = "0.1.3"\nedition = "2024"\n'
        )
        (root / "src").mkdir()
        (root / "src/main.rs").write_text("fn main() {}\n")
        git(root, "add", "Cargo.toml", "src/main.rs")
        git(root, "commit", "--quiet", "-m", "Initial release")
        initial = git(root, "rev-parse", "HEAD")
        git(root, "update-ref", "refs/remotes/origin/main", initial)
        git(root, "tag", "v0.1.3")
        verify(root, "v0.1.3", True, "lightweight tag on main")
        git(root, "tag", "-d", "v0.1.3")
        git(root, "tag", "-a", "v0.1.3", "-m", "Patch release")
        verify(root, "v0.1.3", True, "annotated tag on main")
        git(root, "tag", "v0.1.4")
        verify(root, "v0.1.4", False, "mismatched package version rejected")
        git(root, "tag", "-d", "v0.1.3")
        verify(root, "v0.1.3", False, "nonexistent tag rejected")
        git(root, "tag", "v0.1.3")
        git(root, "commit", "--quiet", "--allow-empty", "-m", "Feature only")
        feature = git(root, "rev-parse", "HEAD")
        verify(root, "v0.1.3", False, "tag outside checked-out commit rejected")
        git(root, "tag", "-f", "v0.1.3")
        verify(root, "v0.1.3", False, "unreleased feature commit rejected")
        git(root, "update-ref", "refs/remotes/origin/main", feature)
        git(root, "checkout", "--quiet", "--detach", initial)
        git(root, "tag", "-f", "v0.1.3")
        verify(root, "v0.1.3", True, "released ancestor of current main accepted")
        git(root, "update-ref", "-d", "refs/remotes/origin/main")
        verify(root, "v0.1.3", False, "missing release branch rejected")


if __name__ == "__main__":
    main()
