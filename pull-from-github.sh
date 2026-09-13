#!/bin/bash
#
# pull-from-github.sh
#
# Pulls latest tracked files from GitHub into the Mac Drive workspace.
# COMPANION TO push-to-github.sh, same clean-clone idea, opposite direction.
# NEVER touches the workspace's own .git (frozen by design, see push-to-github.sh).
#
# Usage:
#   ./pull-from-github.sh              # quiet, but ALWAYS prints a one-line result
#   ./pull-from-github.sh --verbose    # log every step
#
# What it does:
#   1. Take an exclusive lock so a manual run and the launchd timer cannot collide
#   2. Cheap remote check: remote SHA vs cached SHA, exit early if no change
#   3. Fetches into a clone that lives OFF Drive
#   4. Copies ONLY the files that changed between the cached SHA and the remote SHA
#      (all tracked files if there is no usable cached SHA), skipping any whose Drive
#      copy is already identical. No deletes; never .git, node_modules, .claude, .npm
#   5. Updates the cached SHA only if every copy succeeded
#
# 2026-09-13: rewritten to touch Drive as little as possible. The launchd runs of the
# old version rsynced the whole repo (1,000+ files) into the Drive mount, and the
# Drive File Provider fails those reads and writes under launchd with EDEADLK
# ("mmap: Resource deadlock avoided"), so the job had not completed a pull since
# 2026-08-12. launchd now enters through
# ~/Library/Application Support/harvbalu-realty-email-pull/run-pull.sh, which keeps
# the clone, SHA cache and log on local disk (PULL_REPO_DIR, PULL_STATE_DIR) and
# names the Drive workspace as PULL_TARGET_DIR. Every copy is retried; a file that
# still fails leaves the SHA where it was, so the next pass retries the same diff
# (copies are idempotent). Manual runs from the workspace behave as before.
#
# 2026-08-12: per-run clone dir + mkdir lock (a manual run had raced the timer), and
# a result line is always printed so a failed run cannot look like a silent no-op.

set -u

REPO="fremontrealtyexperts-510/RealtyExperts-Daily-Email"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="${PULL_TARGET_DIR:-$SCRIPT_DIR}"
STATE_DIR="${PULL_STATE_DIR:-$SCRIPT_DIR}"
REPO_DIR="${PULL_REPO_DIR:-}"                    # empty = per-run /tmp clone
LOCK_DIR="/tmp/daily-email-pull.lock"            # mkdir is atomic on macOS (no flock)
SHA_CACHE="$STATE_DIR/.git-pull-last-sha"
LOG_FILE="$STATE_DIR/.git-pull.log"
LIST="/tmp/daily-email-pull.$$.list"
VERBOSE=${1:-}

log() {
  echo "[$(date -u +%FT%TZ)] $1" >> "$LOG_FILE" 2>/dev/null
  [ "$VERBOSE" = "--verbose" ] && echo "$1"
}

# Always tell the caller what happened, even without --verbose. A silent failure is
# how the 08/12 stale workspace went unnoticed.
say() { echo "$1"; }

# retry cmd...: Drive I/O fails transiently (EDEADLK) while the File Provider catches up
retry() { local i; for i in 1 2 3 4; do "$@" 2>/dev/null && return 0; sleep 3; done; return 1; }

# --- Exclusive lock (mkdir is atomic; no flock on macOS) -----------------------
# A stale lock from a killed run would block forever, so an old one is reclaimed.
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  LOCK_AGE=$(( $(date +%s) - $(stat -f %m "$LOCK_DIR" 2>/dev/null || date +%s) ))
  if [ "$LOCK_AGE" -gt 1800 ]; then
    log "WARN: reclaiming stale lock (${LOCK_AGE}s old)"
    rm -rf "$LOCK_DIR"
    mkdir "$LOCK_DIR" 2>/dev/null || { say "pull: could not acquire lock"; exit 1; }
  else
    log "another pull is already running (lock ${LOCK_AGE}s old), skipping"
    say "pull: another run in progress, skipped"
    exit 0
  fi
fi

if [ -n "$REPO_DIR" ]; then WORK="$REPO_DIR"; else WORK="/tmp/daily-email-pull.$$.$(date +%s)"; fi
cleanup() { rm -rf "$LOCK_DIR" "$LIST"; [ -z "$REPO_DIR" ] && rm -rf "$WORK"; }
trap cleanup EXIT INT TERM

# --- Get GitHub token (sent as a header, never written into a URL or .git/config) ---
GH_TOKEN=$(gh auth token -u fremontrealtyexperts-510 2>/dev/null)
if [ -z "$GH_TOKEN" ]; then
  log "ERROR: could not get GitHub token for fremontrealtyexperts-510 (run: gh auth login -u fremontrealtyexperts-510)"
  say "pull: FAILED (no GitHub token)"
  exit 1
fi
export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0="http.https://github.com/.extraheader"
export GIT_CONFIG_VALUE_0="AUTHORIZATION: basic $(printf 'x-access-token:%s' "$GH_TOKEN" | base64 | tr -d '\n')"

# --- Cheap remote check: skip if we already have current SHA ---
REMOTE_SHA=$(curl -sf -H "Authorization: Bearer $GH_TOKEN" \
  "https://api.github.com/repos/${REPO}/commits/main" 2>/dev/null \
  | grep -m1 '"sha"' | sed 's/.*"sha": *"\([^"]*\)".*/\1/')

if [ -z "$REMOTE_SHA" ]; then
  log "ERROR: could not query remote SHA"
  say "pull: FAILED (could not reach GitHub)"
  exit 1
fi

CACHED_SHA=""
[ -f "$SHA_CACHE" ] && CACHED_SHA=$(retry cat "$SHA_CACHE" || echo "")
if [ "$CACHED_SHA" = "$REMOTE_SHA" ]; then
  [ "$VERBOSE" = "--verbose" ] && log "no change (still at $REMOTE_SHA)"
  say "pull: already up to date (${REMOTE_SHA:0:7})"
  exit 0
fi

log "remote moved (was ${CACHED_SHA:-none} -> $REMOTE_SHA), pulling..."

# --- Fetch into the off-Drive clone and check out exactly REMOTE_SHA ---
if [ ! -d "$WORK/.git" ]; then
  git clone -q --filter=blob:none --no-checkout "https://github.com/${REPO}.git" "$WORK" 2>>"$LOG_FILE" || {
    log "ERROR: clone failed"; say "pull: FAILED (clone), see .git-pull.log"; exit 1; }
fi
{ git -C "$WORK" fetch -q origin main && git -C "$WORK" reset -q --hard "$REMOTE_SHA"; } 2>>"$LOG_FILE" || {
  log "ERROR: fetch/checkout of $REMOTE_SHA failed"; say "pull: FAILED (fetch), see .git-pull.log"; exit 1; }

# --- Which files? Only what changed since the last good pull, when we know it ---
if [ -n "$CACHED_SHA" ] && git -C "$WORK" cat-file -e "${CACHED_SHA}^{commit}" 2>/dev/null; then
  MODE="diff"
  git -C "$WORK" diff --name-only --no-renames --diff-filter=AMT "$CACHED_SHA" "$REMOTE_SHA" > "$LIST"
else
  MODE="full"
  git -C "$WORK" ls-files > "$LIST"
fi

# --- Copy into the workspace (never deletes; per-file retries) ---
copied=0; same=0; failed=0
while IFS= read -r f; do
  [ -f "$WORK/$f" ] || continue
  if cmp -s "$WORK/$f" "$TARGET_DIR/$f" 2>/dev/null; then same=$((same + 1)); continue; fi
  if retry mkdir -p "$(dirname "$TARGET_DIR/$f")" && retry cp -p "$WORK/$f" "$TARGET_DIR/$f"; then
    copied=$((copied + 1))
  else
    failed=$((failed + 1))
    log "ERROR: could not write $f"
  fi
done < <(grep -v -E '^(node_modules|\.claude|\.npm)/|(^|/)\.DS_Store$' "$LIST")

if [ "$failed" -gt 0 ]; then
  log "ERROR: $failed file(s) not written ($copied copied, $same already current, mode $MODE); SHA kept at ${CACHED_SHA:-none}, next pass retries"
  say "pull: FAILED ($failed file(s) could not be written, will retry), see .git-pull.log"
  exit 1
fi

# --- Update SHA cache (only after every copy succeeded) ---
printf '%s\n' "$REMOTE_SHA" > "$SHA_CACHE"

log "pulled OK to $REMOTE_SHA ($copied copied, $same already current, mode $MODE)"
say "pull: updated to ${REMOTE_SHA:0:7} ($copied copied, $same already current)"
exit 0
