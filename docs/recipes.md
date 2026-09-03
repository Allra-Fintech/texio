# Ten Markdown recipes for agents

Set `TEXIO` to the released binary path. Every Texio command is exercised by
`bash scripts/test-recipes.sh "$TEXIO"`. The alternatives illustrate the extra
text manipulation an agent would otherwise have to generate and maintain.

## 1. Discover document structure

```sh
"$TEXIO" headings README.md
```

instead of

```sh
grep -nE '^(#{1,6})[[:space:]]+' README.md
```

## 2. Read Markdown from stdin

```sh
printf '# Title\n## Install\n' | "$TEXIO" headings - --json
```

instead of

```sh
tmp=$(mktemp)
printf '# Title\n## Install\n' > "$tmp"
grep -nE '^(#{1,6})[[:space:]]+' "$tmp"
rm "$tmp"
```

## 3. Extract a complete section

```sh
"$TEXIO" section README.md Installation
```

instead of

```sh
sed -n '/^## Installation$/,/^## /p' README.md
```

## 4. Extract only the section body

```sh
"$TEXIO" section README.md Installation --body-only
```

instead of

```sh
sed -n '/^## Installation$/,/^## /p' README.md | sed '1d;$d'
```

## 5. Return structured section data

```sh
"$TEXIO" section README.md Installation --json
```

instead of

```sh
body=$(sed -n '/^## Installation$/,/^## /p' README.md | sed '1d;$d')
printf '{"title":"Installation","content":"%s"}\n' "$body"
```

## 6. Preview a targeted replacement

```sh
"$TEXIO" replace README.md --section Installation --text 'New body' --dry-run
```

instead of

```sh
cp README.md README.md.bak
perl -0pi -e 's/(^## Installation\n).*?(?=^## |\z)/$1New body\n\n/ms' README.md
diff -u README.md.bak README.md
mv README.md.bak README.md
```

## 7. Apply an atomic replacement

```sh
"$TEXIO" replace README.md --section Installation --text 'New body' --write
```

instead of

```sh
perl -0pi -e 's/(^## Installation\n).*?(?=^## |\z)/$1New body\n\n/ms' README.md
```

## 8. Read a replacement from a file

```sh
"$TEXIO" replace README.md --section Installation --from new-body.md --write
```

instead of

```sh
body=$(<new-body.md)
BODY="$body" perl -0pi -e 's/(^## Installation\n).*?(?=^## |\z)/$1 . $ENV{BODY} . "\n\n"/mse' README.md
```

## 9. Transform stdin to stdout

```sh
printf '# Doc\n## Target\nold\n' |
  "$TEXIO" replace - --section Target --text new --stdout
```

instead of

```sh
input=$(mktemp)
output=$(mktemp)
printf '# Doc\n## Target\nold\n' > "$input"
perl -0pe 's/(^## Target\n).*?(?=^## |\z)/$1new\n/ms' "$input" > "$output"
cat "$output"
rm "$input" "$output"
```

## 10. Handle errors as JSON

```sh
"$TEXIO" --error-format json section README.md Missing
```

instead of

```sh
body=$(sed -n '/^## Missing$/,/^## /p' README.md)
if [ -z "$body" ]; then
  printf '{"error":"section_not_found","section":"Missing"}\n' >&2
  exit 4
fi
```

The alternatives are intentionally realistic but brittle: they assume ATX
headings, can match heading-like text inside code fences, mishandle duplicate
headings, or require the agent to implement escaping and cleanup itself. Exit
codes and Texio's stable schemas are documented in the [CLI contract](cli-contract.md).
