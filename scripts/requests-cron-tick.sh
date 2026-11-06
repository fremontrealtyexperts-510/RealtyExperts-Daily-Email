#!/bin/bash
# ---------------------------------------------------------------------------
# Agent Hub request tracker: the hourly tick.  Added 2026-11-05.
#
# Pokes the requests-cron edge function every hour at :07. That function does
# ALL the work: from 8 AM Pacific it claims and emails the day's reminders
# ("Due tomorrow", "Waiting on you"), it announces any request a phone filed
# but never sent out, it cleans up uploads nobody posted within 24 hours, and
# it writes its own heartbeat row (requests_cron_heartbeat).
#
# THIS SCRIPT CARRIES NO BUSINESS LOGIC, ON PURPOSE.  It decides nothing about
# what to send or when; the function reads the Pacific clock itself, so neither
# this box's timezone nor the exact minute matters. The only reason it exists
# is that Supabase has no built-in timer. `broadcast-backstop.js` is the
# cautionary tale: it is gitignored, so a copy lives on the Mac and another on
# the VPS with nothing keeping them in sync. This script is TRACKED, so
# git-sync-pull.sh (*/15) delivers exactly one copy and there is nothing to
# drift.
#
# Auth is an HMAC-SHA256 signature over "<unix_ts>.<body>", valid for 120s.
# No bearer token, so nothing reusable travels on the wire and this job has no
# dependency on the 90-day ADMIN_TOKEN rotation. A stolen signature can do
# exactly one thing, for two minutes: run a tick early. A tick is idempotent
# (every email is claimed in the database before it is sent), so even that
# sends nothing twice.
#
# Secret: REQUESTS_CRON_SECRET in the workspace .env (mode 600, gitignored),
# the same value as the Supabase function secret of that name. Its own secret,
# not the notes scheduler's, so either can be rotated or revoked alone. It is
# passed to python3 on STDIN, never in argv and never in the environment:
# /proc/PID/cmdline is world-readable via `ps`, /proc/PID/environ is not, and
# stdin is neither. Headers go to curl through a config file on stdin for the
# same reason: the signature never appears in a process listing either.
#
# Log: .requests-cron.log in the workspace root. Quiet ticks are NOT logged; a
# tick that emailed or cleaned up something gets one line, and every problem
# gets one. At 24 runs a day a line per no-op would bury the real events and
# grow without bound; nothing on this box runs logrotate. The authoritative
# record is the requests_cron_heartbeat table (one row per tick, saying what it
# did), so the local log only needs the exceptions.
#
# Slack: an alert on the FIRST failure of a streak and one when it recovers.
# Silence while healthy.
# ---------------------------------------------------------------------------
set -uo pipefail

# Cron gets Debian's bare default PATH (no PATH/SHELL/MAILTO is set in the
# crontab), so `hermes` would not resolve. Same line every other cron script
# on this box uses.
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$HOME/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

WORKSPACE="/home/harvey-n8n/workspaces/RealtyExperts-Daily-Email"
LOG="$WORKSPACE/.requests-cron.log"
STATE="$WORKSPACE/.requests-cron.state"
LOCK="/tmp/requests-cron-tick.lock"
FN="https://hbsodfrxadlfladdgvgy.supabase.co/functions/v1/requests-cron"
SLACK_TARGET="slack:C09HKFD404T"   # #personal-assistance-re, reaches Harv's phone
MAX_LOG_LINES=2000

# Log times in Pacific, whatever this box's timezone is set to.
log() { printf '%s  %s\n' "$(TZ=America/Los_Angeles date '+%Y-%m-%d %H:%M:%S %Z')" "$*" >> "$LOG"; }

# One instance at a time. A tick that hangs must not be joined by the next
# hour's; the database claims would refuse every duplicate email anyway, but
# piling up curl processes is its own problem.
exec 9>"$LOCK" 2>/dev/null || exit 0
flock -n 9 || exit 0

alert() {
  # Alert on the FIRST failure of a streak and once on recovery. A persistent
  # outage must not send 24 notifications a day.
  local kind="$1" msg="$2" prev=""
  [ -f "$STATE" ] && prev="$(cat "$STATE" 2>/dev/null)"
  if [ "$kind" != "$prev" ]; then
    printf '%s' "$kind" > "$STATE"
    hermes send --to "$SLACK_TARGET" "$msg" >/dev/null 2>&1 \
      || log "WARN could not reach hermes to send: $msg"
  fi
}

SECRET="$(sed -n 's/^REQUESTS_CRON_SECRET=//p' "$WORKSPACE/.env" 2>/dev/null | head -1 | tr -d '"'"'"' \r')"
# The function refuses any secret under 32 characters, so a short one here can
# only be a damaged .env line: say so instead of failing as a mystery 401.
if [ "${#SECRET}" -lt 32 ]; then
  log "FATAL REQUESTS_CRON_SECRET missing or shorter than 32 characters in $WORKSPACE/.env - tick cannot run"
  alert fail "@Harv Agent Hub requests: the hourly check is NOT running because its secret is missing on the VPS. Reminders and catch-up emails will not go out until this is fixed."
  exit 1
fi

BODY='{"action":"tick"}'
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
  alert fail "@Harv Agent Hub requests: the hourly check is NOT running because the VPS could not sign its request (is python3 working?). Reminders and catch-up emails will not go out until this is fixed."
  exit 1
fi

# The body goes to a temp file and curl reads it with data=@file. Inlining it as
# `data = "{"action":"tick"}"` inside a curl config is a quoting trap: the
# inner double quotes end the value and curl posts something malformed, which
# the worker rejects with 400 Invalid JSON. Worse, the signature covers the
# body, so any change between signing and sending breaks auth too. A file keeps
# the posted bytes identical to the signed bytes.
BODYFILE="$(mktemp)"
trap 'rm -f "$BODYFILE"' EXIT
printf '%s' "$BODY" > "$BODYFILE"

# Headers via a curl config on stdin, so neither the signature nor the apikey
# lands in `ps`. The apikey is the PUBLIC anon key (it ships in the web bundle).
# max-time is above the gateway's own 150 s limit on purpose: if a tick ever
# runs that long, curl reports the gateway's answer instead of its own timeout.
RESP="$(printf '%s\n' \
  'silent' \
  'show-error' \
  'request = POST' \
  'max-time = 170' \
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
  # Not `.ok // empty`: jq's // treats false like null, which would read a
  # failed tick as a missing field.
  OK="$(printf '%s' "$PAYLOAD" | jq -r '.ok' 2>/dev/null)"

  if [ "$OK" = "true" ]; then
    # Clear a failure streak.
    PREV=""
    [ -f "$STATE" ] && PREV="$(cat "$STATE" 2>/dev/null)"
    if [ "$PREV" = "fail" ] || [ "$PREV" = "problem" ]; then
      log "RECOVERED the hourly requests tick is running cleanly again"
      alert ok "@Harv Agent Hub requests: the hourly check is working again. Anything it held back (reminders, catch-up emails) goes out on its next runs."
    fi
    printf 'ok' > "$STATE"

    # One line when the tick did something; a quiet tick is deliberately not logged.
    # handed_back: claimed, then given back for the next tick (not reached, or
    # not one email delivered). dropped: a reminder whose request moved on
    # (closed, re-dated, out of review) before its turn, so nothing was sent.
    DID="$(printf '%s' "$PAYLOAD" | jq -r '
      def n(f): (f // 0);
      def nos(f): ((f // []) | join(","));
      if (n(.reminders.claimed) + n(.reminders.released) + n(.announce.claimed) + n(.announce.deferred)
          + n(.files.deleted) + n(.files.deferred)) > 0
      then "reminders=\(n(.reminders.due)) due + \(n(.reminders.review)) waiting [\(nos(.reminders.request_nos))] emails=\(n(.reminders.emails_sent)) handed_back=\(n(.reminders.released)) dropped=\(n(.reminders.stale)) | announced=\(n(.announce.claimed) - n(.announce.released)) [\(nos(.announce.request_nos))] emails=\(n(.announce.emails_sent)) handed_back=\(n(.announce.released)) left_for_next=\(n(.announce.deferred)) | files_deleted=\(n(.files.deleted)) files_left=\(n(.files.deferred)) | \(n(.duration_ms))ms"
      else empty end' 2>/dev/null)"
    [ -n "$DID" ] && log "TICK $DID"
  else
    # The tick ran but something in it went wrong: a step failed, an email
    # bounced at Gmail, or a setting is missing. The function says what.
    # jq -j: no trailing newline to turn into a stray space before the period.
    WHY="$(printf '%s' "$PAYLOAD" | jq -j '(.errors // []) | join("; ")' 2>/dev/null | head -c 300 | tr '\n' ' ')"
    [ -n "$WHY" ] || WHY="$(printf '%s' "$PAYLOAD" | head -c 200 | tr '\n' ' ')"
    log "PROBLEM $WHY"
    alert problem "@Harv Agent Hub requests: the hourly check ran but hit a problem: ${WHY:-no details}. Everything else in the check still ran. Details are in the requests_cron_heartbeat table."
  fi
else
  SUMMARY="$(printf '%s' "$PAYLOAD" | head -c 300 | tr '\n' ' ')"
  log "ERROR http=${STATUS:-none} $SUMMARY"

  if [ "${STATUS:-0}" = "401" ]; then
    # Refused: the two copies of the secret differ, or this clock is off.
    alert fail "@Harv Agent Hub requests: the hourly check was refused (HTTP 401). The REQUESTS_CRON_SECRET on the VPS probably does not match the one in Supabase, or the VPS clock is more than 2 minutes off. Reminders and catch-up emails will NOT go out until this is fixed."
  else
    alert fail "@Harv Agent Hub requests: the hourly check is failing (HTTP ${STATUS:-no response}). Reminders and catch-up emails will NOT go out until this is fixed."
  fi
fi

# Nothing on this box runs logrotate.
if [ -f "$LOG" ] && [ "$(wc -l < "$LOG" 2>/dev/null || echo 0)" -gt "$MAX_LOG_LINES" ]; then
  tail -n "$MAX_LOG_LINES" "$LOG" > "$LOG.tmp" 2>/dev/null && mv "$LOG.tmp" "$LOG"
fi
exit 0
