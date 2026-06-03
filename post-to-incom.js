#!/usr/bin/env node
/**
 * post-to-incom.js  [--date MM/DD/YY] [--html FILE] [--meta FILE]
 *                   [--dry-run] [--blog-only|--landing-only]
 *
 * Publishes the daily CMS page to InCom (harvrealtor.com / Drupal):
 *   1. BLOG    — creates a NEW dated blog entry  (node/add/blog)
 *   2. LANDING — EDITS the fixed "Alameda County Real Estate Interactive Inventory"
 *                node (1319025), swapping only the body, preserving everything else.
 *
 * --dry-run logs in, scrapes the forms, and writes the full intended POST field
 * set to /tmp for review — but submits NOTHING. Always dry-run before the first
 * live publish.
 *
 * Credentials come from .env (INCOM_LOGIN_URL / INCOM_USER / INCOM_PASS).
 */

const fs = require('fs');
const path = require('path');
const { IncomClient, readIncomCreds, extractFormFields } = require('./lib/incom-client');
const { ENV_PATH, TEMPLATE_PATH } = require('./lib/config');

const BLOG_URL = 'https://www.harvrealtor.com/node/add/blog';
const LANDING_URL = 'https://www.harvrealtor.com/node/1319025/edit';
const BODY_FORMAT = '3'; // Drupal input format that allows <script> + inline CSS

function parseMetaTxt(txt) {
  const grab = (label) => {
    const re = new RegExp(label.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '[^\\n]*\\n+([^\\n]+)');
    const m = txt.match(re);
    return m ? m[1].trim() : '';
  };
  return {
    title: grab('TITLE:'),
    copyright: grab('META COPYRIGHT'),
    description: grab('META DESCRIPTION'),
    keywords: grab('META KEYWORDS'),
    robots: grab('ROBOTS META TAG'),
  };
}

function summarize(label, url, fields, bodyHtml) {
  const keys = Object.keys(fields).sort();
  const dump = path.join(require('os').tmpdir(), `incom-plan-${label.toLowerCase()}.json`);
  fs.writeFileSync(dump, JSON.stringify({ url, fields: { ...fields, 'edit[body]': `[${bodyHtml.length} bytes, sent separately]` } }, null, 2));
  console.log(`\n  ── ${label} → ${url}`);
  console.log(`     fields (${keys.length}): full set written to ${dump}`);
  for (const k of ['edit[title]', 'edit[path]', 'edit[format]', 'edit[form_id]', 'edit[form_token]', 'edit[changed]', 'edit[nodewords][description]', 'op']) {
    if (k in fields) {
      const v = String(fields[k]);
      console.log(`       ${k} = ${v.length > 70 ? v.slice(0, 67) + '…' : v}`);
    }
  }
  console.log(`       edit[body] = [${bodyHtml.length} bytes of CMS HTML]`);
  // sanity flags
  const warn = [];
  if (!fields['edit[form_token]']) warn.push('missing form_token');
  if (fields['edit[format]'] !== BODY_FORMAT) warn.push(`format is ${fields['edit[format]']}, expected ${BODY_FORMAT}`);
  if (bodyHtml.length < 5000 || !/plotly/i.test(bodyHtml)) warn.push('body looks too small / no Plotly');
  if (warn.length) console.log('       ⚠️  ' + warn.join('; '));
}

async function main() {
  const argv = process.argv.slice(2);
  const opt = (n) => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : undefined; };
  const dryRun = argv.includes('--dry-run');
  const blogOnly = argv.includes('--blog-only');
  const landingOnly = argv.includes('--landing-only');

  let date = opt('--date');
  if (!date) { try { date = JSON.parse(fs.readFileSync(TEMPLATE_PATH, 'utf8')).date; } catch (_) { /* none */ } }
  if (!date) { console.error('No date — pass --date MM/DD/YY or ensure daily-market-template.json exists.'); process.exit(1); }
  const short = date.replace(/\//g, '');

  const htmlPath = opt('--html') || path.join(__dirname, `alameda-interactive-${short}.html`);
  const metaPath = opt('--meta') || path.join(__dirname, `cms-meta-${short}.txt`);
  if (!fs.existsSync(htmlPath)) { console.error(`CMS HTML not found: ${htmlPath} (run generate-cms-page.js first)`); process.exit(1); }
  if (!fs.existsSync(metaPath)) { console.error(`CMS meta not found: ${metaPath}`); process.exit(1); }
  const bodyHtml = fs.readFileSync(htmlPath, 'utf8');
  const meta = parseMetaTxt(fs.readFileSync(metaPath, 'utf8'));

  console.log('='.repeat(60));
  console.log(`  InCom publish — ${date}  ${dryRun ? '(DRY RUN — nothing will be submitted)' : '(LIVE)'}`);
  console.log('='.repeat(60));
  console.log(`  CMS HTML: ${path.basename(htmlPath)} (${bodyHtml.length} bytes)`);
  console.log(`  Title:    ${meta.title}`);

  const { url, user, pass } = readIncomCreds(ENV_PATH);
  const c = new IncomClient();
  let failures = 0;
  try {
    c.login(url, user, pass);
    console.log('  ✅ logged in');

    // ---- BLOG: new dated entry ----
    if (!landingOnly) {
      const bf = c.getForm(BLOG_URL);
      const fields = extractFormFields(bf.html);
      delete fields['edit[body]'];
      Object.assign(fields, {
        'edit[title]': meta.title || `"At a Glance" Local Housing STATS and News ${date}`,
        'edit[path]': `HarvRealtor-daily-market-glance-${short}`,
        'edit[format]': BODY_FORMAT,
        'edit[nodewords][copyright]': meta.copyright,
        'edit[nodewords][description]': meta.description,
        'edit[nodewords][keywords]': meta.keywords,
        'edit[form_token]': bf.formToken,
        'edit[form_id]': bf.formId || 'blog_node_form',
        op: 'Submit',
      });
      if (dryRun) {
        summarize('BLOG', BLOG_URL, fields, bodyHtml);
      } else {
        const r = c.postNode(BLOG_URL, fields, bodyHtml);
        if (r.ok) {
          console.log(`\n  BLOG → HTTP ${r.status} ✅ created → ${r.finalUrl}`);
        } else if (/path is already in use/i.test(r.body)) {
          // idempotent: a blog entry already exists at this dated path (already posted today)
          console.log(`\n  BLOG → ⏭️  already posted for ${date} (path "HarvRealtor-daily-market-glance-${short}" in use) — skipped.`);
        } else {
          failures++;
          fs.writeFileSync('/tmp/incom-blog-response.html', r.body);
          console.log(`\n  BLOG → HTTP ${r.status} ❌ FAILED → response saved to /tmp/incom-blog-response.html`);
        }
      }
    }

    // ---- LANDING: edit fixed node, swap body only ----
    if (!blogOnly) {
      const lf = c.getForm(LANDING_URL);
      const fields = extractFormFields(lf.html);
      delete fields['edit[body]'];
      fields['edit[format]'] = BODY_FORMAT;       // ensure script-allowing (already 3)
      fields['op'] = 'Submit';                    // title / path / nodewords preserved as-scraped
      if (!fields['edit[form_token]'] && lf.formToken) fields['edit[form_token]'] = lf.formToken;
      if (dryRun) {
        summarize('LANDING', LANDING_URL, fields, bodyHtml);
      } else {
        const r = c.postNode(LANDING_URL, fields, bodyHtml);
        console.log(`\n  LANDING → HTTP ${r.status} ${r.ok ? '✅ updated' : '❌ FAILED'} → ${r.finalUrl}`);
        if (!r.ok) { failures++; fs.writeFileSync('/tmp/incom-landing-response.html', r.body); console.log('     response saved to /tmp/incom-landing-response.html'); }
      }
    }
  } catch (err) {
    console.error('\n  ❌ Error:', err.message);
    failures++;
  } finally {
    c.cleanup();
  }

  console.log('\n' + '='.repeat(60));
  if (dryRun) console.log('  DRY RUN complete — review the plan above, nothing was submitted.');
  else if (failures) { console.log(`  ⚠️  Completed with ${failures} failure(s).`); process.exitCode = 1; }
  else console.log('  ✅ Published to InCom.');
}

if (require.main === module) {
  main().catch(err => { console.error('Fatal:', err.message); process.exit(1); });
}

module.exports = { main, parseMetaTxt };
