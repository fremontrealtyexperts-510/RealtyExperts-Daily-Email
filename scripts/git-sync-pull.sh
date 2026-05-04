#!/usr/bin/env bash
# Periodic background pull for RealtyExperts-Daily-Email on VPS.
# Runs from cron every 15 min. Quiet — only logs when something changed or errored.

REPO_DIR="$HOME/workspaces/RealtyExperts-Daily-Email"
LOG="$REPO_DIR/.git-sync.log"
DEPLOY_KEY="$HOME/.ssh/realty_email_deploy"

cd "$REPO_DIR" || { echo "[$(date -u +%FT%TZ)] ERROR: cd failed" >> "$LOG"; exit 1; }

# Fetch quietly
GIT_SSH_COMMAND="ssh -i $DEPLOY_KEY -o IdentitiesOnly=yes" \
  git fetch origin --quiet 2>>"$LOG" || {
    echo "[$(date -u +%FT%TZ)] ERROR: fetch failed" >> "$LOG"
    exit 1
  }

LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})

# Nothing to do
[ "$LOCAL" = "$REMOTE" ] && exit 0

# Pull with rebase + autostash so workflow-in-progress edits get tucked aside
GIT_SSH_COMMAND="ssh -i $DEPLOY_KEY -o IdentitiesOnly=yes" \
  git pull --rebase --autostash --quiet origin main 2>>"$LOG" && \
  echo "[$(date -u +%FT%TZ)] pulled $LOCAL..$REMOTE OK" >> "$LOG" || {
    echo "[$(date -u +%FT%TZ)] ERROR: pull-rebase failed (may need manual resolution)" >> "$LOG"
    exit 1
  }
