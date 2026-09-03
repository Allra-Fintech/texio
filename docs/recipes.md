# Ten Markdown recipes for agents

Set `TEXIO` to the released binary path. Every recipe is exercised by
`bash scripts/test-recipes.sh "$TEXIO"`.

## 1. Discover document structure

```sh
"$TEXIO" headings README.md
```

## 2. Feed Markdown through stdin

```sh
printf '# Title\n## Install\n' | "$TEXIO" headings - --json
```

## 3. Extract a complete section

```sh
"$TEXIO" section README.md Installation
```

## 4. Extract only the section body

```sh
"$TEXIO" section README.md Installation --body-only
```

## 5. Return structured section data

```sh
"$TEXIO" section README.md Installation --json
```

## 6. Preview a targeted replacement

```sh
"$TEXIO" replace README.md --section Installation --text 'New body' --dry-run
```

## 7. Apply an atomic replacement

```sh
"$TEXIO" replace README.md --section Installation --text 'New body' --write
```

## 8. Read a replacement from a file

```sh
"$TEXIO" replace README.md --section Installation --from new-body.md --write
```

## 9. Transform stdin to stdout without a file write

```sh
printf '# Doc\n## Target\nold\n' |
  "$TEXIO" replace - --section Target --text new --stdout
```

## 10. Handle errors as JSON

```sh
"$TEXIO" --error-format json section README.md Missing
```

Exit codes distinguish invalid input, missing sections, ambiguous sections,
and write failures. See the [CLI contract](cli-contract.md) for the stable map.
