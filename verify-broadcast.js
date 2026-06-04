#!/usr/bin/env node

/**
 * verify-broadcast.js
 *
 * Safety net for the Agent Hub daily broadcast.
 *
 * When update-note-body.js PUTs the note with notify_enabled:true, the Supabase
 * `send-notification` edge function is supposed to email the ~105-agent BCC list
 * AND send a confirmation back to HarvRealtor@outlook.com. On 2026-06-03 the note
 * updated fine but the backend never sent — and nothing noticed, so agents
 * silently got no email. This script closes that gap: it polls HarvRealtor's
 * mailbox for the confirmation email and loudly reports CONFIRMED or FAILED.
 *
 * The success signal (verified against live 06/01 + 06/02 confirmations):
 *   From:    fremontrealtyexperts@gmail.com   (display "RE Agent-Hub")
 *   To:      HarvRealtor@outlook.com
 *   Subject: [Agent Hub] Confirmation: "At a Glance" Local Housing STATS and News MM/DD/YY
 * Absence of that email within the timeout = the broadcast did NOT complete.
 *
 * Usage:
 *   node verify-broadcast.js                       # date from daily-market-template.json
 *   node verify-broadcast.js --date 06/03/26
 *   node verify-broadcast.js --timeout 300 --poll 20 --since 2026-06-03T16:38:00Z
 *
 * Exit codes: 0 = confirmed, 2 = NOT confirmed (timed out), 1 = error.
 */

const fs = require('fs');
const path = require('path');
const { graphGet } = require('./lib/ms365');

const CONFIRMATION_SENDER = 'fremontrealtyexperts@gmail.com';
const SUBJECT_MARKER = '[Agent Hub] Confirmation';
const DEFAULT_TIMEOUT_MS = 5 * 60 * 1000; // 5 min — confirmation usually lands <1 min
const DEFAULT_POLL_MS = 20 * 1000;

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/** Does a Graph message look like today's broadcast confirmation? */
function isConfirmation(msg, date, sinceIso) {
  const subject = msg.subject || '';
  const lower = subject.trim().toLowerCase();
  if (lower.startsWith('re:') || lower.startsWith('fw:') || lower.startsWith('fwd:')) return false;
  if (!subject.includes(SUBJECT_MARKER)) return false;
  if (!subject.includes(date)) return false;
  const from = ((msg.from || {}).emailAddress || {}).address || '';
  if (from.toLowerCase() !== CONFIRMATION_SENDER) return false;
  if (sinceIso && (msg.receivedDateTime || '') < sinceIso) return false;
  return true;
}

/**
 * Poll HarvRealtor's mailbox for the confirmation email.
 * @param {object} opts
 * @param {string} opts.date     - MM/DD/YY string that appears in the subject
 * @param {string} [opts.sinceIso] - only accept confirmations received at/after this ISO time
 * @param {number} [opts.timeoutMs]
 * @param {number} [opts.pollMs]
 * @param {string} [opts.label]  - log prefix
 * @returns {Promise<{confirmed:boolean, message?:object, elapsedMs:number, polls:number}>}
 */
async function verifyBroadcast(opts = {}) {
  const {
    date,
    sinceIso = null,
    timeoutMs = DEFAULT_TIMEOUT_MS,
    pollMs = DEFAULT_POLL_MS,
    label = '',
  } = opts;
  if (!date) throw new Error('verifyBroadcast: opts.date (MM/DD/YY) is required');

  const pfx = label ? `${label} ` : '';
  const start = Date.now();
  // Newest-first; consumer Graph $filter is unreliable so we filter client-side.
  // We poll right after the broadcast fires, so the confirmation is among the
  // newest mail — $top=40 gives headroom for a busy mailbox during the window.
  const query = '/me/messages?$top=40'
    + '&$select=id,subject,from,toRecipients,receivedDateTime,bodyPreview'
    + '&$orderby=receivedDateTime%20desc';

  console.log(`${pfx}🔎 Verifying Agent Hub broadcast for ${date} (looking for the confirmation email)…`);
  if (sinceIso) console.log(`${pfx}   only counting confirmations at/after ${sinceIso}`);
  console.log(`${pfx}   sender=${CONFIRMATION_SENDER}  timeout=${Math.round(timeoutMs / 1000)}s  poll=${Math.round(pollMs / 1000)}s`);

  let polls = 0;
  let fetchedOk = false; // did we ever successfully read the mailbox?
  while (Date.now() - start < timeoutMs) {
    polls += 1;
    let data;
    try {
      data = await graphGet(query);
    } catch (err) {
      // Transient Graph/auth hiccup — keep trying until the timeout. If EVERY
      // poll errors, fetchedOk stays false → "couldn't verify" (not "failed").
      console.log(`${pfx}   ⚠️  poll ${polls} Graph error: ${err.message.split('\n')[0]}`);
      await sleep(pollMs);
      continue;
    }
    fetchedOk = true;
    const match = (data.value || []).find((m) => isConfirmation(m, date, sinceIso));
    if (match) {
      return { confirmed: true, fetchedOk, message: match, elapsedMs: Date.now() - start, polls };
    }
    const elapsed = Math.round((Date.now() - start) / 1000);
    console.log(`${pfx}   …not yet (poll ${polls}, ${elapsed}s elapsed)`);
    if (Date.now() - start + pollMs < timeoutMs) await sleep(pollMs);
    else break;
  }
  return { confirmed: false, fetchedOk, elapsedMs: Date.now() - start, polls };
}

/**
 * Print a loud, unmissable verdict banner.
 * @returns {0|2|3} exit code — 0 confirmed, 2 verified-absent (FAILED), 3 couldn't-verify.
 */
function printVerdict(result, date) {
  const line = '='.repeat(64);
  if (result.confirmed) {
    const m = result.message;
    console.log('\n' + line);
    console.log('  ✅ BROADCAST CONFIRMED — agents were notified');
    console.log(line);
    console.log(`  Confirmation email: "${m.subject}"`);
    console.log(`  Received:           ${m.receivedDateTime}`);
    console.log(`  After ${result.polls} poll(s), ${Math.round(result.elapsedMs / 1000)}s.\n`);
    return 0;
  }
  if (!result.fetchedOk) {
    // Never managed to read the mailbox — do NOT claim the broadcast failed.
    console.log('\n' + line);
    console.log('  ⚠️  COULD NOT VERIFY — mailbox was unreachable');
    console.log(line);
    console.log(`  Every poll to HarvRealtor@outlook.com errored over ${Math.round(result.elapsedMs / 1000)}s`);
    console.log('  (likely MS365 auth — refresh token dead, or Graph down).');
    console.log('  The broadcast may or may not have gone out — verify by hand:');
    console.log('   • Refresh auth per CLAUDE.md "MS365 / Outlook authentication", then');
    console.log(`     node verify-broadcast.js --date ${date}`);
    console.log('   • Or check HarvRealtor@outlook.com for the "[Agent Hub] Confirmation" email.');
    console.log(line + '\n');
    return 3;
  }
  console.log('\n' + line);
  console.log('  ❌❌❌  BROADCAST FAILED — agents did NOT get it  ❌❌❌');
  console.log(line);
  console.log(`  No "[Agent Hub] Confirmation … ${date}" email arrived at`);
  console.log(`  HarvRealtor@outlook.com within ${Math.round(result.elapsedMs / 1000)}s (${result.polls} polls).`);
  console.log('');
  console.log('  The note may have updated, but the Supabase send-notification');
  console.log('  backend did not deliver the broadcast (this is exactly the');
  console.log('  silent failure seen on 06/03 — likely Gmail quota/auth).');
  console.log('');
  console.log('  WHAT TO DO:');
  console.log('   1. Check the agent-hub edge logs:');
  console.log('        supabase functions logs send-notification   (project hbsodfrxadlfladdgvgy)');
  console.log('   2. Once the backend is healthy, re-trigger the broadcast:');
  console.log('        node update-note-body.js          (re-PUTs with notify_enabled:true)');
  console.log('      or re-run with auto-retry:');
  console.log('        node update-note-body.js --retry');
  console.log(line + '\n');
  return 2;
}

function parseArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--date') out.date = argv[++i];
    else if (a === '--since') out.sinceIso = argv[++i];
    else if (a === '--timeout') out.timeoutMs = parseInt(argv[++i], 10) * 1000;
    else if (a === '--poll') out.pollMs = parseInt(argv[++i], 10) * 1000;
  }
  return out;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  let date = args.date;
  if (!date) {
    const tmpl = path.join(__dirname, 'daily-market-template.json');
    if (!fs.existsSync(tmpl)) {
      console.error('❌ No --date given and daily-market-template.json not found.');
      process.exit(1);
    }
    date = JSON.parse(fs.readFileSync(tmpl, 'utf8')).date;
  }

  const result = await verifyBroadcast({
    date,
    sinceIso: args.sinceIso,
    timeoutMs: args.timeoutMs,
    pollMs: args.pollMs,
  });
  process.exit(printVerdict(result, date));
}

if (require.main === module) {
  main().catch((err) => {
    console.error('\nFatal error:', err.message);
    process.exit(1);
  });
}

module.exports = { verifyBroadcast, isConfirmation, printVerdict };
