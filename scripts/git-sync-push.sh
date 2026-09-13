#!/usr/bin/env bash
# git-sync-push.sh — push VPS-side handoff files to GitHub (the VPS->Mac half of the git sync).
#
# SCOPED ON PURPOSE — commits ONLY an allowlist, NEVER `git add -A`.
# The workspace's generated data (inventory-history.json, assistant-inventory.json,
# alameda-interactive-*.html, *.bak) is authored on the MAC and only CONSUMED on the VPS.
# Pushing it from here would fight git-sync-pull.sh's generated-file heal and the Mac's
# regeneration. So this script touches only the handoff file(s) below.
#
# Usage: git-sync-push.sh [extra-file ...]   (extra paths appended to the default allowlist)
# Pairs with the existing pull side: scripts/git-sync-pull.sh (cron, untouched).
#
# 2026-08-11: pull-rebase guard added, so this is safe to run from cron.
#   git-sync-pull.sh (cron */15) owns integration: it runs `git pull --rebase --autostash`
#   against a working tree that is permanently dirty with generated files, and its own
#   header records how badly that goes when it has to replay local commits — conflicted
#   autostash pops, orphaned stashes, 181 consecutive silent failures, 11 commits of drift.
#   If this script commits onto a STALE base, the push is rejected, the commit stays local,
#   and every later pull must replay it — one more replayed commit per failed run. That is
#   the jam this guard exists to prevent.
#   Rule: this script NEVER integrates. It does not fetch-and-merge, rebase, or stash. It
#   acts only when the repo is quiet and already up to date with origin; otherwise it exits
#   0 having changed nothing and leaves integration to the pull cron. A skipped run costs
#   nothing — the next one pushes.

set -u

REPO_DIR="$HOME/workspaces/RealtyExperts-Daily-Email"
DEPLOY_KEY="$HOME/.ssh/realty_email_deploy"
LOG="$REPO_DIR/.git-sync-push.log"
export GIT_SSH_COMMAND="ssh -i $DEPLOY_KEY -o IdentitiesOnly=yes"

ALLOW=( "RealtyExperts-Daily-Email-STATUS.md" )
[ "$#" -gt 0 ] && ALLOW+=( "$@" )

log() { echo "[$(date -u +%FT%TZ)] $*" >> "$LOG"; }
cd "$REPO_DIR" || { log "ERROR: cd failed"; exit 1; }

# Single-flight, so a cron'd push cannot stack on itself. Lock lives outside the repo:
# the pull cron owns this working tree and must not see stray untracked files.
exec 9>"$HOME/.cache/realty-git-sync-push.lock"
if ! flock -n 9; then
  log "skip: another push in flight"; exit 0
fi

# Guard 1 — never touch the repo while the pull cron is mid-integration. Committing into
# an in-progress rebase, or on top of unmerged paths, is how the index gets wedged.
if [ -d .git/rebase-merge ] || [ -d .git/rebase-apply ] || [ -e .git/MERGE_HEAD ]; then
  log "skip: rebase/merge in progress"; exit 0
fi
if [ -n "$(git diff --name-only --diff-filter=U)" ]; then
  log "skip: unmerged paths present (pull cron heals these)"; exit 0
fi

# Guard 2 — never commit onto a stale base. Proceed only when origin/main is an ancestor
# of main (up to date, or ahead with unpushed commits). Behind or diverged => the pull
# cron integrates first and the next run pushes cleanly.
if ! git fetch origin --quiet 2>>"$LOG"; then
  log "skip: fetch failed (offline?)"; exit 0
fi
LOCAL=$(git rev-parse main 2>/dev/null) || { log "ERROR: no main"; exit 1; }
REMOTE=$(git rev-parse origin/main 2>/dev/null) || { log "ERROR: no origin/main"; exit 1; }
BASE=$(git merge-base main origin/main 2>/dev/null) || { log "ERROR: no merge-base"; exit 1; }
if [ "$BASE" != "$REMOTE" ]; then
  log "skip: main is behind/diverged from origin (local=${LOCAL:0:7} origin=${REMOTE:0:7}); pull cron will integrate"
  exit 0
fi

# Stage ONLY existing allowlisted paths.
staged=0
for f in "${ALLOW[@]}"; do
  [ -e "$REPO_DIR/$f" ] || continue
  git add -- "$f" 2>>"$LOG" && staged=1
done
if [ "$staged" -eq 0 ]; then log "nothing to stage (no allowlisted files present)"; exit 0; fi

# Commit ONLY the allowlisted paths (pathspec commit ignores any other index state).
if git diff --cached --quiet -- "${ALLOW[@]}"; then
  log "no changes in allowlisted paths"; exit 0
fi
git commit -m "vps handoff: update STATUS ($(date -u +%FT%TZ))" -- "${ALLOW[@]}" >>"$LOG" 2>&1 \
  || { log "ERROR: commit failed"; exit 1; }

if git push origin main >>"$LOG" 2>&1; then
  log "pushed OK -> $(git rev-parse --short HEAD)"
  exit 0
else
  log "ERROR: push failed"
  exit 1
fi
