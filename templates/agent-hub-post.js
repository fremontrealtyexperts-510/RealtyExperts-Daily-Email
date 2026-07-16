const { GITHUB_RAW_BASE, GITHUB_PAGES_BASE } = require('../lib/config');
const { buildResponsiveBody } = require('../lib/html-builders');

/**
 * Build Agent Hub post title and body from JSON template data.
 * @param {Object} data - Parsed daily-market-template.json
 * @returns {{ title: string, body: string, emailUrl: string, img1Url: string, img2Url: string }}
 */
function buildPost(data) {
  const dateShort = data.date.replace(/\//g, '');
  const emailUrl = `${GITHUB_PAGES_BASE}/daily-market-glance-${dateShort}.html`;
  const img1Url = `${GITHUB_RAW_BASE}/RE-Daily-1-${dateShort}.png`;
  const img2Url = `${GITHUB_RAW_BASE}/RE-Daily-2-${dateShort}.png`;

  // Straight ASCII quotes only. Smart quotes (\u201c \u201d) trip an RFC 2047
  // encoding bug in the Supabase notes-api notification function and produce
  // a malformed Subject header that some Outlook clients render as raw MIME.
  const title = `"At a Glance" Local Housing STATS and News ${data.date}`;
  // Meridian responsive body — same builder the broadcast uses, so the note
  // never shows the legacy card layout between creation and broadcast.
  const body = buildResponsiveBody(data, emailUrl, img1Url, img2Url);

  return { title, body, emailUrl, img1Url, img2Url };
}

module.exports = { buildPost };
