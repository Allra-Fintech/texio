# Install Texio

Texio is an early preview. Release archives support Linux x86-64 (glibc),
Windows x86-64, Intel macOS, and Apple Silicon macOS. Linux ARM, Alpine/musl,
Windows ARM, and other package managers are not verified launch targets.
Archives have SHA-256 checksums; they are not signed or notarized installers.

## Rust installation

With a current stable Rust toolchain:

```sh
cargo install texio-cli --locked
texio --version
```

For an exact version, add `--version 0.1.1`. A source build may take more than
five minutes depending on the machine and network. From a source checkout,
use `cargo install --path . --locked`.

## macOS and Linux binary installation

Choose the target matching your machine:

| Machine | Target |
| --- | --- |
| Apple Silicon macOS | `aarch64-apple-darwin` |
| Intel macOS | `x86_64-apple-darwin` |
| Linux x86-64 with glibc | `x86_64-unknown-linux-gnu` |

The following example uses Apple Silicon. Set `target` to the matching value
above. It installs into a user-owned directory without administrator access.

```sh
version=0.1.1
target=aarch64-apple-darwin
archive="texio-$target.tar.gz"
download_dir=$(mktemp -d)
cd "$download_dir"
curl -fLO "https://github.com/Allra-Fintech/texio/releases/download/v$version/$archive"
curl -fLO "https://github.com/Allra-Fintech/texio/releases/download/v$version/$archive.sha256"
if command -v sha256sum >/dev/null; then
  sha256sum -c "$archive.sha256" || exit 1
else
  shasum -a 256 -c "$archive.sha256" || exit 1
fi
tar -xzf "$archive"
mkdir -p "$HOME/.local/bin"
install -m 755 texio "$HOME/.local/bin/texio"
export PATH="$HOME/.local/bin:$PATH"
texio --version
```

Add `$HOME/.local/bin` to your shell's PATH configuration to keep the command
available in future terminals. macOS may apply its downloaded-app security
checks; these archives do not claim Apple notarization.

## Windows binary installation

Run in PowerShell. This verifies the checksum before extracting the archive
and adds the installation directory to the current session's PATH.

```powershell
$version = '0.1.1'
$archive = 'texio-x86_64-pc-windows-msvc.zip'
$downloadDir = Join-Path ([IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString())
New-Item -ItemType Directory $downloadDir | Out-Null
$zipPath = Join-Path $downloadDir $archive
Invoke-WebRequest "https://github.com/Allra-Fintech/texio/releases/download/v$version/$archive" -OutFile $zipPath
Invoke-WebRequest "https://github.com/Allra-Fintech/texio/releases/download/v$version/$archive.sha256" -OutFile "$zipPath.sha256"
$expected = ((Get-Content "$zipPath.sha256").Trim() -split '\s+')[0]
if ((Get-FileHash $zipPath -Algorithm SHA256).Hash.ToLower() -ne $expected) { throw 'Checksum mismatch' }
$installDir = Join-Path $env:LOCALAPPDATA 'Texio\bin'
Expand-Archive $zipPath -DestinationPath $installDir -Force
$env:PATH = "$installDir;$env:PATH"
texio --version
```

Add that directory to your user PATH in Windows settings for future sessions.

## Homebrew

The launch packaging task is preparing `Allra-Fintech/tap/texio` for both macOS
architectures. Until its verification is recorded in the
[launch readiness report](../launch/readiness.md), use the crate or binary
instructions above. The unqualified command `brew install texio` is not a
supported installation path.
