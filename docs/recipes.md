# Ten Markdown recipes for agents

Set `TEXIO` to the released binary path. Every recipe is exercised by
`bash scripts/test-recipes.sh "$TEXIO"`.

## 1. Inspect Markdown structure instead of grepping for `#`

```sh
"$TEXIO" headings README.md
```

## 2. Pipe Markdown directly instead of creating a temporary file

```sh
printf '# Title\n## Install\n' | "$TEXIO" headings - --json
```

## 3. Extract one section instead of slicing between regex matches

```sh
"$TEXIO" section README.md Installation
```

## 4. Get the section body instead of stripping its heading with regex

```sh
"$TEXIO" section README.md Installation --body-only
```

## 5. Request JSON instead of parsing human-readable text

```sh
"$TEXIO" section README.md Installation --json
```

## 6. Preview the exact change instead of editing blindly

```sh
"$TEXIO" replace README.md --section Installation --text 'New body' --dry-run
```

## 7. Replace one section instead of rewriting the whole file

```sh
"$TEXIO" replace README.md --section Installation --text 'New body' --write
```

## 8. Use a body file instead of escaping multiline text into a regex command

```sh
"$TEXIO" replace README.md --section Installation --from new-body.md --write
```

## 9. Transform stdin to stdout instead of mutating a temporary file

```sh
printf '# Doc\n## Target\nold\n' |
  "$TEXIO" replace - --section Target --text new --stdout
```

## 10. Handle stable JSON errors instead of scraping diagnostic text

```sh
"$TEXIO" --error-format json section README.md Missing
```

Exit codes distinguish invalid input, missing sections, ambiguous sections,
and write failures. See the [CLI contract](cli-contract.md) for the stable map.
