#!/usr/bin/env bash
#
# app-report-rates-cron.sh — VPS cron wrapper for sync-app-report-rates.mjs.
#
# WHY: the HarvRealtor app's Today's Report screen (App Store build 12) prints
# this feed's own rates block. The report is written at about 8:45 AM PT, before
# Mortgage News Daily posts the day's figure, so the tiles carried the previous
# business day all day: September 16's 7.24% under a September 17 masthead while
# the app's own Home hero read 7.19%. Harv caught it on launch day, 2026-09-17.
# Build 13 fixes it inside the app; this keeps the LIVE build right with no App
# Store review. Installed on the VPS rather than the Mac because the Mac sleeps
# and Harv asked for this to happen every day.
#
# WHERE IT RUNS: cron on the n8n VPS, whose system clock is already Pacific:
#   */15 6-16 * * 1-5  /bin/bash $HOME/workspaces/RealtyExperts-Daily-Email/scripts/app-report-rates-cron.sh
#
# ITS OWN CLONE, deliberately. This resets hard on every run, and the shared twin
# at ~/workspaces/RealtyExperts-Daily-Email carries generated files that the VPS's
# own crons are writing (inventory-history.json and friends). Resetting that twin
# would throw their work away mid-run.
#
# QUIET BY DESIGN: it publishes at most once or twice a day, and the log records
# only publishes and errors. .last-run is overwritten every tick, so "is this
# thing alive" is answerable without reading the log.

set -uo pipefail

REPO="git@github-realty-email:fremontrealtyexperts-510/RealtyExperts-Daily-Email.git"
WORK="$HOME/.app-report-rates"
CLONE="$WORK/repo"
LOG="$WORK/sync.log"
LAST="$WORK/.last-run"
DEPLOY_KEY="$HOME/.ssh/realty_email_deploy"

export GIT_SSH_COMMAND="ssh -i $DEPLOY_KEY -o IdentitiesOnly=yes"

mkdir -p "$WORK"
log() { echo "[$(date '+%F %T %Z')] $*" >> "$LOG"; }
stamp() { echo "[$(date '+%F %T %Z')] $*" > "$LAST"; }

if [ ! -d "$CLONE/.git" ]; then
  if ! git clone --quiet --depth 1 "$REPO" "$CLONE"; then
    log "ERROR clone failed"
    stamp "ERROR clone failed"
    exit 1
  fi
  log "cloned $REPO"
fi

cd "$CLONE" || { log "ERROR cd $CLONE failed"; exit 1; }

for attempt in 1 2 3; do
  # Always start from what is actually published. The daily pipeline pushes on
  # its own schedule, and a Stage 5 re-run rewrites this file from the template,
  # which puts the written pair back; the next tick simply re-corrects it.
  if ! git fetch --quiet --depth 1 origin main || ! git reset --quiet --hard FETCH_HEAD; then
    log "ERROR fetch or reset failed"
    stamp "ERROR fetch or reset failed"
    exit 1
  fi

  if ! out="$(node scripts/sync-app-report-rates.mjs 2>&1)"; then
    log "ERROR sync: $out"
    stamp "ERROR sync: $out"
    exit 1
  fi

  if git diff --quiet -- daily-report.json; then
    stamp "$out"
    exit 0
  fi

  git -c user.name='HarvRealtor app feed' \
      -c user.email='fremontrealtyexperts510@gmail.com' \
      commit --quiet -m "app-report: rate tiles to today's MND figure (auto)" -- daily-report.json \
    || { log "ERROR commit failed"; stamp "ERROR commit failed"; exit 1; }

  if git push --quiet origin HEAD:main; then
    log "PUBLISHED $out"
    stamp "PUBLISHED $out"
    # Keep the log from growing without bound. It gains a line or two a day.
    tail -n 2000 "$LOG" > "$LOG.trim" 2>/dev/null && mv "$LOG.trim" "$LOG"
    exit 0
  fi

  log "push raced on attempt $attempt, retrying from the new head"
done

log "ERROR could not push after 3 attempts"
stamp "ERROR could not push after 3 attempts"
exit 1
