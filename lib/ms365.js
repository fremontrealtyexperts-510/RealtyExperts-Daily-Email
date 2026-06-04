/**
 * lib/ms365.js
 *
 * Tiny, dependency-free Microsoft Graph helper for the daily-email scripts.
 * Encapsulates the auth procedure documented in CLAUDE.md ("MS365 / Outlook
 * authentication") so other scripts can read HarvRealtor@outlook.com's mailbox
 * via curl-style Graph calls without reaching for the MCP server.
 *
 * Auth model (personal Microsoft account HarvRealtor@outlook.com):
 *   - Access token (~1h) is cached at /tmp/ms365-token.json (+ ~/.claude mirror).
 *   - Refresh token (~90d) lives in the MSAL cache ~/.ms365-mcp/token-cache.json.
 *   - On a 401/expired access token we silently refresh against the /consumers
 *     endpoint (NOT device-code) and stage→validate→write the new token.
 *
 * Only the bits this repo needs are implemented (read-only Graph GET + refresh).
 * Device-code re-login (when the refresh token itself is dead) stays a manual
 * step — see CLAUDE.md / memory ms365-session-login-procedure.md.
 */

const fs = require('fs');
const os = require('os');
const path = require('path');
const https = require('https');

const CLIENT_ID = '2658285b-1c98-4a9f-bb7c-9cb85118f628';
const TOKEN_ENDPOINT = 'https://login.microsoftonline.com/consumers/oauth2/v2.0/token';
// Same scope set the MCP server requests, so the minted token is a drop-in.
const SCOPES = [
  'openid', 'offline_access', 'Mail.Read', 'Mail.ReadWrite', 'Mail.Send',
  'User.Read', 'Calendars.ReadWrite', 'Files.ReadWrite', 'Contacts.ReadWrite',
  'Notes.ReadWrite', 'Tasks.ReadWrite',
].join(' ');

const TOKEN_FILES = [
  '/tmp/ms365-token.json',
  path.join(os.homedir(), '.claude', 'ms365-token.json'),
];
const STAGING_FILE = '/tmp/ms365-staging.json';
const MSAL_CACHE = path.join(os.homedir(), '.ms365-mcp', 'token-cache.json');

/** Read the cached access token from the first token file that has one. */
function readCachedAccessToken() {
  for (const f of TOKEN_FILES) {
    try {
      const tok = JSON.parse(fs.readFileSync(f, 'utf8')).access_token;
      if (tok) return tok;
    } catch (_) { /* try next */ }
  }
  return null;
}

/** Pull the refresh token out of the MSAL cache (first RefreshToken entry). */
function readRefreshToken() {
  let cache;
  try {
    cache = JSON.parse(fs.readFileSync(MSAL_CACHE, 'utf8'));
  } catch (err) {
    throw new Error(`MSAL cache not readable at ${MSAL_CACHE}: ${err.message}`);
  }
  const entries = cache.RefreshToken || {};
  const key = Object.keys(entries)[0];
  if (!key || !entries[key].secret) {
    throw new Error('No refresh token found in MSAL cache.');
  }
  return entries[key].secret;
}

/** Low-level HTTPS request returning { statusCode, json, raw }. */
function request(options, body) {
  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (c) => (data += c));
      res.on('end', () => {
        let json = null;
        try { json = JSON.parse(data); } catch (_) { /* non-JSON */ }
        resolve({ statusCode: res.statusCode, json, raw: data });
      });
    });
    req.on('error', reject);
    if (body) req.write(body);
    req.end();
  });
}

/** GET a Microsoft Graph path (e.g. "/me/messages?$top=5") with a token. */
function graphRequest(graphPath, accessToken) {
  return request({
    hostname: 'graph.microsoft.com',
    port: 443,
    path: `/v1.0${graphPath}`,
    method: 'GET',
    headers: { Authorization: `Bearer ${accessToken}`, Accept: 'application/json' },
  });
}

/**
 * Silently mint a fresh access token from the refresh token, mirroring the
 * CLAUDE.md curl procedure: POST to /consumers, validate, then atomically
 * write to the live token files (never blind-overwrite).
 * @returns {Promise<string>} the new access token
 * @throws if the refresh token is dead (invalid_grant) → caller falls back to device-code.
 */
async function silentRefresh() {
  const refreshToken = readRefreshToken();
  const form = new URLSearchParams({
    grant_type: 'refresh_token',
    client_id: CLIENT_ID,
    refresh_token: refreshToken,
    scope: SCOPES,
  }).toString();

  const { statusCode, json, raw } = await request({
    hostname: 'login.microsoftonline.com',
    port: 443,
    path: '/consumers/oauth2/v2.0/token',
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Content-Length': Buffer.byteLength(form),
    },
  }, form);

  if (statusCode !== 200 || !json || !json.access_token) {
    const errCode = json && json.error;
    const hint = errCode === 'invalid_grant'
      ? ' Refresh token is dead (>90d or rotated) — run the device-code flow (CLAUDE.md / ms365-session-login-procedure.md Step 4).'
      : '';
    throw new Error(`Silent refresh failed (HTTP ${statusCode}, error=${errCode || '?'}).${hint}\n${raw.slice(0, 300)}`);
  }

  // Stage → validate → write (matches CLAUDE.md: never blind-pipe into live file).
  fs.writeFileSync(STAGING_FILE, JSON.stringify(json));
  for (const f of TOKEN_FILES) {
    try {
      fs.mkdirSync(path.dirname(f), { recursive: true });
      fs.copyFileSync(STAGING_FILE, f);
      fs.chmodSync(f, 0o600);
    } catch (err) {
      // /tmp should always work; the ~/.claude mirror is best-effort.
      if (f === TOKEN_FILES[0]) throw err;
    }
  }
  return json.access_token;
}

/**
 * Return a known-good access token: use the cached one if /me returns 200,
 * otherwise silently refresh. Throws (loudly) only if refresh itself fails.
 */
async function getValidAccessToken() {
  const cached = readCachedAccessToken();
  if (cached) {
    const { statusCode } = await graphRequest('/me', cached);
    if (statusCode === 200) return cached;
  }
  return silentRefresh();
}

/**
 * GET a Graph path, parsed to JSON. Auto-refreshes once on a 401.
 * @returns {Promise<object>} the parsed Graph response body
 */
async function graphGet(graphPath) {
  let token = await getValidAccessToken();
  let res = await graphRequest(graphPath, token);
  if (res.statusCode === 401) {
    token = await silentRefresh();
    res = await graphRequest(graphPath, token);
  }
  if (res.statusCode !== 200) {
    throw new Error(`Graph GET ${graphPath} → HTTP ${res.statusCode}: ${res.raw.slice(0, 300)}`);
  }
  return res.json;
}

module.exports = {
  CLIENT_ID,
  getValidAccessToken,
  silentRefresh,
  graphGet,
  graphRequest,
};
