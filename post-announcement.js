#!/usr/bin/env node
/**
 * post-announcement.js — publish a one-off HTML announcement to the Agent Hub.
 *
 * Two-step on purpose, so Harv can review the LIVE note before ~105 agents get
 * an email. The broadcast fires when notify_enabled flips false -> true on a PUT
 * (same mechanism the daily flow uses via update-note-body.js).
 *
 *   # 1. create silently (notify_enabled:false); prints the share URL for review
 *   node post-announcement.js create --html FILE.html --title "..." [--category announcement,training]
 *
 *   # 1b. revise it as many times as needed, still silent
 *   node post-announcement.js update --note-id UUID --html FILE.html --title "..." [--category ...]
 *
 *   # 2. fire the broadcast for that note, then verify the confirmation email
 *   node post-announcement.js fire --note-id UUID --html FILE.html --title "..." [--category ...] [--no-verify]
 *
 * Verification polls HarvRealtor@outlook.com (Graph, token at /tmp/ms365-token.json)
 * for "[Agent Hub] Confirmation: <title>" received after the PUT, up to 5 minutes.
 * Exit codes mirror update-note-body.js: 0 confirmed, 2 not confirmed, 3 could not verify.
 *
 * Added 2026-08-21 for the Chuck Edell C.A.R. Listing Agreement class announcement.
 */
const fs = require('fs');
const https = require('https');
const { SUPABASE_HOSTNAME, ANON_KEY } = require('./lib/config');
const { readAdminToken } = require('./lib/tokens');
const { notesApiPost } = require('./lib/api');

function arg(name, dflt) {
  const i = process.argv.indexOf(name);
  return i !== -1 ? process.argv[i + 1] : dflt;
}
function has(name) { return process.argv.includes(name); }

const mode = process.argv[2];
const htmlFile = arg('--html');
const title = arg('--title');
const categories = (arg('--category', 'announcement') || '').split(',').map(s => s.trim()).filter(Boolean);
const noteId = arg('--note-id');

function die(msg) { console.error('❌', msg); process.exit(1); }
if (!['create', 'update', 'fire'].includes(mode)) die('usage: post-announcement.js create|update|fire ...');
if (!htmlFile || !fs.existsSync(htmlFile)) die('--html FILE is required and must exist');
if (!title) die('--title is required');
const body = fs.readFileSync(htmlFile, 'utf8');
if (/—|–/.test(body) || /—|–/.test(title)) die('house style: em/en dash found in body or title');

function putNote(id, payload, adminToken, nonce) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify(payload);
    const req = https.request({
      hostname: SUPABASE_HOSTNAME, port: 443, method: 'PUT',
      path: `/functions/v1/notes-api/${id}`,
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data),
        'apikey': ANON_KEY,
        'Authorization': `Bearer ${ANON_KEY}`,
        'x-session-token': adminToken,
        'x-session-id': nonce,
        'Origin': 'https://teamrealtyexperts.com',
      },
    }, res => {
      let out = '';
      res.on('data', c => out += c);
      res.on('end', () => res.statusCode === 200 ? resolve(out) : reject(new Error(`HTTP ${res.statusCode}: ${out}`)));
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

function graphGet(path, token) {
  return new Promise((resolve, reject) => {
    https.get({ hostname: 'graph.microsoft.com', path, headers: { Authorization: `Bearer ${token}` } }, res => {
      let out = '';
      res.on('data', c => out += c);
      res.on('end', () => { try { resolve(JSON.parse(out)); } catch (e) { reject(e); } });
    }).on('error', reject);
  });
}

async function verifyConfirmation(sinceIso, timeoutSec = 300, pollSec = 20) {
  let token;
  try { token = JSON.parse(fs.readFileSync('/tmp/ms365-token.json', 'utf8')).access_token; }
  catch { return { status: 'could-not-verify', reason: 'no MS365 token at /tmp/ms365-token.json' }; }
  const deadline = Date.now() + timeoutSec * 1000;
  const needle = title.slice(0, 40).toLowerCase();
  let poll = 0;
  while (Date.now() < deadline) {
    poll++;
    let data;
    try {
      data = await graphGet('/v1.0/me/messages?$top=30&$select=id,subject,from,receivedDateTime&$orderby=receivedDateTime%20desc', token);
    } catch (e) { return { status: 'could-not-verify', reason: e.message }; }
    if (data.error) return { status: 'could-not-verify', reason: data.error.message || 'graph error' };
    const hit = (data.value || []).find(m => {
      const s = (m.subject || '').toLowerCase();
      const from = ((m.from || {}).emailAddress || {}).address || '';
      return s.includes('[agent hub] confirmation') && s.includes(needle)
        && from.toLowerCase() === 'fremontrealtyexperts@gmail.com'
        && m.receivedDateTime >= sinceIso;
    });
    if (hit) return { status: 'confirmed', subject: hit.subject, received: hit.receivedDateTime, polls: poll };
    console.log(`   …not yet (poll ${poll})`);
    await new Promise(r => setTimeout(r, pollSec * 1000));
  }
  return { status: 'failed', polls: poll };
}

(async () => {
  const { adminToken, nonce } = readAdminToken();
  if (mode === 'create') {
    console.log(`📝 Creating announcement (notify OFF): "${title}"`);
    console.log(`   categories: ${categories.join(', ')} | body: ${body.length} chars`);
    const res = await notesApiPost({
      title, body, category: categories, visibility: 'public', body_format: 'html',
      author_name: 'REALTY EXPERTS', notify_enabled: false,
    }, adminToken, nonce);
    if (!res.id) die('no id returned: ' + JSON.stringify(res));
    console.log(`\n✅ Created. Note ID: ${res.id}`);
    console.log(`   Review: https://teamrealtyexperts.com/share/${res.id}`);
    console.log(`   Fire:   node post-announcement.js fire --note-id ${res.id} --html ${htmlFile} --title "<same title>" --category ${categories.join(',')}`);
    return;
  }
  if (!noteId) die(`--note-id is required for ${mode}`);
  if (mode === 'update') {
    // Explicit notify_enabled:false. shouldNotifyOnUpdate() fires on a "major
    // edit" (title change or >20% body length move) UNLESS isNotifyEnabled is
    // exactly false, so this flag is what makes a revision safe to save.
    console.log(`✏️  Updating note ${noteId} (notify explicitly OFF, no broadcast)`);
    await putNote(noteId, { title, body, category: categories, body_format: 'html', notify_enabled: false }, adminToken, nonce);
    console.log(`✅ Updated. Review: https://teamrealtyexperts.com/share/${noteId}`);
    return;
  }
  const since = new Date(Date.now() - 60 * 1000).toISOString();
  console.log(`🚀 Firing broadcast for note ${noteId} (PUT notify_enabled:true)`);
  await putNote(noteId, { title, body, category: categories, body_format: 'html', notify_enabled: true }, adminToken, nonce);
  console.log('✅ Note updated, broadcast triggered.');
  console.log(`🔗 https://teamrealtyexperts.com/share/${noteId}`);
  if (has('--no-verify')) return;
  console.log('🔎 Verifying the broadcast (looking for the [Agent Hub] Confirmation email)…');
  const v = await verifyConfirmation(since);
  const bar = '='.repeat(64);
  if (v.status === 'confirmed') {
    console.log(`\n${bar}\n  ✅ BROADCAST CONFIRMED — agents were notified\n${bar}\n  "${v.subject}"\n  received ${v.received} after ${v.polls} poll(s)`);
    process.exit(0);
  } else if (v.status === 'failed') {
    console.log(`\n${bar}\n  ❌ BROADCAST NOT CONFIRMED within 5 min\n${bar}\n  check supabase functions logs send-notification`);
    process.exit(2);
  } else {
    console.log(`\n${bar}\n  ⚠️ COULD NOT VERIFY (${v.reason})\n${bar}`);
    process.exit(3);
  }
})().catch(e => die(e.message));
