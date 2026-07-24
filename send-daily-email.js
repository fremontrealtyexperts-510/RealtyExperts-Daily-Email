#!/usr/bin/env node
/**
 * send-daily-email.js
 * Sends the daily "At a Glance" email from HarvRealtor@outlook.com via Graph.
 * Recipients (standing rule): harvrealtor@outlook.com AND chuck@realtyexperts.com,
 * BOTH as TO, no CC. See memory reference_outlook_draft_recipients.
 *
 * Body = the same Meridian responsive body used for the Agent Hub broadcast,
 * so the email and the post stay identical.
 *
 * Usage: node send-daily-email.js [--dry-run]
 */
const fs = require('fs');
const https = require('https');
const { TEMPLATE_PATH, GITHUB_RAW_BASE, GITHUB_PAGES_BASE } = require('./lib/config');
const { buildResponsiveBody } = require('./lib/html-builders');
const { getValidAccessToken } = require('./lib/ms365');

const TO = ['harvrealtor@outlook.com', 'chuck@realtyexperts.com'];
const DRY = process.argv.includes('--dry-run');

function post(url, token, payload) {
  return new Promise((resolve, reject) => {
    const body = Buffer.from(JSON.stringify(payload));
    const req = https.request(url, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Content-Length': body.length,
      },
    }, res => {
      let raw = '';
      res.on('data', c => raw += c);
      res.on('end', () => resolve({ status: res.statusCode, body: raw }));
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

(async () => {
  const data = JSON.parse(fs.readFileSync(TEMPLATE_PATH, 'utf8'));
  const dateForFile = data.date.replace(/\//g, '');
  const emailUrl = `${GITHUB_PAGES_BASE}/daily-market-glance-${dateForFile}.html`;
  const img1Url = `${GITHUB_RAW_BASE}/RE-Daily-1-${dateForFile}.png`;
  const img2Url = `${GITHUB_RAW_BASE}/RE-Daily-2-${dateForFile}.png`;

  const subject = `"At a Glance" Local Housing STATS and News ${data.date}`;
  const html = buildResponsiveBody(data, emailUrl, img1Url, img2Url);

  console.log(`Subject: ${subject}`);
  console.log(`TO: ${TO.join(', ')}`);
  console.log(`HTML size: ${html.length} chars`);
  if (DRY) { console.log('\n--dry-run: not sending.'); return; }

  const token = await getValidAccessToken();
  const res = await post('https://graph.microsoft.com/v1.0/me/sendMail', token, {
    message: {
      subject,
      body: { contentType: 'HTML', content: html },
      toRecipients: TO.map(a => ({ emailAddress: { address: a } })),
    },
    saveToSentItems: true,
  });

  if (res.status === 202) {
    console.log('\n✅ Email sent (HTTP 202).');
  } else {
    console.error(`\n❌ Send failed: HTTP ${res.status}`);
    console.error(res.body.slice(0, 500));
    process.exit(1);
  }
})().catch(e => { console.error('Error:', e.message); process.exit(1); });
