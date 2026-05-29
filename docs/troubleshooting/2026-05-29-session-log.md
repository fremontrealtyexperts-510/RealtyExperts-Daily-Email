# Session Log — 2026-05-29

Daily 05/29 "At a Glance" run + first daily chart by request (SF rent) + a critical
double-broadcast diagnosis. Newest-first.

---

## 05/29 daily report — shipped clean

- **Inventory confirmed up front** (new standing rule): stated 2,964 active / 216 new /
  216 CS / Fremont 21/372 before publishing so Harv could match it against Drive.
- **"FTW Rent In SF" chart** (`sf-rent-052926.png`, by Harv's request) built with matplotlib:
  SF ties NYC at $5,500/2BR, callout "+20-25% YoY on AI hiring → TIED for #1." Embedded in
  the **Real Estate** section of the email, Agent Hub post `4312ed00`, and the alameda CMS HTML.
- Market commentary from today's MB "🤖... ❄️ Snow day" (Snowflake best day ever, Pentagon
  drone equity stakes, Core PCE 3.3% → market leaning toward a Fed hike, CFTC drops Gemini case).
- Rates: MND stamp lagged at 5/28 (6.59/6.11); today's MB independently quoted 6.59/6.11 →
  current, used them (per the MND-lag cross-check rule).
- Broadcast fired; commit `49d2c7b`; `verify-deployment.js` → all 6 green.
- alameda + `cms-meta-052926.txt` built (basic style, SF chart in RE, no View-link / no Agent Hub source).

## New standing rule: confirm the inventory number before publishing
When Harv says "do it," echo one line (active / new / CS + Fremont) from the Drive file so
he can match it before anything broadcasts. Saved: `feedback_confirm_inventory_number_before_publish.md`.

## CRITICAL OPEN ISSUE — daily broadcast goes out as TWO BCC-batch emails

**Symptom:** Harv received 3 emails for the 05/29 broadcast — 1 confirmation (correct) + **2
broadcast emails** to two disjoint BCC batches of agents. Should be 1 confirmation + 1 broadcast.

**Diagnosis (how found):**
- Pulled today's "[Agent Hub]" emails via Graph; both broadcasts were "Updated Note," same
  minute, **disjoint BCC lists** (~13-14 each) → one trigger, not a client double-fire.
- The daily pipeline fired `update-note-body.js` exactly once. The split happens **server-side**:
  the notes-api batches the agent BCC list (~15/email). The roster grew from ~17 to ~27+, so the
  single broadcast now sends as 2 batch emails.
- Cross-referenced the 2026-05-04 log: prior fix got it to "1 confirmation + 1 broadcast"; the
  list growth re-broke the "1 broadcast" half.

**Confirmed audience (Harv):** the broadcast should reach the **entire agent list** ("pretty
much everybody") as **one consolidated email**. ~27 fits comfortably under Gmail's ~100-BCC limit.

**Why the daily pipeline can't fix it:** batching is in the notes-api edge function. VPS has no
`supabase` CLI, no `SUPABASE_ACCESS_TOKEN`, and the Agent-Hub repo is not on the VPS.

**Fix (must happen in the Agent-Hub repo):** `REALTY-EXPERTS-Agent-Hub/supabase/functions/notes-api/`
— send the full agent list in a single BCC (remove/raise the ~15 chunk to ~100, or collapse two
lists), then `supabase functions deploy notes-api`. Verify: Gmail Sent shows exactly 2 emails
(1 confirmation + 1 broadcast). Memory: `project_open_notes_api_bcc_double_broadcast.md`.

**Status:** OPEN. Until deployed, every VPS broadcast will split into 2. Needs to be done from the
Agent-Hub workspace (Mac) — offered to patch+deploy when Harv opens it there.
