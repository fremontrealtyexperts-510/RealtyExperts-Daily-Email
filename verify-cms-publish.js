#!/usr/bin/env node
/**
 * verify-cms-publish.js  [--date MM/DD/YY] [--local] [--quiet]
 *
 * Stage 5 VALUE-CHECK for the harvrealtor.com daily publish.
 *
 * A presence check ("did Plotly draw? are there bars?") is NOT a correctness
 * check. On 2026-07-17 the interactive chart rendered 35 bars and passed every
 * presence test while the entire "New" column was silently 0 (a column-mapping
 * regression that had shipped for a week). This verifier checks the PLOTTED
 * VALUES, not just that pixels exist:
 *
 *   1. The chart JS the LIVE page loads is reachable + parseable.
 *   2. All 12 chart cities are present.
 *   3. NO category ("CO","DE","TH","Active All","New","CS","PEND") is entirely
 *      zero across cities  ← the exact "blank column" failure mode.
 *   4. Per city: Active All == CO + DE + TH   (internal consistency).
 *   5. Per city / per category: the chart value EQUALS a value recomputed
 *      INDEPENDENTLY from the RE-v2 tab (its own header-based column lookup, so
 *      it cannot share a bug with generate-cms-page.js). This is the real
 *      value-check: it catches wrong numbers, not just missing ones.
 *   6. Structural: newsletter markers + Plotly lib + live-inventory strip
 *      (`hb-li-total` + teaser `<script src>`) present in the live HTML.
 *
 * Note: the live-inventory COUNT is filled by JS at runtime, so over HTTP the
 * strip shows its "hundreds of" fallback — this script confirms the strip is
 * present; the count-is-a-number check stays the Chrome-MCP step in the runbook.
 *
 * Targets the two LIVE pages by default. --local additionally value-checks the
 * on-disk alameda-chart-MMDDYY.js as a PRE-publish gate. Exit 0 = all pass.
 *
 * Usage:
 *   node verify-cms-publish.js                 # verify today's live blog + landing
 *   node verify-cms-publish.js --date 07/17/26
 *   node verify-cms-publish.js --local         # also gate the on-disk chart JS
 */
const https = require('https');
const fs = require('fs');
const path = require('path');
const sa = require('./lib/google-sa');
const { TEMPLATE_PATH } = require('./lib/config');

const SHEET_ID = '1YxbK29giJO6XDQAV3RHXml2vjMejmtBpZfD3ICW_gTw';
const REV2_RANGE = 'RE-v2!A1:Z40';
const SCOPE = 'https://www.googleapis.com/auth/spreadsheets.readonly';
// Mirror generate-cms-page.js (kept local so the verifier stays independent of it).
const CATS = ['CO', 'DE', 'TH', 'Active All', 'New', 'CS', 'PEND'];
const CITY_ORDER = [
  'Fremont', 'Union City', 'Castro Valley', 'Danville', 'Hayward', 'Livermore',
  'Newark', 'Pleasanton', 'San Ramon', 'Dublin', 'San Leandro', 'Milpitas',
];

function httpGet(url, headers = {}) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers }, (r) => {
      let s = '';
      r.on('data', (c) => (s += c));
      r.on('end', () => resolve({ status: r.statusCode, body: s }));
    }).on('error', reject);
  });
}

// Independent RE-v2 -> expected chart values (header-based; does NOT reuse the
// generator's parseRev2, so a shared off-by-one cannot hide here).
async function expectedFromRev2() {
  const token = await sa.getAccessToken(SCOPE);
  const r = await httpGet(
    `https://sheets.googleapis.com/v4/spreadsheets/${SHEET_ID}/values/${encodeURIComponent(REV2_RANGE)}?valueRenderOption=UNFORMATTED_VALUE`,
    { Authorization: `Bearer ${token}` }
  );
  if (r.status !== 200) throw new Error(`RE-v2 read HTTP ${r.status}: ${r.body.slice(0, 200)}`);
  const rows = JSON.parse(r.body).values || [];
  if (rows.length < 2) throw new Error('RE-v2 returned no data rows');
  const H = rows[0].map((h) => String(h || '').trim().toLowerCase());
  const col = {
    thA: H.findIndex((h) => h.startsWith('th active')),
    thP: H.findIndex((h) => h.startsWith('th pending')),
    coA: H.findIndex((h) => h.startsWith('co active')),
    coP: H.findIndex((h) => h.startsWith('co pending')),
    ddA: H.findIndex((h) => h.includes('du/de/ph') && h.includes('active')),
    ddP: H.findIndex((h) => h.includes('du/de/ph') && h.includes('pending')),
    cs: H.findIndex((h) => h.includes('all cs')),
    nw: H.findIndex((h) => h.includes('all new')),
  };
  for (const [k, v] of Object.entries(col)) {
    if (v === -1) throw new Error(`RE-v2 header missing the ${k} column (got: ${rows[0].join(' | ')})`);
  }
  const n = (row, i) => { const x = parseInt(row[i], 10); return Number.isFinite(x) ? x : 0; };
  const byCity = {};
  for (const row of rows.slice(1)) {
    const city = String(row[0] || '').trim();
    if (!city) continue;
    const thA = n(row, col.thA), coA = n(row, col.coA), ddA = n(row, col.ddA);
    byCity[city.toLowerCase()] = {
      CO: coA, DE: ddA, TH: thA, 'Active All': thA + coA + ddA,
      New: n(row, col.nw), CS: n(row, col.cs), PEND: n(row, col.thP) + n(row, col.coP) + n(row, col.ddP),
    };
  }
  return byCity;
}

function parseChartData(js) {
  const chunk = js.split(/var\s+baseLayout/)[0];
  const m = chunk.match(/var\s+data\s*=\s*(\[[\s\S]*\])\s*;?\s*$/);
  if (!m) throw new Error('could not locate `var data = [...]` in chart JS');
  return JSON.parse(m[1]);
}

// The core value-check. Returns an array of human-readable issues ([] = pass).
function checkChartValues(chartData, expected) {
  const issues = [];
  const names = new Set(chartData.map((d) => d.name));
  for (const c of CITY_ORDER) if (!names.has(c)) issues.push(`missing city series: ${c}`);

  const catTotal = Object.fromEntries(CATS.map((c) => [c, 0]));
  for (const d of chartData) {
    for (const cat of CATS) { const i = d.x.indexOf(cat); if (i >= 0) catTotal[cat] += (d.y[i] || 0); }
  }
  for (const cat of CATS) if (catTotal[cat] === 0) issues.push(`category "${cat}" is ZERO for every city (blank column)`);

  for (const d of chartData) {
    const val = (c) => d.y[d.x.indexOf(c)];
    const co = val('CO'), de = val('DE'), th = val('TH'), aa = val('Active All');
    if (aa !== co + de + th) issues.push(`${d.name}: "Active All" ${aa} != CO+DE+TH (${co + de + th})`);
    const exp = expected[d.name.toLowerCase()];
    if (!exp) { issues.push(`${d.name}: no RE-v2 row to cross-check against`); continue; }
    for (const cat of CATS) {
      const cv = val(cat);
      if (cv !== exp[cat]) issues.push(`${d.name} "${cat}": chart ${cv} != RE-v2 ${exp[cat]}`);
    }
  }
  return { issues, catTotal };
}

function structural(html, short) {
  return {
    newsletter: ['CRYPTOCURRENCY', 'homebuilder', 'harvrealtor.net/live-inventory'].every((s) => html.includes(s)),
    // 2026-07-19 redesign: the chart is self-rendering (ranked bars) — Plotly must
    // be GONE from the live body. Its presence means a stale pre-redesign body.
    noPlotly: !/plotly/i.test(html),
    liveStrip: html.includes('hb-li-total') && html.includes('live-inventory-teaser.js'),
    chartSrc: (html.match(/src=["']([^"']*alameda-chart-\d+\.js[^"']*)["']/) || [])[1] || null,
  };
}

async function verifyPage(label, url, short, expected) {
  const out = { label, url, ok: true, lines: [] };
  const r = await httpGet(url + `?cb=${label}${short}`);
  if (r.status !== 200) { out.ok = false; out.lines.push(`page HTTP ${r.status}`); return out; }
  const s = structural(r.body, short);
  out.lines.push(`newsletter+strip: ${s.newsletter && s.liveStrip ? 'OK' : 'MISSING'}  no-plotly: ${s.noPlotly ? 'OK' : 'STILL PRESENT (stale body)'}`);
  if (!(s.newsletter && s.liveStrip && s.noPlotly)) out.ok = false;
  if (!s.chartSrc) { out.ok = false; out.lines.push('no chart <script src> found'); return out; }
  out.lines.push(`chart src: ${s.chartSrc.replace(/^https?:\/\//, '')}`);
  let data;
  try { data = await chartFromUrl(s.chartSrc); }
  catch (e) { out.ok = false; out.lines.push(`chart JS: ${e.message}`); return out; }
  const { issues, catTotal } = checkChartValues(data, expected);
  out.lines.push(`category totals: ${CATS.map((c) => `${c}=${catTotal[c]}`).join('  ')}`);
  if (issues.length) { out.ok = false; issues.forEach((i) => out.lines.push('✗ ' + i)); }
  else out.lines.push(`values cross-checked against RE-v2: ${data.length} cities × ${CATS.length} categories all match`);
  return out;
}

async function chartFromUrl(url) {
  const r = await httpGet(url);
  if (r.status !== 200) throw new Error(`${url} -> HTTP ${r.status}`);
  return parseChartData(r.body);
}

async function main() {
  const argv = process.argv.slice(2);
  const opt = (n) => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : undefined; };
  let date = opt('--date');
  if (!date) { try { date = JSON.parse(fs.readFileSync(TEMPLATE_PATH, 'utf8')).date; } catch (_) { /* none */ } }
  if (!date) { console.error('No date — pass --date MM/DD/YY or ensure daily-market-template.json exists.'); process.exit(1); }
  const short = date.replace(/\//g, '');

  console.log('='.repeat(64));
  console.log(`  Stage 5 value-check — ${date}`);
  console.log('='.repeat(64));

  let expected;
  try { expected = await expectedFromRev2(); }
  catch (e) { console.error(`\n❌ Could not read RE-v2 source of truth: ${e.message}`); process.exit(1); }

  const targets = [
    ['BLOG', `https://www.harvrealtor.com/HarvRealtor-daily-market-glance-${short}`],
    ['LANDING', 'https://www.harvrealtor.com/alameda-Interactive'],
  ];
  const results = [];

  if (argv.includes('--local')) {
    const local = path.join(__dirname, `alameda-chart-${short}.js`);
    const out = { label: 'LOCAL', url: local, ok: true, lines: [] };
    try {
      const data = parseChartData(fs.readFileSync(local, 'utf8'));
      const { issues, catTotal } = checkChartValues(data, expected);
      out.lines.push(`category totals: ${CATS.map((c) => `${c}=${catTotal[c]}`).join('  ')}`);
      if (issues.length) { out.ok = false; issues.forEach((i) => out.lines.push('✗ ' + i)); }
      else out.lines.push('values match RE-v2 (pre-publish gate OK)');
    } catch (e) { out.ok = false; out.lines.push(e.message); }
    results.push(out);
  }

  for (const [label, url] of targets) {
    try { results.push(await verifyPage(label, url, short, expected)); }
    catch (e) { results.push({ label, url, ok: false, lines: [e.message] }); }
  }

  for (const r of results) {
    console.log(`\n  ── ${r.label}  ${r.ok ? '✅ PASS' : '❌ FAIL'}  (${r.url})`);
    r.lines.forEach((l) => console.log('     ' + l));
  }

  const allOk = results.every((r) => r.ok);
  console.log('\n' + '='.repeat(64));
  console.log(allOk ? '  ✅ Stage 5 value-check PASSED' : '  ❌ Stage 5 value-check FAILED — do not consider the publish done');
  process.exit(allOk ? 0 : 1);
}

if (require.main === module) {
  main().catch((e) => { console.error('Fatal:', e.message); process.exit(1); });
}

module.exports = { checkChartValues, parseChartData, expectedFromRev2 };
