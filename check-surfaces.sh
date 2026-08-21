#!/usr/bin/env bash
# check-surfaces.sh [MMDDYY]  — verify EVERY daily-report surface for a given day.
#
# WHY THIS EXISTS (2026-08-07): on 08/06 the run did Stages 0 through 4.5 and
# stopped. Email went out, the broadcast fired, Pages deployed, but Stage 5
# (harvrealtor.com) was never run. Nothing caught it. It surfaced a day later
# only because Harv said "I don't see it on harvrealtor.com".
#
# The broadcast has a backstop and self-verification. Stage 5 has neither. This
# script is the missing net: one command that answers "is EVERY surface actually
# carrying this day's report?" Run it at the end of every daily run, and run it
# for YESTERDAY too, since a miss is usually noticed a day late.
#
#   bash check-surfaces.sh            # today (PT)
#   bash check-surfaces.sh 080626     # a specific day
#
# Exit 0 = all surfaces carry that day. Exit 1 = at least one is missing.
# Mail checks are skipped (not failed) when no MS365 token is present.
#
# PAST-DAY MODE (fixed 2026-08-07). Four surfaces are SINGLETONS: they carry only
# the most recent report, by design.
#   * index.html            — redirects to the latest email
#   * live-inventory.json   — one live file, rewritten daily
#   * daily-report.json     — the HarvRealtor app feed, one file, rewritten daily (2026-08-21)
#   * the alameda-Interactive landing node — one node, re-edited daily
# Comparing those against a PAST date can only ever fail, so checking yesterday
# (which CLAUDE.md mandates every run) always exited 1 and then printed recovery
# advice ending in `node post-to-incom.js`. Following that advice for a past day
# would have overwritten the landing node with the OLDER chart, clobbering today.
# For a past day those four are now reported ⏭ "moved on" and do not set FAIL.
# The per-day evidence that actually matters (dated email page, both dated PNGs,
# the dated blog node, the sent email, the broadcast confirmation) stays a hard
# check for every date.

set -uo pipefail

D="${1:-$(TZ=America/Los_Angeles date +%m%d%y)}"
SLASH="${D:0:2}/${D:2:2}/${D:4:2}"
TODAY="$(TZ=America/Los_Angeles date +%m%d%y)"
IS_TODAY=0; [ "$D" = "$TODAY" ] && IS_TODAY=1
PAGES="https://fremontrealtyexperts-510.github.io/RealtyExperts-Daily-Email"
RAW="https://raw.githubusercontent.com/fremontrealtyexperts-510/RealtyExperts-Daily-Email/main"
CMS="https://www.harvrealtor.com"
CB="$(date +%s)"
FAIL=0; SKIP=0

ok()   { printf "  \033[32m✅\033[0m %-34s %s\n" "$1" "${2:-}"; }
bad()  { printf "  \033[31m❌\033[0m %-34s %s\n" "$1" "${2:-}"; FAIL=1; }
skip() { printf "  \033[33m⏭\033[0m  %-34s %s\n" "$1" "${2:-}"; SKIP=1; }
# a singleton surface that has legitimately rolled forward past the asked-for day
moved() { printf "  \033[33m⏭\033[0m  %-34s %s\n" "$1" "${2:-}"; SKIP=1; }

code() { curl -s -o /dev/null -w '%{http_code}' "$1?cb=$CB"; }

echo "================================================================"
echo "  Surface check — $SLASH"
echo "================================================================"

echo; echo "── GitHub Pages"
IDX=$(curl -s "$PAGES/index.html?cb=$CB" | grep -oE 'daily-market-glance-[0-9]{6}' | head -1)
if [ "$IDX" = "daily-market-glance-$D" ]; then
  ok "index points at this day" "$IDX"
elif [ "$IS_TODAY" -eq 0 ]; then
  moved "index points at this day" "now ${IDX:-none} (singleton, expected for a past day)"
else
  bad "index points at this day" "found: ${IDX:-none}"
fi
C=$(code "$PAGES/daily-market-glance-$D.html")
[ "$C" = "200" ] && ok "email page live" "$C" || bad "email page live" "$C"
for n in 1 2; do
  C=$(code "$RAW/RE-Daily-$n-$D.png")
  [ "$C" = "200" ] && ok "RE-Daily-$n-$D.png" "$C" || bad "RE-Daily-$n-$D.png" "$C"
done
LID=$(curl -s "$PAGES/live-inventory.json?cb=$CB" \
      | python3 -c "import json,sys;print(json.load(sys.stdin).get('date',''))" 2>/dev/null)
if [ "$LID" = "$SLASH" ]; then
  ok "live-inventory.json date" "$LID"
elif [ "$IS_TODAY" -eq 0 ]; then
  moved "live-inventory.json date" "now ${LID:-none} (singleton, expected for a past day)"
else
  bad "live-inventory.json date" "found: ${LID:-none}"
fi

# HarvRealtor app + harvrealtor.net/today feed (added 2026-08-21). Singleton.
# (Pages ignores the ?cb= query; a push reaches Pages within <=10 min, /api/daily within ~25.)
# Shape = the consumer predicate (app isReport / .net isDailyReport) in miniature:
# an edition that parses but fails it would publish green and never render.
DRD=$(curl -s "$PAGES/daily-report.json?cb=$CB" | python3 -c "
import json,sys,re
try:
    d=json.load(sys.stdin)
except Exception:
    print('', '', 'unreadable'); sys.exit(0)
r=d.get('rates') or {}; L=d.get('links') or {}; S=d.get('sections')
ok=(d.get('version')==1 and isinstance(d.get('date'),str) and bool(re.match(r'^\d{2}/\d{2}/\d{2}$',d['date']))
    and bool(d.get('headline')) and bool(d.get('teaser'))
    and isinstance(r.get('r30'),(int,float)) and isinstance(r.get('r15'),(int,float))
    and isinstance(S,list) and len(S)>=3
    and all(str(i.get('url','')).startswith('https://') for s in S for i in (s.get('images') or []))
    and all(str(L.get(k,'')).startswith('https://') for k in ('web','blog','liveInventory')))
print(d.get('date',''), d.get('voice',''), 'ok' if ok else 'shape')
" 2>/dev/null)
set -- ${DRD:-"" "" ""}; DRDATE="${1:-}"; DRVOICE="${2:-}"; DRSHAPE="${3:-}"
if [ -n "$DRDATE" ] && [ "$DRSHAPE" != "ok" ]; then
  bad "daily-report.json (app feed)" "$DRDATE but SHAPE FAILED ($DRSHAPE): consumers would refuse it; node generate-app-report.js && bash push-to-github.sh"
elif [ "$DRDATE" = "$SLASH" ]; then
  if [ "$DRVOICE" = "harv" ]; then
    ok "daily-report.json (app feed)" "$DRDATE, voice=harv"
  else
    ok "daily-report.json (app feed)" "$DRDATE, voice=${DRVOICE:-?} (re-run generate-app-report.js after cms-content.json for Harv's voice)"
  fi
elif [ "$IS_TODAY" -eq 0 ]; then
  moved "daily-report.json (app feed)" "now ${DRDATE:-none} (singleton, expected for a past day)"
else
  bad "daily-report.json (app feed)" "found: ${DRDATE:-none}"
fi

echo; echo "── harvrealtor.com (Stage 5 — the one with no safety net)"
C=$(code "$CMS/HarvRealtor-daily-market-glance-$D")
[ "$C" = "200" ] && ok "dated blog node" "$C" || bad "dated blog node" "$C"
LAND=$(curl -s "$CMS/alameda-Interactive?cb=$CB")
LANDHAS=$(grep -oE 'alameda-chart-[0-9]{6}\.js' <<<"$LAND" | sort -u | tr '\n' ' ')
if grep -q "alameda-chart-$D\.js" <<<"$LAND"; then
  ok "landing carries this day's chart" "alameda-chart-$D.js"
elif [ "$IS_TODAY" -eq 0 ]; then
  moved "landing carries this day's chart" "now ${LANDHAS:-none} (singleton, expected for a past day)"
else
  bad "landing carries this day's chart" "found: ${LANDHAS:-none}"
fi

echo; echo "── Email + broadcast"
TOK=$(python3 -c "import json;print(json.load(open('/tmp/ms365-token.json'))['access_token'])" 2>/dev/null)
if [ -z "${TOK:-}" ]; then
  skip "daily email sent" "no MS365 token"
  skip "broadcast confirmed" "no MS365 token"
else
  MSGS=$(curl -s "https://graph.microsoft.com/v1.0/me/messages?\$top=300&\$select=subject&\$orderby=receivedDateTime%20desc" \
         -H "Authorization: Bearer $TOK")
  COUNT=$(SL="$SLASH" python3 -c "
import json,os,sys
w=os.environ['SL']; v=json.load(sys.stdin).get('value',[])
mail=[m for m in v if 'At a Glance' in (m.get('subject') or '') and w in (m.get('subject') or '') and 'Agent Hub' not in (m.get('subject') or '')]
conf=[m for m in v if 'Agent Hub' in (m.get('subject') or '') and w in (m.get('subject') or '') and 'Confirmation' in (m.get('subject') or '')]
print(len(mail), len(conf))
" <<<"$MSGS" 2>/dev/null)
  set -- $COUNT
  [ "${1:-0}" -ge 1 ] && ok "daily email sent" "$1 copies" || bad "daily email sent" "none found"
  # NOTE: census the mailbox, do NOT use verify-broadcast.js for a past date —
  # it gates on a recent arrival window and false-negatives a day later.
  [ "${2:-0}" -ge 1 ] && ok "broadcast confirmed" "confirmation present" \
                      || bad "broadcast confirmed" "no confirmation for $SLASH"
fi

echo
echo "================================================================"
if [ "$FAIL" -eq 0 ]; then
  echo "  ✅ ALL SURFACES CARRY $SLASH"
  [ "$SKIP" -eq 1 ] && echo "  (some checks skipped — see ⏭ above)"
else
  echo "  ❌ AT LEAST ONE SURFACE IS MISSING $SLASH"
  echo "     Stage 5 missing? compose cms-content.json, then:"
  echo "       node generate-cms-page.js --date $SLASH && bash push-to-github.sh"
  if [ "$IS_TODAY" -eq 1 ]; then
    echo "       node post-to-incom.js --dry-run && node post-to-incom.js"
    echo "       node verify-cms-publish.js"
  else
    echo "       ⚠️  $SLASH IS NOT TODAY. Do NOT run post-to-incom.js: it re-edits the"
    echo "          SHARED landing node and would replace today's chart with $SLASH's."
    echo "          Recover the dated BLOG node only:"
    echo "            node edit-incom-node.js --node <id> --date $SLASH   # existing node"
    echo "          Leave the landing node alone; the next daily run refreshes it."
  fi
  echo "     App feed (daily-report.json) missing or stale? regenerate + push:"
  echo "       node generate-app-report.js && bash push-to-github.sh"
  echo "     Pages missing? the deploy may have failed on a runner hiccup:"
  echo "       GH_TOKEN=\$(gh auth token -u fremontrealtyexperts-510) gh run rerun <id> -R fremontrealtyexperts-510/RealtyExperts-Daily-Email"
fi
echo "================================================================"
exit "$FAIL"
