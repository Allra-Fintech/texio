use pulldown_cmark::{Event, HeadingLevel, Options, Parser, Tag, TagEnd};
use similar::TextDiff;
use std::{env, fs, io::Write, path::Path, process};
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

    for (event, range) in Parser::new_ext(input, options).into_offset_iter() {
        match event {
            Event::Start(Tag::Heading { level, .. }) => {
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
    let first_line = input[start..first_end].trim_start();
    if first_line.starts_with('#') {
        first_end
    } else {
        line_end(input, first_end)
    }
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

fn usage() -> ! {
    eprintln!(
        "texio — reliable Markdown operations\n\nUSAGE:\n  texio headings <file> [--json]\n  texio section <file> <heading> [--body-only] [--json]\n  texio replace <file> --section <heading> (--from <file> | --text <text>) [--dry-run]\n"
    );
    process::exit(2);
}

fn fail(message: impl std::fmt::Display) -> ! {
    eprintln!("texio: {message}");
    process::exit(1);
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

fn main() {
    let args: Vec<String> = env::args().skip(1).collect();
    let Some(command) = args.first().map(String::as_str) else {
        usage()
    };

    match command {
        "headings" => {
            let Some(path) = args.get(1) else { usage() };
            let input = fs::read_to_string(path).unwrap_or_else(|e| fail(e));
            let all = headings(&input);
            if args.iter().any(|a| a == "--json") {
                print!("[");
                for (i, h) in all.iter().enumerate() {
                    if i > 0 {
                        print!(",");
                    }
                    print!(
                        "{{\"level\":{},\"title\":\"{}\"}}",
                        h.level,
                        json_escape(&h.title)
                    );
                }
                println!("]");
            } else {
                for h in all {
                    println!("H{}\t{}", h.level, h.title);
                }
            }
        }
        "section" => {
            let (Some(path), Some(title)) = (args.get(1), args.get(2)) else {
                usage()
            };
            let input = fs::read_to_string(path).unwrap_or_else(|e| fail(e));
            let all = headings(&input);
            let h = select_heading(&all, title).unwrap_or_else(|e| fail(e));
            let body_only = args.iter().any(|a| a == "--body-only");
            let start = if body_only { h.body_start } else { h.start };
            let value = &input[start..h.end];
            if args.iter().any(|a| a == "--json") {
                println!(
                    "{{\"heading\":\"{}\",\"level\":{},\"content\":\"{}\"}}",
                    json_escape(&h.title),
                    h.level,
                    json_escape(value)
                );
            } else {
                print!("{value}");
            }
        }
        "replace" => {
            let Some(path) = args.get(1) else { usage() };
            let section_pos = args
                .iter()
                .position(|a| a == "--section")
                .unwrap_or_else(|| usage());
            let title = args.get(section_pos + 1).unwrap_or_else(|| usage());
            let replacement = if let Some(pos) = args.iter().position(|a| a == "--from") {
                fs::read_to_string(args.get(pos + 1).unwrap_or_else(|| usage()))
                    .unwrap_or_else(|e| fail(e))
            } else if let Some(pos) = args.iter().position(|a| a == "--text") {
                args.get(pos + 1).unwrap_or_else(|| usage()).clone()
            } else {
                usage()
            };
            let input = fs::read_to_string(path).unwrap_or_else(|e| fail(e));
            let all = headings(&input);
            let h = select_heading(&all, title).unwrap_or_else(|e| fail(e));
            let old = &input[h.body_start..h.end];
            let normalized = normalize_replacement(replacement, &input);
            let output = format!(
                "{}{}{}",
                &input[..h.body_start],
                normalized,
                &input[h.end..]
            );
            if args.iter().any(|a| a == "--dry-run") {
                unified_preview(
                    path,
                    old,
                    &output[h.body_start..h.body_start + normalized.len()],
                );
            } else {
                atomic_write(path, &output).unwrap_or_else(|e| fail(e));
            }
        }
        "--help" | "-h" => usage(),
        _ => usage(),
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
}
