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
#
# 2026-08-07: two gaps in the above, both found jamming a live VPS.
#   (1) assistant-inventory.json is ALSO tracked and ALSO regenerated on the VPS by its
#       own cron, but was missing from GENERATED_FILES. When it was the conflicting
#       file the heal refused it as a "source conflict" and the sync hard-jammed.
#   (2) A --autostash POP can conflict even when the rebase itself SUCCEEDED. Git then
#       leaves the index unmerged, writes conflict markers into the working file, and
#       RETAINS the stash, yet `git pull` still exits 0. This script trusted that exit
#       code, so it logged "pulled OK" and walked away leaving invalid JSON on disk
#       until the next tick, while a fresh orphaned stash piled up every cycle (15 had
#       accumulated). Now: re-check for conflicts AFTER a "successful" pull, and drop
#       orphaned autostashes once they are provably generated-file-only.

REPO_DIR="$HOME/workspaces/RealtyExperts-Daily-Email"
LOG="$REPO_DIR/.git-sync.log"
DEPLOY_KEY="$HOME/.ssh/realty_email_deploy"
GIT_SSH="ssh -i $DEPLOY_KEY -o IdentitiesOnly=yes"

# Machine-generated, safe to overwrite from origin. Keep this list tight: adding a file
# here grants permission to silently discard the VPS's copy of it.
GENERATED_FILES="inventory-history.json live-inventory.json assistant-inventory.json"

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

# Drop leftover autostash entries from failed --autostash pops. Conservative on
# purpose: clears ONLY when EVERY entry is an autostash whose changes are confined to
# GENERATED_FILES. If anything else is stashed it may be real work, so it is kept and
# logged instead. A stash is not reachable from any branch, so dropping the wrong one
# would be an unrecoverable loss.
prune_orphan_autostashes() {
  local total i msg files leftover
  total=$(git stash list 2>/dev/null | wc -l | tr -d ' ')
  [ "${total:-0}" -eq 0 ] && return 0

  i=0
  while [ "$i" -lt "$total" ]; do
    msg=$(git stash list --format='%gs' 2>/dev/null | sed -n "$((i + 1))p")
    case "$msg" in
      *autostash*) ;;
      *) log "WARN: $total stash entries kept; stash@{$i} is not an autostash ($msg)"
         return 0 ;;
    esac

    files=$(git stash show --name-only "stash@{$i}" 2>/dev/null)
    leftover="$files"
    for g in $GENERATED_FILES; do
      leftover=$(printf '%s\n' "$leftover" | grep -vx "$g")
    done
    if [ -n "$(printf '%s' "$leftover" | tr -d '[:space:]')" ]; then
      log "WARN: $total stash entries kept; stash@{$i} touches non-generated files: $(printf '%s' "$leftover" | tr '\n' ' ')"
      return 0
    fi
    i=$((i + 1))
  done

  git stash clear 2>>"$LOG" \
    && log "dropped $total orphaned autostash entries (generated files only)"
}

GIT_SSH_COMMAND="$GIT_SSH" git fetch origin --quiet 2>>"$LOG" || {
  log "ERROR: fetch failed"; exit 1;
}

# Clear a pre-existing jam (e.g. left by an earlier aborted pull) before comparing.
heal_generated_conflicts || exit 1
prune_orphan_autostashes

LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})
[ "$LOCAL" = "$REMOTE" ] && exit 0

if GIT_SSH_COMMAND="$GIT_SSH" git pull --rebase --autostash --quiet origin main 2>>"$LOG"; then
  # Exit 0 is NOT proof of a clean tree: a conflicted autostash pop still reports
  # success while leaving unmerged paths and conflict markers behind. Verify.
  heal_generated_conflicts || { log "ERROR: post-pull source conflict needs a human"; exit 1; }
  prune_orphan_autostashes
  log "pulled $LOCAL..$REMOTE OK"
  exit 0
fi

# First attempt failed. If it was only generated files, heal and retry once.
if heal_generated_conflicts; then
  git rebase --continue >/dev/null 2>>"$LOG" || git rebase --abort >/dev/null 2>&1 || true
  if GIT_SSH_COMMAND="$GIT_SSH" git pull --rebase --autostash --quiet origin main 2>>"$LOG"; then
    heal_generated_conflicts || { log "ERROR: post-pull source conflict needs a human"; exit 1; }
    prune_orphan_autostashes
    log "pulled $LOCAL..$REMOTE OK (after auto-heal)"
    exit 0
  fi
fi

log "ERROR: pull-rebase failed (may need manual resolution)"
exit 1
