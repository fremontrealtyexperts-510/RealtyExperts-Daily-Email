#!/bin/bash
# launchd entry point for com.harvbalu.live-inventory-refresh (added Sunday,
# September 13, 2026, PT). Everything this job EXECUTES lives OFF the Google
# Drive mount on purpose: under launchd the Drive File Provider fails reads
# with EDEADLK (bash exit 126 "Resource deadlock avoided", Node "Unknown system
# error -11"), and that silently stopped every run after Friday, September 11,
# 2026 9:00 AM PT. See reference-mac-launchd-drive-edeadlk in the Daily-Email
# project memory.
#
# How: keeps a local clone of fremontrealtyexperts-510/RealtyExperts-Daily-Email
# in ./src, hard-reset to origin/main on every run (the repo is canonical for
# the code), copies the two gitignored secrets (SA key, .env) from Drive when
# Drive is readable and otherwise keeps the last good local copies, then runs
# the clone's refresh-live-inventory.sh. Edit the scripts in the repo, not here.
set -u

DRIVE="$HOME/Library/CloudStorage/GoogleDrive-harvinder.balu@gmail.com/My Drive/ClaudeCode/RealtyExperts-Daily-Email"
HERE="$HOME/Library/Application Support/harvbalu-live-inventory"
SRC="$HERE/src"
REPO_URL="https://github.com/fremontrealtyexperts-510/RealtyExperts-Daily-Email.git"
ts() { date '+%Y-%m-%d %H:%M:%S'; }
mkdir -p "$HERE/stage"

# gh token rides in an env-scoped header, never in the clone URL or .git/config
TOK=$(gh auth token -u fremontrealtyexperts-510 2>/dev/null || echo "")
if [ -n "$TOK" ]; then
  export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0="http.https://github.com/.extraheader"
  export GIT_CONFIG_VALUE_0="AUTHORIZATION: basic $(printf 'x-access-token:%s' "$TOK" | base64 | tr -d '\n')"
fi

if [ -d "$SRC/.git" ]; then
  if git -C "$SRC" fetch -q --depth=1 origin main && git -C "$SRC" reset -q --hard origin/main; then :; else
    echo "[$(ts)] WARN: could not update the local clone, running the last good checkout" >&2
  fi
else
  rm -rf "$SRC"
  git clone -q --depth=1 "$REPO_URL" "$SRC" || { echo "[$(ts)] ERROR: initial clone failed" >&2; exit 1; }
fi

for f in harvrealtor-0819122f6566-google-drive.json .env; do
  for i in 1 2 3; do
    if cp "$DRIVE/$f" "$SRC/$f.new" 2>/dev/null && [ -s "$SRC/$f.new" ]; then
      chmod 600 "$SRC/$f.new"; mv "$SRC/$f.new" "$SRC/$f"; break
    fi
    sleep 5
  done
  rm -f "$SRC/$f.new"
  [ -s "$SRC/$f" ] || echo "[$(ts)] WARN: no local copy of $f yet (Drive unreadable)" >&2
done

export LIVE_INV_SRC_DIR="$SRC"
export LIVE_INV_STAGE="$HERE/stage"
export LIVE_INV_MIRROR_DIR="$DRIVE"
exec /bin/bash "$SRC/refresh-live-inventory.sh"
