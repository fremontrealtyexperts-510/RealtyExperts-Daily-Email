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
# PAST-DAY MODE (fixed 2026-08-07). Five surfaces are SINGLETONS: they carry only
# the most recent report, by design.
#   * index.html            — redirects to the latest email
#   * live-inventory.json   — one live file, rewritten daily
#   * daily-report.json     — the HarvRealtor app feed, one file, rewritten daily (2026-08-21)
#   * the alameda-Interactive landing node — one node, re-edited daily
#   * the thebayarearealestate.com homepage date (Newark, Stage 6, 2026-09-11)
# Comparing those against a PAST date can only ever fail, so checking yesterday
# (which CLAUDE.md mandates every run) always exited 1 and then printed recovery
# advice ending in `node post-to-incom.js`. Following that advice for a past day
# would have overwritten the landing node with the OLDER chart, clobbering today.
# For a past day those four are now reported ⏭ "moved on" and do not set FAIL.
# The per-day evidence that actually matters (dated email page, both dated PNGs,
# the dated blog node, the sent email, the broadcast confirmation) stays a hard
# check for every date.
#
# BOUNCES (added 2026-10-30). The confirmation email only proves the send was
# attempted: on 10/30 Google rejected the whole second batch (20 of 100 agents)
# and this script still said "broadcast confirmed". It now counts the bounce
# notices. 5+ agents is a rejected batch, the same line verify-broadcast.js uses.
# That FAILS for today and only warns for a past day: yesterday's bounce cannot
# be fixed by anything here, and a recovered day should not hold the gate red.

set -uo pipefail

D="${1:-$(TZ=America/Los_Angeles date +%m%d%y)}"
SLASH="${D:0:2}/${D:2:2}/${D:4:2}"
TODAY="$(TZ=America/Los_Angeles date +%m%d%y)"
IS_TODAY=0; [ "$D" = "$TODAY" ] && IS_TODAY=1
PAGES="https://fremontrealtyexperts-510.github.io/RealtyExperts-Daily-Email"
RAW="https://raw.githubusercontent.com/fremontrealtyexperts-510/RealtyExperts-Daily-Email/main"
CMS="https://www.harvrealtor.com"
CB="$(date +%s)"
FAIL=0; SKIP=0; BOUNCED=0

ok()   { printf "  \033[32m✅\033[0m %-34s %s\n" "$1" "${2:-}"; }
bad()  { printf "  \033[31m❌\033[0m %-34s %s\n" "$1" "${2:-}"; FAIL=1; }
skip() { printf "  \033[33m⏭\033[0m  %-34s %s\n" "$1" "${2:-}"; SKIP=1; }
warn() { printf "  \033[33m⚠️\033[0m  %-34s %s\n" "$1" "${2:-}"; }
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
# Section floor lowered 3 -> 2 on 2026-09-05. The real contract (isReport in
# ~/harvrealtor-app/src/lib/dispatch.ts, isDailyReport in ~/harvrealtor-net-live)
# requires only Array.isArray(sections) && sections.every(isSection), with NO
# minimum count, so 3 was stricter than the predicate this claims to mirror. It
# false-FAILED the 09/05/26 jobs special, a Real Estate + Economy edition that
# every real consumer renders fine. Keep a floor of 2 as an empty-file guard.
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
    and isinstance(S,list) and len(S)>=2
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

# Share images (og:image), from 10/26/26 on. InCom builds og:image from the body's
# FIRST <img src>, so a first picture on dscloud or GitHub shares
# "https://www.harvrealtor.comhttps://..." and no link preview can load it.
# post-to-incom.js hosts that picture on harvrealtor.com (lib/incom-share-image.js).
# No og:image at all means no picture in that day's body: nothing to share, not a fail.
# The landing is a singleton, so it is checked on its own day only.
share_check() {  # $1 label, $2 page HTML
  local og ct
  og=$(grep -oE '<meta property="og:image" content="[^"]*"' <<<"$2" | head -1 | sed -E 's/.*content="([^"]*)"/\1/')
  if [ -z "$og" ]; then ok "$1" "none (no picture in the body)"; return; fi
  if [[ "$og" =~ ^https://www\.harvrealtor\.com/files/blog/[0-9]+/[0-9]+\.(jpe?g|png|gif)$ ]]; then
    ct=$(curl -s -o /dev/null -w '%{http_code} %{content_type}' "$og")
    if [[ "$ct" == "200 image/"* ]]; then ok "$1" "${og#"$CMS"}"; else bad "$1" "$og answers $ct"; fi
  else
    bad "$1" "broken: $og"
  fi
}
YMD="${D:4:2}${D:0:2}${D:2:2}"
if [[ "$YMD" > "261025" ]]; then
  share_check "dated blog share image" "$(curl -s "$CMS/HarvRealtor-daily-market-glance-$D?cb=$CB")"
  [ "$IS_TODAY" -eq 1 ] && share_check "landing share image" "$LAND"
fi

# thebayarearealestate.com, the Newark partnership site (Stage 6, added 2026-09-11).
# Stage 6 was MISSED on 09/10/26 and caught only at the next morning's wrap up,
# because nothing here checked it. The dated brief is a hard check for every date.
# The homepage date is a SINGLETON (it shows only the latest run), so a past day
# reports ⏭ moved on. Apex host on purpose: www returns 307, which a plain curl
# reads as a failure. Read only, against the PUBLIC site; nothing from this
# workspace flows the other way (privacy boundary, project-tbare-newark-daily-stage).
echo; echo "── thebayarearealestate.com (Stage 6, Newark)"
TBARE="https://thebayarearealestate.com"
NSLUG=$(python3 -c "import datetime,sys;d=datetime.datetime.strptime(sys.argv[1],'%m%d%y');print(f'newark-daily-brief-{d:%B}-{d.day}-{d.year}'.lower())" "$D")
C=$(code "$TBARE/blog/$NSLUG")
[ "$C" = "200" ] && ok "Newark daily brief" "$C" || bad "Newark daily brief" "$C  /blog/$NSLUG"
NHOME=$(curl -s "$TBARE/?cb=$CB" | grep -oE '[0-9]{2}/[0-9]{2}/[0-9]{2}' | sort -u | tr '\n' ' ')
if grep -q "$SLASH" <<<"$NHOME"; then
  ok "Newark homepage date" "$SLASH"
elif [ "$IS_TODAY" -eq 0 ]; then
  moved "Newark homepage date" "now ${NHOME:-none}(singleton, expected for a past day)"
else
  bad "Newark homepage date" "found: ${NHOME:-none}(prerender can lag ~1 min after a push; re-run before recovering)"
fi

echo; echo "── Email + broadcast"
TOK=$(python3 -c "import json;print(json.load(open('/tmp/ms365-token.json'))['access_token'])" 2>/dev/null)
if [ -z "${TOK:-}" ]; then
  skip "daily email sent" "no MS365 token"
  skip "broadcast confirmed" "no MS365 token"
  skip "broadcast bounces" "no MS365 token"
else
  # Page back until we pass the start of that day (PT). A flat $top=300 only
  # reached ~1.5 days on this mailbox: on 10/22/26 the 10/20 email and
  # confirmation sat at positions 469 to 473 and were reported missing.
  COUNT=$(SL="$SLASH" TOK="$TOK" python3 -c "
import json,os,re,urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo
w=os.environ['SL']; tok=os.environ['TOK']
day=datetime.strptime(w,'%m/%d/%y').replace(tzinfo=ZoneInfo('America/Los_Angeles'))
u='https://graph.microsoft.com/v1.0/me/messages?\$top=250&\$select=subject,receivedDateTime,bodyPreview&\$orderby=receivedDateTime%20desc'
v=[]
for _ in range(12):
    d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'Authorization':'Bearer '+tok}),timeout=30))
    v+=d.get('value',[])
    u=d.get('@odata.nextLink')
    if not u or not v or datetime.fromisoformat(v[-1]['receivedDateTime'].replace('Z','+00:00'))<day: break
mail=[m for m in v if 'At a Glance' in (m.get('subject') or '') and w in (m.get('subject') or '') and 'Agent Hub' not in (m.get('subject') or '')]
conf=[m for m in v if 'Agent Hub' in (m.get('subject') or '') and w in (m.get('subject') or '') and 'Confirmation' in (m.get('subject') or '')]
# bounce notices; the sender bounces too on a rejected batch (its To: line), and it is not an agent
ndr=[m for m in v if (m.get('subject') or '').strip().lower().startswith('undeliverable:') and '[Agent Hub]' in (m.get('subject') or '') and w in (m.get('subject') or '')]
who=sorted({a.group(1) for a in (re.search(r'recipients or groups:\s+(\S+)',m.get('bodyPreview') or '') for m in ndr) if a})
who=[a for a in who if a.lower()!='fremontrealtyexperts@gmail.com']
print(len(mail), len(conf), len(who), *who)
" 2>/dev/null)
  set -- $COUNT
  [ "${1:-0}" -ge 1 ] && ok "daily email sent" "$1 copies" || bad "daily email sent" "none found"
  # NOTE: census the mailbox, do NOT use verify-broadcast.js for a past date —
  # it gates on a recent arrival window and false-negatives a day later.
  [ "${2:-0}" -ge 1 ] && ok "broadcast confirmed" "confirmation present" \
                      || bad "broadcast confirmed" "no confirmation for $SLASH"
  if [ -z "${3:-}" ]; then
    skip "broadcast bounces" "mailbox not read"
  else
    NDR="$3"; shift 3
    if [ "$NDR" -eq 0 ]; then
      ok "broadcast bounces" "none"
    elif [ "$NDR" -lt 5 ]; then
      warn "broadcast bounces" "$NDR, single mailboxes: $*"
    elif [ "$IS_TODAY" -eq 1 ]; then
      bad "broadcast bounces" "$NDR agents did NOT get it: $*"
      BOUNCED=1
    else
      warn "broadcast bounces" "$NDR agents bounced on $SLASH, confirm they were sent it: $*"
    fi
  fi
fi

echo
echo "================================================================"
if [ "$FAIL" -eq 0 ]; then
  echo "  ✅ ALL SURFACES CARRY $SLASH"
  [ "$SKIP" -eq 1 ] && echo "  (some checks skipped — see ⏭ above)"
else
  echo "  ❌ AT LEAST ONE SURFACE IS MISSING $SLASH"
  if [ "$BOUNCED" -eq 1 ]; then
    echo "     Broadcast bounced? NEVER re-fire it: the agents who got it would get it twice."
    echo "       Show Harv the list. With his OK, send those addresses the same email from"
    echo "       Outlook, blind copied (memory: session-2026-10-30-daily-horton-amazon-coinbase-gmail-rejected-batch)."
  fi
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
  echo "     Share image broken? the dated blog, any day (never touches the landing):"
  echo "       node edit-incom-node.js --share-image-only --date $SLASH"
  [ "$IS_TODAY" -eq 1 ] && echo "       then the landing (today only): node post-to-incom.js --landing-only"
  echo "     Newark brief missing? run Stage 6 (daily-report skill section 4.7):"
  echo "       cd /tmp/tbare && node scripts/update-newark-listings.mjs /tmp/mls-today.csv --date $SLASH"
  echo "       then the brief, tsc + tests, commit as thebayarearealestate, push (gh auth switch)"
  [ "$IS_TODAY" -eq 0 ] && echo "       ⚠️  past day: /tmp/mls-today.csv is TODAY's sheet. Dump $SLASH's dated sheet first (recipe in project-tbare-newark-daily-stage)."
  echo "     App feed (daily-report.json) missing or stale? regenerate + push:"
  echo "       node generate-app-report.js && bash push-to-github.sh"
  echo "     Pages missing? the deploy may have failed on a runner hiccup:"
  echo "       GH_TOKEN=\$(gh auth token -u fremontrealtyexperts-510) gh run rerun <id> -R fremontrealtyexperts-510/RealtyExperts-Daily-Email"
fi
echo "================================================================"
exit "$FAIL"
