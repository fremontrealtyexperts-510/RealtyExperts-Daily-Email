#!/bin/bash
#
# pull-from-github.sh
#
# Pulls latest tracked files from GitHub into the Mac OneDrive workspace.
# COMPANION TO push-to-github.sh — same /tmp clone pattern, opposite direction.
# NEVER touches Mac OneDrive .git (frozen by design — see push-to-github.sh).
#
# Usage:
#   ./pull-from-github.sh              # quiet, but ALWAYS prints a one-line result
#   ./pull-from-github.sh --verbose    # log every step
#
# What it does:
#   1. Take an exclusive lock so a manual run and the launchd timer cannot collide
#   2. Cheap remote check: SHA vs cached SHA — exit early if no change
#   3. Clones repo from GitHub to a PER-RUN /tmp dir
#   4. rsync /tmp clone → workspace (NO --delete, --exclude=.git, etc.)
#   5. Updates cached SHA
#   6. Cleans up the /tmp clone
#
# 2026-08-12 — two fixes after a manual run silently corrupted a scheduled one:
#   * DST_DIR was the HARDCODED /tmp/daily-email-pull, and launchd
#     (com.harvbalu.realty-email-pull) runs this same script every 900s against the
#     same path. A manual run landing on a timer run had one process rm -rf'ing the
#     directory while the other cloned into it, producing
#     "invalid index-pack output" / "rsync failed" and leaving the workspace stale.
#     The launchd job's last exit status had been 1 for this reason. DST_DIR is now
#     unique per run ($$ + timestamp), so concurrent runs cannot touch each other.
#   * A flock-style lock now makes a second concurrent run exit 0 immediately
#     instead of racing at all (belt AND braces: the lock prevents the race, the
#     unique dir means even a lock failure cannot corrupt anything).
#   * The script was SILENT without --verbose, so a failed manual run looked like a
#     successful no-op. It now always prints one result line to stdout.

set -u

REPO="fremontrealtyexperts-510/RealtyExperts-Daily-Email"
SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
DST_DIR="/tmp/daily-email-pull.$$.$(date +%s)"   # per-run: never shared with the timer
LOCK_DIR="/tmp/daily-email-pull.lock"            # mkdir is atomic on macOS (no flock)
SHA_CACHE="$SRC_DIR/.git-pull-last-sha"
LOG_FILE="$SRC_DIR/.git-pull.log"
VERBOSE=${1:-}

log() {
  echo "[$(date -u +%FT%TZ)] $1" >> "$LOG_FILE"
  [ "$VERBOSE" = "--verbose" ] && echo "$1"
}

# Always tell the caller what happened, even without --verbose. A silent failure is
# how the 08/12 stale workspace went unnoticed.
say() { echo "$1"; }

# --- Exclusive lock (mkdir is atomic; no flock on macOS) -----------------------
# A stale lock from a killed run would block forever, so an old one is reclaimed.
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  LOCK_AGE=$(( $(date +%s) - $(stat -f %m "$LOCK_DIR" 2>/dev/null || date +%s) ))
  if [ "$LOCK_AGE" -gt 1800 ]; then
    log "WARN: reclaiming stale lock (${LOCK_AGE}s old)"
    rm -rf "$LOCK_DIR"
    mkdir "$LOCK_DIR" 2>/dev/null || { say "pull: could not acquire lock"; exit 1; }
  else
    log "another pull is already running (lock ${LOCK_AGE}s old) — skipping"
    say "pull: another run in progress, skipped"
    exit 0
  fi
fi

cleanup() { rm -rf "$DST_DIR" "$LOCK_DIR"; }
trap cleanup EXIT INT TERM

# --- Get GitHub token ---
GH_TOKEN=$(gh auth token -u fremontrealtyexperts-510 2>/dev/null)
if [ -z "$GH_TOKEN" ]; then
  log "ERROR: could not get GitHub token for fremontrealtyexperts-510 (run: gh auth login -u fremontrealtyexperts-510)"
  say "pull: FAILED (no GitHub token)"
  exit 1
fi

# --- Cheap remote check: skip if we already have current SHA ---
REMOTE_SHA=$(curl -sf -H "Authorization: Bearer $GH_TOKEN" \
  "https://api.github.com/repos/${REPO}/commits/main" 2>/dev/null \
  | grep -m1 '"sha"' | sed 's/.*"sha": *"\([^"]*\)".*/\1/')

if [ -z "$REMOTE_SHA" ]; then
  log "ERROR: could not query remote SHA"
  say "pull: FAILED (could not reach GitHub)"
  exit 1
fi

if [ -f "$SHA_CACHE" ]; then
  CACHED_SHA=$(cat "$SHA_CACHE")
  if [ "$CACHED_SHA" = "$REMOTE_SHA" ]; then
    [ "$VERBOSE" = "--verbose" ] && log "no change (still at $REMOTE_SHA)"
    say "pull: already up to date (${REMOTE_SHA:0:7})"
    exit 0
  fi
fi

log "remote moved (was $(cat "$SHA_CACHE" 2>/dev/null || echo none) -> $REMOTE_SHA), pulling..."

# --- Clone fresh (into the per-run dir; trap cleans it up on any exit) ---
rm -rf "$DST_DIR"
git clone --depth 1 "https://x-access-token:${GH_TOKEN}@github.com/${REPO}.git" "$DST_DIR" 2>>"$LOG_FILE" || {
  log "ERROR: clone failed"
  say "pull: FAILED (clone) — see .git-pull.log"
  exit 1
}

# --- rsync into OneDrive workspace ---
# Critical excludes: .git (would corrupt Mac frozen HEAD), node_modules (per-machine),
# .claude (per-machine session), .DS_Store (Mac noise). NO --delete (preserve Mac WIP).
rsync -a \
  --exclude='.git/' \
  --exclude='node_modules/' \
  --exclude='.claude/' \
  --exclude='.DS_Store' \
  --exclude='.npm/' \
  "$DST_DIR/" "$SRC_DIR/" 2>>"$LOG_FILE" || {
  log "ERROR: rsync failed"
  say "pull: FAILED (rsync) — see .git-pull.log"
  exit 1
}

# --- Update SHA cache (only after a fully successful rsync) ---
echo "$REMOTE_SHA" > "$SHA_CACHE"

log "pulled OK to $REMOTE_SHA"
say "pull: updated to ${REMOTE_SHA:0:7}"
exit 0
