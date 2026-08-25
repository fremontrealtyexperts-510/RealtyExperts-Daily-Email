#!/bin/bash
#
# trigger-net-rebuild.sh
#
# Rebuilds harvrealtor.net (Vercel) so its PRERENDERED HTML carries today's
# live-inventory feed.
#
# Why this exists
# ---------------
# harvrealtor.net is a Vite SPA whose routes are prerendered at build time by
# scripts/prerender.mjs: a headless browser visits every route and saves the
# rendered HTML into dist/. The inventory surfaces (/live-inventory,
# /inventory-history, the homepage pulse band, the per-city market bands) read
# the feed from GitHub Pages at runtime, so whatever the feed said AT BUILD
# TIME is what gets frozen into the HTML Vercel serves from its edge cache
# until the next deploy.
#
# On 2026-08-25 that cached HTML came from the Aug 23 deploy and still read
# "MLS export of August 21, 2026", four days stale. Hydration corrects it in a
# real browser a moment later, but the first paint, the no-JS view and any
# scraper that does not run JavaScript all see the old numbers under a
# confident old date.
#
# So: once the new feed is actually being served by Pages, poke Vercel to
# rebuild. Fires at most once per feed date (see the stamp file below).
#
# Safety posture: this NEVER fails its caller and always exits 0. A missing
# hook, a dead network or a Pages CDN that has not caught up all leave
# yesterday's HTML in place, which is exactly the status quo it is improving
# on. It also refuses to fire before Pages serves the new date, because the
# prerender fetches that live URL and rebuilding too early would just bake the
# previous day again.
#
# ONE-TIME SETUP (until this is done the script prints a notice and no-ops):
#   1. Vercel dashboard -> project harvrealtor-static-0515f -> Settings -> Git
#      -> Deploy Hooks. Create one named "daily-inventory" on branch "main".
#   2. Put the URL it gives you into this workspace's .env (gitignored):
#        HARVREALTOR_NET_DEPLOY_HOOK=https://api.vercel.com/v1/integrations/deploy/prj_xxx/yyy
#   Treat that URL as a secret: anyone holding it can trigger a production build.
#
# Usage:
#   ./trigger-net-rebuild.sh            # date read from local live-inventory.json
#   ./trigger-net-rebuild.sh 08/25/26   # explicit feed date
#   ./trigger-net-rebuild.sh 08/25/26 --force   # ignore the once-per-date stamp

set -u

SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
PAGES_URL="https://fremontrealtyexperts-510.github.io/RealtyExperts-Daily-Email/live-inventory.json"
STAMP="$SRC_DIR/.net-rebuild-last-date"
# Overridable so the negative path is testable without an 8-minute wait.
POLL_TRIES="${NET_REBUILD_POLL_TRIES:-32}"
POLL_SLEEP="${NET_REBUILD_POLL_SLEEP:-15}"

say() { echo "[net-rebuild] $*"; }

FEED_DATE="${1:-}"
FORCE="${2:-}"
[ "$FEED_DATE" = "--force" ] && { FORCE="--force"; FEED_DATE=""; }

if [ -z "$FEED_DATE" ]; then
  FEED_DATE=$(python3 -c "import json;print(json.load(open('$SRC_DIR/live-inventory.json')).get('date',''))" 2>/dev/null || echo "")
fi

if [ -z "$FEED_DATE" ]; then
  say "no feed date on disk — skipping"
  exit 0
fi

# --- Once per edition -------------------------------------------------------
# Both refresh-live-inventory.sh and push-to-github.sh publish the feed and
# both call this, and push-to-github.sh runs more than once on a Stage 5 day.
# The stamp makes every call after the first a no-op.
if [ "$FORCE" != "--force" ] && [ -f "$STAMP" ] && [ "$(cat "$STAMP" 2>/dev/null)" = "$FEED_DATE" ]; then
  say "already rebuilt for $FEED_DATE — skipping"
  exit 0
fi

# --- Hook URL: environment wins, then .env ----------------------------------
HOOK="${HARVREALTOR_NET_DEPLOY_HOOK:-}"
if [ -z "$HOOK" ] && [ -f "$SRC_DIR/.env" ]; then
  HOOK=$(grep -E '^[[:space:]]*HARVREALTOR_NET_DEPLOY_HOOK[[:space:]]*=' "$SRC_DIR/.env" \
         | head -1 | cut -d= -f2- | tr -d '"'\''\r' | xargs || echo "")
fi

if [ -z "$HOOK" ]; then
  say "HARVREALTOR_NET_DEPLOY_HOOK is not set — skipping the .net rebuild."
  say "harvrealtor.net will keep serving its last prerender until someone deploys."
  say "See the ONE-TIME SETUP block at the top of $0"
  exit 0
fi

# --- Wait for Pages to actually serve this edition --------------------------
# The prerender fetches PAGES_URL from inside the Vercel build. Firing before
# the CDN has the new file just bakes the previous day again, silently.
say "waiting for Pages to serve $FEED_DATE ..."
LIVE=""
for _ in $(seq 1 "$POLL_TRIES"); do
  LIVE=$(curl -sf --max-time 15 -H 'Cache-Control: no-cache' "$PAGES_URL" \
         | python3 -c "import json,sys;print(json.load(sys.stdin).get('date',''))" 2>/dev/null || echo "")
  [ "$LIVE" = "$FEED_DATE" ] && break
  sleep "$POLL_SLEEP"
done

if [ "$LIVE" != "$FEED_DATE" ]; then
  say "Pages still serving '${LIVE:-unknown}' after $((POLL_TRIES * POLL_SLEEP / 60)) min — NOT rebuilding"
  say "a rebuild now would re-bake the old feed; re-run this script once Pages catches up"
  exit 0
fi
say "Pages is serving $FEED_DATE"

# --- Fire ------------------------------------------------------------------
RESP="/tmp/net-rebuild-resp-$$.json"
CODE=$(curl -s -o "$RESP" -w '%{http_code}' --max-time 30 -X POST "$HOOK" || echo "000")

if [ "$CODE" = "200" ] || [ "$CODE" = "201" ]; then
  echo "$FEED_DATE" > "$STAMP"
  JOB=$(python3 -c "import json;d=json.load(open('$RESP'));print((d.get('job') or {}).get('id',''))" 2>/dev/null || echo "")
  say "✅ harvrealtor.net rebuild queued for $FEED_DATE (job ${JOB:-n/a})"
  say "   prerendered HTML will carry this feed in a few minutes"
else
  say "⚠️  deploy hook returned HTTP $CODE — harvrealtor.net keeps its previous prerender"
  say "   (not fatal: the site still self-corrects in the browser after hydration)"
fi

rm -f "$RESP"
exit 0
