#!/bin/bash
#
# refresh-live-inventory.sh
#
# Hands-off refresher for the harvrealtor.net live-inventory feed (homepage
# pulse band + /live-inventory page) and its harvbalu.homes assistant
# derivative. Regenerates live-inventory.json from the NEWEST dated
# "MLS_Defined_Spread_Sheet_4- MMDDYY" file in Google Drive and publishes to
# GitHub Pages, but ONLY when something is actually newer than Pages, so
# re-runs on an unchanged Drive are silent no-ops (no commit spam):
#   - live-inventory.json (+ inventory-history.json) when the export date moved
#   - assistant-inventory.json whenever its data_date is newer than Pages', even
#     if the daily email already published the day's live feed (before
#     2026-09-13 that case exited early and the assistant feed sat at 09/02)
#
# Runs from Mac launchd (com.harvbalu.live-inventory-refresh, 9:00 / 11:00 /
# 15:00 PT) through a LOCAL wrapper, ~/Library/Application Support/
# harvbalu-live-inventory/run-refresh.sh, which sets LIVE_INV_SRC_DIR to this
# Drive folder. launchd must not read a script on the Drive mount: when the
# File Provider wedges, bash fails with exit 126 "Resource deadlock avoided"
# and every run is lost (Sep 11 2026). The VPS backstop cron (9:30 / 11:30 /
# 15:30) runs this same file from its git clone and publishes with the SSH
# deploy key. Safe to run by hand any time:
#   ./refresh-live-inventory.sh
#
# The manual daily-email flow (run-daily.js Stage 3 / update-inventory.js 6b)
# still publishes the same files; whichever runs first wins, the other no-ops.
#
# Failure posture: generate-live-inventory.js has its own sanity gates and
# refuses to write a bad file; every file is validated in a local stage dir
# before it can be committed; any failure exits non-zero WITHOUT touching the
# published feed, and the site keeps serving yesterday's data with its honest
# date label.

set -e

REPO="fremontrealtyexperts-510/RealtyExperts-Daily-Email"
PAGES_BASE="https://fremontrealtyexperts-510.github.io/RealtyExperts-Daily-Email"
SELF="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
SRC_DIR="${LIVE_INV_SRC_DIR:-$(cd "$(dirname "$0")" && pwd)}"
STAGE="${LIVE_INV_STAGE:-${TMPDIR:-/tmp}/live-inventory-stage}"
DST_DIR="/tmp/live-inventory-refresh-push"

# retry N cmd...: Drive reads fail transiently (EDEADLK) while files hydrate
retry() { local n=$1 i=1; shift; until "$@"; do [ $i -ge $n ] && return 1; i=$((i + 1)); sleep 5; done; }
valid_json() { [ -s "$1" ] && python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$1" 2>/dev/null; }
json_field() { python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get(sys.argv[2],''))" "$1" "$2" 2>/dev/null || echo ""; }
pages_field() { curl -sf --max-time 20 "$PAGES_BASE/$1?t=$(date +%s)" | python3 -c "import json,sys; print(json.load(sys.stdin).get(sys.argv[1],''))" "$2" 2>/dev/null || echo ""; }
# newer A B: A (MM/DD/YY) is a real date and later than B (or B is unknown)
ymd() { case "$1" in ??/??/??) echo "${1:6:2}${1:0:2}${1:3:2}" ;; *) echo "" ;; esac; }
newer() { local a b; a=$(ymd "$1"); b=$(ymd "$2"); [ -n "$a" ] && { [ -z "$b" ] || [ "$a" \> "$b" ]; }; }

cd "$SRC_DIR"
mkdir -p "$STAGE"
rm -f "$STAGE"/*.json

echo "[$(date '+%Y-%m-%d %H:%M:%S')] refresh-live-inventory: start"

# --- What is already published? (empty if Pages is unreachable) ---
PUBLISHED_DATE=$(pages_field live-inventory.json date)
PUBLISHED_ASSIST=$(pages_field assistant-inventory.json data_date)
echo "Published date: ${PUBLISHED_DATE:-unknown} (assistant: ${PUBLISHED_ASSIST:-unknown})"

# --- Regenerate from the newest Drive export (sanity-gated) ---
retry 3 node generate-live-inventory.js

# --- Stage and validate locally; nothing is read back from Drive at push time ---
retry 4 cp "$SRC_DIR/live-inventory.json" "$STAGE/live-inventory.json"
if ! valid_json "$STAGE/live-inventory.json"; then
  echo "ERROR: staged live-inventory.json is empty or not JSON, not publishing"
  exit 1
fi
HAVE_HISTORY=0
if [ -f "$SRC_DIR/inventory-history.json" ]; then
  if retry 4 cp "$SRC_DIR/inventory-history.json" "$STAGE/inventory-history.json" && valid_json "$STAGE/inventory-history.json"; then
    HAVE_HISTORY=1
  else
    echo "WARN: inventory-history.json unreadable, publishing without it"
    rm -f "$STAGE/inventory-history.json"
  fi
fi

# Compact derivative for the harvbalu.homes AI assistant (n8n get_inventory
# tool), derived IN the stage dir. Guarded: a derive failure must never block
# the main feed publish.
HAVE_ASSIST=0
if retry 4 cp "$SRC_DIR/derive-assistant-inventory.py" "$STAGE/derive-assistant-inventory.py" \
  && (cd "$STAGE" && python3 derive-assistant-inventory.py) \
  && valid_json "$STAGE/assistant-inventory.json"; then
  HAVE_ASSIST=1
  echo "assistant-inventory.json derived"
else
  echo "WARN: derive-assistant-inventory.py failed, publishing main feed only"
  rm -f "$STAGE/assistant-inventory.json"
fi

NEW_DATE=$(json_field "$STAGE/live-inventory.json" date)
NEW_ASSIST=""
[ "$HAVE_ASSIST" = 1 ] && NEW_ASSIST=$(json_field "$STAGE/assistant-inventory.json" data_date)
echo "Generated date: $NEW_DATE (assistant: ${NEW_ASSIST:-none})"

if [ -z "$NEW_DATE" ]; then
  echo "ERROR: generated file has no date, not publishing"
  exit 1
fi

LIVE_MOVED=0
ASSIST_MOVED=0
if newer "$NEW_DATE" "$PUBLISHED_DATE"; then LIVE_MOVED=1; fi
if [ "$HAVE_ASSIST" = 1 ] && newer "$NEW_ASSIST" "$PUBLISHED_ASSIST"; then ASSIST_MOVED=1; fi

if [ "$LIVE_MOVED" = 0 ] && [ "$ASSIST_MOVED" = 0 ]; then
  echo "Feed already current ($NEW_DATE, assistant ${NEW_ASSIST:-n/a}), nothing to publish"
  exit 0
fi

# --- Publish from a clean /tmp clone (never the Drive .git) ---
# Auth: prefer gh (Mac launchd path), with the token in an env-scoped header so
# it never lands in a clone URL or .git/config; fall back to the SSH deploy key
# when gh is absent (VPS backstop path, gh is not installed there).
GH_TOKEN=""
if command -v gh >/dev/null 2>&1; then
  GH_TOKEN=$(gh auth token -u fremontrealtyexperts-510 2>/dev/null || echo "")
fi
DEPLOY_KEY="$HOME/.ssh/realty_email_deploy"
if [ -n "$GH_TOKEN" ]; then
  export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0="http.https://github.com/.extraheader"
  export GIT_CONFIG_VALUE_0="AUTHORIZATION: basic $(printf 'x-access-token:%s' "$GH_TOKEN" | base64 | tr -d '\n')"
  CLONE_URL="https://github.com/${REPO}.git"
elif [ -f "$DEPLOY_KEY" ]; then
  export GIT_SSH_COMMAND="ssh -i $DEPLOY_KEY -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"
  CLONE_URL="git@github.com:${REPO}.git"
else
  echo "ERROR: no gh token and no deploy key at $DEPLOY_KEY, cannot publish"
  exit 1
fi

rm -rf "$DST_DIR"
git clone --depth=1 "$CLONE_URL" "$DST_DIR" 2>&1 | tail -1
cd "$DST_DIR"
git config user.name "User8888-Level3"
git config user.email "fremontrealtyexperts510@gmail.com"

PUBLISH=""
if [ "$LIVE_MOVED" = 1 ]; then
  PUBLISH="live-inventory.json"
  # long-run daily series for harvrealtor.net /inventory-history (upserted by
  # generate-live-inventory.js on the same run that refreshed the live feed)
  [ "$HAVE_HISTORY" = 1 ] && PUBLISH="$PUBLISH inventory-history.json"
fi
# compact AI-assistant derivative (harvbalu.homes chatbot tool)
[ "$ASSIST_MOVED" = 1 ] && PUBLISH="$PUBLISH assistant-inventory.json"
for f in $PUBLISH; do
  cp "$STAGE/$f" "$DST_DIR/$f"
  if ! valid_json "$DST_DIR/$f"; then
    echo "ERROR: $f is empty or not JSON in the push clone, refusing to publish"
    exit 1
  fi
done
# keep the refresher itself versioned so the VPS picks it up via git auto-pull
cp "$SELF" "$DST_DIR/refresh-live-inventory.sh"
cp "$STAGE/derive-assistant-inventory.py" "$DST_DIR/derive-assistant-inventory.py" 2>/dev/null || true
chmod +x "$DST_DIR/refresh-live-inventory.sh"

git add $PUBLISH refresh-live-inventory.sh derive-assistant-inventory.py
if [ -z "$(git status --short)" ]; then
  echo "No changes after copy, nothing to publish"
  cd /
  rm -rf "$DST_DIR"
  exit 0
fi

if [ "$LIVE_MOVED" = 1 ]; then
  git commit -q -m "live-inventory: refresh feed to $NEW_DATE (auto)"
else
  git commit -q -m "assistant-inventory: publish $NEW_ASSIST (auto)"
fi
# the daily-email push can land between our clone and push; rebase once
git push -q origin main || { git pull -q --rebase origin main && git push -q origin main; }
cd /
rm -rf "$DST_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Published:$PUBLISH (live $NEW_DATE, assistant ${NEW_ASSIST:-n/a})"

# Mirror the fresh assistant file back to Drive so push-to-github.sh never
# sees a stale copy there. Mac only (on the VPS SRC_DIR is a git working tree
# that must stay clean for auto-pull), best effort, LAST.
if [ "$ASSIST_MOVED" = 1 ] && [ "$(uname)" = Darwin ]; then
  cp "$STAGE/assistant-inventory.json" "$SRC_DIR/assistant-inventory.json" 2>/dev/null \
    || echo "WARN: could not mirror assistant-inventory.json back to Drive"
fi

# --- Rebuild harvrealtor.net so its PRERENDERED html carries this feed ---
# The .net routes are prerendered at Vercel build time and served from the
# edge until the next deploy, so without this the first paint (and every
# scraper that does not run JS) keeps showing the feed from the last deploy.
# Never fatal: the trigger always exits 0 and no-ops when unconfigured.
if [ "$LIVE_MOVED" = 1 ]; then
  "$SRC_DIR/trigger-net-rebuild.sh" "$NEW_DATE" || true
fi
