/**
 * lib/mls-notice.js: the Bay East MLS Rule 12.9 notice (added 2026-09-28, Harv).
 *
 * Rule 12.9 allows statistics from the MLS compilation in any public
 * representation, but every such piece "must clearly demonstrate the period of
 * time over which such claims are based and must include the following, or
 * substantially similar, notice, in a manner readily visible to consumers but
 * not less than 7-pt type". The wording below is the rule's own, as quoted in
 * My Drive/Web/docs/2026-09-02-live-inventory-feed-vs-bay-east-mls-rules.md,
 * and it matches thebayarearealestate.com's mlsNotice().
 *
 * Every daily surface that prints MLS counts or medians carries it:
 *   - harvrealtor.com daily blog + landing node    generate-cms-page.js
 *   - the email body + the Agent Hub note          lib/html-builders.js buildResponsiveBody
 *   - the GitHub Pages web copy of the email       generate-daily-email.js
 *
 * Keep it at 11px or larger (7 pt is about 9.3px on screen), do not shorten it,
 * and never delete it when hand editing a page body. verify-cms-publish.js fails
 * a live page that is missing it, for every date from 09/28/26 on.
 *
 * Zero dependencies on purpose: generate-daily-email.js is otherwise fs + path only.
 */

const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'];

// The string verify-cms-publish.js looks for (it keeps its own copy on purpose).
const MLS_NOTICE_MARKER = 'Based on information from the Bay East Association of REALTORS';

/** "MM/DD/YY" -> "September 28, 2026". Anything else is taken as a finished label. */
function mlsAsOf(date) {
  const m = String(date || '').trim().match(/^(\d{1,2})\/(\d{1,2})\/(\d{2})$/);
  if (!m) {
    if (!date) throw new Error('mlsNotice needs the MLS data date');
    return String(date);
  }
  const mm = parseInt(m[1], 10), dd = parseInt(m[2], 10), yy = parseInt(m[3], 10);
  if (mm < 1 || mm > 12 || dd < 1 || dd > 31) throw new Error(`bad MLS date "${date}"`);
  return `${MONTHS[mm - 1]} ${dd}, ${2000 + yy}`;
}

/** The notice as plain text. `date` is the day the MLS export was taken. */
function mlsNotice(date) {
  return `${MLS_NOTICE_MARKER}® (Bay East MLS) as of ${mlsAsOf(date)}. `
    + 'All data, including all measurements and calculations of area, is obtained from various sources '
    + 'and has not been, and will not be, verified by broker or MLS. All information should be '
    + 'independently reviewed and verified for accuracy. Properties may or may not be listed by the '
    + 'office/agent presenting the information.';
}

/** The same notice for HTML bodies (registered mark as an entity). */
function mlsNoticeHtml(date) {
  return mlsNotice(date).replace(/®/g, '&reg;');
}

module.exports = { mlsNotice, mlsNoticeHtml, mlsAsOf, MLS_NOTICE_MARKER };
