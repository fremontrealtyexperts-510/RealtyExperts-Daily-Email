#!/bin/bash
# ---------------------------------------------------------------------------
# Agent Hub scheduled-post sweep.  Added 2026-09-03 (PR 8 of scheduled posts).
#
# Pokes the notes-scheduler edge function every 5 minutes. That function does
# ALL the work: it stamps its own heartbeat, expires overdue rows, claims at
# most one due broadcast, and sends it.
#
# THIS SCRIPT CARRIES NO BUSINESS LOGIC, ON PURPOSE.  It decides nothing about
# what to send or when. The only reason it exists is that Supabase has no
# built-in timer. `broadcast-backstop.js` is the cautionary tale: it is
# gitignored, so a byte-identical copy lives on the Mac and on the VPS with
# nothing keeping them in sync. This script is TRACKED, so git-sync-pull.sh
# (*/15) delivers exactly one copy and there is nothing to drift.
#
# Auth is an HMAC-SHA256 signature over "<unix_ts>.<body>", valid for 120s.
# No bearer token, so nothing reusable travels on the wire and this job has no
# dependency on the 90-day ADMIN_TOKEN rotation. A stolen signature can do
# exactly one thing: make an ALREADY-DUE post go out a few minutes early --
# publish-now and resume are admin-JWT-only and reject the cron signature.
#
# Secret: NOTES_SCHEDULER_SECRET in the workspace .env (mode 600, gitignored).
# It is passed to python3 on STDIN, never in argv and never in the environment:
# /proc/PID/cmdline is world-readable via `ps`, /proc/PID/environ is not, and
# stdin is neither. Headers go to curl through a config file on stdin for the
# same reason -- the signature never appears in a process listing either.
#
# Log: .notes-scheduler.log in the workspace root. Quiet ticks are NOT logged.
# At 288 runs a day, logging every no-op would bury the real events and grow
# without bound; nothing on this box runs logrotate. The authoritative
# heartbeat lives in the database (scheduler_heartbeat) and is shown in the
# Hub's Scheduled panel, so the local log only needs the exceptions.
# ---------------------------------------------------------------------------
set -uo pipefail

# Cron gets Debian's bare default PATH -- no PATH/SHELL/MAILTO is set in the
# crontab -- so `hermes` would not resolve. Same line every other cron script
# on this box uses.
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$HOME/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

WORKSPACE="/home/harvey-n8n/workspaces/RealtyExperts-Daily-Email"
LOG="$WORKSPACE/.notes-scheduler.log"
STATE="$WORKSPACE/.notes-scheduler.state"
LOCK="/tmp/notes-scheduler-sweep.lock"
FN="https://hbsodfrxadlfladdgvgy.supabase.co/functions/v1/notes-scheduler"
SLACK_TARGET="slack:C09HKFD404T"   # #personal-assistance-re, reaches Harv's phone
MAX_LOG_LINES=2000

log() { printf '%s  %s\n' "$(date '+%Y-%m-%d %H:%M:%S %Z')" "$*" >> "$LOG"; }

# One instance at a time. A sweep that hangs must not be joined by a second
# every 5 minutes; the database claim would refuse the duplicate anyway
# (FOR UPDATE SKIP LOCKED), but piling up curl processes is its own problem.
exec 9>"$LOCK" 2>/dev/null || exit 0
flock -n 9 || exit 0

alert() {
  # Alert on the FIRST failure of a streak and once on recovery. A persistent
  # outage must not send 288 notifications a day.
  local kind="$1" msg="$2" prev=""
  [ -f "$STATE" ] && prev="$(cat "$STATE" 2>/dev/null)"
  if [ "$kind" != "$prev" ]; then
    printf '%s' "$kind" > "$STATE"
    hermes send --to "$SLACK_TARGET" "$msg" >/dev/null 2>&1 \
      || log "WARN could not reach hermes to send: $msg"
  fi
}

SECRET="$(sed -n 's/^NOTES_SCHEDULER_SECRET=//p' "$WORKSPACE/.env" 2>/dev/null | head -1 | tr -d '"'"'"' \r')"
if [ -z "$SECRET" ]; then
  log "FATAL NOTES_SCHEDULER_SECRET missing from $WORKSPACE/.env - sweep cannot run"
  alert fail "@Harv Agent Hub scheduled posts are NOT running: the scheduler secret is missing on the VPS. Nothing will send until this is fixed."
  exit 1
fi

BODY='{"action":"sweep"}'
TS="$(date +%s)"

# Secret in on stdin; the message (timestamp + body) is not secret.
SIG="$(printf '%s' "$SECRET" | SIG_MSG="$TS.$BODY" python3 -c '
import hmac, hashlib, os, sys
key = sys.stdin.buffer.read().strip()
print(hmac.new(key, os.environ["SIG_MSG"].encode(), hashlib.sha256).hexdigest())
' 2>/dev/null)"
unset SECRET
if [ -z "$SIG" ]; then
  log "FATAL could not compute the request signature"
  exit 1
fi

# The body goes to a temp file and curl reads it with data=@file. Inlining it as
# `data = "{"action":"sweep"}"` inside a curl config is a quoting trap -- the
# inner double quotes terminate the value and curl posts something malformed,
# which the worker rejects as 400 Invalid JSON. Worse, the signature covers the
# body, so any transformation between signing and sending breaks auth too. A
# file keeps the posted bytes byte-identical to the signed bytes.
BODYFILE="$(mktemp)"
trap 'rm -f "$BODYFILE"' EXIT
printf '%s' "$BODY" > "$BODYFILE"

# Headers via a curl config on stdin, so neither the signature nor the apikey
# lands in `ps`. The apikey is the PUBLIC anon key (it ships in the web bundle).
RESP="$(printf '%s\n' \
  'silent' \
  'show-error' \
  'request = POST' \
  'max-time = 90' \
  "header = \"apikey: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imhic29kZnJ4YWRsZmxhZGRndmd5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI5MTA2MDcsImV4cCI6MjA4ODQ4NjYwN30.tuF35cSBp4mS31X4wtmBsFnLQil-UZ-oX_FXu6QN-fM\"" \
  'header = "Content-Type: application/json"' \
  "header = \"x-scheduler-ts: $TS\"" \
  "header = \"x-scheduler-sig: $SIG\"" \
  "data = @$BODYFILE" \
  "url = \"$FN\"" \
  'write-out = \nHTTP_STATUS:%{http_code}' \
  | curl -K - 2>&1)"
unset SIG

STATUS="$(printf '%s' "$RESP" | sed -n 's/.*HTTP_STATUS:\([0-9]*\).*/\1/p' | tail -1)"
PAYLOAD="$(printf '%s' "$RESP" | sed 's/HTTP_STATUS:[0-9]*//')"

if [ "$STATUS" = "200" ]; then
  CLAIMED="$(printf '%s' "$PAYLOAD" | jq -r '.claimed // empty' 2>/dev/null)"
  EXPIRED="$(printf '%s' "$PAYLOAD" | jq -r '.expired // 0' 2>/dev/null)"
  NOTE="$(printf '%s' "$PAYLOAD" | jq -r '.note_id // empty' 2>/dev/null)"
  OUTCOME="$(printf '%s' "$PAYLOAD" | jq -r '.outcome // empty' 2>/dev/null)"

  # Clear a failure streak.
  if [ -f "$STATE" ] && [ "$(cat "$STATE" 2>/dev/null)" = "fail" ]; then
    log "RECOVERED sweep is reaching the scheduler again"
    alert ok "@Harv Agent Hub scheduled posts: the scheduler is reachable again. Check the Scheduled panel for anything that was missed."
  fi
  printf 'ok' > "$STATE"

  if [ -n "$NOTE" ]; then
    SENT="$(printf '%s' "$PAYLOAD" | jq -r '.recipientsSent // 0' 2>/dev/null)"
    BOK="$(printf '%s' "$PAYLOAD" | jq -r '.batchesOk // 0' 2>/dev/null)"
    BTOT="$(printf '%s' "$PAYLOAD" | jq -r '.batchesTotal // 0' 2>/dev/null)"
    log "SENT note=$NOTE outcome=$OUTCOME recipients=$SENT batches=$BOK/$BTOT"
    if [ "$OUTCOME" != "ok" ]; then
      alert partial "@Harv Agent Hub: a scheduled post only PARTIALLY sent ($SENT recipients, $BOK of $BTOT batches). Open the Scheduled panel in the Hub and use Resume - do not re-save the note, that re-mails everyone."
    fi
  elif [ "${EXPIRED:-0}" != "0" ]; then
    log "EXPIRED $EXPIRED broadcast(s) reaped as missed or stuck"
    alert expired "@Harv Agent Hub: $EXPIRED scheduled post(s) missed their send time and were NOT sent. Open the Scheduled panel in the Hub."
  fi
  # A quiet tick (claimed:0, expired:0) is deliberately not logged.
else
  log "ERROR http=${STATUS:-none} $(printf '%s' "$PAYLOAD" | head -c 300 | tr '\n' ' ')"
  alert fail "@Harv Agent Hub scheduled posts: the 5-minute scheduler check is failing (HTTP ${STATUS:-no response}). Anything scheduled will NOT go out until this is fixed."
fi

# Nothing on this box runs logrotate, and this job wakes 288 times a day.
if [ -f "$LOG" ] && [ "$(wc -l < "$LOG" 2>/dev/null || echo 0)" -gt "$MAX_LOG_LINES" ]; then
  tail -n "$MAX_LOG_LINES" "$LOG" > "$LOG.tmp" 2>/dev/null && mv "$LOG.tmp" "$LOG"
fi
exit 0
