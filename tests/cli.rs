use assert_cmd::Command;
use predicates::prelude::*;
use std::fs;

fn texio() -> Command {
    Command::cargo_bin("texio").unwrap()
}

#[test]
fn headings_reads_stdin_and_emits_json() {
    texio()
        .args(["headings", "-", "--json"])
        .write_stdin("# One\n## Two\n")
        .assert()
        .success()
        .stdout("[{\"level\":1,\"title\":\"One\"},{\"level\":2,\"title\":\"Two\"}]\n");
}

#[test]
fn missing_section_has_stable_json_error_and_exit_code() {
    texio()
        .args(["--error-format", "json", "section", "-", "Missing"])
        .write_stdin("# Present\n")
        .assert()
        .code(4)
        .stdout("")
        .stderr(predicate::str::contains(
            "{\"error\":{\"code\":\"section_not_found\",\"message\":\"section not found: Missing\"}}",
        ));
}

#[test]
fn ambiguous_section_has_stable_exit_code() {
    texio()
        .args(["section", "-", "Same"])
        .write_stdin("# Same\none\n# Same\ntwo\n")
        .assert()
        .code(5)
        .stderr(predicate::str::contains(
            "ambiguous section: Same (2 matches)",
        ));
}

#[test]
fn multiline_setext_extraction_excludes_the_title_and_underline() {
    texio()
        .args(["section", "-", "Alpha Beta", "--body-only"])
        .write_stdin("Alpha\nBeta\n---\nold body\n\n## Next\nkeep\n")
        .assert()
        .success()
        .stdout("old body\n\n");
}

#[test]
fn multiline_setext_write_preserves_the_heading_and_following_section() {
    let directory = tempfile::tempdir().unwrap();
    let path = directory.path().join("doc.md");
    let original = "Alpha\nBeta\n---\nold body\n\n## Next\nkeep\n";
    fs::write(&path, original).unwrap();

    texio()
        .args([
            "replace",
            path.to_str().unwrap(),
            "--section",
            "Alpha Beta",
            "--text",
            "new body",
            "--dry-run",
        ])
        .assert()
        .success();
    assert_eq!(fs::read_to_string(&path).unwrap(), original);

    texio()
        .args([
            "replace",
            path.to_str().unwrap(),
            "--section",
            "Alpha Beta",
            "--text",
            "new body",
            "--write",
        ])
        .assert()
        .success();
    assert_eq!(
        fs::read_to_string(&path).unwrap(),
        "Alpha\nBeta\n---\nnew body\n## Next\nkeep\n"
    );
}

#[test]
fn unreadable_input_has_stable_exit_code() {
    texio()
        .args(["headings", "file-that-does-not-exist.md"])
        .assert()
        .code(3)
        .stderr(predicate::str::starts_with("texio: "));
}

#[test]
fn replace_requires_an_explicit_mode() {
    texio()
        .args(["replace", "doc.md", "--section", "A", "--text", "new"])
        .assert()
        .code(2)
        .stderr(predicate::str::is_empty().not());
}

#[test]
fn stdout_mode_does_not_modify_the_file() {
    let directory = tempfile::tempdir().unwrap();
    let path = directory.path().join("doc.md");
    fs::write(&path, "# A\nold\n# B\nkeep\n").unwrap();

    texio()
        .args([
            "replace",
            path.to_str().unwrap(),
            "--section",
            "A",
            "--text",
            "new",
            "--stdout",
        ])
        .assert()
        .success()
        .stdout("# A\nnew\n# B\nkeep\n");

    assert_eq!(fs::read_to_string(path).unwrap(), "# A\nold\n# B\nkeep\n");
}

#[test]
fn dry_run_is_a_unified_diff_and_does_not_modify_the_file() {
    let directory = tempfile::tempdir().unwrap();
    let path = directory.path().join("doc.md");
    fs::write(&path, "# A\nold\n").unwrap();

    texio()
        .args([
            "replace",
            path.to_str().unwrap(),
            "--section",
            "A",
            "--text",
            "new",
            "--dry-run",
        ])
        .assert()
        .success()
        .stdout(predicate::str::contains("-old\n+new\n"));

    assert_eq!(fs::read_to_string(path).unwrap(), "# A\nold\n");
}

#[test]
fn write_mode_updates_the_file() {
    let directory = tempfile::tempdir().unwrap();
    let path = directory.path().join("doc.md");
    fs::write(&path, "# A\nold\n").unwrap();

    texio()
        .args([
            "replace",
            path.to_str().unwrap(),
            "--section",
            "A",
            "--text",
            "new",
            "--write",
        ])
        .assert()
        .success()
        .stdout("");

    assert_eq!(fs::read_to_string(path).unwrap(), "# A\nnew\n");
}

#[test]
fn replace_can_transform_a_document_from_stdin_to_stdout() {
    texio()
        .args([
            "replace",
            "-",
            "--section",
            "A",
            "--text",
            "new",
            "--stdout",
        ])
        .write_stdin("# A\nold\n")
        .assert()
        .success()
        .stdout("# A\nnew\n");
}

#[test]
fn replace_rejects_using_stdin_twice() {
    texio()
        .args(["replace", "-", "--section", "A", "--from", "-", "--stdout"])
        .assert()
        .code(2)
        .stderr(predicate::str::contains(
            "document and replacement cannot both read from stdin",
        ));
}

#[test]
fn replacing_a_section_preserves_next_heading_markers_and_indentation() {
    for following in ["> ## Next", "- ## Next", "   ## Next"] {
        let input = format!("## Target\nold\n\n{following}\nkeep\n");
        let expected = format!("## Target\nnew\n{following}\nkeep\n");
        texio()
            .args([
                "replace",
                "-",
                "--section",
                "Target",
                "--text",
                "new",
                "--stdout",
            ])
            .write_stdin(input)
            .assert()
            .success()
            .stdout(expected);
    }
}

#[test]
fn section_extraction_retains_the_heading_source_prefix() {
    texio()
        .args(["section", "-", "Quoted"])
        .write_stdin("> ## Quoted\n> body\n\n## Next\nkeep\n")
        .assert()
        .success()
        .stdout("> ## Quoted\n> body\n\n");
}

#[test]
fn replacement_keeps_the_following_setext_heading_separate() {
    texio()
        .args([
            "replace",
            "-",
            "--section",
            "Target",
            "--text",
            "new body",
            "--stdout",
        ])
        .write_stdin("## Target\nold\n\nNext\n---\nkeep\n")
        .assert()
        .success()
        .stdout("## Target\nnew body\n\nNext\n---\nkeep\n");
}
