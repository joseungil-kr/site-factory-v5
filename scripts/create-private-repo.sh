#!/usr/bin/env bash
# To run only in an authenticated environment with gh CLI and network.
# Never creates/updates any V4 repository.
set -euo pipefail
EXPECTED_USER='joseungil-kr'
REPO="$EXPECTED_USER/site-factory-v5"
cd "$(dirname "$0")/.."
command -v gh >/dev/null || { echo 'GitHub CLI gh missing'; exit 2; }
[[ "$(gh api user --jq '.login')" == "$EXPECTED_USER" ]] || { echo 'Authenticated GitHub user mismatch'; exit 3; }
if gh repo view "$REPO" --json visibility >/dev/null 2>&1; then
  visibility=$(gh repo view "$REPO" --json visibility --jq '.visibility')
  [[ "$visibility" == 'PRIVATE' ]] || { echo 'Existing repo is not private; refusing to push'; exit 4; }
else
  gh repo create "$REPO" --private --description 'Site Factory V5 independent noindex staging source' --disable-wiki
fi
if git remote get-url origin >/dev/null 2>&1; then
  [[ "$(git remote get-url origin)" == "https://github.com/$REPO.git" ]] || {
    echo 'Existing origin is different; refusing to modify'; exit 5;
  }
else
  git remote add origin "https://github.com/$REPO.git"
fi
git push -u origin HEAD:main
sha=$(git rev-parse HEAD)
remote=$(gh api "repos/$REPO/commits/main" --jq .sha)
[[ "$sha" == "$remote" ]] || { echo 'Remote SHA mismatch'; exit 6; }
[[ "$(gh repo view "$REPO" --json visibility --jq '.visibility')" == 'PRIVATE' ]] || {
 echo 'Remote is not private'; exit 7;
}
printf 'Verified private GitHub repo: https://github.com/%s at %s\n' "$REPO" "$remote"
