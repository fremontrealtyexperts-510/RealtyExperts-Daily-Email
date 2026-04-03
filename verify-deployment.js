#!/usr/bin/env node

/**
 * verify-deployment.js
 *
 * Runs all 4 post-workflow verification checks in one command.
 * Use after completing the daily email workflow.
 *
 * Usage:
 *   node verify-deployment.js                    # auto-detects from template
 *   node verify-deployment.js 040226 <noteId>    # explicit date and note ID
 *
 * Checks:
 *   1. Note body length (>= 25000 chars)
 *   2. Note category is ['At a Glance']
 *   3. QR code URL present in note body
 *   4. Images accessible on GitHub (HTTP 200)
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

const SUPABASE_HOST = 'hbsodfrxadlfladdgvgy.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imhic29kZnJ4YWRsZmxhZGRndmd5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI5MTA2MDcsImV4cCI6MjA4ODQ4NjYwN30.tuF35cSBp4mS31X4wtmBsFnLQil-UZ-oX_FXu6QN-fM';
const GITHUB_RAW = 'https://raw.githubusercontent.com/fremontrealtyexperts-510/RealtyExperts-Daily-Email/main';

function loadEnv() {
  const envPath = path.join(__dirname, '.env');
  if (!fs.existsSync(envPath)) return {};
  const vars = {};
  fs.readFileSync(envPath, 'utf8').split('\n').forEach(line => {
    const match = line.match(/^([^=]+)=(.*)$/);
    if (match) vars[match[1].trim()] = match[2].trim();
  });
  return vars;
}

function fetchJSON(url, headers) {
  return new Promise((resolve, reject) => {
    const parsed = new URL(url);
    const opts = {
      hostname: parsed.hostname,
      path: parsed.pathname + parsed.search,
      method: 'GET',
      headers: headers || {}
    };
    https.get(url, { headers: headers || {} }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch { resolve({ _raw: data, _status: res.statusCode }); }
      });
    }).on('error', reject);
  });
}

function headCheck(url) {
  return new Promise((resolve) => {
    https.request(url, { method: 'HEAD' }, (res) => {
      resolve(res.statusCode);
    }).on('error', () => resolve(0)).end();
  });
}

async function main() {
  const args = process.argv.slice(2);
  let dateStr, noteId;

  if (args.length >= 2) {
    dateStr = args[0];
    noteId = args[1];
  } else {
    // Auto-detect from template
    const templatePath = path.join(__dirname, 'daily-market-template.json');
    if (!fs.existsSync(templatePath)) {
      console.error('❌ daily-market-template.json not found. Provide date and noteId as arguments.');
      process.exit(1);
    }
    const data = JSON.parse(fs.readFileSync(templatePath, 'utf8'));
    dateStr = data.date.replace(/\//g, '');
    const linkMatch = (data.agent_hub_link || '').match(/\/share\/([a-f0-9-]+)/);
    if (!linkMatch) {
      console.error('❌ No agent_hub_link in template');
      process.exit(1);
    }
    noteId = linkMatch[1];
  }

  console.log(`\n🔍 Verifying deployment for ${dateStr} (note: ${noteId.substring(0, 8)}...)\n`);

  const env = loadEnv();
  const adminToken = env.ADMIN_TOKEN || '';
  let passed = 0;
  let failed = 0;

  // --- Check 1: Note content via GET /notes-api/{noteId} ---
  console.log('1️⃣  Checking Agent Hub note...');
  const headers = {
    'x-session-token': adminToken,
    'apikey': SUPABASE_ANON_KEY,
    'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
    'Origin': 'https://teamrealtyexperts.com'
  };
  const note = await fetchJSON(
    `https://${SUPABASE_HOST}/functions/v1/notes-api/${noteId}`,
    headers
  );

  const body = note.body || '';
  const bodyLen = body.length;
  const category = note.category;
  const hasQR = body.includes('note-qr');
  const title = note.title || '';

  // Body length
  if (bodyLen >= 25000) {
    console.log(`   ✅ Body: ${bodyLen.toLocaleString()} chars`);
    passed++;
  } else {
    console.log(`   ❌ Body: ${bodyLen.toLocaleString()} chars (need 25,000+)`);
    failed++;
  }

  // Category
  const catOK = Array.isArray(category) && category.includes('At a Glance');
  if (catOK) {
    console.log(`   ✅ Category: ${JSON.stringify(category)}`);
    passed++;
  } else {
    console.log(`   ❌ Category: ${JSON.stringify(category)} (should be ['At a Glance'])`);
    failed++;
  }

  // QR in body
  if (hasQR) {
    console.log(`   ✅ QR code URL present in body`);
    passed++;
  } else {
    console.log(`   ❌ QR code URL NOT found in body`);
    failed++;
  }

  // Title
  console.log(`   📌 Title: ${title}`);

  // --- Check 2: Images on GitHub ---
  console.log('\n2️⃣  Checking GitHub images...');
  const images = [
    `RE-Daily-1-${dateStr}.png`,
    `RE-Daily-2-${dateStr}.png`
  ];

  // Also find QR code filename from body
  const qrMatch = body.match(/note-qr-[a-f0-9]+\.png/);
  if (qrMatch) images.push(qrMatch[0]);

  for (const img of images) {
    const status = await headCheck(`${GITHUB_RAW}/${img}`);
    if (status === 200) {
      console.log(`   ✅ ${img}: HTTP ${status}`);
      passed++;
    } else {
      console.log(`   ❌ ${img}: HTTP ${status}`);
      failed++;
    }
  }

  // --- Summary ---
  console.log(`\n${'─'.repeat(40)}`);
  if (failed === 0) {
    console.log(`✅ All ${passed} checks passed!`);
  } else {
    console.log(`⚠️  ${passed} passed, ${failed} failed`);
  }
  console.log(`🔗 Agent Hub: https://teamrealtyexperts.com/share/${noteId}`);
  console.log(`🌐 Web view:  https://fremontrealtyexperts-510.github.io/RealtyExperts-Daily-Email/daily-market-glance-${dateStr}.html`);
  console.log('');

  process.exit(failed > 0 ? 1 : 0);
}

main();
