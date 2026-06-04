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
 * The PUT carries notify_enabled:true, which fires the Agent Hub team broadcast.
 * After the PUT, this script VERIFIES the broadcast actually went out by polling
 * HarvRealtor@outlook.com for the "[Agent Hub] Confirmation" email (see
 * verify-broadcast.js). On 2026-06-03 the note updated but the backend never
 * sent and nothing noticed — this safety net makes that silent failure loud.
 *
 * Usage:
 *   node update-note-body.js [json-template] [html-file]
 *   node update-note-body.js --no-verify          # just PUT, skip the safety net
 *   node update-note-body.js --retry              # auto re-broadcast once if unconfirmed
 *   node update-note-body.js --timeout 300 --poll 20
 *
 * If no positional args provided, auto-detects from daily-market-template.json.
 * Reads note ID from agent_hub_link in JSON template; ADMIN_TOKEN from .env.
 * Exit codes: 0 = updated (+ broadcast confirmed, unless --no-verify),
 *             2 = broadcast NOT confirmed, 3 = could not verify, 1 = error.
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const { verifyBroadcast, printVerdict } = require('./verify-broadcast');

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
      body: htmlBody,
      category: ['At a Glance'],
      notify_enabled: true
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

/**
 * Update the Agent Hub note body with the final email HTML. The PUT carries
 * notify_enabled:true, which fires the team broadcast.
 * @param {object} [o]
 * @param {string} [o.jsonFile] - template path (default daily-market-template.json)
 * @param {string} [o.htmlFile] - HTML path (default daily-market-glance-MMDDYY.html)
 * @returns {Promise<{noteId, date, agentHubLink, title, htmlSize}>}
 */
async function updateNoteBody({ jsonFile = 'daily-market-template.json', htmlFile } = {}) {
  if (!fs.existsSync(jsonFile)) {
    throw new Error(`JSON template not found: ${jsonFile}`);
  }
  const data = JSON.parse(fs.readFileSync(jsonFile, 'utf8'));

  if (!data.agent_hub_link) {
    throw new Error('No agent_hub_link found in JSON template');
  }
  const noteId = extractNoteId(data.agent_hub_link);

  const dateForFile = data.date.replace(/\//g, '');
  const resolvedHtml = htmlFile || `daily-market-glance-${dateForFile}.html`;
  if (!fs.existsSync(resolvedHtml)) {
    throw new Error(`HTML file not found: ${resolvedHtml}. Run generate-daily-email.js first.`);
  }
  const htmlBody = fs.readFileSync(resolvedHtml, 'utf8');

  const env = loadEnv();
  if (!env.ADMIN_TOKEN) {
    throw new Error('ADMIN_TOKEN not found in .env');
  }

  const title = `"At a Glance" Local Housing STATS and News ${data.date}`;

  console.log(`📝 Updating Agent Hub note: ${noteId}`);
  console.log(`   Title: ${title}`);
  console.log(`   HTML size: ${htmlBody.length} chars`);

  await updateNote(noteId, title, htmlBody, env.ADMIN_TOKEN);
  console.log(`✅ Agent Hub note updated — broadcast triggered.`);
  console.log(`🔗 View at: ${data.agent_hub_link}`);

  return { noteId, date: data.date, agentHubLink: data.agent_hub_link, title, htmlSize: htmlBody.length };
}

function parseCliArgs(argv) {
  const opts = { verify: true, retry: false, positionals: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--no-verify') opts.verify = false;
    else if (a === '--verify') opts.verify = true;
    else if (a === '--retry') opts.retry = true;
    else if (a === '--timeout') opts.timeoutMs = parseInt(argv[++i], 10) * 1000;
    else if (a === '--poll') opts.pollMs = parseInt(argv[++i], 10) * 1000;
    else if (!a.startsWith('--')) opts.positionals.push(a);
  }
  return opts;
}

async function main() {
  const opts = parseCliArgs(process.argv.slice(2));
  const jsonFile = opts.positionals[0] || 'daily-market-template.json';
  const htmlFile = opts.positionals[1];

  // Capture the trigger window BEFORE the PUT (90s back-buffer for clock skew),
  // so verification only counts a confirmation produced by THIS broadcast — and
  // a same-day re-run won't false-match an earlier confirmation.
  const sinceIso = new Date(Date.now() - 90 * 1000).toISOString();

  let info;
  try {
    info = await updateNoteBody({ jsonFile, htmlFile });
  } catch (err) {
    console.error(`❌ Failed to update note: ${err.message}`);
    process.exit(1);
  }

  if (!opts.verify) {
    console.log('\n⏭️  Skipping broadcast verification (--no-verify). The broadcast WAS triggered;');
    console.log(`   confirm by hand or run:  node verify-broadcast.js --date ${info.date}`);
    process.exit(0);
  }

  // --- Broadcast safety net: prove the confirmation email actually arrived. ---
  let result = await verifyBroadcast({ date: info.date, sinceIso, timeoutMs: opts.timeoutMs, pollMs: opts.pollMs });

  // Optional single auto-retry — only when we positively saw the confirmation is
  // ABSENT (fetchedOk). If we couldn't read the mailbox at all, blindly
  // re-broadcasting risks double-spamming agents, so we don't.
  if (!result.confirmed && result.fetchedOk && opts.retry) {
    console.log('\n🔁 --retry: broadcast not confirmed — re-triggering once…');
    const retrySince = new Date(Date.now() - 90 * 1000).toISOString();
    try {
      await updateNoteBody({ jsonFile, htmlFile });
    } catch (err) {
      console.error(`❌ Retry PUT failed: ${err.message}`);
    }
    result = await verifyBroadcast({ date: info.date, sinceIso: retrySince, timeoutMs: opts.timeoutMs, pollMs: opts.pollMs });
  }

  process.exit(printVerdict(result, info.date));
}

if (require.main === module) {
  main().catch((err) => {
    console.error('\nFatal error:', err.message);
    process.exit(1);
  });
}

module.exports = { updateNoteBody, updateNote, parseCliArgs, main };
