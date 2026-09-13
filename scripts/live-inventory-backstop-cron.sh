#!/usr/bin/env bash
# VPS backup cron for the harvrealtor.net live-inventory feed refresh (added 2026-07-17).
# Backstops the Mac launchd job com.harvbalu.live-inventory-refresh (9:00/11:00/15:00 PT):
# regenerates live-inventory.json from the newest Drive MLS export and publishes to
# GitHub Pages ONLY when the export date moved. refresh-live-inventory.sh is idempotent,
# so Mac+VPS overlap is safe -- whichever runs first wins, the other no-ops.
# Cron fires it at 9:30 / 11:30 / 15:30 PT -- staggered 30 min AFTER the Mac passes
# (system TZ = America/Los_Angeles, so crontab times are Pacific-local).
# gh is not installed on the VPS, so refresh-live-inventory.sh falls back to the SSH
# deploy key (~/.ssh/realty_email_deploy) for the publish push.
set -o pipefail

REPO_DIR="$HOME/workspaces/RealtyExperts-Daily-Email"
LOG="$REPO_DIR/.live-inventory-backstop.log"

cd "$REPO_DIR" || { echo "[$(date -u +%FT%TZ)] ERROR: cd $REPO_DIR failed" >> "$LOG"; exit 1; }

echo "[$(date -u +%FT%TZ)] --- cron wake ---" >> "$LOG"
./refresh-live-inventory.sh >> "$LOG" 2>&1
rc=$?

# The generator always rewrites the tracked live-inventory.json (intra-day inventory
# shifts even when the date field does not), which would dirty the working tree and make
# the 15-min git auto-pull's --autostash pop conflict against an incoming publish commit.
# The authoritative feed lives on origin / GitHub Pages, not this working copy, so discard
# any local regeneration to keep the tree clean for auto-pull.
git checkout -- live-inventory.json 2>/dev/null

echo "[$(date -u +%FT%TZ)] refresh exit=$rc; tree recleaned" >> "$LOG"
exit $rc
