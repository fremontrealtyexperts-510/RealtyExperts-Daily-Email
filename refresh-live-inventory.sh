#!/bin/bash
#
# refresh-live-inventory.sh
#
# Hands-off refresher for the harvrealtor.net live-inventory feed (homepage
# pulse band + /live-inventory page). Regenerates live-inventory.json from the
# NEWEST dated "MLS_Defined_Spread_Sheet_4- MMDDYY" file in Google Drive and
# publishes it to GitHub Pages — but ONLY when the export date actually moved
# forward, so re-runs on an unchanged Drive are silent no-ops (no commit spam).
#
# Runs from Mac launchd (com.harvbalu.live-inventory-refresh, 9:00 / 11:00 /
# 15:00 PT; launchd defers missed passes to the next wake) and is safe to run
# by hand any time:
#   ./refresh-live-inventory.sh
#
# The manual daily-email flow (run-daily.js Stage 3 / update-inventory.js 6b)
# still publishes the same file; whichever runs first wins, the other no-ops.
#
# Failure posture: generate-live-inventory.js has its own sanity gates and
# refuses to write a bad file; any failure here exits non-zero WITHOUT
# touching the published feed, and the site keeps serving yesterday's data
# with its honest date label.

set -e

REPO="fremontrealtyexperts-510/RealtyExperts-Daily-Email"
PAGES_URL="https://fremontrealtyexperts-510.github.io/RealtyExperts-Daily-Email/live-inventory.json"
SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
DST_DIR="/tmp/live-inventory-refresh-push"

cd "$SRC_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] refresh-live-inventory: start"

# --- What date is already published? (empty if Pages is unreachable) ---
PUBLISHED_DATE=$(curl -sf --max-time 20 "$PAGES_URL" | python3 -c "import json,sys; print(json.load(sys.stdin).get('date',''))" 2>/dev/null || echo "")
echo "Published date: ${PUBLISHED_DATE:-unknown}"

# --- Regenerate from the newest Drive export (sanity-gated) ---
node generate-live-inventory.js

NEW_DATE=$(python3 -c "import json; print(json.load(open('live-inventory.json')).get('date',''))")
echo "Generated date: $NEW_DATE"

if [ -z "$NEW_DATE" ]; then
  echo "ERROR: generated file has no date — not publishing"
  exit 1
fi

if [ "$NEW_DATE" = "$PUBLISHED_DATE" ]; then
  echo "Feed already current ($NEW_DATE) — nothing to publish"
  exit 0
fi

# --- Publish just this file from a clean /tmp clone (never the Drive .git) ---
GH_TOKEN=$(gh auth token -u fremontrealtyexperts-510 2>/dev/null)
if [ -z "$GH_TOKEN" ]; then
  echo "ERROR: no GitHub token for fremontrealtyexperts-510 (gh auth login -u fremontrealtyexperts-510)"
  exit 1
fi

rm -rf "$DST_DIR"
git clone --depth=1 "https://x-access-token:${GH_TOKEN}@github.com/${REPO}.git" "$DST_DIR" 2>&1 | tail -1
cd "$DST_DIR"
git config user.name "User8888-Level3"
git config user.email "fremontrealtyexperts510@gmail.com"

cp "$SRC_DIR/live-inventory.json" "$DST_DIR/live-inventory.json"
# long-run daily series for harvrealtor.net /inventory-history (upserted by
# generate-live-inventory.js on the same run that refreshed the live feed)
if [ -f "$SRC_DIR/inventory-history.json" ]; then
  cp "$SRC_DIR/inventory-history.json" "$DST_DIR/inventory-history.json"
fi
# keep the refresher itself versioned so the VPS picks it up via git auto-pull
cp "$SRC_DIR/refresh-live-inventory.sh" "$DST_DIR/refresh-live-inventory.sh"
chmod +x "$DST_DIR/refresh-live-inventory.sh"

git add live-inventory.json inventory-history.json refresh-live-inventory.sh
if [ -z "$(git status --short)" ]; then
  echo "No changes after copy — nothing to publish"
  rm -rf "$DST_DIR"
  exit 0
fi

git commit -m "live-inventory: refresh feed to $NEW_DATE (auto)"
git push origin main
cd /
rm -rf "$DST_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Published live-inventory.json for $NEW_DATE"
