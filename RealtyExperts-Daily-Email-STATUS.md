# RealtyExperts-Daily-Email — Working Status & Handoff

_Last updated: Sunday, November 15, 2026 (PT) · Update this at the end of each session._

This note is the shared handoff for the RealtyExperts-Daily-Email workspace. It lives **inside** the workspace and travels via **git/GitHub** (this workspace is a git repo, NOT rclone-synced). **Any Claude session — on the Mac or the `claud-realty-email` VPS session — should read this FIRST.**

---

## Where things stand (most recent first)

### Sunday, November 15, 2026 — catch-up: what changed between Sep 2 and Nov 15 (this file had gone stale)
Written from the Mac A.I session from `git log` (262 commits since 09/02; HEAD `e79ad2d`, "Daily email - 11/15/26") and this
workspace's Mac memory. The detail behind each line lives in the repo `CLAUDE.md` and the memory files named there.
- **The daily run never stopped.** Latest: Sunday 11/15/26, the weekly markets edition. Most days now run unattended;
  per-day notes are in memory `session-2026-MM-DD-daily-*.md`.
- **Mercy (Claude Duet) joined, 11/15/26.** Shares the Agent Hub setup: Duet channel *agent-hub*, Slack `#agent-hub`,
  signed `Mercy Daily Email:` / `Claude Daily Email:`. Mercy only READS this repo; its notes go to Drive
  `REALTY-EXPERTS-Agent-Hub/_daily-email/`. `.gitignore` gained a backstop (`inbox/`, `HANDOFF-*.md`, `*-mercy-*.md`,
  `_daily-email/`) on the Mac copy; it rides the next Mac push. Outlook folders: `Inbox › 0_RealtyExperts › Agent-Hub`
  (primary), `Inbox › 0_ Education › The Market` (source).
- **Rules and compliance:** Bay East MLS Rule 12.9 notice on every daily surface since 09/28 (`067bbdb`, generator-owned,
  never hand-edit); Stage 6 (thebayarearealestate.com, Newark) is statistics only since 09/27; NO charts or series derived
  from ISM, S&P Global PMIs, MBA's weekly survey or ADP (license terms 10/28 and 11/05), quote their numbers in text only.
- **Data guards:** an implausible MLS sheet-name date is refused (`e3c2bae`, 10/02); the `MLS_Listing_Summary_Spreadsheet`
  export name is accepted (`68c8e78`); `mls-pipeline.js` reads Sheets with UNFORMATTED_VALUE (`072c53e`, 10/14); PCH
  counts as Active (10/06); validate every Market Briefs number; Brent stays on `get-brent.js` (watch the front-month roll).
- **Broadcast:** bounces counted in `verify-broadcast` and `check-surfaces` (`4ef8385`, 10/30, after Google rejected batch
  2 of 100). Exit 4 = 5+ agents bounced: never re-fire. On FAILED, read Supabase `function_logs` before anything (11/13:
  the verifier said FAILED but 99 agents were sent once).
- **Web and app:** chart scripts load from commit-pinned jsDelivr when it answers, else the Pages URL (`fea3f89`, 10/25);
  every harvrealtor.com daily post gets a share image (`2bc14f2`, 10/26); the app feed's rate tiles follow the day's MND
  figure via an auto job (`714f528`, 09/17); `assistant-inventory.json` is no longer derived or published here, it moved
  to harvrealtor.net (`6827190`, 11/09).
- **Plumbing:** VPS cron scripts and Mac launchd wrappers are versioned in `scripts/` (09/13); the live-inventory refresh
  runs from a local clone on the Mac (Drive EDEADLK); the Agent Hub scheduled-post sweep (09/03) and request-tracker hourly
  tick (`1263be2`, 11/05) live here too.
- **Monthly city stats** keep landing as `market-stats: <City> <Month> 2026` commits (latest: Union City October, 11/09).
- **⚠️ Mac Drive note (11/15):** Google Drive for desktop on the Mac stopped syncing from about 1:30 PM PT. Git is
  unaffected (it works on the local files), but Drive-side copies may lag until it recovers.

### Sep 2, 2026 (evening) — `live-inventory.json` is STATISTICS ONLY (version 2) and its per-listing history is PURGED
Commit `15291df` then the rewrite `3af4300`: the public feed carries no per-listing rows, addresses or MLS numbers anymore (Bay East MLS Rules 12.12 / 12.15.4 / 12.16(l)): per city and for the five together, `counts` (every live status), an `allLive` block (the same figures the history record carries) and a `market` block (the homes on the market: medians, new this week, types, price bands, days-on-market buckets, medians by type and status). The history record and the feed share one set of helpers in `generate-live-inventory.js`. `live-inventory-teaser.js` accepts version 2; `derive-assistant-inventory.py` reads the blocks (its price bands are now the site's seven). Every consumer was deployed BEFORE the switch (harvrealtor.net parser + app parser accept version 1 and 2). **History rewrite:** `git filter-repo --path live-inventory.json --invert-paths` on a fresh clone, force-pushed (412 commits, HEAD `3af4300`, the file now has exactly one commit); the VPS clone was reset to the new main the same minute; a verified pre-purge bundle sits on the Mac at `~/Backups/RealtyExperts-Daily-Email-pre-purge/`. ⚠️ Any other clone of this repo must `git fetch && git reset --hard origin/main`. The `.git-pull-last-sha` on the Mac simply sees a new SHA and re-syncs.

### Sep 2, 2026 — `live-inventory.json` no longer itemizes Coming Soon (MLS rules)
The Bay East MLS Rules (10.1.1 item 12, and the note under 12.16(a)) keep Coming Soon listings off every public-facing product except the listing brokerage's own, and this feed is fetched by public pages (harvrealtor.net, the HarvRealtor app, the .com teaser strip). Commit `d711268`: `generate-live-inventory.js` still builds the per-city `counts` and the `inventory-history.json` record from EVERY live row (so no total moved: 695 on 09/02), but the published `listings` array now carries Active, New and Back on Market rows only (590 that day; 105 Coming Soon counted, never itemized). New top-level `listed` key documents the shape. Consumers read the Coming Soon figure from `counts[city].CS`: `live-inventory-teaser.js` (.com strip) now totals from `counts`; harvrealtor.net's parser drops any CS row that still arrives and takes totals from `counts`; the app's `parseSnapshot` does the same. `derive-assistant-inventory.py`'s note says the medians cover on-market rows only. Side fix in the same commit: `push-to-github.sh` now copies `assistant-inventory.json` (its public copy had sat at 07/23, because only the refresher pushed it and the refresher no-ops once the morning push has published the day). Still open, owned by the Web workspace: rebuild `/live-inventory` as a statistics page (other brokers' active rows are still itemized publicly), an aggregate-only feed with the repo history purged, and the 12.9 notice.

### Aug 21, 2026 — HarvRealtor APP feed added: `daily-report.json` (singleton)
New `generate-app-report.js` builds the HarvRealtor-branded feed the mobile app (Today's Report) and `harvrealtor.net/today` read, from the template + `cms-content.json` + `live-inventory.json`. Run in Stage 3 (template voice) and again in Stage 5 after `generate-cms-page.js` (Harv's voice); `push-to-github.sh` now copies `daily-report.json` + `cms-content.json`; `check-surfaces.sh` checks the feed's date (10 surfaces). One file, rewritten daily, nothing accumulates. The app no longer frames the RE email or reads harvrealtor.com RSS. Details: repo CLAUDE.md callout "The HarvRealtor APP feed".

### Aug 8, 2026 — Bidirectional git handoff wired
Added this STATUS.md and a controlled `scripts/git-sync-push.sh` so VPS-side handoffs reach the Mac through GitHub. Recent commits:
- `da9b6e1` git-sync: cover assistant-inventory.json and conflicted autostash pops
- `3865d91` Daily email - 08/07/26: Add Agent Hub note + QR code
- `38e1c4e` Add check-surfaces.sh: closing gate that verifies every daily surface

---

## Open items / next up
- (none recorded yet — add here as work lands)

---

## Setup notes (how this workspace is wired)
- **Sync transport: GIT via GitHub** (`origin` = `github-realty-email:fremontrealtyexperts-510/RealtyExperts-Daily-Email.git`). NOT rclone — rclone would corrupt the repo and fight the pull cron.
- **VPS → GitHub:** `scripts/git-sync-push.sh` — **scoped**: it commits + pushes ONLY this STATUS.md (and any file explicitly added to its allowlist), NOT the whole tree. This is deliberate: the workspace's generated data (`inventory-history.json`, `assistant-inventory.json`, `alameda-interactive-*.html`, `*.bak`) is authored on the **Mac** and only *consumed* on the VPS, so it must never be pushed from here.
- **GitHub → VPS:** existing `scripts/git-sync-pull.sh` (cron every 15 min) pulls Mac-authored commits and auto-heals generated-file conflicts to origin's copy. Left untouched.
- **To publish a VPS-side edit to the Mac:** add the file to the git-sync-push.sh allowlist (or commit it by hand) — do NOT `git add -A`.
- **VPS session:** drive it from **claude.ai/code** as **`claud-realty-email`**.
- **Note on memory:** per-project memory lives *outside* the workspace (`~/.claude/projects/…`) and does **not** travel with git — which is why this file exists. Keep it current.

---

_At the end of a session, update "Where things stand" and "Open items" above so the next session — on either machine — starts current._
