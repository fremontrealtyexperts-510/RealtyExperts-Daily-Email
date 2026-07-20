#!/usr/bin/env bash
# Periodic background pull for RealtyExperts-Daily-Email on VPS.
# Runs from cron every 15 min. Quiet — only logs when something changed or errored.
#
# 2026-07-20: added self-healing for GENERATED data files.
#   Both the Mac and the VPS regenerate inventory-history.json / live-inventory.json,
#   and both are tracked, so a conflict there is inevitable rather than exceptional.
#   On 07-18 one such conflict left the index in an unmerged state; every pull for the
#   next 2 days then died with "Pulling is not possible because you have unmerged
#   files" (181 consecutive failures) and the VPS silently drifted 11 commits behind.
#   Nobody reads .git-sync.log, so it failed invisibly.
#
#   Rule now: if EVERY unmerged path is in GENERATED_FILES, take origin's copy and
#   carry on (the Mac authors these; the VPS only consumes them). If ANYTHING else is
#   conflicted it is a real source conflict, so leave it alone and log loudly.

REPO_DIR="$HOME/workspaces/RealtyExperts-Daily-Email"
LOG="$REPO_DIR/.git-sync.log"
DEPLOY_KEY="$HOME/.ssh/realty_email_deploy"
GIT_SSH="ssh -i $DEPLOY_KEY -o IdentitiesOnly=yes"

# Machine-generated, safe to overwrite from origin. Keep this list tight.
GENERATED_FILES="inventory-history.json live-inventory.json"

log() { echo "[$(date -u +%FT%TZ)] $*" >> "$LOG"; }

cd "$REPO_DIR" || { log "ERROR: cd failed"; exit 1; }

# Reset any generated file that is currently unmerged, but ONLY if the generated set
# fully covers the conflict. Returns 0 if the tree is clear to pull, 1 otherwise.
heal_generated_conflicts() {
  local unmerged
  unmerged=$(git diff --name-only --diff-filter=U)
  [ -z "$unmerged" ] && return 0

  local leftover="$unmerged"
  for g in $GENERATED_FILES; do
    leftover=$(printf '%s\n' "$leftover" | grep -vx "$g")
  done
  if [ -n "$leftover" ]; then
    log "ERROR: source conflict needs a human: $(printf '%s' "$leftover" | tr '\n' ' ')"
    return 1
  fi

  for g in $GENERATED_FILES; do
    if printf '%s\n' "$unmerged" | grep -qx "$g"; then
      git checkout origin/main -- "$g" 2>>"$LOG" && git add "$g" 2>>"$LOG"
    fi
  done
  log "auto-healed generated-file conflict: $(printf '%s' "$unmerged" | tr '\n' ' ')"
  return 0
}

GIT_SSH_COMMAND="$GIT_SSH" git fetch origin --quiet 2>>"$LOG" || {
  log "ERROR: fetch failed"; exit 1;
}

# Clear a pre-existing jam (e.g. left by an earlier aborted pull) before comparing.
heal_generated_conflicts || exit 1

LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})
[ "$LOCAL" = "$REMOTE" ] && exit 0

if GIT_SSH_COMMAND="$GIT_SSH" git pull --rebase --autostash --quiet origin main 2>>"$LOG"; then
  log "pulled $LOCAL..$REMOTE OK"
  exit 0
fi

# First attempt failed. If it was only generated files, heal and retry once.
if heal_generated_conflicts; then
  git rebase --continue >/dev/null 2>>"$LOG" || git rebase --abort >/dev/null 2>&1 || true
  if GIT_SSH_COMMAND="$GIT_SSH" git pull --rebase --autostash --quiet origin main 2>>"$LOG"; then
    log "pulled $LOCAL..$REMOTE OK (after auto-heal)"
    exit 0
  fi
fi

log "ERROR: pull-rebase failed (may need manual resolution)"
exit 1
