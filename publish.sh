#!/usr/bin/env bash
# Push every radar-wow repo to a GitHub org. Requires: gh installed and logged in (gh auth login),
# and the org already created at https://github.com/organizations/plan
set -euo pipefail
ORG=${1:-radar-wow}
cd "$(dirname "$0")"
for d in . radarwow-*; do
  name=$(basename "$(cd "$d" && pwd)")
  (cd "$d" && gh repo create "$ORG/$name" --public --source . --push --description "$(head -3 README.md | tail -1 | cut -c1-300)")
done
