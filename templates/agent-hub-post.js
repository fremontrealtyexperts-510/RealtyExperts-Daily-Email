const { GITHUB_RAW_BASE, GITHUB_PAGES_BASE } = require('../lib/config');

/**
 * Meridian placeholder body for the INITIAL note create.
 *
 * ⚠️ Deliberately tiny — do NOT post the full report body at create time.
 * The Supabase notes-api PUT handler only fires the team broadcast on a
 * "major edit" (title changed OR body length +/-20% — notes-api/index.ts
 * isMajorEdit). If the note is created with the same full body that
 * update-note-body.js later PUTs, that broadcast PUT is a minor edit and the
 * notification silently never fires (bit us on 2026-07-16, the first
 * Meridian v2 run). A ~600-char stub guarantees the broadcast PUT is always
 * a major edit, and anyone opening the share link in the minutes before the
 * broadcast sees a clean "being finalized" card instead of a half-built post.
 */
function stubBody(data) {
  return `<div style="max-width:680px;margin:0 auto;background:#FAF7F0;border:1px solid #E8E4DA;border-radius:16px;padding:36px 20px;text-align:center;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
  <div style="font-size:10px;text-transform:uppercase;letter-spacing:.22em;color:#B08C1E;font-weight:700;">REALTY EXPERTS®</div>
  <div style="font-family:Georgia,'Times New Roman',serif;font-size:24px;font-weight:600;color:#2E2E2E;margin:8px 0 6px;">Daily Market Glance</div>
  <div style="font-size:13px;color:#4A4640;">The ${data.date} report is being finalized. Check back in a few minutes.</div>
</div>`;
}

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

  // Straight ASCII quotes only. Smart quotes (“ ”) trip an RFC 2047
  // encoding bug in the Supabase notes-api notification function and produce
  // a malformed Subject header that some Outlook clients render as raw MIME.
  const title = `"At a Glance" Local Housing STATS and News ${data.date}`;
  // Tiny Meridian stub at create time; update-note-body.js PUTs the full
  // buildResponsiveBody() later, which then always registers as a major edit
  // and fires the broadcast. See stubBody() docblock before changing this.
  const body = stubBody(data);

  return { title, body, emailUrl, img1Url, img2Url };
}

module.exports = { buildPost, stubBody };
