#!/usr/bin/env node
/**
 * get-brent.js — THE single locked-in Brent source for the daily report.
 *
 * WHY THIS EXISTS (2026-08-05): Brent came back four materially different ways
 * in one morning (Market Briefs $79.62, a search result $81.77, Fortune $89.81,
 * FRED $88.90), none reconciled, and the Economy section shipped without an oil
 * card. The disagreement was not four sources being wrong, it was TWO DIFFERENT
 * INSTRUMENTS being quoted as "Brent":
 *
 *   ICE Brent front-month FUTURES  (Yahoo BZ=F)      08/03 83.77  08/04 79.36
 *   Brent Europe physical SPOT     (FRED DCOILBRENTEU) 08/03 88.90  (2-day lag)
 *
 * Spot runs roughly $7 to $9 above front-month futures and lags two business
 * days. Our own published history is the FUTURES series (we printed $83.73 for
 * 08/03 and $78.94 for 08/04), and futures are what the financial press and
 * Market Briefs quote. So futures it is, permanently.
 *
 * CONVENTION: report the LATEST COMPLETED SESSION CLOSE and its change versus
 * the session before it, both taken from this one series. That matches how we
 * already quote stocks and the 10-Year ("as of the August 4 close"), it is
 * exactly reproducible from a dated series, and it never mixes an intraday
 * quote from one source with a close from another. Do NOT reconcile this
 * against yesterday's published level from a different vendor; reconcile it
 * against the prior close this script prints.
 *
 * Keyless, no dependencies (https only), so it cannot hang on Drive
 * node_modules the way require('qrcode') does.
 *
 * IN-PROGRESS SESSIONS: Yahoo's daily bar for the CURRENT trading day is a live
 * tick, not a settlement, so on a morning run the newest row is unsettled. By
 * default this script drops any bar dated today (New York time) and reports the
 * last SETTLED session, which is what "as of the August 4 close" means in our
 * copy. Pass --include-today to quote the live in-progress bar instead.
 *
 * Usage:
 *   node get-brent.js                  # last settled session (USE THIS)
 *   node get-brent.js --json           # machine readable
 *   node get-brent.js --include-today  # include today's unsettled bar
 */
const https = require('https');

const URL =
  'https://query1.finance.yahoo.com/v8/finance/chart/BZ=F?range=1mo&interval=1d';

function fetchJSON(url) {
  return new Promise((resolve, reject) => {
    https
      .get(url, { headers: { 'User-Agent': 'Mozilla/5.0' } }, (res) => {
        if (res.statusCode !== 200) {
          res.resume();
          return reject(new Error(`HTTP ${res.statusCode} from Yahoo`));
        }
        let body = '';
        res.setEncoding('utf8');
        res.on('data', (c) => (body += c));
        res.on('end', () => {
          try {
            resolve(JSON.parse(body));
          } catch (e) {
            reject(new Error('unparseable JSON from Yahoo'));
          }
        });
      })
      .on('error', reject);
  });
}

const ymd = (sec) => new Date(sec * 1000).toISOString().slice(0, 10);

(async () => {
  const wantJson = process.argv.includes('--json');
  const d = await fetchJSON(URL);
  const r = d && d.chart && d.chart.result && d.chart.result[0];
  if (!r) throw new Error('no chart result for BZ=F');

  const ts = r.timestamp || [];
  const closes = (r.indicators.quote[0] || {}).close || [];

  let rows = ts
    .map((t, i) => ({ date: ymd(t), close: closes[i] }))
    .filter((x) => typeof x.close === 'number' && isFinite(x.close));

  // Today's bar is a live tick, not a settlement. Drop it unless asked.
  const todayNY = new Date()
    .toLocaleDateString('en-CA', { timeZone: 'America/New_York' });
  let droppedLive = null;
  if (!process.argv.includes('--include-today')) {
    const lastRow = rows[rows.length - 1];
    if (lastRow && lastRow.date === todayNY) {
      droppedLive = lastRow;
      rows = rows.slice(0, -1);
    }
  }

  if (rows.length < 2) throw new Error('need at least 2 settled sessions');

  const last = rows[rows.length - 1];
  const prev = rows[rows.length - 2];
  const chg = last.close - prev.close;
  const pct = (chg / prev.close) * 100;

  const out = {
    symbol: 'BZ=F',
    instrument: 'ICE Brent Crude front-month futures',
    date: last.date,
    close: Number(last.close.toFixed(2)),
    prior_date: prev.date,
    prior_close: Number(prev.close.toFixed(2)),
    change: Number(chg.toFixed(2)),
    change_pct: Number(pct.toFixed(2)),
    settled: droppedLive ? true : last.date !== todayNY,
    live_bar_excluded: droppedLive
      ? { date: droppedLive.date, price: Number(droppedLive.close.toFixed(2)) }
      : null,
    // ready to paste into daily-market-template.json economy.wti
    template_value: `$${last.close.toFixed(2)} (${pct >= 0 ? '+' : ''}${pct.toFixed(2)}%)`,
    source_url: 'https://finance.yahoo.com/quote/BZ%3DF/',
  };

  if (wantJson) {
    console.log(JSON.stringify(out, null, 2));
    return;
  }

  console.log('Brent (ICE front-month futures, BZ=F)');
  if (droppedLive) {
    console.log(
      `  [excluded ${droppedLive.date} live tick $${droppedLive.close.toFixed(2)}, ` +
        'session not settled]'
    );
  }
  console.log(`  ${out.date} close : $${out.close.toFixed(2)}   <- report this`);
  console.log(`  ${out.prior_date} close : $${out.prior_close.toFixed(2)}`);
  console.log(
    `  change        : ${out.change >= 0 ? '+' : ''}${out.change.toFixed(2)} ` +
      `(${out.change_pct >= 0 ? '+' : ''}${out.change_pct.toFixed(2)}%)`
  );
  console.log();
  console.log(`  economy.wti   -> "${out.template_value}"`);
  console.log(`  oil_label     -> "Brent Crude"`);
  console.log(`  note          -> Brent is the ${out.date} settlement.`);
})().catch((e) => {
  console.error('❌ get-brent.js failed:', e.message);
  console.error(
    '   Fallback: FRED DCOILBRENTEU is a DIFFERENT instrument (spot, ~$7-9 higher,\n' +
      '   2-day lag). Do not substitute it. Omit the oil card instead.'
  );
  process.exit(1);
});
