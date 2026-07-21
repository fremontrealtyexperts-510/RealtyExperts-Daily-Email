/**
 * dump-mls-csv.js  [outCsv]
 * READ-ONLY: lists the MLS_Defined* files the service account can see, reads the
 * newest (Sheet via Sheets API UNFORMATTED_VALUE, else CSV), writes it to a local
 * CSV, and prints the file list + row count. No sheet writes, no Drive uploads.
 * Auth + read logic mirrors mls-pipeline.js getRows().
 */
const https = require('https'), crypto = require('crypto'), fs = require('fs'), path = require('path');
const KEY = path.join(__dirname, 'harvrealtor-0819122f6566-google-drive.json');
const SCOPES = 'https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/spreadsheets';
const OUT = process.argv[2] || '/tmp/mls-today.csv';
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
const toCsv = rows => rows.map(r => r.map(v => {
  const s = v == null ? '' : String(v);
  return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}).join(',')).join('\n') + '\n';
(async () => {
  const creds = JSON.parse(fs.readFileSync(KEY, 'utf8'));
  const tr = await req('POST', 'https://oauth2.googleapis.com/token', '', { headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: `grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer&assertion=${makeJwt(creds)}` });
  const token = j(tr.body).access_token;
  if (!token) throw new Error('auth failed: ' + tr.body.toString().slice(0, 300));
  const q = encodeURIComponent("name contains 'MLS_Defined' and trashed=false and mimeType!='application/vnd.google-apps.folder'");
  const list = j((await req('GET', `https://www.googleapis.com/drive/v3/files?q=${q}&fields=files(id,name,mimeType,modifiedTime)&orderBy=modifiedTime desc&pageSize=10`, token)).body);
  console.log('=== MLS_Defined* files (newest first) ===');
  (list.files || []).forEach(f => console.log(`${f.modifiedTime}  ${f.mimeType.includes('spreadsheet') ? 'SHEET' : 'csv  '}  ${f.name}`));
  const SHEET = 'application/vnd.google-apps.spreadsheet';
  const f = (list.files || []).find(x => x.mimeType === 'text/csv' || x.mimeType === SHEET);
  if (!f) throw new Error('no MLS_Defined* CSV/Sheet visible to the service account');
  console.log('\nUsing:', f.name, `(${f.mimeType === SHEET ? 'google-sheet' : 'csv'}, ${f.modifiedTime})`);
  let rows;
  if (f.mimeType === SHEET) {
    const res = await req('GET', `https://sheets.googleapis.com/v4/spreadsheets/${f.id}/values/${encodeURIComponent('A1:AZ100000')}?valueRenderOption=UNFORMATTED_VALUE&dateTimeRenderOption=FORMATTED_STRING`, token);
    if (res.status !== 200) throw new Error('sheet read failed: ' + res.body.toString().slice(0, 300));
    rows = (j(res.body).values || []).filter(row => row.some(c => c !== '' && c != null));
  } else {
    rows = parseCsv((await req('GET', `https://www.googleapis.com/drive/v3/files/${f.id}?alt=media`, token)).body.toString('utf8'));
  }
  fs.writeFileSync(OUT, toCsv(rows));
  console.log(`\nwrote ${OUT}: ${rows.length} rows x ${rows[0].length} cols | header[1]=${rows[0][1]} header[5]=${rows[0][5]} header[9]=${rows[0][9]}`);
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });
