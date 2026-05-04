# 2026-05-04 — Daily run + notification bug fix

First end-to-end run of the daily email workflow from the VPS mirror.
Surfaced a duplicate-and-malformed notification email problem, diagnosed it,
and shipped a fix.

---

## TL;DR

- Ran the full daily workflow on the VPS for the first time. All four
  primary outputs shipped: Agent Hub note, Outlook draft, todays-inventory
  page (3 of 4 slots), and the harvrealtor.com CMS HTML. Custom CBO
  debt-vs-GDP chart added under the Economy section.
- Discovered the Supabase notes-api notification function fired **4 emails
  for today's note (2 clean + 2 malformed)** instead of the historical 2.
- Root cause was local: `templates/agent-hub-post.js` used smart curly
  quotes in the title. The Supabase function smart-quotes the title and
  then RFC-2047-encodes it via an old SMTP library that produces a
  malformed `Subject:` header (truncated encoded-word, duplicate
  `MIME-Version`, unquoted boundaries). Some Outlook clients render this
  as raw MIME source.
- Fixed in commit `9441acc`. Two changes:
  1. Smart quotes → straight ASCII in the create-event title
  2. `notify_enabled: false` on the create POST so only the update PUT
     fires a broadcast (eliminates the duplicate)

Tomorrow's run should produce **exactly 2 clean emails** (1 confirmation
to HarvRealtor + 1 broadcast to the team list).

---

## What ran today

Stages executed manually (not via `run-daily.js` because of the
interactive Y/n prompts). All commands run from
`/home/harvey-n8n/workspaces/RealtyExperts-Daily-Email`.

| Step | Command | Output |
|---|---|---|
| Pre-flight | `node fetch-images.js` | Pulled today's `RE-Daily-1.png` + `RE-Daily-2.png` from Drive Raw-data folder |
| Pre-flight | `curl …mortgagenewsdaily.com…` | 30-yr 6.44%, 15-yr 6.01% |
| Pre-flight | `curl …investing.com/…/crude-oil` | WTI $105.48 (+3.47%) |
| Pre-flight | MS365 Graph search | Pulled "🌅 Into the sunset" Market Briefs body |
| Chart build | `python3 scripts/generate-debt-chart.py debt-vs-gdp-050426.png` | Custom CBO debt-vs-GDP PNG, navy historical + maroon projected, blue border |
| Stage 1 | `node create-post.js` | Agent Hub placeholder note created (note ID `9bb469c3-7dc1-445d-8f23-73bcfb747894`), QR generated |
| Stage 2 | `node generate-daily-email.js daily-market-template.json` | `daily-market-glance-050426.html` |
| Push | `git add … && git commit && git push` | Commit `4b596c5` pushed to GitHub |
| Stage 2.5 | `node update-note-body.js` | Note body updated with final HTML (this fired the team-broadcast notification — see bug section) |
| Stage 3 | `node update-glance-content.js --with-chart` | 3 of 4 slots updated; `html_display` slot failed (Mac-path issue) |
| Stage 4 | Python-to-curl pipe | Outlook draft created in `HarvRealtor@outlook.com` Drafts |
| Stage 5 | Python sed-style edits to `alameda-interactive-050126.html` | `alameda-interactive-050426.html` for harvrealtor.com CMS paste |
| Final | `node verify-deployment.js` | All 6 checks passed |

---

## The bug

### Symptom
Two notification emails arrived in `HarvRealtor@outlook.com` ~1 minute
apart for today's note update. The first (8:48 AM PT) displayed as
unparseable raw MIME source in Outlook for Mac. The second (8:49 AM PT)
rendered fine.

### Diagnostic process — what I actually did, in order

1. **Pulled both messages from Outlook via Graph API** with the `$value`
   endpoint to get the raw MIME source (not just the rendered body).

   ```bash
   curl -s -H "Authorization: Bearer $TOKEN" \
     "https://graph.microsoft.com/v1.0/me/messages/$ID/\$value"
   ```

2. **Compared headers byte-for-byte:**

   | Header | BAD email | GOOD email |
   |---|---|---|
   | `Subject` | `=?utf-8?Q?[Agent Hub] Confirmation: =e2=80=9c…STAT=` (truncated encoded-word, no `?=` close) | `[Agent Hub] Confirmation: "At a Glance" Local Housing STATS and News 05/04/26` (plain ASCII) |
   | `MIME-Version` | **Two copies** | One |
   | Top-level `Content-Type` | `text/plain` (conflicts with `multipart/mixed`) | Just `multipart/mixed` |
   | Boundary param | `boundary=attachment100` (unquoted) | `boundary="attachment100"` (quoted) |
   | Subject text | smart curly `"…"` (U+201C/D) | straight ASCII `"…"` |

   These are MIME library bugs (duplicate header, unquoted boundaries) —
   classic signs of an old/buggy SMTP library on the BAD path.

3. **Checked the note title in Supabase** — it was straight ASCII
   (matches what `update-note-body.js:137` PUTs). So the smart-quoting
   was happening **server-side inside the notification function**, not in
   our code — at least, that's what the evidence pointed to before step 5.

4. **Asked Harv for a Sent-folder screenshot from the
   `fremontrealtyexperts@gmail.com` account.** Critical move. Showed:
   - **Today: 4 emails** (2 BAD via BCC + 2 GOOD via TO)
   - **May 1 and every prior day: only 2 emails** (both GOOD)
   - The BAD pair includes a broadcast to the team list — meaning
     **the agents likely received the malformed email today**

5. **Code archaeology — grepped the create-post code path.** Found
   `templates/agent-hub-post.js:16`:

   ```js
   const title = `“At a Glance” Local Housing STATS and News ${data.date}`;
   ```

   `“` and `”` are smart curly quotes. So the smart quotes
   weren't introduced server-side — they were sent by **`create-post.js`
   itself** every time it created a note. The Supabase function did
   smart-quote the title, but it's also passing through whatever was
   already smart-quoted from the create call.

6. **Reconciled "why now":** smart quotes have been in the template
   since `2026-03-03` per git log, but today was the first day this VPS
   ran the full pipeline end-to-end (Mac probably wasn't running Stage 1
   the same way). So the same code that worked manually on Mac fired
   `create-post.js` on the VPS for the first time today, exposing the
   latent bug.

### Why two emails, not one

Two separate events fired notifications:
- **Create event** (from `create-post.js`) — payload had no
  `notify_enabled`, Supabase defaulted to firing — used title with
  smart quotes — produced **BAD pair**
- **Update event** (from `update-note-body.js`) — payload had
  `notify_enabled: true` — used title with straight quotes — produced
  **GOOD pair**

Each event produces 2 emails (1 confirmation to owner + 1 broadcast to
team), so 2 events × 2 = **4 emails per day**.

---

## Fix (commit 9441acc)

### Change 1 — `templates/agent-hub-post.js`

```diff
-  // Title with smart/curly quotes
-  const title = `“At a Glance” Local Housing STATS and News ${data.date}`;
+  // Straight ASCII quotes only. Smart quotes (U+201C/D) trip an RFC 2047
+  // encoding bug in the Supabase notes-api notification function.
+  const title = `"At a Glance" Local Housing STATS and News ${data.date}`;
```

### Change 2 — `create-post.js`

```diff
   const response = await notesApiPost({
     title,
     body,
     category: ['at-a-glance'],
     visibility: 'public',
     body_format: 'html',
     author_name: 'REALTY EXPERTS',
+    notify_enabled: false,
   }, adminToken, nonce);
```

### Verification before commit

- `node --check` on both files: OK
- Dry-test: loaded `daily-market-template.json`, called `buildPost()`,
  confirmed title has straight quotes and zero smart quotes

### Sync

Pushed to `origin/main`. Mac auto-pulls within 15 minutes via the
launchd job at `~/Library/LaunchAgents/com.harvbalu.realty-email-pull.plist`.

---

## How to verify tomorrow

After tomorrow's run, open Gmail Sent folder for
`fremontrealtyexperts@gmail.com`. Expected:

- **Exactly 2 emails** for the daily note
- Both subjects show **straight ASCII `"…"`** (not raw `=?utf-8?Q?…`)
- One to `HarvRealtor` (confirmation), one to `melrosehomes …` (broadcast)

If you see 4 emails: Change 2 (`notify_enabled: false`) wasn't honored
on create. The 4 will all be readable (Change 1 still works) but you
get 2 extra. Fall-back is to skip the create event entirely and have
`update-note-body.js` do create-or-update logic.

If you see 2 emails but they're malformed: Change 1 wasn't enough.
Smart-quotes are coming from somewhere else. Re-grep the codebase for
`“|”|“|”`.

---

## Open follow-ups (none block tomorrow's run)

1. **Inventory chart slot on todays-inventory page** — `upload-inventory-chart.js`
   hardcodes `/Users/harvinderbalu1/.../latest_inventory_chart.html`,
   which doesn't exist on the VPS. Today's run kept yesterday's chart
   in that slot. To fix permanently, generate the chart locally on the
   VPS (port the Plotly+Sheets build) or change the hardcoded path.

2. **Plotly bar chart inside `alameda-interactive-050426.html`** — the
   per-city bars (lines ~261+) are still yesterday's numbers. The
   header/data widgets/headlines/new debt chart embed are today's, but
   the `data = [{…}]` block needs a per-category breakdown
   (CO/DU/DE/TH/Pending/CS) we don't currently extract from `RE-Daily-1.png`.

3. **Orphan commit `b672601`** still publicly fetchable on GitHub
   (the WORKSPACE-HANDOFF doc was force-push-scrubbed but the orphan SHA
   is still served). Pending decision on whether to flush GitHub's
   cache via toggle-private-then-public.

4. **Underlying Supabase encoding bug** — the function still mishandles
   smart quotes if any future caller sends them (iOS autocorrect, paste
   from Word, etc.). Today's commit removes the only known caller, but
   the function itself remains fragile. Fix lives in the Agent Hub repo
   (`~/Library/CloudStorage/OneDrive-Personal/ClaudeCode/REALTY-EXPERTS-Agent-Hub/`)
   and needs `SUPABASE_ACCESS_TOKEN` to deploy.

---

## References

- Bug-fix commit: `9441acc`
- Daily-output commit: `4b596c5`
- Today's note ID: `9bb469c3-7dc1-445d-8f23-73bcfb747894`
- Today's email URL: <https://fremontrealtyexperts-510.github.io/RealtyExperts-Daily-Email/daily-market-glance-050426.html>
- Today's Agent Hub URL: <https://teamrealtyexperts.com/share/9bb469c3-7dc1-445d-8f23-73bcfb747894>
