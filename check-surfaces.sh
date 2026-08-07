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

set -uo pipefail

D="${1:-$(TZ=America/Los_Angeles date +%m%d%y)}"
SLASH="${D:0:2}/${D:2:2}/${D:4:2}"
PAGES="https://fremontrealtyexperts-510.github.io/RealtyExperts-Daily-Email"
RAW="https://raw.githubusercontent.com/fremontrealtyexperts-510/RealtyExperts-Daily-Email/main"
CMS="https://www.harvrealtor.com"
CB="$(date +%s)"
FAIL=0; SKIP=0

ok()   { printf "  \033[32m✅\033[0m %-34s %s\n" "$1" "${2:-}"; }
bad()  { printf "  \033[31m❌\033[0m %-34s %s\n" "$1" "${2:-}"; FAIL=1; }
skip() { printf "  \033[33m⏭\033[0m  %-34s %s\n" "$1" "${2:-}"; SKIP=1; }

code() { curl -s -o /dev/null -w '%{http_code}' "$1?cb=$CB"; }

echo "================================================================"
echo "  Surface check — $SLASH"
echo "================================================================"

echo; echo "── GitHub Pages"
IDX=$(curl -s "$PAGES/index.html?cb=$CB" | grep -oE 'daily-market-glance-[0-9]{6}' | head -1)
[ "$IDX" = "daily-market-glance-$D" ] && ok "index points at today" "$IDX" \
                                     || bad "index points at today" "found: ${IDX:-none}"
C=$(code "$PAGES/daily-market-glance-$D.html")
[ "$C" = "200" ] && ok "email page live" "$C" || bad "email page live" "$C"
for n in 1 2; do
  C=$(code "$RAW/RE-Daily-$n-$D.png")
  [ "$C" = "200" ] && ok "RE-Daily-$n-$D.png" "$C" || bad "RE-Daily-$n-$D.png" "$C"
done
LID=$(curl -s "$PAGES/live-inventory.json?cb=$CB" \
      | python3 -c "import json,sys;print(json.load(sys.stdin).get('date',''))" 2>/dev/null)
[ "$LID" = "$SLASH" ] && ok "live-inventory.json date" "$LID" \
                      || bad "live-inventory.json date" "found: ${LID:-none}"

echo; echo "── harvrealtor.com (Stage 5 — the one with no safety net)"
C=$(code "$CMS/HarvRealtor-daily-market-glance-$D")
[ "$C" = "200" ] && ok "dated blog node" "$C" || bad "dated blog node" "$C"
LAND=$(curl -s "$CMS/alameda-Interactive?cb=$CB")
if grep -q "alameda-chart-$D\.js" <<<"$LAND"; then
  ok "landing carries today's chart" "alameda-chart-$D.js"
else
  bad "landing carries today's chart" "found: $(grep -oE 'alameda-chart-[0-9]{6}\.js' <<<"$LAND" | sort -u | tr '\n' ' ')"
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
  echo "       node post-to-incom.js --dry-run && node post-to-incom.js"
  echo "       node verify-cms-publish.js"
  echo "     Pages missing? the deploy may have failed on a runner hiccup:"
  echo "       GH_TOKEN=\$(gh auth token -u fremontrealtyexperts-510) gh run rerun <id> -R fremontrealtyexperts-510/RealtyExperts-Daily-Email"
fi
echo "================================================================"
exit "$FAIL"
