#!/bin/bash
# launchd entry point for com.harvbalu.realty-broadcast-backstop (added Sunday,
# September 13, 2026, PT). Everything this job EXECUTES lives OFF the Google Drive
# mount on purpose: under launchd the Drive File Provider fails reads with EDEADLK
# (Node "Unknown system error -11"), so the Mac pass had been failing every run.
# See reference-mac-launchd-drive-edeadlk in the Daily-Email project memory.
#
# How: keeps a local clone of fremontrealtyexperts-510/RealtyExperts-Daily-Email in
# ./src, hard-reset to origin/main on every run, then copies from Drive the files
# git does not carry: broadcast-backstop.js (gitignored; it lives only on Drive and
# the VPS) and .env (ADMIN_TOKEN). If Drive is unreadable it keeps the last good
# copies. It then runs the backstop from the clone, which reads the same
# GitHub copy of daily-market-template.json the VPS twin (10:45 / 1:45 / 4:30 PT)
# reads. All four no-double-send gates live in broadcast-backstop.js, unchanged.
set -u

DRIVE="$HOME/Library/CloudStorage/GoogleDrive-harvinder.balu@gmail.com/My Drive/ClaudeCode/RealtyExperts-Daily-Email"
HERE="$HOME/Library/Application Support/harvbalu-broadcast-backstop"
SRC="$HERE/src"
REPO_URL="https://github.com/fremontrealtyexperts-510/RealtyExperts-Daily-Email.git"
ts() { date '+%Y-%m-%d %H:%M:%S'; }

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

for f in broadcast-backstop.js .env; do
  for i in 1 2 3; do
    if cp "$DRIVE/$f" "$SRC/$f.new" 2>/dev/null && [ -s "$SRC/$f.new" ]; then
      chmod 600 "$SRC/$f.new"; mv "$SRC/$f.new" "$SRC/$f"; break
    fi
    sleep 5
  done
  rm -f "$SRC/$f.new"
  [ -s "$SRC/$f" ] || { echo "[$(ts)] ERROR: no local copy of $f (Drive unreadable)" >&2; exit 1; }
done

cd "$SRC" && exec /opt/homebrew/bin/node broadcast-backstop.js
