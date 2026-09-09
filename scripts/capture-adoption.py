#!/usr/bin/env python3
"""Capture public aggregate launch metrics; use gh authentication without recording it."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import urllib.error
import urllib.request

REPO = "Allra-Fintech/texio"


def github(endpoint):
    result = subprocess.run(["gh", "api", endpoint], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError("GitHub request failed: " + endpoint)
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    parser.add_argument("--note", default="")
    args = parser.parse_args()
    snapshot = {"schema_version": 1, "repository": REPO,
                "started_at": datetime.now(timezone.utc).isoformat(), "note": args.note}
    repo = github("repos/" + REPO)
    snapshot["github"] = {"source": "https://api.github.com/repos/" + REPO,
                          "stars": repo["stargazers_count"], "forks": repo["forks_count"],
                          "subscribers": repo["subscribers_count"]}
    for kind in ("issue", "pr"):
        for state in ("open", "closed"):
            endpoint = "search/issues?q=repo%3AAllra-Fintech%2Ftexio+is%3A" + kind + "+is%3A" + state + "&per_page=1"
            value = github(endpoint)
            if value.get("incomplete_results"):
                raise RuntimeError("GitHub search returned incomplete counts")
            snapshot["github"][kind + "s_" + state] = {"count": value["total_count"], "source": "https://api.github.com/" + endpoint}
    releases = []
    page = 1
    while True:
        batch = github("repos/" + REPO + "/releases?per_page=100&page=" + str(page))
        releases.extend(r for r in batch if not r["draft"])
        if len(batch) < 100:
            break
        page += 1
    snapshot["releases"] = [{"tag": r["tag_name"], "source": r["url"], "published_at": r["published_at"],
        "assets": [{"name": a["name"], "downloads": a["download_count"], "source": a["url"],
                    "kind": "checksum" if a["name"].endswith(".sha256") else "binary_archive" if a["name"].endswith((".tar.gz", ".zip")) else "other"}
                   for a in r["assets"]]} for r in releases]
    url = "https://crates.io/api/v1/crates/texio-cli"
    request = urllib.request.Request(url, headers={"User-Agent": "Texio-launch-metrics (https://github.com/Allra-Fintech/texio)"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            crate = json.load(response)
        snapshot["crates_io"] = {"source": url, "available": True, "downloads": crate["crate"]["downloads"],
            "versions": [{"version": v["num"], "downloads": v["downloads"], "yanked": v["yanked"]} for v in crate["versions"]]}
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise
        snapshot["crates_io"] = {"source": url, "available": False, "downloads": None, "http_status": 404}
    query = 'query { repository(owner:"Allra-Fintech", name:"texio") { discussions { totalCount } } }'
    result = subprocess.run(["gh", "api", "graphql", "-f", "query=" + query], capture_output=True, text=True)
    data = json.loads(result.stdout) if result.stdout else {}
    snapshot["discussions"] = {"source": "https://github.com/" + REPO + "/discussions",
        "count": data.get("data", {}).get("repository", {}).get("discussions", {}).get("totalCount") if not data.get("errors") else None}
    snapshot["evidence_ledger"] = {"verified_external_installs": None, "independent_agent_trials": None,
        "external_repository_adoptions": None, "substantive_feedback": None,
        "note": "Not measured by API counts. Record verified evidence separately; null does not mean zero."}
    snapshot["limitations"] = ["Downloads include maintainer and CI verification, retries and bots; they are not unique installs.",
        "Checksum downloads are separate from binary downloads. GitHub source archives are not counted.",
        "Stars, forks, issues and discussions do not establish adoption or substantive feedback.",
        "Endpoints are collected sequentially and may update at different times. No personal tracking is collected."]
    snapshot["completed_at"] = datetime.now(timezone.utc).isoformat()
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("x") as output:
        json.dump(snapshot, output, indent=2)
        output.write("\n")
    print(str(destination))


if __name__ == "__main__":
    main()
