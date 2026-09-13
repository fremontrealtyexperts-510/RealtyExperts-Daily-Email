#!/bin/bash
# launchd entry point for com.harvbalu.realty-email-pull (added Sunday, September 13,
# 2026, PT). The job keeps the Drive workspace in step with GitHub. It used to run
# pull-from-github.sh straight off the Drive mount and rsync the whole repo into it;
# under launchd the Drive File Provider fails those reads and writes with EDEADLK, so
# it had not completed a pull since 2026-08-12.
#
# How: keeps a partial clone of fremontrealtyexperts-510/RealtyExperts-Daily-Email in
# ./repo, copies the clone's pull-from-github.sh OUT of the clone (the script resets
# the clone, and bash must not run a file that is being rewritten), and runs it with
# the clone, lock state, SHA cache and log all on local disk. Drive is only the copy
# TARGET, and only for files GitHub actually changed.
set -u

DRIVE="$HOME/Library/CloudStorage/GoogleDrive-harvinder.balu@gmail.com/My Drive/ClaudeCode/RealtyExperts-Daily-Email"
HERE="$HOME/Library/Application Support/harvbalu-realty-email-pull"
CLONE="$HERE/repo"
REPO_URL="https://github.com/fremontrealtyexperts-510/RealtyExperts-Daily-Email.git"
ts() { date '+%Y-%m-%d %H:%M:%S'; }
mkdir -p "$HERE"

TOK=$(gh auth token -u fremontrealtyexperts-510 2>/dev/null || echo "")
if [ -n "$TOK" ]; then
  export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0="http.https://github.com/.extraheader"
  export GIT_CONFIG_VALUE_0="AUTHORIZATION: basic $(printf 'x-access-token:%s' "$TOK" | base64 | tr -d '\n')"
fi

if [ -d "$CLONE/.git" ]; then
  if git -C "$CLONE" fetch -q origin main && git -C "$CLONE" reset -q --hard FETCH_HEAD; then :; else
    echo "[$(ts)] WARN: could not update the local clone, using the last good pull script" >&2
  fi
else
  rm -rf "$CLONE"
  git clone -q --filter=blob:none "$REPO_URL" "$CLONE" || { echo "[$(ts)] ERROR: initial clone failed" >&2; exit 1; }
fi

if cp "$CLONE/pull-from-github.sh" "$HERE/pull-from-github.sh.new" 2>/dev/null \
  && /bin/bash -n "$HERE/pull-from-github.sh.new"; then
  mv "$HERE/pull-from-github.sh.new" "$HERE/pull-from-github.sh"
fi
rm -f "$HERE/pull-from-github.sh.new"
[ -s "$HERE/pull-from-github.sh" ] || { echo "[$(ts)] ERROR: no local pull-from-github.sh" >&2; exit 1; }

# First pass only: start from the Drive workspace's last good SHA, so the first pull
# copies just what GitHub changed since then instead of comparing every file.
if [ ! -s "$HERE/.git-pull-last-sha" ]; then
  cp "$DRIVE/.git-pull-last-sha" "$HERE/.git-pull-last-sha" 2>/dev/null || true
fi

export PULL_TARGET_DIR="$DRIVE" PULL_STATE_DIR="$HERE" PULL_REPO_DIR="$CLONE"
exec /bin/bash "$HERE/pull-from-github.sh"
