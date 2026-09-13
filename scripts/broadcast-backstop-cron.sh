#!/usr/bin/env bash
# VPS always-on backstop for the daily Agent Hub broadcast (added 2026-06-04).
# Mirrors the Mac launchd job com.harvbalu.realty-broadcast-backstop, but runs on the
# always-on VPS so the broadcast still gets backstopped when the Mac is asleep/off.
# Cron fires it at 10:45 / 13:45 / 16:30 PT -- staggered 15 min AFTER the Mac's 10:30 /
# 13:30 passes so the two backstops can never double-fire (a sent broadcast flips
# notify_enabled=true, the no-double-send gate inside broadcast-backstop.js).
set -o pipefail
REPO_DIR="$HOME/workspaces/RealtyExperts-Daily-Email"
LOG="$REPO_DIR/.broadcast-backstop.log"
cd "$REPO_DIR" || { echo "[$(date -u +%FT%TZ)] ERROR: cd $REPO_DIR failed" >> "$LOG"; exit 1; }
echo "[$(date -u +%FT%TZ)] --- cron wake ---" >> "$LOG"
/usr/bin/node broadcast-backstop.js >> "$LOG" 2>&1
