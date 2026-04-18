#!/usr/bin/env node

/**
 * mint-service-token.js
 *
 * Mints a 90-day ADMIN_TOKEN by calling validate-access-code with loginType: 'service'.
 * Reads ADMIN_ACCESS_CODE from REALTY-EXPERTS-Agent-Hub/.env.secrets — no user prompt.
 * Saves token to .env (overwrites existing ADMIN_TOKEN line, preserves others).
 *
 * Usage: node mint-service-token.js
 *
 * Run automatically by ensure-token.js when the existing token is expired/invalid.
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

const SECRETS_FILE = '/Users/harvinderbalu1/Library/CloudStorage/OneDrive-Personal/ClaudeCode/REALTY-EXPERTS-Agent-Hub/.env.secrets';
const ENV_FILE = path.join(__dirname, '.env');
const SUPABASE_HOST = 'hbsodfrxadlfladdgvgy.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imhic29kZnJ4YWRsZmxhZGRndmd5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI5MTA2MDcsImV4cCI6MjA4ODQ4NjYwN30.tuF35cSBp4mS31X4wtmBsFnLQil-UZ-oX_FXu6QN-fM';

function readAdminCode() {
  if (!fs.existsSync(SECRETS_FILE)) {
    throw new Error(`Secrets file not found: ${SECRETS_FILE}`);
  }
  const content = fs.readFileSync(SECRETS_FILE, 'utf8');
  const match = content.match(/^ADMIN_ACCESS_CODE=(.+)$/m);
  if (!match) {
    throw new Error('ADMIN_ACCESS_CODE not found in .env.secrets');
  }
  return match[1].trim();
}

function callValidateAccessCode(code) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({ code, loginType: 'service' });
    const req = https.request({
      hostname: SUPABASE_HOST,
      path: '/functions/v1/validate-access-code',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body),
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
        'Origin': 'https://teamrealtyexperts.com',
      },
    }, (res) => {
      let raw = '';
      res.on('data', c => raw += c);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(raw);
          if (res.statusCode === 200 && parsed.valid) resolve(parsed.sessionToken);
          else reject(new Error(`HTTP ${res.statusCode}: ${raw}`));
        } catch (e) {
          reject(new Error(`Parse error: ${raw}`));
        }
      });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

function saveTokenToEnv(token) {
  let envContent = '';
  if (fs.existsSync(ENV_FILE)) {
    envContent = fs.readFileSync(ENV_FILE, 'utf8');
  }
  // Replace existing ADMIN_TOKEN line, or append if missing
  if (/^ADMIN_TOKEN=/m.test(envContent)) {
    envContent = envContent.replace(/^ADMIN_TOKEN=.*$/m, `ADMIN_TOKEN=${token}`);
  } else {
    envContent = envContent.trimEnd() + (envContent ? '\n' : '') + `ADMIN_TOKEN=${token}\n`;
  }
  fs.writeFileSync(ENV_FILE, envContent, 'utf8');
}

function decodeTokenExp(token) {
  try {
    const [payloadB64] = token.split('.');
    const padded = payloadB64 + '==='.slice((payloadB64.length + 3) % 4);
    const payload = JSON.parse(Buffer.from(padded.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString('utf8'));
    return new Date(payload.exp).toISOString();
  } catch {
    return 'unknown';
  }
}

async function main() {
  console.log('🔑 Reading ADMIN_ACCESS_CODE from .env.secrets...');
  const code = readAdminCode();

  console.log('📡 Calling validate-access-code (loginType: service)...');
  const token = await callValidateAccessCode(code);

  console.log('💾 Saving 90-day ADMIN_TOKEN to .env...');
  saveTokenToEnv(token);

  console.log(`✅ Token minted. Expires: ${decodeTokenExp(token)}`);
}

main().catch(err => {
  console.error(`❌ ${err.message}`);
  process.exit(1);
});
