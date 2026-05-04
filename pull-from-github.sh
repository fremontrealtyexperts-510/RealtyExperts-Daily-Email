#!/bin/bash
#
# pull-from-github.sh
#
# Pulls latest tracked files from GitHub into the Mac OneDrive workspace.
# COMPANION TO push-to-github.sh — same /tmp clone pattern, opposite direction.
# NEVER touches Mac OneDrive .git (frozen by design — see push-to-github.sh).
#
# Usage:
#   ./pull-from-github.sh              # silent, only logs on changes/errors
#   ./pull-from-github.sh --verbose    # log every step
#
# What it does:
#   1. Cheap remote check: ls-remote vs cached SHA — exit early if no change
#   2. Clones repo from GitHub to /tmp/daily-email-pull
#   3. rsync /tmp clone → OneDrive workspace (NO --delete, --exclude=.git, etc.)
#   4. Updates cached SHA
#   5. Cleans up /tmp clone

set -u

REPO="fremontrealtyexperts-510/RealtyExperts-Daily-Email"
SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
DST_DIR="/tmp/daily-email-pull"
SHA_CACHE="$SRC_DIR/.git-pull-last-sha"
LOG_FILE="$SRC_DIR/.git-pull.log"
VERBOSE=${1:-}

log() {
  echo "[$(date -u +%FT%TZ)] $1" >> "$LOG_FILE"
  [ "$VERBOSE" = "--verbose" ] && echo "$1"
}

# --- Get GitHub token ---
GH_TOKEN=$(gh auth token -u fremontrealtyexperts-510 2>/dev/null)
if [ -z "$GH_TOKEN" ]; then
  log "ERROR: could not get GitHub token for fremontrealtyexperts-510 (run: gh auth login -u fremontrealtyexperts-510)"
  exit 1
fi

# --- Cheap remote check: skip if we already have current SHA ---
REMOTE_SHA=$(curl -sf -H "Authorization: Bearer $GH_TOKEN" \
  "https://api.github.com/repos/${REPO}/commits/main" 2>/dev/null \
  | grep -m1 '"sha"' | sed 's/.*"sha": *"\([^"]*\)".*/\1/')

if [ -z "$REMOTE_SHA" ]; then
  log "ERROR: could not query remote SHA"
  exit 1
fi

if [ -f "$SHA_CACHE" ]; then
  CACHED_SHA=$(cat "$SHA_CACHE")
  if [ "$CACHED_SHA" = "$REMOTE_SHA" ]; then
    [ "$VERBOSE" = "--verbose" ] && log "no change (still at $REMOTE_SHA)"
    exit 0
  fi
fi

log "remote moved (was $(cat "$SHA_CACHE" 2>/dev/null || echo none) -> $REMOTE_SHA), pulling..."

# --- Clone fresh ---
rm -rf "$DST_DIR"
git clone --depth 1 "https://x-access-token:${GH_TOKEN}@github.com/${REPO}.git" "$DST_DIR" 2>>"$LOG_FILE" || {
  log "ERROR: clone failed"
  rm -rf "$DST_DIR"
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
  rm -rf "$DST_DIR"
  exit 1
}

# --- Update SHA cache ---
echo "$REMOTE_SHA" > "$SHA_CACHE"

# --- Cleanup ---
rm -rf "$DST_DIR"

log "pulled OK to $REMOTE_SHA"
exit 0
