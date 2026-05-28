# Session Log — 2026-05-26 → 2026-05-28

Multi-day session covering three daily "At a Glance" runs, a batch of CMS/alameda
refinements, and a 05/28 inventory-correction incident. Newest work first.

---

## 2026-05-28 — Inventory correction (no re-broadcast) + re-upload-churn diagnosis

### What happened
A 05/28 daily report had **already run** that morning (~10:17 AM PT, commit `9de2a61`,
Agent Hub post `59faf96e`) and broadcast to the 17 agents. It used an early version of
the Drive inventory file showing **2,903 active / 185 new**. Liliana then re-uploaded a
**corrected** `RE-Daily-1.png` showing **2,943 active / 193 new**. Harv spotted the
mismatch between "today's Drive file" and the published report.

### How the information was found (diagnosis method)
1. **Pulled the live Drive file via the service-account JWT** (never the Drive MCP) and
   listed every `RE-Daily-1*` in the Raw-data folder (`1H3A4_Lryr9sgQw3x4JEW8jBss1vQiR4H`)
   with `modifiedTime` + size, newest first. Found the current `RE-Daily-1.png`
   (id `1XRAF…`, 144,562 bytes, modified 17:02Z) plus archived dated copies.
2. **Hash-compared** the committed `RE-Daily-1-052726.png` (yesterday) against the Drive
   archive `RE-Daily-1 052726.png` → identical sha256 (`55e067…`). Proved yesterday's
   05/27 run was byte-correct; nothing shipped was wrong.
3. **Read the published numbers directly** rather than trusting memory: `curl` the live
   GitHub Pages email + grep `NNN new listings` / `2,9NN active`. The live 05/27 email =
   171/2,901; the live 05/28 email = 185/2,903.
4. **Reconciled three distinct totals** — 171 (published 05/27), 185 (published 05/28,
   early file), 193 (corrected Drive file now). Confirmed the 185 came from the already-
   broadcast 05/28 run and the 193 is the corrected file.
5. Root cause: **the RE-Daily Drive file is re-uploaded with corrections after the morning
   run.** File names are unreliable (saw a `052926`-named file dated May 20, duplicate
   `050726` names) — trust the data + hash + modifiedTime, not the name.

### The fix (no second notification)
- Re-fetched corrected images, `cp` over `RE-Daily-1/2-052826.png`.
- Updated ONLY the RE inventory section of `daily-market-template.json` (rates were already
  correct at 6.59/6.11; corrected local totals 2,943/193/218 + per-city snapshot with
  day-over-day deltas vs 05/27). **Kept stocks/economy/crypto commentary verbatim** —
  verified it matched today's MB "🤖 Money bot" (Goldman +16%, Robinhood AI agents, SoFi
  stablecoin, oil spike, etc.), so no rewrite needed.
- Regenerated email, committed + pushed (`759f1c4`), verified raws 200.
- **Updated post `59faf96e` via a custom curl PUT with `notify_enabled: FALSE`** — NOT
  `update-note-body.js` (which hardcodes `true` and would re-broadcast). Reused the same
  note ID so the share URL + QR stayed valid.
- Refreshed glance-api slots + chart slot (from rebuilt alameda), created a corrected
  Outlook draft (TO/CC pre-filled), built `alameda-interactive-052826.html` (basic style)
  + `cms-meta-052826.txt`. `verify-deployment.js` → all 6 green.

### New standing rules from today
- **Confirm the inventory number before publishing.** Going forward, before Phase 3, echo
  one line of the numbers about to publish (active / new / closed sales + Fremont) so Harv
  can match against Drive. → `feedback_confirm_inventory_number_before_publish.md`
- **Re-upload churn + no-broadcast correction procedure** documented in
  `feedback_drive_file_reupload_churn.md`.

---

## 2026-05-27 — Daily run + Oil Workaround chart

- Full pipeline for 05/27 (post `20c432ff`, broadcast fired). Rates 6.61/6.14, board
  2,901 active / 171 new.
- Built the **Oil Workaround** chart (`oil-workaround-052726.png`, matplotlib) from the MB
  "🚗 Speed bump" Global Scoop item (Japan ME oil imports −67% YoY, U.S. +4x, total −39%).
  Embedded in the Economy section of both the email and the alameda HTML.
- Removed the always-zero **DU column** from the inventory chart (Harv flagged it as
  confusing) → x-axis is now 7 cols `["CO","DE","TH","Active All","New","CS","PEND"]`.
- Fixed the **CASTROVAEY → Castro Valley** legend typo.
- Repointed the alameda "View Full Email Version" link from the Agent Hub share URL to the
  **GitHub Pages** email URL (Agent Hub link wasn't clickable in the CMS embed).

---

## 2026-05-26 → ongoing — CMS / alameda refinements & new conventions

Established this session (all saved to memory):
- **Light-humor + professional tone** for the daily email — one wry line per section, in
  prose only, never in data. (`feedback_daily_email_tone_light_humor.md`)
- **Keep total volume tight** — RE ~5 short paras, Stocks/Econ 2 each, Crypto 1-2; per-city
  snapshot unchanged. (`feedback_daily_email_keep_it_tight.md`)
- **Alameda CMS prose tight** + **basic-style HTML** — the harvrealtor.com CMS doesn't
  render heavy CSS/JS cleanly. Keep the chart + 4 colored section bars; drop rate-box /
  data-box / highlight-box / loc-tag; use plain `stat-line` + `<h3>` + `<ul>`.
  (`feedback_alameda_cms_prose_tight.md`, `feedback_alameda_cms_html_basic_style.md`)
- **No "View Full Email Version" H2 link** and **no Agent Hub source line** in the alameda
  CMS HTML (public surface; both are internal links). The chart slot on
  teamrealtyexperts.com keeps the View link.
- **CMS metadata sidecar** — every alameda build also drops `cms-meta-MMDDYY.txt` (Title /
  Meta Description / Meta Keywords / Meta Copyright / Robots) for the InCom form.
  (`feedback_cms_metadata_sidecar.md`)
- scp brace-expansion gotcha: pull both files with the **unquoted** form
  `scp n8n:~/…/{alameda-interactive-MMDDYY.html,cms-meta-MMDDYY.txt} ~/Desktop/`.

---

## Recurring infra notes (confirmed this session)
- **MS365 token** dies with `IDX14100` (opaque-token quirk) several times a day on this
  VPS; refresh-and-retry works every time. Keep `offline_access` in the refresh scope.
- **Drive freshness** must use the service-account JWT (sees the Raw-data shared folder),
  never the Drive MCP.
- **git push** from the VPS works via the deploy-key SSH remote `github-realty-email`;
  `gh` CLI is NOT installed here, so `push-to-github.sh` (which needs `gh`) fails on the
  VPS — push directly instead.
