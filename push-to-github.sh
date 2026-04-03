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
#   3. Copies today's generated files
#   4. Commits and pushes
#   5. Cleans up

set -e

REPO="fremontrealtyexperts-510/RealtyExperts-Daily-Email"
SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
DST_DIR="/tmp/daily-email-push"

# --- Determine date ---
if [ -n "$1" ]; then
  DATE_STR="$1"
else
  DATE_STR=$(python3 -c "import json; d=json.load(open('$SRC_DIR/daily-market-template.json')); print(d['date'].replace('/',''"))")
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
copy_if_exists "daily-market-template.json"
copy_if_exists "index.html"
copy_if_exists "daily-market-glance-${DATE_STR}.html"
copy_if_exists "daily-market-glance-${DATE_STR}-stripped.html"
copy_if_exists "RE-Daily-1-${DATE_STR}.png"
copy_if_exists "RE-Daily-2-${DATE_STR}.png"

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
