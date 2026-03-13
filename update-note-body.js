#!/usr/bin/env node

/**
 * update-note-body.js
 *
 * Updates the Agent Hub note body with the final generated email HTML.
 *
 * This solves the chicken-and-egg workflow problem:
 *   Step 1: Note created (but QR code doesn't exist yet → incomplete HTML)
 *   Step 3: QR code generated (needs note ID from step 1)
 *   Step 6: Email HTML regenerated with correct QR code path
 *   Step 6.5: THIS SCRIPT → updates note body with final HTML
 *
 * Usage:
 *   node update-note-body.js [json-template] [html-file]
 *
 * If no arguments provided, auto-detects from daily-market-template.json
 *
 * Reads note ID from agent_hub_link in JSON template.
 * Reads ADMIN_TOKEN from .env file.
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

// Supabase config
const SUPABASE_HOST = 'hbsodfrxadlfladdgvgy.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imhic29kZnJ4YWRsZmxhZGRndmd5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI5MTA2MDcsImV4cCI6MjA4ODQ4NjYwN30.tuF35cSBp4mS31X4wtmBsFnLQil-UZ-oX_FXu6QN-fM';

function loadEnv() {
  const envPath = path.join(__dirname, '.env');
  if (!fs.existsSync(envPath)) {
    console.error('❌ .env file not found');
    process.exit(1);
  }
  const envContent = fs.readFileSync(envPath, 'utf8');
  const vars = {};
  envContent.split('\n').forEach(line => {
    const match = line.match(/^([^=]+)=(.*)$/);
    if (match) vars[match[1].trim()] = match[2].trim();
  });
  return vars;
}

function extractNoteId(agentHubLink) {
  // Extract UUID from https://teamrealtyexperts.com/share/{noteId}
  const match = agentHubLink.match(/\/share\/([a-f0-9-]+)/);
  if (!match) {
    console.error('❌ Could not extract note ID from agent_hub_link:', agentHubLink);
    process.exit(1);
  }
  return match[1];
}

function updateNote(noteId, title, htmlBody, adminToken) {
  return new Promise((resolve, reject) => {
    const payload = JSON.stringify({
      title: title,
      body: htmlBody
    });

    const options = {
      hostname: SUPABASE_HOST,
      port: 443,
      path: `/functions/v1/notes-api/${noteId}`,
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(payload),
        'x-session-token': adminToken,
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
        'Origin': 'https://teamrealtyexperts.com'
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode === 200) {
          resolve(data);
        } else {
          reject(new Error(`HTTP ${res.statusCode}: ${data}`));
        }
      });
    });

    req.on('error', reject);
    req.write(payload);
    req.end();
  });
}

async function main() {
  const args = process.argv.slice(2);
  const jsonFile = args[0] || 'daily-market-template.json';

  // Load JSON template
  if (!fs.existsSync(jsonFile)) {
    console.error(`❌ JSON template not found: ${jsonFile}`);
    process.exit(1);
  }
  const data = JSON.parse(fs.readFileSync(jsonFile, 'utf8'));

  // Extract note ID
  if (!data.agent_hub_link) {
    console.error('❌ No agent_hub_link found in JSON template');
    process.exit(1);
  }
  const noteId = extractNoteId(data.agent_hub_link);

  // Determine HTML file
  const dateForFile = data.date.replace(/\//g, '');
  const htmlFile = args[1] || `daily-market-glance-${dateForFile}.html`;

  if (!fs.existsSync(htmlFile)) {
    console.error(`❌ HTML file not found: ${htmlFile}`);
    console.error('   Run generate-daily-email.js first to create the HTML file.');
    process.exit(1);
  }

  // Load HTML body
  const htmlBody = fs.readFileSync(htmlFile, 'utf8');

  // Load admin token
  const env = loadEnv();
  if (!env.ADMIN_TOKEN) {
    console.error('❌ ADMIN_TOKEN not found in .env');
    process.exit(1);
  }

  // Build title
  const title = `"At a Glance" Local Housing STATS and News ${data.date}`;

  console.log(`📝 Updating Agent Hub note: ${noteId}`);
  console.log(`   Title: ${title}`);
  console.log(`   HTML size: ${htmlBody.length} chars`);

  try {
    const response = await updateNote(noteId, title, htmlBody, env.ADMIN_TOKEN);
    console.log(`✅ Agent Hub note updated successfully!`);
    console.log(`🔗 View at: ${data.agent_hub_link}`);
  } catch (err) {
    console.error(`❌ Failed to update note: ${err.message}`);
    process.exit(1);
  }
}

main();
