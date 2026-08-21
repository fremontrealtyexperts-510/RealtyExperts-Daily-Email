# RealtyExperts-Daily-Email — Working Status & Handoff

_Last updated: 2026-08-21 · Update this at the end of each session._

This note is the shared handoff for the RealtyExperts-Daily-Email workspace. It lives **inside** the workspace and travels via **git/GitHub** (this workspace is a git repo, NOT rclone-synced). **Any Claude session — on the Mac or the `claud-realty-email` VPS session — should read this FIRST.**

---

## Where things stand (most recent first)

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
