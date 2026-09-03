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
        .stderr(predicate::str::contains(
            "required arguments were not provided",
        ));
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
