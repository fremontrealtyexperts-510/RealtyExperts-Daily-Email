#!/usr/bin/env node
/**
 * edit-incom-node.js  --node NNNN  [--date MM/DD/YY] [--html FILE] [--dry-run]
 *
 * EDITS an existing InCom (Drupal) node, swapping ONLY the body for the
 * generated CMS HTML of the given date — the same proven mechanic as
 * post-to-incom.js's LANDING path, generalized to any node id.
 *
 * Why this exists: post-to-incom.js's BLOG path is create-only (it skips when
 * the dated path already exists), so a same-day RE-publish of a dated blog
 * node had no tool. Rule: same-day re-publish = edit the node by id, never
 * re-create (Drupal would refuse the alias anyway). Find the node id in the
 * live page source (`node/NNNN`).
 *
 * All non-body fields are re-POSTed exactly as scraped — Drupal blanks any
 * omitted field on edit. Remember: failed saves can return HTTP 200; always
 * verify the live DOM afterwards (verify-cms-publish.js).
 */

const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');
const { IncomClient, readIncomCreds, extractFormFields } = require('./lib/incom-client');
const { ENV_PATH, TEMPLATE_PATH, GITHUB_PAGES_BASE, JSDELIVR_GH_BASE } = require('./lib/config');

const BODY_FORMAT = '3'; // Drupal input format that allows <script src> + inline CSS

// Same pinning as post-to-incom.js: live bodies reference the chart JS via a
// commit-pinned jsDelivr URL (Pages can lag many minutes; @main caches ~12h).
function pinChartToJsdelivr(html, short) {
  const pagesUrl = `${GITHUB_PAGES_BASE}/alameda-chart-${short}.js`;
  if (!html.includes(pagesUrl)) return html;
  let sha;
  try {
    sha = process.env.CHART_SHA
      || execFileSync('git', ['ls-remote', 'https://github.com/fremontrealtyexperts-510/RealtyExperts-Daily-Email.git', 'HEAD'], { cwd: __dirname, encoding: 'utf8' }).split(/\s+/)[0].trim();
  } catch (_) { console.log('   ⚠️  could not resolve remote HEAD SHA — leaving Pages chart URL as-is'); return html; }
  const cdnUrl = `${JSDELIVR_GH_BASE}@${sha}/alameda-chart-${short}.js`;
  console.log(`   chart src pinned to jsDelivr @${sha.slice(0, 8)}`);
  return html.split(pagesUrl).join(cdnUrl);
}

async function main() {
  const argv = process.argv.slice(2);
  const opt = (n) => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : undefined; };
  const dryRun = argv.includes('--dry-run');
  const node = opt('--node');
  if (!node || !/^\d+$/.test(node)) { console.error('Pass --node NNNN (numeric Drupal node id)'); process.exit(1); }

  let date = opt('--date');
  if (!date) { try { date = JSON.parse(fs.readFileSync(TEMPLATE_PATH, 'utf8')).date; } catch (_) { /* none */ } }
  if (!date) { console.error('No date — pass --date MM/DD/YY or ensure daily-market-template.json exists.'); process.exit(1); }
  const short = date.replace(/\//g, '');

  const htmlPath = opt('--html') || path.join(__dirname, `alameda-interactive-${short}.html`);
  if (!fs.existsSync(htmlPath)) { console.error(`CMS HTML not found: ${htmlPath} (run generate-cms-page.js first)`); process.exit(1); }
  const bodyHtml = pinChartToJsdelivr(fs.readFileSync(htmlPath, 'utf8'), short);

  const editUrl = `https://www.harvrealtor.com/node/${node}/edit`;
  console.log('='.repeat(60));
  console.log(`  InCom node EDIT — node ${node}, body from ${path.basename(htmlPath)}  ${dryRun ? '(DRY RUN)' : '(LIVE)'}`);
  console.log('='.repeat(60));

  const { url, user, pass } = readIncomCreds(ENV_PATH);
  const c = new IncomClient();
  try {
    c.login(url, user, pass);
    console.log('  ✅ logged in');

    const lf = c.getForm(editUrl);
    const fields = extractFormFields(lf.html);
    delete fields['edit[body]'];
    fields['edit[format]'] = BODY_FORMAT;
    fields['op'] = 'Submit'; // title / path / nodewords preserved as-scraped
    if (!fields['edit[form_token]'] && lf.formToken) fields['edit[form_token]'] = lf.formToken;
    console.log(`  scraped form: title="${(fields['edit[title]'] || '').slice(0, 60)}" path="${fields['edit[path]'] || ''}" fields=${Object.keys(fields).length}`);

    if (dryRun) {
      const dump = path.join(require('os').tmpdir(), `incom-plan-node${node}.json`);
      fs.writeFileSync(dump, JSON.stringify({ url: editUrl, fields: { ...fields, 'edit[body]': `[${bodyHtml.length} bytes, sent separately]` } }, null, 2));
      console.log(`  DRY RUN — full field set written to ${dump}; nothing submitted.`);
    } else {
      const r = c.postNode(editUrl, fields, bodyHtml);
      console.log(`  EDIT → HTTP ${r.status} ${r.ok ? '✅ updated' : '❌ FAILED'} → ${r.finalUrl}`);
      if (!r.ok) { fs.writeFileSync(`/tmp/incom-node${node}-response.html`, r.body); console.log(`     response saved to /tmp/incom-node${node}-response.html`); process.exitCode = 1; }
    }
  } catch (err) {
    console.error('  ❌ Error:', err.message);
    process.exitCode = 1;
  } finally {
    c.cleanup();
  }
}

if (require.main === module) {
  main().catch((err) => { console.error('Fatal:', err.message); process.exit(1); });
}
