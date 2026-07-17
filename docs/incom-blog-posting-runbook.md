# harvrealtor.com (InCom / Drupal) — Daily Blog + Interactive-Inventory Publishing Runbook

> **What this covers:** exactly how to publish the daily market update to the **main
> website** harvrealtor.com (InCom-hosted Drupal site). Two targets, one flow:
>   1. **BLOG** — a NEW dated blog entry (`/node/add/blog`).
>   2. **LANDING** — the fixed *"Alameda County Real Estate Interactive Inventory"*
>      page, **node 1319025**, edited in place (body swapped, everything else preserved).
>
> Both get the **same** body: a daily newsletter writeup + an interactive Plotly chart.
> This is **separate** from the daily email / teamrealtyexperts.com flow (`run-daily.js`)
> and is **not** wired into it — run it as the steps below.
>
> Established + verified end-to-end in a browser on 2026-06-03 (commit `15923af`).

---

## 0. The one constraint that dictates everything

**InCom's Drupal body filter STRIPS inline `<script>` and truncates everything after
the first one — but it PRESERVES external `<script src="…">`.**

Consequences (learned the hard way — see `docs/troubleshooting` / memory
`project-incom-cms-chart-fix.md`):

- The interactive **chart cannot be an inline `<script>`**. Its data/`Plotly.newPlot`
  call must live in an **external `.js` file hosted on GitHub Pages**, referenced via
  `<script src>`. `generate-cms-page.js` does this automatically (`alameda-chart-MMDDYY.js`).
- The chart JS **must be hosted on GitHub *Pages*** (`…github.io/…`), **NOT**
  `raw.githubusercontent.com` — raw serves `text/plain` + `nosniff`, so browsers refuse
  to execute it as a script.
- The newsletter is ordered **before** the chart in the body, so even a worst-case
  truncation can't eat the editorial content.

If you ever see the chart area blank or the newsletter cut off, this is why — the body
contains an inline `<script>`, or the external chart JS isn't hosted/reachable yet.

---

## 1. TL;DR — the command sequence (run from the project root)

```bash
cd ~/Library/CloudStorage/GoogleDrive-*/My\ Drive/ClaudeCode/RealtyExperts-Daily-Email   # (Mac)
# or:  ~/workspaces/RealtyExperts-Daily-Email                                              # (VPS)

# 1. Compose today's editorial into cms-content.json   (see §3 — do NOT assume it's current)
# 2. Build the CMS artifacts (html + meta + EXTERNAL chart js)
node generate-cms-page.js --date MM/DD/YY

# 3. Host the chart JS (+ artifacts) on GitHub Pages.  Mac: push-to-github.sh (fresh clone).
bash push-to-github.sh
#    VPS: git add alameda-chart-MMDDYY.js alameda-interactive-MMDDYY.html cms-meta-MMDDYY.txt && git commit && git push

# 4. WAIT ~1–2 min, then confirm the chart JS is live and executable:
curl -sI "https://fremontrealtyexperts-510.github.io/RealtyExperts-Daily-Email/alameda-chart-MMDDYY.js" | grep -iE "HTTP|content-type"
#    want:  HTTP… 200   AND   content-type: application/javascript

# 5. Dry-run the InCom publish (logs in, scrapes forms, writes intended POST to /tmp — submits nothing)
node post-to-incom.js --dry-run

# 6. Go live (BLOG create + LANDING edit)
node post-to-incom.js

# 7. VERIFY the live pages (do NOT trust the script's "✅" — see §6). The gate:
node verify-cms-publish.js     # asserts the LIVE chart VALUES match RE-v2 (not just "bars exist")
```

Order matters: **generate → push (host chart JS) → post-to-incom.** If you post before the
chart JS is on Pages, the chart 404s in browsers until Pages catches up.

---

## 2. Architecture — files & what each does

| File | Role |
|---|---|
| `cms-content.json` | **Daily editorial input.** `{ newsletter_html, meta:{description,keywords,copyright?,robots?} }`. Composed each morning (§3). |
| `generate-cms-page.js` | Builds the CMS artifacts. Reads `cms-content.json` (editorial) **+** the master sheet's **`RE-v2`** tab live (chart data, 12 cities). Writes 3 files (§4). |
| `alameda-interactive-MMDDYY.html` | The node **body** posted to both blog + landing. Newsletter (inline HTML) + `<div id="chart">` + `<script src=…alameda-chart-MMDDYY.js>`. |
| `alameda-chart-MMDDYY.js` | **External** chart data + `Plotly.newPlot('chart',…)`. **Must be hosted on GitHub Pages.** |
| `cms-meta-MMDDYY.txt` | Title / copyright / description / keywords / robots sidecar (parsed by `post-to-incom.js`). |
| `push-to-github.sh` | Hosts the 3 CMS artifacts on GitHub Pages (copies them into a fresh clone, commits, pushes). The chart JS hosting is the critical part. |
| `post-to-incom.js` | Logs into Drupal and publishes BLOG + LANDING (§5). Flags: `--dry-run`, `--blog-only`, `--landing-only`, `--date`, `--html`, `--meta`. |
| `lib/incom-client.js` | Headless Drupal client (curl-based): `login()`, `getForm()` (scrapes form_token/form_id/changed), `postNode()`, `extractFormFields()`. |
| `lib/google-sa.js` | Service-account reader for the `RE-v2` sheet (chart data). |

**Credentials** live in `.env`: `INCOM_LOGIN_URL`, `INCOM_USER`, `INCOM_PASS`
(read by `readIncomCreds()`). No CAPTCHA / 2FA on this Drupal login.

---

## 3. Step 1 — compose `cms-content.json` (the editorial)

`cms-content.json` is the **only** hand-composed input. It holds the harvrealtor.com
newsletter (a regional-grouped writeup, different layout from the email) + SEO meta.

⚠️ **It is NOT auto-current.** The Mac launchd auto-pull / git sync can revert it to the
last-committed (often *yesterday's*) version mid-session. **Always re-compose it fresh**
and sanity-check the numbers before generating. Quick check:

```bash
python3 -c "import json,re;h=json.load(open('cms-content.json'))['newsletter_html'];print('today?' , '2,849' in h, ' stale?', '2,909' in h)"
```

Structure to match (HTML, uses entities like `&mdash;`, `&rsquo;`, `&amp;`):

```
newsletter_html:
  <div class="section-bar-re">REAL ESTATE</div>      ← rate stat-line, 3 paragraphs
  <h3>Fremont & Milpitas</h3>  <ul>… per-city new / active …</ul>
  <h3>I-880 Corridor</h3>      <ul>…</ul>
  <h3>Tri-Valley</h3>          <ul>…</ul>
  <h3>Oakland & Contra Costa</h3> <ul>…</ul>
  <div class="section-bar-stocks">STOCKS</div>       ← stat-line + 2 paragraphs
  <div class="section-bar-economy">ECONOMY</div>     ← stat-line + 2 paragraphs
  <div class="section-bar-crypto">CRYPTOCURRENCY</div>← stat-line + 1 paragraph
  <div class="sources-box">…</div>
  <blockquote class="disclaimer">…</blockquote>
meta:
  description  (~20 words, no HTML, ≤1024 chars)
  keywords     (comma-separated, ≤450 chars)
```

The CSS classes are styled by `STYLE_BLOCK` inside `generate-cms-page.js` — just reuse the
class names; don't inline styles. The numbers come from the same data as the daily email
(`daily-market-template.json` + the dated MLS pivot). **Tip:** build it with a small Python
script (`json.dump`) to avoid hand-escaping; verify with a today-vs-stale grep before moving on.

---

## 4. Step 2 — generate the CMS artifacts

```bash
node generate-cms-page.js --date 06/03/26
# → wrote alameda-interactive-060326.html (12 cities, ~8.8 KB)
#        + cms-meta-060326.txt
#        + alameda-chart-060326.js
```

- The **12-city chart** is read **live** from the master sheet `RE-v2!A1:Z40`
  (sheet id `1YxbK29giJO6XDQAV3RHXml2vjMejmtBpZfD3ICW_gTw`). Make sure the sheet has been
  refreshed with today's MLS data first (it is, if Harv ran his morning export).
- Sanity-check the generated body **before** publishing:

```bash
python3 - <<'PY'
h=open('alameda-interactive-060326.html').read(); js=open('alameda-chart-060326.js').read()
print('inline newPlot in body (want 0):', h.count('Plotly.newPlot'))
print('references external chart js  :', 'alameda-chart-060326.js' in h)
print('newsletter present            :', 'Local board' in h and '2,849' in h)
print('chart js has newPlot          :', js.count('Plotly.newPlot'))
PY
node --check alameda-chart-060326.js && node --check generate-cms-page.js
```

---

## 5. Steps 3–6 — host the chart, then publish

### Host the chart JS (GitHub Pages)
```bash
bash push-to-github.sh          # Mac (fresh clone — Mac .git is intentionally broken)
```
`push-to-github.sh` already copies `alameda-chart-${DATE}.js`,
`alameda-interactive-${DATE}.html`, `cms-meta-${DATE}.txt`. Then **wait 1–2 min** and confirm:
```bash
curl -sI "https://fremontrealtyexperts-510.github.io/RealtyExperts-Daily-Email/alameda-chart-060326.js" | grep -iE "HTTP|content-type"
# HTTP/2 200   +   content-type: application/javascript   ← both required
```

### Dry-run, then publish
```bash
node post-to-incom.js --dry-run     # review /tmp/.../incom-plan-blog.json + incom-plan-landing.json
node post-to-incom.js               # LIVE
```

**What `post-to-incom.js` does under the hood** (`lib/incom-client.js`):

1. **Login** → POST `${INCOM_LOGIN_URL}?destination=visitor` with
   `edit[name]/edit[pass]/edit[form_id]=user_login/op=Log in`, cookie jar in `/tmp`.
2. **BLOG** (unless `--landing-only`): GET `https://www.harvrealtor.com/node/add/blog`,
   scrape the form, then POST it with:
   - `edit[title]` = `"At a Glance" Local Housing STATS and News MM/DD/YY` (from cms-meta)
   - `edit[path]`  = `HarvRealtor-daily-market-glance-MMDDYY`  ← the URL alias (must be unique/day)
   - `edit[format]` = `3`  (the input format that allows external `<script src>` + inline CSS)
   - `edit[body]` = the full `alameda-interactive-MMDDYY.html` (streamed from a temp file)
   - `edit[nodewords][description|keywords|copyright]` = from cms-meta
   - `edit[form_token]`, `edit[form_id]=blog_node_form`, `op=Submit`
   - Live URL → `https://www.harvrealtor.com/HarvRealtor-daily-market-glance-MMDDYY`
3. **LANDING** (unless `--blog-only`): GET `https://www.harvrealtor.com/node/1319025/edit`,
   scrape **all** fields (Drupal blanks any omitted field), then POST **only** swapping
   `edit[body]` + forcing `edit[format]=3` + `op=Submit`. Title / path
   (`alameda-Interactive`) / `changed` token / nodewords are preserved **as-scraped**.
   - Live URL → `https://www.harvrealtor.com/alameda-Interactive`

Drupal optimistic-concurrency: the edit form carries a hidden `edit[changed]` timestamp;
`getForm()` re-scrapes it each run, so a fresh run always has a valid token.

---

## 6. Step 7 — VERIFY (do not trust the script's "✅")

> `post-to-incom.js` reports success on HTTP 200, but a *failed* Drupal save also returns
> 200 (re-rendered form) and a redirect to `/node/<id>` looks like success. **Its "✅
> updated" is unreliable. Always verify the live page yourself.**

**(0) Automated VALUE-check — REQUIRED, run first:**
```bash
node verify-cms-publish.js          # verifies today's live blog + landing
node verify-cms-publish.js --local  # also gate the on-disk chart JS before posting
```
This is the authoritative Stage 5 gate. Unlike a presence check ("did Plotly draw? are
there bars?"), it validates the **plotted values**: it fetches the chart JS each LIVE page
actually loads, parses `var data`, and asserts — for all 12 cities × 7 categories — that the
numbers **equal an independent recompute from the RE-v2 tab** (its own header-based column
lookup, so it can't share a bug with `generate-cms-page.js`). It also fails if any category is
entirely zero across cities (the exact "New column blanked" regression of 2026-07-17, which
rendered 35 bars and passed every presence check while being wrong for a week) or if
`Active All != CO+DE+TH`. Exit 0 = pass. **Why this exists:** a chart can render perfectly and
still plot wrong numbers — bars-exist is not values-correct. The count-is-a-number check for the
live-inventory strip is JS-runtime, so it stays the Chrome-MCP step in (c) below.

The manual checks below stay useful for a human eyeball, but (0) is the gate that must pass.

**(a) Structural check** — newsletter survived + external chart referenced:
```bash
for U in "https://www.harvrealtor.com/HarvRealtor-daily-market-glance-060326" \
         "https://www.harvrealtor.com/alameda-Interactive"; do
  curl -sL "$U?cb=$(date +%s)" -o /tmp/p.html
  python3 - "$U" <<'PY'
import sys; h=open('/tmp/p.html',encoding='utf-8',errors='replace').read()
print(sys.argv[1])
print('  newsletter :', all(s in h for s in ['Local board','2,849','CRYPTOCURRENCY']))
print('  chart <src>:', 'alameda-chart-060326.js' in h)
print('  plotly lib :', 'cdn.plot.ly' in h)
PY
done
```

**(b) Functional check** — confirm Plotly actually drew the chart (Chrome MCP):
```js
// navigate to the page, wait ~6s, then eval:
JSON.stringify({
  plotlySVG: !!document.querySelector('#chart svg.main-svg'),
  barsDrawn: document.querySelectorAll('#chart g.points path').length,   // expect ~35–40
  newsletterOK: /Local board/.test(document.body.innerText) && /2,849/.test(document.body.innerText)
})
```
`plotlySVG:true` + `barsDrawn>0` + `newsletterOK:true` = fully working.

**(c) LIVE INVENTORY strip check (standing since 2026-07-16)** — the generator bakes a
gold "TODAY'S LIVE INVENTORY" strip (link to harvrealtor.net/live-inventory) between the
chart and the newsletter, plus a `live-inventory-teaser.js` external `<script src>` that
fills the live count. On BOTH pages:
```bash
curl -s "$U?cb=$(date +%s)" | grep -cE 'hb-li-total|live-inventory-teaser\.js'   # expect 2+
```
Functional (same Chrome MCP eval): `document.getElementById('hb-li-total').textContent`
must be a NUMBER (today's 4-city count), not the "hundreds of" fallback. Missing strip =
stale checkout or hand-edited body → regenerate + re-publish via §7. Never delete the
strip, its `hb-li-total` id, or the teaser `<script src>` when editing a node body.

---

## 7. Re-publishing / fixing an already-posted blog (IMPORTANT)

The blog `edit[path]` is dated, so **re-running `post-to-incom.js` for the same day skips
the blog** ("path is already in use" → idempotent). To **fix/replace** an existing blog
post you must **edit its node by ID**, not create a new one:

1. Find the node id from the live page:
   ```bash
   curl -sL "https://www.harvrealtor.com/HarvRealtor-daily-market-glance-MMDDYY" | grep -oE "node/[0-9]+" | sort -u
   ```
   (06/03/26's blog node was **1559901**.)
2. Edit it with the same mechanism as the landing — POST to `https://www.harvrealtor.com/node/<id>/edit`,
   swapping `edit[body]`, `edit[format]=3`, `op=Submit`, preserving the rest. Minimal Node:
   ```js
   const { IncomClient, readIncomCreds, extractFormFields } = require('./lib/incom-client');
   const { ENV_PATH } = require('./lib/config'); const fs = require('fs');
   const URL = 'https://www.harvrealtor.com/node/<id>/edit';
   const { url, user, pass } = readIncomCreds(ENV_PATH);
   const c = new IncomClient(); c.login(url, user, pass);
   const f = extractFormFields(c.getForm(URL).html);
   delete f['edit[body]']; f['edit[format]']='3'; f['op']='Submit';
   c.postNode(URL, f, fs.readFileSync('alameda-interactive-MMDDYY.html','utf8')); c.cleanup();
   ```
3. Verify per §6.

(The landing, node 1319025, is always an edit, so it has no idempotency issue.)

---

## 8. Quick reference

| Item | Value |
|---|---|
| Login | `.env` → `INCOM_LOGIN_URL` / `INCOM_USER` / `INCOM_PASS` |
| Blog create form | `https://www.harvrealtor.com/node/add/blog` (`form_id=blog_node_form`) |
| Blog live URL | `https://www.harvrealtor.com/HarvRealtor-daily-market-glance-MMDDYY` |
| Landing edit | `https://www.harvrealtor.com/node/1319025/edit` (`form_id=page_node_form`) |
| Landing live URL | `https://www.harvrealtor.com/alameda-Interactive` |
| Body input format | `edit[format] = 3` (allows external `<script src>` + inline CSS; still strips inline `<script>`) |
| Chart JS host (REQUIRED Pages) | `https://fremontrealtyexperts-510.github.io/RealtyExperts-Daily-Email/alameda-chart-MMDDYY.js` |
| Chart data source | master sheet `RE-v2` tab, id `1YxbK29giJO6XDQAV3RHXml2vjMejmtBpZfD3ICW_gTw` |

### Gotchas checklist
- [ ] `cms-content.json` re-composed for **today** (not reverted to yesterday by the sync).
- [ ] Chart JS hosted on **Pages** (200 + `application/javascript`) **before** posting.
- [ ] Order: **generate → push → wait → post-to-incom**.
- [ ] **Run `node verify-cms-publish.js`** — the value-check gate (chart values == RE-v2, no
      blank category). `post-to-incom.js`'s success message and "bars rendered" both lie; matching
      *values* do not.
- [ ] Re-publishing the blog = **edit the node by id**, not re-create.
- [ ] Never put the chart as an **inline** `<script>` — Drupal eats it + everything after.
