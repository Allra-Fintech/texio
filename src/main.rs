use std::{env, fs, process};

#[derive(Debug, Clone, PartialEq, Eq)]
struct Heading {
    level: usize,
    title: String,
    start: usize,
    body_start: usize,
    end: usize,
}

fn headings(input: &str) -> Vec<Heading> {
    let mut found: Vec<Heading> = Vec::new();
    let mut offset = 0;
    let mut fence: Option<(char, usize)> = None;

    for line_with_end in input.split_inclusive('\n') {
        let line = line_with_end.strip_suffix('\n').unwrap_or(line_with_end);
        let trimmed = line.trim_start();

        if let Some((marker, width)) = fence {
            if trimmed.chars().take_while(|c| *c == marker).count() >= width {
                fence = None;
            }
            offset += line_with_end.len();
            continue;
        }

        let first = trimmed.chars().next();
        if matches!(first, Some('`' | '~')) {
            let marker = first.unwrap();
            let width = trimmed.chars().take_while(|c| *c == marker).count();
            if width >= 3 {
                fence = Some((marker, width));
                offset += line_with_end.len();
                continue;
            }
        }

        let level = line.chars().take_while(|c| *c == '#').count();
        if (1..=6).contains(&level) && line.as_bytes().get(level) == Some(&b' ') {
            let raw = line[level + 1..].trim();
            let title = raw.trim_end_matches('#').trim_end().to_string();
            found.push(Heading {
                level,
                title,
                start: offset,
                body_start: offset + line_with_end.len(),
                end: input.len(),
            });
        }
        offset += line_with_end.len();
    }

    for i in 0..found.len() {
        if let Some(next) = found[i + 1..].iter().find(|h| h.level <= found[i].level) {
            found[i].end = next.start;
        }
    }
    found
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
    value
        .replace('\\', "\\\\")
        .replace('"', "\\\"")
        .replace('\n', "\\n")
        .replace('\r', "\\r")
        .replace('\t', "\\t")
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
    println!("--- {path}");
    println!("+++ {path} (proposed)");
    println!("@@ section replacement @@");
    for line in before.lines() {
        println!("-{line}");
    }
    for line in after.lines() {
        println!("+{line}");
    }
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
            let mut normalized = replacement;
            if !normalized.ends_with('\n') {
                normalized.push('\n');
            }
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
                fs::write(path, output).unwrap_or_else(|e| fail(e));
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
    fn duplicate_titles_are_rejected() {
        let all = headings("## Same\na\n## Same\nb\n");
        assert!(
            select_heading(&all, "Same")
                .unwrap_err()
                .contains("ambiguous")
        );
    }
}
