# Plan — Automate the MLS Run with Claude-in-Chrome + code

**Date:** 2026-06-01
**Goal:** Offload Harv's manual morning "MLS Run Report" (documented in OneNote → Realty Experts → Daily Reports → "MLS Run Report") so the daily inputs `RE-Daily-1.png` (summary table) and `RE-Daily-2.png` (bar chart) land in Google Drive `Raw-data` with minimal hands-on. After that, the existing email pipeline runs unchanged (`fetch-images.js` already pulls those two files).

**Decisions locked (2026-06-01):**
- Architecture = **browser exports the CSV, code builds the PNGs.** Claude-in-Chrome only does the browser-reliable part; a script does the deterministic data→image part. Chosen because Claude-in-Chrome runs inside the browser tab and cannot operate the macOS Save dialog, Drive's file-upload chooser, or the screenshot tool.
- MLS login = **username + password only** (no 2FA / CAPTCHA).

---

## Current manual workflow (5 phases, from the OneNote page)

1. **Pull from MLS (Paragon):** login `maxebrdi.clareityiam.net/idp/login` → SEARCH → Residential → Load Saved Search → **"RealtyExperts"** → Search (~3,175 listings) → Reports → **"MLS Defined Spread Sheet 4"** → Export → Export to CSV → All Listings → save Desktop `MLS_Defined_Spread_Sheet_4-MMDDYY.csv`.
2. **Land in Drive + master sheet:** Drive (`harvrealtor@gmail.com`) → `My Drive/Daily-Reports/Daily-Realty-Experts` → upload CSV → open it + master **"Alameda-County-New Stats-Daily"** → select-all/copy → paste into master's `MLS_Defined_Spread_4` tab.
3. **Capture visuals:** master's **"RE-v2"** tab recalculates → screenshot summary table ("bars") + bar chart ("graph").
4. **Publish to Raw-data:** in `Daily-Realty-Experts/Raw-data`, archive yesterday's `RE-Daily-1/2.png` (append date) → upload today's 2 screenshots → rename table → `RE-Daily-1.png`, chart → `RE-Daily-2.png`.
5. (Then Harv tells Claude Code "run the daily email" — existing pipeline.)

**New design collapses phases 2–4 into code.** Browser does phase 1 only (plus dropping the file where code can read it).

---

## Target architecture (Path B)

```
Claude-in-Chrome (Mac browser)                 Code (VPS, service account)
────────────────────────────────              ─────────────────────────────────
login → RealtyExperts saved search   ──CSV──▶  read newest MLS CSV from Raw-data
→ Reports → MLS Defined Spread Sheet 4         → compute RE-v2 pivot (city×type×status)
→ Export to CSV (auto-download into             → render RE-Daily-1.png (table)
   the Drive-for-Desktop Raw-data folder)       → render RE-Daily-2.png (bar chart)
                                                → upload both to Drive Raw-data
                                                         │
                                                         ▼
                                            existing pipeline: fetch-images.js → email
```

### Transport (browser → code), recommended
Set Chrome's **default download folder = the Google-Drive-for-Desktop local path that maps to `Daily-Reports/Daily-Realty-Experts/Raw-data`**, and turn **off** "Ask where to save each file." Then Export drops the CSV straight into Raw-data with no Save dialog and no manual upload; it syncs to Drive; the service account (already has Raw-data access) reads the newest `MLS_Defined_Spread_Sheet_4-*.csv`.
- *Fallback if Drive-for-Desktop is awkward:* run the renderer on the Mac reading `~/Downloads`, upload PNGs to Raw-data via the same service account. Keeps it off the VPS.

---

## Component 1 — Chrome agent prompt (the paste-in text)

A single, deterministic instruction block Harv pastes into Claude-in-Chrome. Outline:
- Preconditions: logged into the right Chrome profile; Chrome download dir already set to the Raw-data synced folder (one-time).
- Steps: open login URL → enter credentials → SEARCH → Residential → Load Saved Search → filter "My Searches" → click **RealtyExperts** → Search → wait for results grid → **Reports** → **MLS Defined Spread Sheet 4** → **Export** → **Export to CSV** → select **All Listings** → **Export** → confirm the file downloaded.
- Guardrails: verify the saved-search name is exactly "RealtyExperts" and the report is "MLS Defined Spread Sheet 4" before exporting; stop and report if listing count is wildly off (< 2,000 or > 5,000) so a bad search doesn't propagate.
- Credentials handling (decide at wiring time): (a) Harv completes the login, agent takes over; or (b) credentials inline in the prompt (note the tradeoff — the prompt text would hold a password).

## Component 2 — `mls-csv-to-images.js` (or .py) renderer

Input: newest `MLS_Defined_Spread_Sheet_4-*.csv` (from Raw-data or Downloads).
Output: `RE-Daily-1.png` (summary table) + `RE-Daily-2.png` (grouped bar chart), uploaded to Raw-data.

**Pivot spec (reverse-engineered from screenshots — confirm exact code maps from the sheet):**
- Rows = 15 cities: Fremont, Union City, Newark, Hayward, Danville, Milpitas, Oakland, Livermore, Castro Valley, Pleasanton, San Ramon, Dublin, Sunol, San Lorenzo, San Leandro + Total row.
- Property-type groups: **TH**, **CO**, **DU/DE/PH** (exact BT-code → group mapping = TBD from sheet; criteria BT set = DE, DU, PV, CO, TH).
- Per type, two status buckets: **Active/BOMK/PCH/New** and **Pending** (exact status-code → bucket mapping TBD from sheet; criteria status set = ACTV, BOMK, AC, NEW, PCH, CS, PEND).
- **Total** = sum of the 6 type×status cells (verified: Fremont 52+11+84+22+123+80 = 372; grand total = 2,964 ✓).
- **All CS** and **All New** = separate per-city counts (CS, NEW).
- Visual fidelity: both PNGs are embedded as clickable images in the client email, so match the current look — blue/white banded table with dark "Total" column (RE-Daily-1) and the branded grouped bar chart titled `www.TeamRealtyExperts.com` (RE-Daily-2). Rendering: matplotlib (consistent with the existing SF-rent chart; no new heavy deps) unless a styled HTML→PNG render proves cleaner for the table.

**Validation gate:** reproduce the 05/29 dataset and assert the output table equals the known numbers (Total 2,964 / All CS 216 / All New 216 / Fremont 372·46·21) before trusting it on live data.

---

## Open inputs needed from Harv

1. **Unblocks the build now:** share the master sheet **"Alameda-County-New Stats-Daily" (read-only)** with the service account `usrnumber22-claude@harvrealtor.iam.gserviceaccount.com`. That single share gives me the raw data (MLS_Defined_Spread_4 tab) + the exact RE-v2 formulas + the expected output to validate against. (Alternative: send one real exported CSV — but the share also lets me read the pivot formulas.)
2. **Needed at wiring time:** the local Mac path of the Drive-for-Desktop `Raw-data` folder (for the Chrome download dir). Likely `~/Library/CloudStorage/GoogleDrive-harvrealtor@gmail.com/My Drive/Daily-Reports/Daily-Realty-Experts/Raw-data` — confirm.
3. **Needed at wiring time:** MLS username + password, and the credential-handling choice (manual login vs. inline in prompt).

---

## Phased rollout

- **Phase A (build, offline):** write the renderer; validate against the 05/29 numbers. No browser, no creds. *(Blocked only on input #1.)*
- **Phase B (transport):** set Chrome download dir + Drive-for-Desktop; confirm a CSV dropped there is readable by the service account.
- **Phase C (Chrome prompt):** finalize Component 1; dry-run the browser half to a throwaway download.
- **Phase D (end-to-end):** real run → CSV → PNGs in Raw-data → existing email pipeline. Compare generated PNGs against a same-day manual run once before going hands-off.

## REVISION — 2026-06-01 (after first live browser test)

First Claude-in-Chrome run worked perfectly through Export (ran "RealtyExperts", 3,166 listings, clicked Export to CSV) but **froze on the macOS "Save As" dialog** — confirms a browser agent can't operate native dialogs. Fix: Chrome → Settings → Downloads → turn OFF "Ask where to save each file" so the export auto-saves with no dialog.

Harv's chosen split (supersedes the Drive-for-Desktop transport above):
1. **Claude-in-Chrome** downloads the CSV to the Mac (auto-save after the Chrome fix).
2. **Harv manually uploads** the CSV into Drive `Raw-data`.
3. **`mls-pipeline.js`** (built) does the rest, all in code — no manual paste, no screenshots:
   - reads the newest `MLS_Defined_Spread*` from Drive (service account),
   - writes the raw CSV into the master sheet's `MLS_Defined_Spread_Sheet_4` tab (keeps RE-v2/Interactive/blog tabs current) — **chose "also keep the master sheet current"**,
   - renders RE-Daily-1/2.png via `mls-csv-to-images.py`,
   - archives yesterday's PNGs and uploads today's to `Raw-data`.

Status: pipeline dry-run-validated (folder auto-located, CSV parse + render correct). Live writes pending two grants — **Raw-data folder = Editor** and **master sheet = Editor** for `usrnumber22-claude@harvrealtor.iam.gserviceaccount.com`. Will verify end-to-end on the first real CSV.

## Risks / notes
- Claude-in-Chrome reliability on the multi-step Paragon UI (dropdowns, modals) — the guardrail count-check catches a wrong search.
- Paragon export occasionally returns `.xlsx` vs `.csv` depending on the dialog; renderer should accept both.
- Today (06/01) `RE-Daily-1/2.png` already exist in Raw-data (generated as the OneNote example) — fine, the renderer overwrites by upload.
- The Google Sheet master stays intact; this runs alongside it (Liliana's parallel process, if any, is untouched).
