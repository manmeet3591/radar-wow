#!/usr/bin/env bash
# Push every radar-wow repo to GitHub as public repos under OWNER (default: the manmeet3591 account).
# Requires: gh installed and logged in (gh auth login). For an org, create it first and pass its name.
set -euo pipefail
ORG=${1:-manmeet3591}
cd "$(dirname "$0")"
for d in . radarwow-*; do
  name=$(basename "$(cd "$d" && pwd)")
  (cd "$d" && gh repo create "$ORG/$name" --public --source . --push --description "$(head -3 README.md | tail -1 | cut -c1-300)")
done
