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
 * Since 2026-09-02 (version 2) the file carries STATISTICS ONLY: no
 * per-listing rows, no addresses, no MLS numbers. The Bay East MLS Rules treat
 * the per-listing compilation as confidential to participants and subscribers
 * (12.12, 12.15.4, 12.16(l)), keep Coming Soon listings off every
 * public-facing product (10.1.1 item 12), and this file is fetched by public
 * pages. What is published, per city and for the five cities together:
 *   counts   every live status: total, ACTV, NEW, CS, BOMK
 *   allLive  every live status, Coming Soon included: medianLP, types, bands,
 *            medianLPByType, the same figures the inventory-history.json
 *            record carries, so the site's "today" overlay is exact
 *   market   the homes on the market (Active, New, Back on Market): count,
 *            medians (price, $/sq ft, days), new this week, waiting 60+,
 *            under $1M, min/max, types, price bands, days-on-market buckets,
 *            medians by type and by status
 * The homes themselves are on the harvrealtor.com map search (the IDX).
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

// Milpitas joined the Paragon export on 2026-01-05 and has been in every
// export since. CORE_CITIES are the four with continuous history back to
// 2024; fourCityTotal stays defined over those four ONLY, so the long-run
// history line never steps up on the day the export definition changed.
const CORE_CITIES = ['FREMONT', 'HAYWARD', 'UNION CITY', 'NEWARK'];
const TARGET_CITIES = [...CORE_CITIES, 'MILPITAS'];
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

  // Every live-status row in the target cities (Coming Soon included). The
  // counts and the history record are built from this; the published
  // per-listing array is the subset below.
  const liveRows = [];
  let dropped = 0;
  // County-wide live-status count (all Alameda cities in the export), used by
  // the inventory-history record as a share-of-county denominator.
  let countyLiveTotal = 0;
  for (const r of rows.slice(1)) {
    const status = String(r[col.Status] || '').trim().toUpperCase();
    const city = String(r[col.City] || '').trim().toUpperCase();
    if (!LIVE_STATUSES[status]) continue;
    countyLiveTotal++;
    if (!TARGET_CITIES.includes(city)) continue;

    const price = num(r[col.LP]);
    const address = String(r[col.Address] || '').trim();
    if (!address || price === null || price < GATES.minPrice || price > GATES.maxPrice) {
      dropped++;
      continue;
    }
    liveRows.push({
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
  if (liveRows.length < GATES.minListings || liveRows.length > GATES.maxListings) {
    throw new Error(`listing count ${liveRows.length} outside sanity band — not publishing`);
  }
  const citiesPresent = new Set(liveRows.map((l) => l.city));
  if (citiesPresent.size < GATES.minCitiesPresent) {
    throw new Error(`only ${citiesPresent.size} cities present — not publishing`);
  }

  // Deterministic order: city, then price ascending.
  liveRows.sort((a, b) => a.city.localeCompare(b.city) || a.price - b.price);

  // Aggregates over every live status, Coming Soon included.
  const counts = {};
  for (const l of liveRows) {
    counts[l.city] = counts[l.city] || { total: 0, ACTV: 0, NEW: 0, CS: 0, BOMK: 0 };
    counts[l.city].total++;
    counts[l.city][l.status]++;
  }

  // Statistics only (see the header). Per city and for the five together.
  const truncated = pricesTruncated(liveRows);
  const cities = {};
  for (const c of [...citiesPresent].sort()) {
    cities[c] = cityBlock(liveRows.filter((l) => l.city === c), truncated);
  }
  const all = cityBlock(liveRows, truncated);
  const comingSoon = all.counts.CS;

  const payload = {
    version: 2,
    date: reportDate(date, source.name),
    generatedAt: new Date().toISOString(),
    source: 'Paragon MLS daily export via REALTY EXPERTS',
    itemized: false,
    note: 'Statistics only. No per-listing data is published; the homes themselves are on the harvrealtor.com map search.',
    statuses: LIVE_STATUSES,
    typeLabels: TYPE_LABELS,
    bandBounds: BAND_BOUNDS,
    bandLabels: BAND_LABELS,
    domBucketBounds: DOM_BUCKET_BOUNDS,
    domBucketLabels: DOM_BUCKET_LABELS,
    counts,
    cities,
    all,
  };

  const tmp = out + '.tmp';
  fs.writeFileSync(tmp, JSON.stringify(payload));
  fs.renameSync(tmp, out);

  // Append today's snapshot to the long-run history series (non-fatal: the
  // live feed is the critical artifact; history failures only warn).
  try {
    const hist = await updateInventoryHistory({
      listings: liveRows, // every live status, so the series stays continuous
      countyLiveTotal,
      feedDate: payload.date,
      sourceName: source.name,
      dir: path.dirname(out),
    });
    if (hist) console.log(`inventory-history.json: ${hist.count} dates (latest ${hist.latest})`);
  } catch (err) {
    console.warn(`WARN inventory-history update failed: ${err.message}`);
  }

  return {
    out,
    count: all.market.count,
    comingSoon,
    rows: liveRows.length,
    dropped,
    cities: citiesPresent.size,
    date: payload.date,
  };
}

// ---------------------------------------------------------------------------
// Aggregate blocks (the public feed is statistics only, see the header).
// ---------------------------------------------------------------------------
const MARKET_TYPES = ['DE', 'CO', 'TH', 'DU'];
const MARKET_STATUSES = ['ACTV', 'NEW', 'BOMK'];
const DOM_BUCKET_BOUNDS = [7, 14, 30, 60];
const DOM_BUCKET_LABELS = ['First week', '8 to 14 days', '15 to 30 days', '31 to 60 days', 'Over 60 days'];
const domBucket = (dom) => {
  for (let i = 0; i < DOM_BUCKET_BOUNDS.length; i++) if (dom <= DOM_BUCKET_BOUNDS[i]) return i;
  return DOM_BUCKET_BOUNDS.length;
};

function countsOf(rows) {
  const c = { total: 0, ACTV: 0, NEW: 0, CS: 0, BOMK: 0 };
  for (const l of rows) {
    c.total++;
    if (c[l.status] !== undefined) c[l.status]++;
  }
  return c;
}

// Price-integrity guard: a Fremont sample of 30+ with max LP under $1M means
// the export truncated $1M+ prices — counts stay valid, every price figure
// is poisoned and published as null.
function pricesTruncated(rows) {
  const fre = rows.filter((l) => l.city === 'Fremont' && l.price > 0).map((l) => l.price);
  return fre.length >= 30 && Math.max(...fre) < 1000000;
}

// Every live status, Coming Soon included. Same figures as the history record.
function allLiveBlock(rows, truncated) {
  const lp = [];
  const types = { DE: 0, CO: 0, TH: 0, DU: 0 };
  const bands = Array(BAND_BOUNDS.length + 1).fill(0);
  const lpt = { DE: [], CO: [], TH: [], DU: [] };
  for (const l of rows) {
    if (l.price > 0) {
      lp.push(l.price);
      bands[bandIndex(l.price)]++;
      if (l.type && lpt[l.type]) lpt[l.type].push(l.price);
    }
    if (l.type && types[l.type] !== undefined) types[l.type]++;
  }
  const medianLPByType = {};
  for (const t of MEDIAN_TYPES) medianLPByType[t] = truncated ? null : median(lpt[t]);
  return {
    medianLP: truncated ? null : median(lp),
    types,
    bands: truncated ? null : bands,
    medianLPByType,
  };
}

// The homes on the market: Active, New and Back on Market rows only. Mirrors
// harvrealtor-net src/lib/liveInventory.ts computeStats, which computed the
// same figures from the rows while the rows were published.
function marketBlock(rows, truncated) {
  const on = rows.filter((l) => l.status !== 'CS');
  const prices = [];
  const ppsf = [];
  const doms = [];
  const types = { DE: 0, CO: 0, TH: 0, DU: 0 };
  const bands = Array(BAND_BOUNDS.length + 1).fill(0);
  const domBuckets = Array(DOM_BUCKET_BOUNDS.length + 1).fill(0);
  const lpt = { DE: [], CO: [], TH: [], DU: [] };
  const lps = { ACTV: [], NEW: [], BOMK: [] };
  let newThisWeek = 0;
  let waitingSixtyPlus = 0;
  let underMillion = 0;
  let minPrice = null;
  let maxPrice = null;
  for (const l of on) {
    if (l.price > 0) {
      prices.push(l.price);
      bands[bandIndex(l.price)]++;
      if (l.price < 1000000) underMillion++;
      if (minPrice === null || l.price < minPrice) minPrice = l.price;
      if (maxPrice === null || l.price > maxPrice) maxPrice = l.price;
      if (l.sqft && l.sqft > 0) ppsf.push(l.price / l.sqft);
      if (l.type && lpt[l.type]) lpt[l.type].push(l.price);
      if (lps[l.status]) lps[l.status].push(l.price);
    }
    if (l.type && types[l.type] !== undefined) types[l.type]++;
    if (typeof l.dom === 'number' && Number.isFinite(l.dom)) {
      doms.push(l.dom);
      if (l.dom <= 7) newThisWeek++;
      if (l.dom > 60) waitingSixtyPlus++;
      domBuckets[domBucket(l.dom)]++;
    }
  }
  const priced = (v) => (truncated ? null : v);
  const medianLPByType = {};
  for (const t of MARKET_TYPES) medianLPByType[t] = priced(median(lpt[t]));
  const medianLPByStatus = {};
  for (const st of MARKET_STATUSES) medianLPByStatus[st] = priced(median(lps[st]));
  return {
    count: on.length,
    medianPrice: priced(median(prices)),
    medianPpsf: priced(ppsf.length ? Math.round(median(ppsf)) : null),
    medianDom: median(doms),
    newThisWeek,
    waitingSixtyPlus,
    underMillion: priced(underMillion),
    minPrice: priced(minPrice),
    maxPrice: priced(maxPrice),
    types,
    bands: priced(bands),
    domBuckets,
    medianLPByType,
    medianLPByStatus,
  };
}

function cityBlock(rows, truncated) {
  return { counts: countsOf(rows), allLive: allLiveBlock(rows, truncated), market: marketBlock(rows, truncated) };
}

// ---------------------------------------------------------------------------
// inventory-history.json — one record per day, powering the harvrealtor.net
// /inventory-history page. Seeded 2026-07-17 with a 386-day backfill parsed
// from every archived MLS_Defined export back to Jan 2024; this function only
// ever UPSERTS (today's date replaces today's record, everything else is
// preserved). Base = the published GitHub Pages copy unioned with the local
// file, so Mac and VPS runs converge instead of clobbering each other.
// ---------------------------------------------------------------------------
const HISTORY_URL =
  'https://fremontrealtyexperts-510.github.io/RealtyExperts-Daily-Email/inventory-history.json';
const HISTORY_STATUSES = ['ACTV', 'NEW', 'CS', 'BOMK'];
// Property-type + price-band dimensions (added with the 2026-07-18 v3 rebuild;
// every historical record carries them, this keeps today's record matching).
// BAND_BOUNDS mirror harvrealtor-net src/lib/liveInventory.ts PRICE_BAND_EDGES
// and _inventory-history rebuild-v3.py — keep all three in sync.
const HISTORY_TYPES = ['DE', 'CO', 'TH', 'DU'];
// Dates proven corrupt and excluded by the v3 rebuild (2026-07-18): the
// 2025-10-10 "…(1).csv" was a stale re-download whose MLS number sequence was
// months older than its neighbors. Never let a cached copy resurrect them.
const EXCLUDED_DATES = new Set(['2025-10-10']);
const MEDIAN_TYPES = ['DE', 'CO', 'TH'];
const BAND_BOUNDS = [800000, 1000000, 1250000, 1500000, 2000000, 3000000];
const BAND_LABELS = ['Under $800K', '$800K to $1M', '$1M to $1.25M', '$1.25M to $1.5M',
  '$1.5M to $2M', '$2M to $3M', '$3M and up'];
const TYPE_LABELS = { DE: 'House', CO: 'Condo', TH: 'Townhome', DU: 'Duplex' };
const bandIndex = (lp) => {
  for (let i = 0; i < BAND_BOUNDS.length; i++) if (lp < BAND_BOUNDS[i]) return i;
  return BAND_BOUNDS.length;
};

function fetchJson(url, timeoutMs = 20000) {
  return new Promise((resolve) => {
    const req = https.get(url, { headers: { 'cache-control': 'no-cache' } }, (res) => {
      if (res.statusCode !== 200) { res.resume(); return resolve(null); }
      let raw = '';
      res.on('data', (c) => (raw += c));
      res.on('end', () => {
        try { resolve(JSON.parse(raw)); } catch (_) { resolve(null); }
      });
    });
    req.on('error', () => resolve(null));
    req.setTimeout(timeoutMs, () => { req.destroy(); resolve(null); });
  });
}

const median = (arr) => {
  if (!arr.length) return null;
  const s = [...arr].sort((a, b) => a - b);
  const mid = Math.floor(s.length / 2);
  return s.length % 2 ? s[mid] : Math.round((s[mid - 1] + s[mid]) / 2);
};

async function updateInventoryHistory({ listings, countyLiveTotal, feedDate, sourceName, dir }) {
  const histPath = path.join(dir, 'inventory-history.json');

  // Today's record, same shape as the seeded backfill.
  const m = String(feedDate).match(/^(\d{2})\/(\d{2})\/(\d{2})$/);
  if (!m) throw new Error(`unexpected feed date "${feedDate}"`);
  const iso = `20${m[3]}-${m[1]}-${m[2]}`;
  const weekday = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][
    new Date(Date.UTC(2000 + Number(m[3]), Number(m[1]) - 1, Number(m[2]))).getUTCDay()
  ];
  // One record per city: the counts plus the all-live block, the same helpers
  // the public feed's `allLive` uses, so the two can never disagree.
  const byCity = new Map();
  for (const l of listings) {
    if (!byCity.has(l.city)) byCity.set(l.city, []);
    byCity.get(l.city).push(l);
  }
  const truncated = pricesTruncated(listings);
  const cities = {};
  for (const [name, rows] of byCity) {
    cities[name] = { ...countsOf(rows), ...allLiveBlock(rows, truncated) };
  }
  // fourCityTotal is defined over the four continuously-tracked cities ONLY
  // (Milpitas entered the export 2026-01-05); the long-run history line stays
  // apples-to-apples across that change. Milpitas rides in `cities` and in
  // trackedTotal.
  const CORE = ['Fremont', 'Hayward', 'Union City', 'Newark'];
  const coreTotal = CORE.reduce((s, c) => s + (cities[c] ? cities[c].total : 0), 0);
  const record = {
    date: iso,
    weekday,
    cities,
    fourCityTotal: coreTotal,
    trackedTotal: listings.length,
    countyActiveTotal: countyLiveTotal || null,
    sourceFile: sourceName,
  };

  // Base series = published ∪ local (published wins are irrelevant — same-date
  // records should be identical; union keeps the superset of dates).
  const published = await fetchJson(HISTORY_URL);
  let local = null;
  try { local = JSON.parse(fs.readFileSync(histPath, 'utf8')); } catch (_) { /* absent is fine */ }
  const base = published && Array.isArray(published.series) ? published : local;
  if (!base || !Array.isArray(base.series)) {
    // Never invent a 1-record history: without a seeded base we would push a
    // file that clobbers the published 386-day series. Skip and warn instead.
    throw new Error('no base history reachable (Pages + local both missing) — skipping upsert');
  }
  const byDate = new Map(base.series.map((r) => [r.date, r]));
  if (local && Array.isArray(local.series)) {
    // Union keeps the superset of dates AND, per date, the richer record: a
    // record carrying the per-type dimension outranks a counts-only one, so
    // the v3 enrichment can never be undone by whichever copy fetched first.
    const hasTypes = (r) =>
      r && r.cities && Object.values(r.cities).some((c) => c && c.types);
    for (const r of local.series) {
      const cur = byDate.get(r.date);
      if (!cur || (!hasTypes(cur) && hasTypes(r))) byDate.set(r.date, r);
    }
  }
  byDate.set(iso, record); // upsert today
  for (const d of EXCLUDED_DATES) byDate.delete(d);
  const series = [...byDate.values()].sort((a, b) => a.date.localeCompare(b.date));
  if (series.length < base.series.length - EXCLUDED_DATES.size) {
    throw new Error('refusing to shrink the history series'); // belt and braces
  }

  const out = {
    version: 1,
    generatedAt: new Date().toISOString(),
    source: base.source || 'Paragon MLS daily exports (MLS_Defined_Spread_Sheet_4) via REALTY EXPERTS',
    filter: base.filter || { cities: ['Fremont', 'Hayward', 'Newark', 'Union City'], statuses: HISTORY_STATUSES, note: 'matches live-inventory.json feed filter' },
    statuses: base.statuses || LIVE_STATUSES,
    cities: base.cities || ['Fremont', 'Hayward', 'Newark', 'Union City'],
    coreCities: base.coreCities || CORE_CITIES.map((c) => c.split(' ').map((w) => w[0] + w.slice(1).toLowerCase()).join(' ')),
    milpitasFrom: base.milpitasFrom || '2026-01-05',
    typeLabels: base.typeLabels || TYPE_LABELS,
    bandBounds: base.bandBounds || BAND_BOUNDS,
    bandLabels: base.bandLabels || BAND_LABELS,
    excluded: base.excluded || undefined,
    count: series.length,
    series,
  };
  const tmpHist = histPath + '.tmp';
  fs.writeFileSync(tmpHist, JSON.stringify(out));
  fs.renameSync(tmpHist, histPath);
  return { count: series.length, latest: iso };
}

if (require.main === module) {
  const dateArgIdx = process.argv.indexOf('--date');
  const outArgIdx = process.argv.indexOf('--out');
  buildLiveInventory({
    date: dateArgIdx !== -1 ? process.argv[dateArgIdx + 1] : null,
    outFile: outArgIdx !== -1 ? process.argv[outArgIdx + 1] : null,
  })
    .then((r) => console.log(`live-inventory.json (statistics only): ${r.rows} live rows, ${r.count} on the market + ${r.comingSoon} coming soon, ${r.cities} cities, date ${r.date} (${r.dropped} rows dropped)`))
    .catch((e) => { console.error('ERROR:', e.message); process.exit(1); });
}

module.exports = { buildLiveInventory };
