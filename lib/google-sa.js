/**
 * lib/google-sa.js
 * Service-account auth + read helpers for Google APIs (Sheets, Drive).
 * No external dependencies — Node.js built-ins only (https, crypto, fs).
 *
 * Reuses the JWT-bearer flow proven in fetch-images.js. Used by the interactive
 * chart generator to read the master sheet's "Interactive" tab live.
 */

const https = require('https');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const DEFAULT_KEY_FILE = path.join(__dirname, '..', 'harvrealtor-0819122f6566-google-drive.json');

const SCOPES = {
  SHEETS_RO: 'https://www.googleapis.com/auth/spreadsheets.readonly',
  DRIVE_RO: 'https://www.googleapis.com/auth/drive.readonly',
};

// ── JWT helpers ──────────────────────────────────────────────────────────────

function base64url(input) {
  return Buffer.from(input).toString('base64')
    .replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
}

function makeJwt(credentials, scope) {
  const now = Math.floor(Date.now() / 1000);
  const header = base64url(JSON.stringify({ alg: 'RS256', typ: 'JWT' }));
  const payload = base64url(JSON.stringify({
    iss: credentials.client_email,
    scope,
    aud: 'https://oauth2.googleapis.com/token',
    iat: now,
    exp: now + 3600,
  }));
  const unsigned = `${header}.${payload}`;
  const sig = crypto.createSign('RSA-SHA256').update(unsigned)
    .sign(credentials.private_key, 'base64')
    .replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
  return `${unsigned}.${sig}`;
}

// ── HTTP helpers ─────────────────────────────────────────────────────────────

function httpsPost(url, body) {
  return new Promise((resolve, reject) => {
    const data = Buffer.from(body);
    const req = https.request(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': data.length,
      },
    }, (res) => {
      let raw = '';
      res.on('data', c => raw += c);
      res.on('end', () => resolve({ status: res.statusCode, body: raw }));
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

function httpsGet(url, token) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { Authorization: `Bearer ${token}` } }, (res) => {
      let raw = '';
      res.on('data', c => raw += c);
      res.on('end', () => resolve({ status: res.statusCode, body: raw }));
    }).on('error', reject);
  });
}

// ── Public API ───────────────────────────────────────────────────────────────

/**
 * Mint a short-lived OAuth access token for the given scope via the
 * service-account JWT-bearer grant.
 */
async function getAccessToken(scope, keyFile = DEFAULT_KEY_FILE) {
  const creds = JSON.parse(fs.readFileSync(keyFile, 'utf8'));
  const res = await httpsPost(
    'https://oauth2.googleapis.com/token',
    `grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer&assertion=${makeJwt(creds, scope)}`
  );
  let parsed;
  try { parsed = JSON.parse(res.body); } catch (_) { parsed = {}; }
  if (!parsed.access_token) {
    throw new Error(`token request failed (HTTP ${res.status}): ${res.body.slice(0, 300)}`);
  }
  return parsed.access_token;
}

/**
 * Read a range from a Google Sheet and return its `values` (array of rows).
 * Range example: 'Interactive!A1:Z30'.
 */
async function getSheetValues(spreadsheetId, range, token) {
  const url = `https://sheets.googleapis.com/v4/spreadsheets/${spreadsheetId}/values/${encodeURIComponent(range)}`;
  const res = await httpsGet(url, token);
  if (res.status !== 200) {
    throw new Error(`sheet read failed (HTTP ${res.status}): ${res.body.slice(0, 300)}`);
  }
  return JSON.parse(res.body).values || [];
}

module.exports = { getAccessToken, getSheetValues, SCOPES };
