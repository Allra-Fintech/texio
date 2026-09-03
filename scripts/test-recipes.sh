#!/usr/bin/env bash
set -euo pipefail

TEXIO=${1:?usage: test-recipes.sh /path/to/texio}
WORK_DIR=$(mktemp -d "${TMPDIR:-/tmp}/texio-recipes.XXXXXX")
trap 'rm -rf "$WORK_DIR"' EXIT

cat > "$WORK_DIR/doc.md" <<'EOF'
# Document

## Installation

old

## Usage

keep
EOF
printf 'from file\n' > "$WORK_DIR/body.md"

"$TEXIO" headings "$WORK_DIR/doc.md" | grep -q $'H2\tInstallation'
printf '# Title\n## Install\n' | "$TEXIO" headings - --json | grep -q '"Install"'
"$TEXIO" section "$WORK_DIR/doc.md" Installation | grep -q '## Installation'
"$TEXIO" section "$WORK_DIR/doc.md" Installation --body-only | grep -q old
"$TEXIO" section "$WORK_DIR/doc.md" Installation --json | grep -q '"content"'
"$TEXIO" replace "$WORK_DIR/doc.md" --section Installation --text preview --dry-run | grep -q '+preview'
"$TEXIO" replace "$WORK_DIR/doc.md" --section Installation --text written --write
grep -q written "$WORK_DIR/doc.md"
"$TEXIO" replace "$WORK_DIR/doc.md" --section Installation --from "$WORK_DIR/body.md" --write
grep -q 'from file' "$WORK_DIR/doc.md"
printf '# Doc\n## Target\nold\n' | "$TEXIO" replace - --section Target --text new --stdout | grep -q new
if "$TEXIO" --error-format json section "$WORK_DIR/doc.md" Missing 2> "$WORK_DIR/error"; then
  exit 1
fi
grep -q 'section_not_found' "$WORK_DIR/error"
