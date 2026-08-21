#!/bin/bash
#
# push-to-github.sh
#
# Pushes daily email files to GitHub from a clean clone.
# ALWAYS clones from GitHub (never OneDrive — broken HEAD every time).
#
# Usage:
#   ./push-to-github.sh              # auto-detects date from daily-market-template.json
#   ./push-to-github.sh 040226       # explicit date (MMDDYY)
#   ./push-to-github.sh 040226 "Custom commit message"
#
# What it does:
#   1. Clones repo from GitHub to /tmp/daily-email-push
#   2. Sets git config + auth token
#   3. Copies today's generated files + ALL tooling (make-*.py, verify-*.js,
#      check-surfaces.sh, scripts/) + this script itself
#   4. Commits and pushes
#   5. Cleans up
#
# Chart scripts (make-*.py) are copied EVERY run, not just when new. They are
# git-tracked but are not date-stamped, so before 2026-08-18 they sat outside
# this curated list: a new or edited one had to be pushed by hand via a separate
# /tmp clone, and if that was forgotten the Mac launchd auto-pull silently
# reverted it (that is how the 08/07 copper rebuild was lost). Copying them here
# also makes an ACCIDENTAL OVERWRITE visible: reusing an existing filename for a
# different chart shows up as `M` in the staged-changes list below, and the
# script now calls that out explicitly instead of leaving it as a one-character
# tell. (On 08/18 make-gdp-chart.py, a 06/26 BEA quarterly-GDP chart, was
# clobbered by a new world-GDP chart that reused the name.)
#
# verify-*.js, check-surfaces.sh and scripts/ were added for the same reason
# (2026-08-18): they are git-tracked, not date-stamped, and were therefore
# exposed to the same silent revert. Adding them recovered
# scripts/build-interactive-chart.py, which had never been pushed.
# Deliberately NOT copied: broadcast-backstop.js and daily-report-skill/ are
# gitignored on purpose so the Mac/VPS git-sync leaves them alone (CLAUDE.md
# "Stage 4.5b"). cms-content.json and daily-report.json ARE copied (2026-08-21):
# the HarvRealtor app feed is built from the former and IS the latter.

set -e

REPO="fremontrealtyexperts-510/RealtyExperts-Daily-Email"
SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
DST_DIR="/tmp/daily-email-push"

# --- Determine date ---
if [ -n "$1" ]; then
  DATE_STR="$1"
else
  DATE_STR=$(python3 -c "import json; d=json.load(open('$SRC_DIR/daily-market-template.json')); print(d['date'].replace('/',''))")
fi

echo "📅 Date: $DATE_STR"

# --- Get GitHub token ---
GH_TOKEN=$(gh auth token -u fremontrealtyexperts-510 2>/dev/null)
if [ -z "$GH_TOKEN" ]; then
  echo "❌ Could not get GitHub token for fremontrealtyexperts-510"
  echo "   Run: gh auth login -u fremontrealtyexperts-510"
  exit 1
fi
echo "🔑 GitHub token acquired"

# --- Clone from GitHub (NEVER from OneDrive) ---
rm -rf "$DST_DIR"
echo "📦 Cloning from GitHub..."
cd /tmp
git clone "https://x-access-token:${GH_TOKEN}@github.com/${REPO}.git" "$DST_DIR" 2>&1 | tail -1
cd "$DST_DIR"

# --- Configure git ---
git config user.name "User8888-Level3"
git config user.email "fremontrealtyexperts510@gmail.com"
echo "⚙️  Git configured"

# --- Copy files ---
FILES_COPIED=0

copy_if_exists() {
  if [ -f "$SRC_DIR/$1" ]; then
    cp "$SRC_DIR/$1" "$DST_DIR/$1"
    FILES_COPIED=$((FILES_COPIED + 1))
  fi
}

# Always copy these
# This script itself: without this line an edit to the curated list is reverted
# by the Mac launchd auto-pull, i.e. the fix silently undoes itself.
copy_if_exists "push-to-github.sh"
copy_if_exists "check-surfaces.sh"
copy_if_exists "daily-market-template.json"
copy_if_exists "index.html"
copy_if_exists "daily-market-glance-${DATE_STR}.html"
copy_if_exists "daily-market-glance-${DATE_STR}-stripped.html"
copy_if_exists "RE-Daily-1-${DATE_STR}.png"
copy_if_exists "RE-Daily-2-${DATE_STR}.png"
# harvrealtor.com CMS artifacts — alameda-chart-*.js MUST be hosted on Pages so the
# InCom landing/blog body can load the interactive chart via <script src> (Drupal
# strips inline <script>, so the chart data has to live in an external file).
copy_if_exists "alameda-chart-${DATE_STR}.js"
copy_if_exists "alameda-interactive-${DATE_STR}.html"
copy_if_exists "cms-meta-${DATE_STR}.txt"
# harvrealtor.net /live-inventory feed — fetched client-side from GitHub Pages
copy_if_exists "live-inventory.json"
# harvrealtor.net /inventory-history feed — long-run daily series (same origin)
copy_if_exists "inventory-history.json"
# HarvRealtor APP feed + harvrealtor.net/today (added 2026-08-21): ONE file,
# rewritten every run by generate-app-report.js, so nothing accumulates. The
# app reads it from Pages instead of the REALTY EXPERTS email or the .com RSS.
copy_if_exists "daily-report.json"
# ...and its generator, so the VPS twin (git auto-pull) has the script too.
copy_if_exists "generate-app-report.js"
# The HarvRealtor-voice .com body the app feed is built from. Pushed so the
# public copy is current (it sat at 07/31 until 2026-08-21).
copy_if_exists "cms-content.json"

# Copy QR code (glob for note-qr-*.png that's newer than 1 hour)
for qr in "$SRC_DIR"/note-qr-*.png; do
  if [ -f "$qr" ]; then
    BASENAME=$(basename "$qr")
    # Only copy if not already on remote
    if [ ! -f "$DST_DIR/$BASENAME" ]; then
      cp "$qr" "$DST_DIR/$BASENAME"
      FILES_COPIED=$((FILES_COPIED + 1))
    fi
  fi
done

# Chart scripts — copy ALL of them every run (see header note). Unlike the QR
# glob above these are copied unconditionally, so local edits propagate instead
# of being skipped because the filename already exists on the remote.
CHART_SCRIPTS=0
for mk in "$SRC_DIR"/make-*.py; do
  if [ -f "$mk" ]; then
    cp "$mk" "$DST_DIR/$(basename "$mk")"
    CHART_SCRIPTS=$((CHART_SCRIPTS + 1))
    FILES_COPIED=$((FILES_COPIED + 1))
  fi
done
echo "📊 Chart scripts copied: $CHART_SCRIPTS"

# Verifier scripts — same rationale as make-*.py above.
VERIFY_SCRIPTS=0
for v in "$SRC_DIR"/verify-*.js; do
  if [ -f "$v" ]; then
    cp "$v" "$DST_DIR/$(basename "$v")"
    VERIFY_SCRIPTS=$((VERIFY_SCRIPTS + 1))
    FILES_COPIED=$((FILES_COPIED + 1))
  fi
done
echo "🔎 Verifier scripts copied: $VERIFY_SCRIPTS"

# scripts/ helper directory (cron wrappers, launchd plist, chart builders).
# Copy-only: files present on the remote but not locally are left alone, so this
# can never delete anything. scripts/README.md is gitignored and stays untracked.
if [ -d "$SRC_DIR/scripts" ]; then
  mkdir -p "$DST_DIR/scripts"
  cp -R "$SRC_DIR/scripts/." "$DST_DIR/scripts/"
  SCRIPTS_N=$(find "$SRC_DIR/scripts" -type f | wc -l | tr -d ' ')
  FILES_COPIED=$((FILES_COPIED + SCRIPTS_N))
  echo "🗂  scripts/ files copied: $SCRIPTS_N"
fi

echo "📋 Copied $FILES_COPIED files"

# --- Stage and check ---
git add -A
CHANGES=$(git status --short)
if [ -z "$CHANGES" ]; then
  echo "⚠️  No changes to commit"
  rm -rf "$DST_DIR"
  exit 0
fi

echo "📝 Staged changes:"
echo "$CHANGES"

# A MODIFIED (not added) chart script is either a deliberate edit or an
# accidental clobber of a different chart that already owned that filename.
# Surface it loudly rather than leaving it as an `M` to be spotted by eye.
MODIFIED_CHARTS=$(echo "$CHANGES" | grep -E '^ ?M[ M]? +(make-.*\.py|verify-.*\.js|check-surfaces\.sh|scripts/.*)$' | awk '{print $NF}' || true)
if [ -n "$MODIFIED_CHARTS" ]; then
  echo ""
  echo "⚠️  EXISTING tooling file(s) MODIFIED (not new):"
  for f in $MODIFIED_CHARTS; do
    echo "      $f"
  done
  echo "    If you meant to edit these, carry on. If you just created a NEW file"
  echo "    and expected 'A', you have overwritten something that already used"
  echo "    that name. Recover it and rename yours:"
  echo "      git log --oneline -- <file>            # find the prior commit"
  echo "      git show <sha>:<file> > <file>         # restore it"
  echo ""
fi

# --- Commit ---
COMMIT_MSG="${2:-Daily email - $(echo $DATE_STR | sed 's/\(..\)\(..\)\(..\)/\1\/\2\/\3/'): Add Agent Hub note + QR code}"

git commit -m "$(cat <<EOF
${COMMIT_MSG}

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"

# --- Push ---
echo "🚀 Pushing to GitHub..."
git push origin main 2>&1

echo ""
echo "✅ Pushed successfully!"
echo "🌐 Web: https://${REPO/\//.github.io/}/daily-market-glance-${DATE_STR}.html"

# --- Cleanup ---
rm -rf "$DST_DIR"
echo "🧹 Cleaned up /tmp clone"
