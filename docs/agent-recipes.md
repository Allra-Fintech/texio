# Markdown recipes for AI agents

## How do I extract one section from a README?

```sh
texio section README.md "Installation"
```

## How do I give an agent only the relevant Markdown context?

```sh
texio section DESIGN.md "Authentication" --body-only
```

## How do I list Markdown headings as JSON?

```sh
texio headings README.md --json
```

## How do I replace a section without rewriting the document?

```sh
texio replace README.md --section "Installation" --from installation.md --dry-run
```

Review the preview, then repeat without `--dry-run`.

