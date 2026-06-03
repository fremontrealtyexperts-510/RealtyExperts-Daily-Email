/**
 * mls-pipeline.js  [csvPath]  [--dry-run]
 *
 * Turns the Paragon "MLS Defined Spread Sheet 4" CSV into the daily artifacts:
 *   1. Writes the raw CSV into the master sheet's MLS_Defined_Spread_Sheet_4 tab
 *      (so RE-v2 / Interactive / blog tabs recalc).            [needs sheet = Editor]
 *   2. Renders RE-Daily-1.png (table) + RE-Daily-2.png (chart) via mls-csv-to-images.py.
 *   3. Archives yesterday's PNGs and uploads today's to Raw-data. [needs Raw-data folder = Editor]
 *
 * CSV source: a local path if given, else the newest MLS_Defined_Spread* file the
 * service account can see in Drive (i.e. uploaded into the shared Raw-data folder).
 * No external deps (Node built-ins + the python renderer).
 */
const https = require('https'), crypto = require('crypto'), fs = require('fs'),
      path = require('path'), { execFileSync } = require('child_process');

const KEY = path.join(__dirname, 'harvrealtor-0819122f6566-google-drive.json');
const SHEET_ID = '1YxbK29giJO6XDQAV3RHXml2vjMejmtBpZfD3ICW_gTw';
const DATA_TAB = 'MLS_Defined_Spread_Sheet_4';
const SCOPES = 'https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/spreadsheets';
const DRY = process.argv.includes('--dry-run');
const LOCAL_CSV = process.argv.slice(2).find(a => !a.startsWith('--'));

// ── auth ─────────────────────────────────────────────────────────────────────
const b64u = s => Buffer.from(s).toString('base64').replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
function makeJwt(c) {
  const now = Math.floor(Date.now() / 1000);
  const h = b64u(JSON.stringify({ alg: 'RS256', typ: 'JWT' }));
  const p = b64u(JSON.stringify({ iss: c.client_email, scope: SCOPES, aud: 'https://oauth2.googleapis.com/token', iat: now, exp: now + 3600 }));
  const u = `${h}.${p}`;
  const sig = crypto.createSign('RSA-SHA256').update(u).sign(c.private_key, 'base64').replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
  return `${u}.${sig}`;
}
function req(method, url, token, { headers = {}, body = null } = {}) {
  return new Promise((res, rej) => {
    const opts = { method, headers: { Authorization: `Bearer ${token}`, ...headers } };
    const r = https.request(url, opts, x => { let raw = Buffer.alloc(0); x.on('data', c => raw = Buffer.concat([raw, c])); x.on('end', () => res({ status: x.statusCode, body: raw })); });
    r.on('error', rej); if (body) r.write(body); r.end();
  });
}
const j = b => { try { return JSON.parse(b.toString()); } catch { return b.toString(); } };

async function getToken() {
  const creds = JSON.parse(fs.readFileSync(KEY, 'utf8'));
  const r = await req('POST', 'https://oauth2.googleapis.com/token', '', {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer&assertion=${makeJwt(creds)}`,
  });
  const t = j(r.body).access_token;
  if (!t) throw new Error('auth failed: ' + r.body.toString().slice(0, 300));
  return t;
}

// ── CSV ──────────────────────────────────────────────────────────────────────
function parseCsv(text) {
  const rows = []; let row = [], cell = '', q = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (q) { if (ch === '"') { if (text[i + 1] === '"') { cell += '"'; i++; } else q = false; } else cell += ch; }
    else if (ch === '"') q = true;
    else if (ch === ',') { row.push(cell); cell = ''; }
    else if (ch === '\n') { row.push(cell); rows.push(row); row = []; cell = ''; }
    else if (ch === '\r') {} else cell += ch;
  }
  if (cell.length || row.length) { row.push(cell); rows.push(row); }
  return rows.filter(r => r.some(c => c !== ''));
}
async function getCsv(token) {
  if (LOCAL_CSV) { console.log('CSV source: local', LOCAL_CSV); return fs.readFileSync(LOCAL_CSV, 'utf8'); }
  const q = encodeURIComponent("name contains 'MLS_Defined' and trashed=false and mimeType!='application/vnd.google-apps.folder'");
  const r = j((await req('GET', `https://www.googleapis.com/drive/v3/files?q=${q}&fields=files(id,name,mimeType,modifiedTime)&orderBy=modifiedTime desc&pageSize=10`, token)).body);
  const SHEET = 'application/vnd.google-apps.spreadsheet';
  const f = (r.files || []).find(x => x.mimeType === 'text/csv' || x.mimeType === SHEET); // newest CSV upload or auto-converted Sheet
  if (!f) throw new Error("no MLS_Defined* CSV/Sheet visible to the service account — upload today's export to a shared Drive folder first");
  console.log('CSV source: Drive', f.name, `(${f.mimeType === SHEET ? 'google-sheet' : 'csv'}, ${f.modifiedTime})`);
  const url = f.mimeType === SHEET
    ? `https://www.googleapis.com/drive/v3/files/${f.id}/export?mimeType=text/csv`
    : `https://www.googleapis.com/drive/v3/files/${f.id}?alt=media`;
  return (await req('GET', url, token)).body.toString('utf8');
}

// ── 1. write into master sheet ────────────────────────────────────────────────
async function updateSheet(token, rows) {
  if (DRY) { console.log(`[dry-run] would CLEAR '${DATA_TAB}' then write ${rows.length} rows x ${rows[0].length} cols`); return; }
  let r = await req('POST', `https://sheets.googleapis.com/v4/spreadsheets/${SHEET_ID}/values/${encodeURIComponent(DATA_TAB)}:clear`, token, { headers: { 'Content-Type': 'application/json' }, body: '{}' });
  if (r.status !== 200) throw new Error('clear failed: ' + r.body.toString().slice(0, 300));
  const body = JSON.stringify({ values: rows });
  r = await req('PUT', `https://sheets.googleapis.com/v4/spreadsheets/${SHEET_ID}/values/${encodeURIComponent(DATA_TAB + '!A1')}?valueInputOption=USER_ENTERED`, token, { headers: { 'Content-Type': 'application/json' }, body });
  if (r.status !== 200) throw new Error('sheet update failed: ' + r.body.toString().slice(0, 300));
  console.log(`sheet updated: ${rows.length} rows into '${DATA_TAB}'`);
}

// ── 3. update PNGs in place ───────────────────────────────────────────────────
// Service accounts have no storage quota, so they can't CREATE files in a personal
// My Drive — but they can overwrite the CONTENT of existing ones. RE-Daily-1/2.png
// already exist in Raw-data, so we PATCH their media. (GitHub keeps the dated history.)
async function findFile(token, name) {
  const q = encodeURIComponent(`name='${name}' and trashed=false`);
  const r = j((await req('GET', `https://www.googleapis.com/drive/v3/files?q=${q}&fields=files(id,name,parents)&pageSize=1`, token)).body);
  return (r.files || [])[0] || null;
}
async function pushPngs(token, outDir) {
  for (const base of ['RE-Daily-1', 'RE-Daily-2']) {
    const existing = await findFile(token, base + '.png');
    if (!existing) throw new Error(`${base}.png not found in Drive — the SA can't create it; upload it once manually, then this runs forever`);
    if (DRY) { console.log(`[dry-run] would UPDATE-in-place ${base}.png (id ${existing.id})`); continue; }
    const media = fs.readFileSync(path.join(outDir, base + '.png'));
    const r = await req('PATCH', `https://www.googleapis.com/upload/drive/v3/files/${existing.id}?uploadType=media&fields=id,size,modifiedTime`, token, { headers: { 'Content-Type': 'image/png', 'Content-Length': media.length }, body: media });
    if (r.status !== 200) throw new Error(`update ${base}.png failed: ` + r.body.toString().slice(0, 300));
    console.log(`updated ${base}.png in place (id ${existing.id}, ${j(r.body).size} bytes)`);
  }
}

// ── main ─────────────────────────────────────────────────────────────────────
(async () => {
  const token = await getToken();
  const csvText = await getCsv(token);
  const rows = parseCsv(csvText);
  console.log(`parsed CSV: ${rows.length} rows, ${rows[0].length} cols, header[5]=${rows[0][5]} header[1]=${rows[0][1]} header[9]=${rows[0][9]}`);

  await updateSheet(token, rows);

  const tmpCsv = LOCAL_CSV || '/tmp/mls-pipeline-input.csv';
  if (!LOCAL_CSV) fs.writeFileSync(tmpCsv, csvText);
  console.log(execFileSync('python3', [path.join(__dirname, 'mls-csv-to-images.py'), tmpCsv, '/tmp'], { encoding: 'utf8' }).trim());

  await pushPngs(token, '/tmp');
  console.log(DRY ? '\n[dry-run] complete — no writes performed.' : '\nDone.');
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });
