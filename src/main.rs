use clap::{ArgGroup, Parser as ClapParser, Subcommand, ValueEnum};
use pulldown_cmark::{Event, HeadingLevel, Options, Parser, Tag, TagEnd};
use serde_json::json;
use similar::TextDiff;
use std::{
    fs,
    io::{self, Read, Write},
    ops::Range,
    path::Path,
    process::ExitCode,
};
use tempfile::NamedTempFile;

#[derive(Debug, Clone, PartialEq, Eq)]
struct Heading {
    level: usize,
    title: String,
    start: usize,
    body_start: usize,
    end: usize,
}

fn headings(input: &str) -> Vec<Heading> {
    let options = Options::ENABLE_TABLES
        | Options::ENABLE_FOOTNOTES
        | Options::ENABLE_STRIKETHROUGH
        | Options::ENABLE_TASKLISTS;
    let mut found = Vec::new();
    let mut current: Option<(usize, usize, String)> = None;
    let front_matter_end = yaml_front_matter_end(input);

    for (event, range) in Parser::new_ext(input, options).into_offset_iter() {
        match event {
            Event::Start(Tag::Heading { level, .. }) if range.start >= front_matter_end => {
                current = Some((heading_level(level), range.start, String::new()));
            }
            Event::Text(text) | Event::Code(text) if current.is_some() => {
                current.as_mut().unwrap().2.push_str(&text);
            }
            Event::SoftBreak | Event::HardBreak if current.is_some() => {
                current.as_mut().unwrap().2.push(' ');
            }
            Event::End(TagEnd::Heading(_)) => {
                if let Some((level, start, title)) = current.take() {
                    found.push(Heading {
                        level,
                        title: title.trim().to_string(),
                        start,
                        body_start: heading_body_start(input, start),
                        end: input.len(),
                    });
                }
            }
            _ => {}
        }
    }

    for i in 0..found.len() {
        if let Some(next) = found[i + 1..].iter().find(|h| h.level <= found[i].level) {
            found[i].end = next.start;
        }
    }
    found
}

fn yaml_front_matter_end(input: &str) -> usize {
    let first_end = line_end(input, 0);
    if input[..first_end].trim_end_matches(['\r', '\n']) != "---" {
        return 0;
    }
    let mut offset = first_end;
    let mut has_mapping_key = false;
    for line in input[first_end..].split_inclusive('\n') {
        offset += line.len();
        let content = line.trim_end_matches(['\r', '\n']);
        if matches!(content, "---" | "...") {
            return if has_mapping_key { offset } else { 0 };
        }
        has_mapping_key |= looks_like_yaml_mapping_line(content);
    }
    0
}

fn looks_like_yaml_mapping_line(line: &str) -> bool {
    let Some((key, _)) = line.split_once(':') else {
        return false;
    };
    let key = key.trim();
    !key.is_empty()
        && key
            .bytes()
            .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'_' | b'-'))
}

fn heading_level(level: HeadingLevel) -> usize {
    match level {
        HeadingLevel::H1 => 1,
        HeadingLevel::H2 => 2,
        HeadingLevel::H3 => 3,
        HeadingLevel::H4 => 4,
        HeadingLevel::H5 => 5,
        HeadingLevel::H6 => 6,
    }
}

fn line_end(input: &str, from: usize) -> usize {
    input[from..]
        .find('\n')
        .map_or(input.len(), |relative| from + relative + 1)
}

fn heading_body_start(input: &str, start: usize) -> usize {
    let first_end = line_end(input, start);
    let first_line = input[start..first_end].trim_end_matches(['\r', '\n']);
    if is_atx_heading_line(first_line) {
        first_end
    } else {
        line_end(input, first_end)
    }
}

fn is_atx_heading_line(line: &str) -> bool {
    let indent = line.bytes().take_while(|byte| *byte == b' ').count();
    if indent > 3 {
        return false;
    }
    let content = &line[indent..];
    let hashes = content.bytes().take_while(|byte| *byte == b'#').count();
    (1..=6).contains(&hashes)
        && content
            .as_bytes()
            .get(hashes)
            .is_none_or(u8::is_ascii_whitespace)
}

fn select_heading<'a>(all: &'a [Heading], title: &str) -> Result<&'a Heading, String> {
    let matches: Vec<&Heading> = all
        .iter()
        .filter(|h| h.title.eq_ignore_ascii_case(title))
        .collect();
    match matches.as_slice() {
        [] => Err(format!("section not found: {title}")),
        [heading] => Ok(heading),
        _ => Err(format!(
            "ambiguous section: {title} ({} matches)",
            matches.len()
        )),
    }
}

#[cfg(test)]
fn json_escape(value: &str) -> String {
    let mut escaped = String::with_capacity(value.len());
    for character in value.chars() {
        match character {
            '"' => escaped.push_str("\\\""),
            '\\' => escaped.push_str("\\\\"),
            '\u{08}' => escaped.push_str("\\b"),
            '\u{0c}' => escaped.push_str("\\f"),
            '\n' => escaped.push_str("\\n"),
            '\r' => escaped.push_str("\\r"),
            '\t' => escaped.push_str("\\t"),
            control if control <= '\u{1f}' => {
                escaped.push_str(&format!("\\u{:04x}", control as u32));
            }
            other => escaped.push(other),
        }
    }
    escaped
}

fn line_ending(input: &str) -> &'static str {
    if input.contains("\r\n") { "\r\n" } else { "\n" }
}

fn normalize_replacement(mut replacement: String, document: &str) -> String {
    let ending = line_ending(document);
    replacement = replacement.replace("\r\n", "\n").replace('\r', "\n");
    if !replacement.ends_with('\n') {
        replacement.push('\n');
    }
    if ending == "\r\n" {
        replacement = replacement.replace('\n', "\r\n");
    }
    replacement
}

fn replace_section(
    input: &str,
    title: &str,
    replacement: String,
) -> Result<(String, Range<usize>, String), String> {
    let all = headings(input);
    let heading = select_heading(&all, title)?;
    let before = heading.body_start..heading.end;
    let after = normalize_replacement(replacement, input);
    let output = format!(
        "{}{}{}",
        &input[..heading.body_start],
        after,
        &input[heading.end..]
    );
    Ok((output, before, after))
}

#[derive(ClapParser)]
#[command(name = "texio", version, about = "Reliable Markdown operations")]
struct Cli {
    /// Emit runtime errors as text or JSON on stderr.
    #[arg(long, global = true, value_enum, default_value_t = ErrorFormat::Text)]
    error_format: ErrorFormat,
    #[command(subcommand)]
    command: Command,
}

#[derive(Clone, Copy, ValueEnum)]
enum ErrorFormat {
    Text,
    Json,
}

#[derive(Subcommand)]
enum Command {
    /// List structural headings.
    Headings {
        /// Markdown file, or - for stdin.
        file: String,
        #[arg(long)]
        json: bool,
    },
    /// Extract one section by visible heading text.
    Section {
        /// Markdown file, or - for stdin.
        file: String,
        heading: String,
        #[arg(long)]
        body_only: bool,
        #[arg(long)]
        json: bool,
    },
    /// Replace one section body.
    #[command(
        group(ArgGroup::new("source").required(true).multiple(false).args(["from", "text"])),
        group(ArgGroup::new("mode").required(true).multiple(false).args(["write", "dry_run", "stdout"]))
    )]
    Replace {
        /// Markdown file, or - for stdin with --stdout/--dry-run.
        file: String,
        #[arg(long)]
        section: String,
        /// Read replacement text from a file, or - for stdin.
        #[arg(long)]
        from: Option<String>,
        #[arg(long)]
        text: Option<String>,
        /// Atomically update FILE.
        #[arg(long)]
        write: bool,
        /// Print a unified diff without changing FILE.
        #[arg(long)]
        dry_run: bool,
        /// Print the updated document without changing FILE.
        #[arg(long)]
        stdout: bool,
    },
}

struct AppError {
    code: u8,
    kind: &'static str,
    message: String,
}

fn error(code: u8, kind: &'static str, message: impl ToString) -> AppError {
    AppError {
        code,
        kind,
        message: message.to_string(),
    }
}

fn read_input(path: &str) -> Result<String, AppError> {
    if path == "-" {
        let mut input = String::new();
        io::stdin()
            .read_to_string(&mut input)
            .map_err(|e| error(3, "input", e))?;
        Ok(input)
    } else {
        fs::read_to_string(path).map_err(|e| error(3, "input", e))
    }
}

fn selection_error(message: String) -> AppError {
    if message.starts_with("ambiguous") {
        error(5, "ambiguous_section", message)
    } else {
        error(4, "section_not_found", message)
    }
}

fn unified_preview(path: &str, before: &str, after: &str) {
    print!(
        "{}",
        TextDiff::from_lines(before, after)
            .unified_diff()
            .header(path, &format!("{path} (proposed)"))
    );
}

fn atomic_write(path: &str, content: &str) -> Result<(), String> {
    let requested = Path::new(path);
    let target_path = if fs::symlink_metadata(requested)
        .map_err(|e| e.to_string())?
        .file_type()
        .is_symlink()
    {
        fs::canonicalize(requested).map_err(|e| e.to_string())?
    } else {
        requested.to_path_buf()
    };
    let target = target_path.as_path();
    let parent = parent_directory(target);
    let permissions = fs::metadata(target)
        .map_err(|e| e.to_string())?
        .permissions();
    let mut temporary = NamedTempFile::new_in(parent).map_err(|e| e.to_string())?;
    temporary
        .write_all(content.as_bytes())
        .and_then(|_| temporary.flush())
        .map_err(|e| e.to_string())?;
    temporary
        .as_file()
        .set_permissions(permissions)
        .map_err(|e| e.to_string())?;
    temporary.persist(target).map_err(|e| e.error.to_string())?;
    Ok(())
}

fn parent_directory(path: &Path) -> &Path {
    path.parent()
        .filter(|parent| !parent.as_os_str().is_empty())
        .unwrap_or_else(|| Path::new("."))
}

fn run(cli: &Cli) -> Result<(), AppError> {
    match &cli.command {
        Command::Headings {
            file,
            json: as_json,
        } => {
            let input = read_input(file)?;
            let all = headings(&input);
            if *as_json {
                let values: Vec<_> = all
                    .iter()
                    .map(|h| json!({"level": h.level, "title": h.title}))
                    .collect();
                println!("{}", serde_json::to_string(&values).unwrap());
            } else {
                for h in all {
                    println!("H{}\t{}", h.level, h.title);
                }
            }
        }
        Command::Section {
            file,
            heading,
            body_only,
            json: as_json,
        } => {
            let input = read_input(file)?;
            let all = headings(&input);
            let h = select_heading(&all, heading).map_err(selection_error)?;
            let start = if *body_only { h.body_start } else { h.start };
            let value = &input[start..h.end];
            if *as_json {
                println!(
                    "{}",
                    json!({"heading": h.title, "level": h.level, "content": value})
                );
            } else {
                print!("{value}");
            }
        }
        Command::Replace {
            file,
            section,
            from,
            text,
            write,
            dry_run,
            stdout,
        } => {
            if file == "-" && *write {
                return Err(error(
                    2,
                    "usage",
                    "--write requires a filesystem path; use --stdout with FILE -",
                ));
            }
            if file == "-" && from.as_deref() == Some("-") {
                return Err(error(
                    2,
                    "usage",
                    "document and replacement cannot both read from stdin",
                ));
            }
            let replacement = match (from, text) {
                (Some(path), None) => read_input(path)?,
                (None, Some(value)) => value.clone(),
                _ => unreachable!("clap validates the source group"),
            };
            let input = read_input(file)?;
            let (output, old_range, normalized) =
                replace_section(&input, section, replacement).map_err(selection_error)?;
            if *dry_run {
                unified_preview(file, &input[old_range], &normalized);
            } else if *stdout {
                print!("{output}");
            } else if *write {
                atomic_write(file, &output).map_err(|e| error(6, "write", e))?;
            }
        }
    }
    Ok(())
}

fn main() -> ExitCode {
    let cli = Cli::parse();
    match run(&cli) {
        Ok(()) => ExitCode::SUCCESS,
        Err(failure) => {
            match cli.error_format {
                ErrorFormat::Text => eprintln!("texio: {}", failure.message),
                ErrorFormat::Json => eprintln!(
                    "{}",
                    json!({"error": {"code": failure.kind, "message": failure.message}})
                ),
            }
            ExitCode::from(failure.code)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn section_stops_at_same_or_higher_heading() {
        let md = "# A\nintro\n## B\nbody\n### C\ndeep\n## D\nend\n";
        let all = headings(md);
        let b = select_heading(&all, "B").unwrap();
        assert_eq!(&md[b.start..b.end], "## B\nbody\n### C\ndeep\n");
    }

    #[test]
    fn ignores_headings_inside_fences() {
        let md = "# Real\n```md\n# Fake\n```\n## Next\n";
        let all = headings(md);
        assert_eq!(
            all.iter().map(|h| h.title.as_str()).collect::<Vec<_>>(),
            ["Real", "Next"]
        );
    }

    #[test]
    fn supports_setext_headings() {
        let md = "Title\n=====\nintro\n\nSection\n-------\nbody\n";
        let all = headings(md);
        assert_eq!(
            all.iter()
                .map(|h| (h.level, h.title.as_str()))
                .collect::<Vec<_>>(),
            [(1, "Title"), (2, "Section")]
        );
        let section = select_heading(&all, "Section").unwrap();
        assert_eq!(&md[section.body_start..section.end], "body\n");
    }

    #[test]
    fn setext_title_starting_with_hash_has_correct_body_boundary() {
        let md = "#Title\n------\nbody\n";
        let all = headings(md);
        let section = select_heading(&all, "#Title").unwrap();
        assert_eq!(&md[section.body_start..section.end], "body\n");
    }

    #[test]
    fn handles_crlf_without_inventing_a_heading() {
        let md = "# Real\r\ntext\r\n```md\r\n# Fake\r\n```\r\n## Next\r\n";
        let all = headings(md);
        assert_eq!(
            all.iter().map(|h| h.title.as_str()).collect::<Vec<_>>(),
            ["Real", "Next"]
        );
    }

    #[test]
    fn preserves_unrelated_bytes_during_replacement() {
        let md = "# Top\nkeep\n## Target\nold\n## Last\nkeep too\n";
        let all = headings(md);
        let target = select_heading(&all, "Target").unwrap();
        let output = format!(
            "{}{}{}",
            &md[..target.body_start],
            "new\n",
            &md[target.end..]
        );
        assert_eq!(output, "# Top\nkeep\n## Target\nnew\n## Last\nkeep too\n");
    }

    #[test]
    fn replacement_uses_the_documents_crlf_line_endings() {
        let md = "# Top\r\n## Target\r\nold\r\n## Last\r\nkeep\r\n";
        let all = headings(md);
        let target = select_heading(&all, "Target").unwrap();
        let replacement = normalize_replacement("first\nsecond".to_string(), md);
        let output = format!(
            "{}{}{}",
            &md[..target.body_start],
            replacement,
            &md[target.end..]
        );
        assert_eq!(
            output,
            "# Top\r\n## Target\r\nfirst\r\nsecond\r\n## Last\r\nkeep\r\n"
        );
    }

    #[test]
    fn replacement_uses_the_documents_lf_line_endings() {
        assert_eq!(
            normalize_replacement("first\r\nsecond\r".to_string(), "# Document\n"),
            "first\nsecond\n"
        );
    }

    #[test]
    fn json_escape_handles_all_control_characters() {
        assert_eq!(json_escape("a\u{0}b\u{8}\u{c}\n"), "a\\u0000b\\b\\f\\n");
    }

    #[test]
    fn parentless_relative_paths_use_the_current_directory() {
        assert_eq!(parent_directory(Path::new("README.md")), Path::new("."));
    }

    #[test]
    fn atomic_write_replaces_content_and_preserves_permissions() {
        let directory = tempfile::tempdir().unwrap();
        let path = directory.path().join("document.md");
        fs::write(&path, "before").unwrap();
        let permissions = fs::metadata(&path).unwrap().permissions();

        atomic_write(path.to_str().unwrap(), "after").unwrap();

        assert_eq!(fs::read_to_string(&path).unwrap(), "after");
        assert_eq!(fs::metadata(&path).unwrap().permissions(), permissions);
    }

    #[cfg(unix)]
    #[test]
    fn atomic_write_preserves_a_symlink_and_updates_its_target() {
        use std::os::unix::fs::symlink;

        let directory = tempfile::tempdir().unwrap();
        let target = directory.path().join("target.md");
        let link = directory.path().join("link.md");
        fs::write(&target, "before").unwrap();
        symlink(&target, &link).unwrap();

        atomic_write(link.to_str().unwrap(), "after").unwrap();

        assert!(
            fs::symlink_metadata(&link)
                .unwrap()
                .file_type()
                .is_symlink()
        );
        assert_eq!(fs::read_to_string(&target).unwrap(), "after");
    }

    #[test]
    fn duplicate_titles_are_rejected() {
        let all = headings("## Same\na\n## Same\nb\n");
        assert!(
            select_heading(&all, "Same")
                .unwrap_err()
                .contains("ambiguous")
        );
    }

    #[test]
    fn complex_gfm_fixture_has_only_structural_headings() {
        let md = include_str!("../tests/fixtures/complex-gfm.md");
        let all = headings(md);
        assert_eq!(
            all.iter().map(|h| h.title.as_str()).collect::<Vec<_>>(),
            ["Document", "Target", "Nested section", "After"]
        );
        let target = select_heading(&all, "Target").unwrap();
        let section = &md[target.start..target.end];
        assert!(section.contains("| Tables | yes |"));
        assert!(section.contains("- [x] Parsed task"));
        assert!(section.contains("## Heading inside a fence"));
        assert!(section.contains("## Heading inside an HTML block"));
        assert!(section.contains("[^note]: Footnote text."));
        assert!(!section.contains("This must remain outside Target."));
    }

    #[test]
    fn opening_thematic_break_does_not_hide_later_headings() {
        let md = "---\nIntro text\n\n# Visible\nbody\n\n---\n";
        assert_eq!(yaml_front_matter_end(md), 0);
        assert_eq!(
            headings(md)
                .iter()
                .map(|heading| heading.title.as_str())
                .collect::<Vec<_>>(),
            ["Visible"]
        );
    }

    #[test]
    fn front_matter_requires_a_top_level_mapping_key() {
        assert_eq!(yaml_front_matter_end("---\ntitle: Texio\n---\n# Doc\n"), 21);
        assert_eq!(yaml_front_matter_end("---\nplain scalar\n---\n# Doc\n"), 0);
    }

    #[test]
    fn setext_fixture_handles_hash_prefixed_title() {
        let md = include_str!("../tests/fixtures/setext.md");
        let all = headings(md);
        assert_eq!(
            all.iter().map(|h| h.title.as_str()).collect::<Vec<_>>(),
            ["Document title", "#Target", "Following section"]
        );
        let target = select_heading(&all, "#Target").unwrap();
        assert_eq!(
            md[target.body_start..target.end].replace("\r\n", "\n"),
            "\nSetext body.\n\n"
        );
    }

    #[test]
    fn fixture_replacement_preserves_every_byte_outside_the_body() {
        let md = include_str!("../tests/fixtures/complex-gfm.md");
        let all = headings(md);
        let target = select_heading(&all, "Target").unwrap();
        let prefix = &md[..target.body_start];
        let suffix = &md[target.end..];
        let (output, _, normalized) =
            replace_section(md, "Target", "Replacement body.".to_string()).unwrap();
        assert_eq!(&output[..prefix.len()], prefix);
        assert_eq!(
            &output[prefix.len()..prefix.len() + normalized.len()],
            normalized
        );
        assert_eq!(&output[prefix.len() + normalized.len()..], suffix);
    }

    #[test]
    fn document_without_final_newline_is_preserved() {
        let md = "# First\nbody\n# Last\nold";
        assert_eq!(
            headings(md)
                .iter()
                .map(|heading| heading.title.as_str())
                .collect::<Vec<_>>(),
            ["First", "Last"]
        );
        let (output, _, _) = replace_section(md, "First", "new".to_string()).unwrap();
        assert_eq!(output, "# First\nnew\n# Last\nold");
        let (output, _, _) = replace_section(md, "Last", "new".to_string()).unwrap();
        assert_eq!(output, "# First\nbody\n# Last\nnew\n");
    }
}
