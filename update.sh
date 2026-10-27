#!/usr/bin/env bash
# Weekly refresh: rerun on fresh FRED data, refresh outputs/latest, archive a dated copy, commit, push.
set -euo pipefail
cd "$(dirname "$0")"
D=$(date +%F)
git pull --rebase --quiet || true
python3 -m pytest -q tests
python3 -m hourglass.run --out outputs/latest
mkdir -p "outputs/runs/$D"
cp outputs/latest/* "outputs/runs/$D/"
git add -A outputs
if git diff --cached --quiet; then echo "No changes."; exit 0; fi
git -c user.name="Harry Plendl" -c user.email="12847375+hplendl@users.noreply.github.com" commit -q -m "Weekly run $D (FRED data)"
git push -q origin HEAD
echo "Published run $D"
