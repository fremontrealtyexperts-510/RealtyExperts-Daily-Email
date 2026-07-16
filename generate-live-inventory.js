#!/usr/bin/env node
/**
 * generate-live-inventory.js  [--date MM/DD/YY]  [--out <path>]
 *
 * Builds live-inventory.json for the harvrealtor.net /live-inventory page.
 *
 * Source: the newest dated "MLS_Defined_Spread_Sheet_4- MMDDYY" file in Drive
 * (the raw Paragon export, discovered the same way mls-pipeline.js getRows()
 * does), read via the service account with valueRenderOption=UNFORMATTED_VALUE.
 *
 * NOT the master sheet's MLS_Defined_Spread_Sheet_4 tab: reading the dated
 * sheet directly avoids depending on the master tab's fill timing. (The tab
 * itself is fine now — mls-pipeline.js also reads UNFORMATTED_VALUE, so $1M+
 * LPs land there as real numbers, not the old CSV-export "#########".)
 *
 * Filter: Fremont, Hayward, Union City, Newark only; live statuses only
 * (ACTV, NEW, CS = Coming Soon, BOMK = Back on Market). AC (contingent) and
 * PEND are excluded on purpose: the page shows homes a buyer can still get.
 *
 * Output: live-inventory.json at the repo root. push-to-github.sh and
 * run-daily.js Stage 3 publish it to GitHub Pages, where harvrealtor.net
 * fetches it client-side (Pages serves access-control-allow-origin: *).
 *
 * The file is only written after sanity gates pass (see GATES below), so a
 * bad sheet read can never clobber yesterday's good file. Failures exit 1;
 * update-inventory.js wraps the call in try/catch so the daily flow never
 * blocks on this artifact.
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const sa = require('./lib/google-sa');
const { TEMPLATE_PATH } = require('./lib/config');

const SCOPE =
  'https://www.googleapis.com/auth/drive.readonly https://www.googleapis.com/auth/spreadsheets.readonly';
const RANGE = 'A1:U10000'; // no tab name -> first sheet of the dated file

const TARGET_CITIES = ['FREMONT', 'HAYWARD', 'UNION CITY', 'NEWARK'];
const LIVE_STATUSES = { ACTV: 'Active', NEW: 'New', CS: 'Coming Soon', BOMK: 'Back on Market' };

// Sanity gates — refuse to publish a file that fails any of these.
const GATES = {
  minListings: 50,     // 4-city live inventory has been ~600; 50 = deeply wrong day
  maxListings: 5000,
  minCitiesPresent: 3, // at least 3 of the 4 cities must have listings
  minPrice: 50000,     // rows outside this band are dropped, not fatal
  maxPrice: 20000000,
};

const num = (v) => {
  const n = parseFloat(String(v == null ? '' : v).replace(/[$,%\s,]/g, ''));
  return Number.isFinite(n) ? n : null;
};
const int = (v) => {
  const n = num(v);
  return n === null ? null : Math.round(n);
};
// Paragon uses 9999 as an "unknown" placeholder (same convention as the Area
// column); 0 is equally meaningless for a size. Null both so the page never
// renders a bogus 9,999 sq ft or a $39/sq ft.
const sizeInt = (v) => {
  const n = int(v);
  return n === null || n <= 0 || n === 9999 ? null : n;
};
// Unit arrives with spreadsheet formatting artifacts ("$6" for "#6"); keep
// the meaningful token only.
const cleanUnit = (v) => String(v == null ? '' : v).replace(/[$#,\s]/g, '').trim() || null;

const titleCase = (s) =>
  String(s).toLowerCase().replace(/\b[a-z]/g, (c) => c.toUpperCase());

function todayPT() {
  const d = new Date(new Date().toLocaleString('en-US', { timeZone: 'America/Los_Angeles' }));
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  const yy = String(d.getFullYear() % 100).padStart(2, '0');
  return `${mm}/${dd}/${yy}`;
}

function reportDate(explicit, sourceName) {
  if (explicit) return explicit;
  // The dated file name is the truth: "MLS_Defined_Spread_Sheet_4- 071626".
  const m = String(sourceName || '').match(/(\d{2})(\d{2})(\d{2})\s*$/);
  if (m) return `${m[1]}/${m[2]}/${m[3]}`;
  try {
    const t = JSON.parse(fs.readFileSync(TEMPLATE_PATH, 'utf8'));
    if (t && typeof t.date === 'string' && /^\d{2}\/\d{2}\/\d{2}$/.test(t.date)) return t.date;
  } catch (_) { /* fall through */ }
  return todayPT();
}

function apiGet(url, token) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { Authorization: `Bearer ${token}` } }, (res) => {
      let raw = '';
      res.on('data', (c) => (raw += c));
      res.on('end', () => resolve({ status: res.statusCode, body: raw }));
    }).on('error', reject);
  });
}

// Same tolerant CSV parser as mls-pipeline.js, for a raw text/csv upload.
function parseCsv(text) {
  const rows = []; let row = [], cell = '', q = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (q) { if (ch === '"') { if (text[i + 1] === '"') { cell += '"'; i++; } else q = false; } else cell += ch; }
    else if (ch === '"') q = true;
    else if (ch === ',') { row.push(cell); cell = ''; }
    else if (ch === '\n') { row.push(cell); rows.push(row); row = []; cell = ''; }
    else if (ch === '\r') { /* skip */ } else cell += ch;
  }
  if (cell.length || row.length) { row.push(cell); rows.push(row); }
  return rows.filter((r) => r.some((c) => c !== ''));
}

// Newest dated Paragon export the service account can see (Sheet or CSV),
// discovered exactly like mls-pipeline.js getRows().
async function findNewestExport(token) {
  const q = encodeURIComponent(
    "name contains 'MLS_Defined' and trashed=false and mimeType!='application/vnd.google-apps.folder'"
  );
  const r = JSON.parse((await apiGet(
    `https://www.googleapis.com/drive/v3/files?q=${q}&fields=files(id,name,mimeType,modifiedTime)&orderBy=modifiedTime desc&pageSize=10`,
    token
  )).body);
  const SHEET = 'application/vnd.google-apps.spreadsheet';
  const f = (r.files || []).find((x) => x.mimeType === SHEET || x.mimeType === 'text/csv');
  if (!f) throw new Error('no MLS_Defined* Sheet/CSV visible to the service account');
  return f;
}

// Read the dated file as rows. Google Sheet -> Sheets API with
// valueRenderOption=UNFORMATTED_VALUE (CSV export would render "#########"
// for $1M+ prices). Raw CSV upload -> download and parse.
async function readExportRows(file, token) {
  if (file.mimeType === 'application/vnd.google-apps.spreadsheet') {
    const res = await apiGet(
      `https://sheets.googleapis.com/v4/spreadsheets/${file.id}/values/${encodeURIComponent(RANGE)}?valueRenderOption=UNFORMATTED_VALUE`,
      token
    );
    if (res.status !== 200) throw new Error(`sheet read failed (HTTP ${res.status}): ${res.body.slice(0, 300)}`);
    return JSON.parse(res.body).values || [];
  }
  const res = await apiGet(`https://www.googleapis.com/drive/v3/files/${file.id}?alt=media`, token);
  if (res.status !== 200) throw new Error(`csv download failed (HTTP ${res.status})`);
  return parseCsv(res.body);
}

async function buildLiveInventory({ date = null, outFile = null } = {}) {
  const out = outFile || path.join(__dirname, 'live-inventory.json');
  const token = await sa.getAccessToken(SCOPE);
  const source = await findNewestExport(token);
  console.log(`source: ${source.name} (${source.mimeType === 'text/csv' ? 'csv' : 'google-sheet'}, modified ${source.modifiedTime})`);
  const rows = await readExportRows(source, token);
  if (!rows.length) throw new Error('sheet returned no rows');

  const hdr = rows[0].map((h) => String(h).trim());
  const col = {};
  ['MLS No', 'Status', 'DOM', 'Address', 'Unit', 'City', 'LP', 'BT', 'SqFt', 'BR', 'Bth', 'PB', 'YrBlt', 'Lot SqFt', 'HOA Fee', 'Freq'].forEach((name) => {
    col[name] = hdr.indexOf(name);
    if (col[name] === -1) throw new Error(`column "${name}" missing from ${source.name} header`);
  });

  const listings = [];
  let dropped = 0;
  for (const r of rows.slice(1)) {
    const status = String(r[col.Status] || '').trim().toUpperCase();
    const city = String(r[col.City] || '').trim().toUpperCase();
    if (!LIVE_STATUSES[status] || !TARGET_CITIES.includes(city)) continue;

    const price = num(r[col.LP]);
    const address = String(r[col.Address] || '').trim();
    if (!address || price === null || price < GATES.minPrice || price > GATES.maxPrice) {
      dropped++;
      continue;
    }
    listings.push({
      mls: String(r[col['MLS No']] || '').trim(),
      status,
      dom: int(r[col.DOM]),
      address,
      unit: cleanUnit(r[col.Unit]),
      city: titleCase(city),
      price,
      type: String(r[col.BT] || '').trim().toUpperCase() || null,
      sqft: sizeInt(r[col.SqFt]),
      beds: int(r[col.BR]),
      baths: int(r[col.Bth]),
      halfBaths: int(r[col.PB]),
      yearBuilt: int(r[col.YrBlt]),
      lotSqft: int(r[col['Lot SqFt']]),
      hoaFee: int(r[col['HOA Fee']]),
      hoaFreq: String(r[col.Freq] || '').trim() || null,
    });
  }

  // Gates
  if (listings.length < GATES.minListings || listings.length > GATES.maxListings) {
    throw new Error(`listing count ${listings.length} outside sanity band — not publishing`);
  }
  const citiesPresent = new Set(listings.map((l) => l.city));
  if (citiesPresent.size < GATES.minCitiesPresent) {
    throw new Error(`only ${citiesPresent.size} cities present — not publishing`);
  }

  // Deterministic order: city, then price ascending.
  listings.sort((a, b) => a.city.localeCompare(b.city) || a.price - b.price);

  const counts = {};
  for (const l of listings) {
    counts[l.city] = counts[l.city] || { total: 0, ACTV: 0, NEW: 0, CS: 0, BOMK: 0 };
    counts[l.city].total++;
    counts[l.city][l.status]++;
  }

  const payload = {
    version: 1,
    date: reportDate(date, source.name),
    generatedAt: new Date().toISOString(),
    source: 'Paragon MLS daily export via REALTY EXPERTS',
    statuses: LIVE_STATUSES,
    counts,
    listings,
  };

  const tmp = out + '.tmp';
  fs.writeFileSync(tmp, JSON.stringify(payload));
  fs.renameSync(tmp, out);
  return { out, count: listings.length, dropped, cities: citiesPresent.size, date: payload.date };
}

if (require.main === module) {
  const dateArgIdx = process.argv.indexOf('--date');
  const outArgIdx = process.argv.indexOf('--out');
  buildLiveInventory({
    date: dateArgIdx !== -1 ? process.argv[dateArgIdx + 1] : null,
    outFile: outArgIdx !== -1 ? process.argv[outArgIdx + 1] : null,
  })
    .then((r) => console.log(`live-inventory.json: ${r.count} listings, ${r.cities} cities, date ${r.date} (${r.dropped} rows dropped)`))
    .catch((e) => { console.error('ERROR:', e.message); process.exit(1); });
}

module.exports = { buildLiveInventory };
