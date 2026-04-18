#!/usr/bin/env node

/**
 * ensure-token.js
 *
 * Pre-flight check: ensures ADMIN_TOKEN in .env is valid.
 * Auto-renews via mint-service-token.js when needed. Zero user involvement.
 *
 * Renews if:
 *   - .env or ADMIN_TOKEN line missing
 *   - Token is malformed
 *   - Token expires within 7 days
 *   - Live API ping returns 401 (token rotated/invalidated server-side)
 *
 * Otherwise prints status and exits 0.
 *
 * Usage: node ensure-token.js
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const { execFileSync } = require('child_process');

const ENV_FILE = path.join(__dirname, '.env');
const SUPABASE_HOST = 'hbsodfrxadlfladdgvgy.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imhic29kZnJ4YWRsZmxhZGRndmd5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI5MTA2MDcsImV4cCI6MjA4ODQ4NjYwN30.tuF35cSBp4mS31X4wtmBsFnLQil-UZ-oX_FXu6QN-fM';
const RENEW_THRESHOLD_MS = 7 * 24 * 60 * 60 * 1000;

function readToken() {
  if (!fs.existsSync(ENV_FILE)) return null;
  const match = fs.readFileSync(ENV_FILE, 'utf8').match(/^ADMIN_TOKEN=(.+)$/m);
  return match ? match[1].trim() : null;
}

function decodeExp(token) {
  try {
    const [payloadB64] = token.split('.');
    const padded = payloadB64 + '==='.slice((payloadB64.length + 3) % 4);
    const payload = JSON.parse(Buffer.from(padded.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString('utf8'));
    return payload.exp;
  } catch {
    return null;
  }
}

function pingNotesApi(token) {
  return new Promise((resolve) => {
    const req = https.request({
      hostname: SUPABASE_HOST,
      path: '/functions/v1/notes-api?limit=1',
      method: 'GET',
      headers: {
        'x-session-token': token,
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
        'Origin': 'https://teamrealtyexperts.com',
      },
    }, (res) => {
      res.on('data', () => {});
      res.on('end', () => resolve(res.statusCode));
    });
    req.on('error', () => resolve(0));
    req.end();
  });
}

function mintNewToken() {
  console.log('🔄 Renewing token via mint-service-token.js...');
  execFileSync('node', [path.join(__dirname, 'mint-service-token.js')], { stdio: 'inherit' });
}

async function main() {
  const token = readToken();

  if (!token) {
    console.log('⚠️  No ADMIN_TOKEN in .env — minting new one');
    mintNewToken();
    return;
  }

  const exp = decodeExp(token);
  if (!exp) {
    console.log('⚠️  Token is malformed — minting new one');
    mintNewToken();
    return;
  }

  const msUntilExp = exp - Date.now();
  const daysLeft = Math.floor(msUntilExp / (24 * 60 * 60 * 1000));

  if (msUntilExp <= 0) {
    console.log(`⚠️  Token expired ${Math.abs(daysLeft)} days ago — minting new one`);
    mintNewToken();
    return;
  }

  if (msUntilExp < RENEW_THRESHOLD_MS) {
    console.log(`⚠️  Token expires in ${daysLeft} days (under 7-day threshold) — renewing`);
    mintNewToken();
    return;
  }

  // Live ping — catches server-side token rotation
  const status = await pingNotesApi(token);
  if (status === 401 || status === 403) {
    console.log(`⚠️  Token rejected by API (HTTP ${status}) — renewing`);
    mintNewToken();
    return;
  }

  if (status !== 200) {
    console.log(`⚠️  API ping returned HTTP ${status} — token may still be valid, proceeding`);
  }

  console.log(`✅ Token valid (${daysLeft} days left, API ping ${status})`);
}

main().catch(err => {
  console.error(`❌ ${err.message}`);
  process.exit(1);
});
