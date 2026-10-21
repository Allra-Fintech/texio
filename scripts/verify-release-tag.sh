#!/usr/bin/env bash
set -euo pipefail

release_tag=${1:?Usage: verify-release-tag.sh RELEASE_TAG}
package_version=$(cargo metadata --offline --no-deps --format-version 1 |
  jq -er '.packages[] | select(.name == "texio-cli") | .version')
if [[ "$release_tag" != "v$package_version" ]]; then
  echo "Release tag must match package version v$package_version" >&2
  exit 1
fi

tag_commit=$(git rev-parse --verify "refs/tags/$release_tag^{commit}")
if [[ "$tag_commit" != "$(git rev-parse HEAD)" ]]; then
  echo "Release tag must point to the checked-out commit" >&2
  exit 1
fi
if ! git merge-base --is-ancestor "$tag_commit" refs/remotes/origin/main; then
  echo "Release commit must belong to origin/main" >&2
  exit 1
fi

echo "Verified $release_tag: package version matches and commit belongs to main."
