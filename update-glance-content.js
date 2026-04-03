#!/usr/bin/env node

/**
 * update-glance-content.js
 *
 * Updates all 4 content types on the todays-inventory page via glance-api.
 * Auto-detects date and note ID from daily-market-template.json.
 *
 * Usage:
 *   node update-glance-content.js                # updates news, image_1, image_2
 *   node update-glance-content.js --with-chart   # also updates html_display (runs upload-inventory-chart.js)
 *
 * Content types:
 *   - news: banner card with title, date, link to Agent Hub note
 *   - image_1: GitHub raw URL for RE-Daily-1-MMDDYY.png
 *   - image_2: GitHub raw URL for RE-Daily-2-MMDDYY.png
 *   - html_display: inventory chart (via upload-inventory-chart.js)
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const { execFileSync } = require('child_process');

const SUPABASE_HOST = 'hbsodfrxadlfladdgvgy.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imhic29kZnJ4YWRsZmxhZGRndmd5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI5MTA2MDcsImV4cCI6MjA4ODQ4NjYwN30.tuF35cSBp4mS31X4wtmBsFnLQil-UZ-oX_FXu6QN-fM';
const GITHUB_RAW = 'https://raw.githubusercontent.com/fremontrealtyexperts-510/RealtyExperts-Daily-Email/main';

function loadEnv() {
  const envPath = path.join(__dirname, '.env');
  if (!fs.existsSync(envPath)) { console.error('❌ .env not found'); process.exit(1); }
  const vars = {};
  fs.readFileSync(envPath, 'utf8').split('\n').forEach(line => {
    const match = line.match(/^([^=]+)=(.*)$/);
    if (match) vars[match[1].trim()] = match[2].trim();
  });
  return vars;
}

function postGlanceAPI(payload) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify(payload);
    const req = https.request({
      hostname: SUPABASE_HOST,
      path: '/functions/v1/glance-api',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body),
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
      }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          // Success = response has 'id' field. No 'message' field exists.
          if (parsed.id) {
            resolve({ success: true, content_type: parsed.content_type, id: parsed.id });
          } else {
            resolve({ success: false, error: parsed.error || data });
          }
        } catch {
          resolve({ success: false, error: `HTTP ${res.statusCode}: ${data}` });
        }
      });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

function formatDate(dateStr) {
  // "04/02/26" → "April 2, 2026"
  const months = ['January','February','March','April','May','June','July','August','September','October','November','December'];
  const [mm, dd, yy] = dateStr.split('/');
  return `${months[parseInt(mm)-1]} ${parseInt(dd)}, 20${yy}`;
}

async function main() {
  const withChart = process.argv.includes('--with-chart');

  // Load template
  const templatePath = path.join(__dirname, 'daily-market-template.json');
  if (!fs.existsSync(templatePath)) {
    console.error('❌ daily-market-template.json not found');
    process.exit(1);
  }
  const data = JSON.parse(fs.readFileSync(templatePath, 'utf8'));
  const dateStr = data.date.replace(/\//g, '');
  const prettyDate = formatDate(data.date);
  const agentHubLink = data.agent_hub_link;
  const env = loadEnv();

  console.log(`\n📊 Updating todays-inventory page for ${data.date}\n`);

  let passed = 0;
  let failed = 0;

  // --- 1. News banner ---
  const newsHTML = `<div style='padding:16px;background:#fff7ed;border-left:4px solid #ea580c;border-radius:8px;margin-bottom:12px;'><div style='font-weight:700;font-size:16px;color:#ea580c;margin-bottom:4px;'>"At a Glance" Local Housing STATS and News</div><div style='font-size:13px;color:#64748b;margin-bottom:8px;'>${prettyDate}</div><div style='font-size:14px;color:#334155;'>Today&apos;s market update is ready.</div><div style='margin-top:10px;'><a href='${agentHubLink}' style='color:#ea580c;font-weight:600;text-decoration:none;font-size:14px;'>Read Full Report &rarr;</a></div></div>`;

  const newsResult = await postGlanceAPI({
    action: 'UPDATE', token: env.ADMIN_TOKEN,
    content_type: 'news', content: newsHTML
  });
  if (newsResult.success) { console.log('   ✅ news: updated'); passed++; }
  else { console.log(`   ❌ news: ${newsResult.error}`); failed++; }

  // --- 2. Image 1 ---
  const img1Result = await postGlanceAPI({
    action: 'UPDATE', token: env.ADMIN_TOKEN,
    content_type: 'image_1',
    image_url: `${GITHUB_RAW}/RE-Daily-1-${dateStr}.png`
  });
  if (img1Result.success) { console.log('   ✅ image_1: updated'); passed++; }
  else { console.log(`   ❌ image_1: ${img1Result.error}`); failed++; }

  // --- 3. Image 2 ---
  const img2Result = await postGlanceAPI({
    action: 'UPDATE', token: env.ADMIN_TOKEN,
    content_type: 'image_2',
    image_url: `${GITHUB_RAW}/RE-Daily-2-${dateStr}.png`
  });
  if (img2Result.success) { console.log('   ✅ image_2: updated'); passed++; }
  else { console.log(`   ❌ image_2: ${img2Result.error}`); failed++; }

  // --- 4. Chart (optional) ---
  if (withChart) {
    console.log('   📈 Running upload-inventory-chart.js...');
    try {
      const output = execFileSync('node', ['upload-inventory-chart.js'], { cwd: __dirname, encoding: 'utf8' });
      if (output.includes('Successfully')) {
        console.log('   ✅ html_display: updated');
        passed++;
      } else {
        console.log(`   ❌ html_display: ${output.trim()}`);
        failed++;
      }
    } catch (err) {
      console.log(`   ❌ html_display: ${err.message}`);
      failed++;
    }
  }

  // --- Summary ---
  console.log(`\n${failed === 0 ? '✅' : '⚠️'}  ${passed} updated, ${failed} failed`);
  console.log(`🔗 Live at: https://teamrealtyexperts.com/todays-inventory\n`);

  process.exit(failed > 0 ? 1 : 0);
}

main();
