#!/usr/bin/env node
/**
 * post-to-incom.js  [--date MM/DD/YY] [--html FILE] [--meta FILE]
 *                   [--dry-run] [--blog-only|--landing-only]
 *
 * Publishes the daily CMS page to InCom (harvrealtor.com / Drupal):
 *   1. BLOG    — creates a NEW dated blog entry  (node/add/blog)
 *   1b. SHARE IMAGE — hosts the blog's first picture on harvrealtor.com as its Featured
 *                Image and points that first <img src> at it (lib/incom-share-image.js),
 *                because InCom builds og:image from the body's FIRST <img src> and the
 *                daily's first picture lives on dscloud or GitHub (10/26/26). Also runs
 *                when the blog is already posted, so a same-day re-run retries it.
 *   2. LANDING — EDITS the fixed "Alameda County Real Estate Interactive Inventory"
 *                node (1319025), swapping only the body, preserving everything else.
 *                Its first picture points at the blog's hosted copy when it is the
 *                same picture, so the landing's share image loads too.
 *
 * --dry-run logs in, scrapes the forms, and writes the full intended POST field
 * set to /tmp for review — but submits NOTHING (the share-image step only reads
 * and downloads). Always dry-run before the first live publish.
 *
 * Credentials come from .env (INCOM_LOGIN_URL / INCOM_USER / INCOM_PASS).
 */

const fs = require('fs');
const path = require('path');
const { execSync, execFileSync } = require('child_process');
const { IncomClient, readIncomCreds, extractFormFields } = require('./lib/incom-client');
const { ENV_PATH, TEMPLATE_PATH, GITHUB_PAGES_BASE, JSDELIVR_GH_BASE } = require('./lib/config');
const share = require('./lib/incom-share-image');

// Repoint the chart <script src> from the GitHub Pages URL (which can 404 for many
// minutes on publish day while Pages rebuilds) to a commit-pinned jsDelivr CDN URL,
// which serves the .js executably and immediately. The committed HTML keeps the
// canonical Pages URL; only the live Drupal body gets the pinned CDN URL. The SHA is
// HEAD, which always already contains the chart JS (committed before this step runs).
function pinChartToJsdelivr(html, short) {
  const pagesUrl = `${GITHUB_PAGES_BASE}/alameda-chart-${short}.js`;
  if (!html.includes(pagesUrl)) return html;
  let sha;
  // Prefer the REAL remote HEAD (ls-remote) so a frozen/stale local .git (the Mac
  // OneDrive/Drive copy) cannot pin to a commit that lacks today's chart JS. CHART_SHA
  // overrides; local rev-parse is the last resort.
  try {
    sha = process.env.CHART_SHA
      || execSync('git ls-remote https://github.com/fremontrealtyexperts-510/RealtyExperts-Daily-Email.git HEAD', { cwd: __dirname }).toString().split(/\s+/)[0].trim()
      || execSync('git rev-parse HEAD', { cwd: __dirname }).toString().trim();
  }
  catch (_) { console.log('   ⚠️  could not resolve HEAD SHA — leaving Pages chart URL as-is'); return html; }
  const cdnUrl = `${JSDELIVR_GH_BASE}@${sha}/alameda-chart-${short}.js`;
  // jsDelivr refuses GitHub packages over 50 MB, and this repo passed that on
  // 10/25/26 (56.4 MB): the first fetch of a new commit came back 403 "Package size
  // exceeded the configured limit" and only served about 3 minutes later. A pinned
  // URL that does not answer leaves the live chart blank, so pin only when the CDN
  // serves the file right now; otherwise keep the canonical Pages URL, which the
  // Stage 5 runbook confirms is serving before this step runs.
  if (!urlServes(cdnUrl)) {
    console.log(`   ⚠️  jsDelivr @${sha.slice(0, 8)} does not serve the chart yet — keeping the Pages URL`);
    if (!urlServes(pagesUrl)) console.log('   ⚠️  the Pages chart URL does not serve yet either — the live chart stays blank until Pages finishes building');
    return html;
  }
  console.log(`   chart src pinned to jsDelivr @${sha.slice(0, 8)}`);
  return html.split(pagesUrl).join(cdnUrl);
}

// True when the URL answers 200 right now (one GET through curl, 20 s cap).
function urlServes(url) {
  try {
    return execFileSync('curl', ['-s', '-o', '/dev/null', '-w', '%{http_code}', '--max-time', '20', url], { encoding: 'utf8' }).trim() === '200';
  } catch (_) { return false; }
}

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

// Step 1b: give the dated blog a share image that loads. Never undoes the publish: on
// an error it prints how to retry and returns { result: 'FAILED' } for the caller to count.
function shareImageStep(c, node, alias, date, live) {
  try {
    const nid = node || share.nodeIdForAlias(c, alias);
    if (!nid) {
      if (!live) { console.log('\n  SHARE IMAGE → (dry run) the blog is not posted yet: right after it is created, its first picture is hosted on harvrealtor.com and the src repointed'); return null; }
      throw new Error(`could not find the node id behind ${alias}`);
    }
    const s = share.fixShareImage(c, { node: nid, alias, live });
    s.node = nid;
    console.log(`\n  SHARE IMAGE → node ${nid}: ${share.describe(s)}`);
    return s;
  } catch (e) {
    console.log(`\n  SHARE IMAGE → ❌ ${e.message}`);
    if (live) {
      console.log('     The blog IS posted. Retry today: node post-to-incom.js (the blog is skipped, the share image retried, the landing re-saved).');
      console.log(`     Any day, the blog only: node edit-incom-node.js --share-image-only --date ${date}`);
    }
    return { result: 'FAILED', error: e.message };
  }
}

// The landing carries the same body as the blog, so its first picture is the blog's first
// picture: point it at the blog's hosted copy when the two <img> tags match apart from src.
function landingWithHostedPicture(c, bodyHtml, pic, alias, dryRun) {
  const mine = share.firstImg(bodyHtml);
  if (!mine || share.isHosted(mine.src)) return bodyHtml;
  if (!pic || !pic.hosted) {
    try {
      const nid = (pic && pic.node) || share.nodeIdForAlias(c, alias);
      pic = nid ? share.readFirstPicture(c, nid, alias) : null;
    } catch (e) { console.log(`\n  ⚠️  could not read today's blog first picture: ${e.message}`); pic = null; }
  }
  if (pic && pic.hosted && share.sameTagApartFromSrc(pic.tag, mine.tag)) {
    console.log(`\n  LANDING first picture → ${pic.hosted} (the blog's hosted copy, so the landing's share image loads)`);
    return share.repointFirstImg(bodyHtml, pic.hosted);
  }
  console.log(dryRun
    ? '\n  LANDING first picture → (dry run) follows the blog\'s hosted copy once the live blog step has run'
    : '\n  ⚠️  LANDING first picture stays off-site (today\'s blog has no hosted copy of the same picture): the landing\'s share image will not load');
  return bodyHtml;
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
  // 2026-07-19: chart is self-rendering (no Plotly) — sanity-check the external
  // chart <script src> instead of the old Plotly CDN tag.
  if (bodyHtml.length < 5000 || !/alameda-chart-\d+\.js/.test(bodyHtml)) warn.push('body looks too small / no chart script src');
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
  const bodyHtml = pinChartToJsdelivr(fs.readFileSync(htmlPath, 'utf8'), short);
  const meta = parseMetaTxt(fs.readFileSync(metaPath, 'utf8'));

  console.log('='.repeat(60));
  console.log(`  InCom publish — ${date}  ${dryRun ? '(DRY RUN — nothing will be submitted)' : '(LIVE)'}`);
  console.log('='.repeat(60));
  console.log(`  CMS HTML: ${path.basename(htmlPath)} (${bodyHtml.length} bytes)`);
  console.log(`  Title:    ${meta.title}`);

  const { url, user, pass } = readIncomCreds(ENV_PATH);
  const c = new IncomClient();
  const alias = `HarvRealtor-daily-market-glance-${short}`;
  let failures = 0;
  let pic = null;   // the blog's share-image result; the landing reuses its hosted picture
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
        'edit[path]': alias,
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
        pic = shareImageStep(c, '', alias, date, false);
      } else {
        const r = c.postNode(BLOG_URL, fields, bodyHtml);
        let posted = true, node = '';
        if (r.ok) {
          console.log(`\n  BLOG → HTTP ${r.status} ✅ created → ${r.finalUrl}`);
          node = (r.finalUrl.match(/\/node\/(\d+)(?:[/?#]|$)/) || [])[1] || '';
        } else if (/path is already in use/i.test(r.body)) {
          // idempotent: a blog entry already exists at this dated path (already posted today)
          console.log(`\n  BLOG → ⏭️  already posted for ${date} (path "${alias}" in use) — skipped.`);
        } else {
          posted = false;
          failures++;
          fs.writeFileSync('/tmp/incom-blog-response.html', r.body);
          console.log(`\n  BLOG → HTTP ${r.status} ❌ FAILED → response saved to /tmp/incom-blog-response.html`);
        }
        if (posted) {
          pic = shareImageStep(c, node, alias, date, true);
          if (pic && pic.result === 'FAILED') failures++;
        }
      }
    }

    // ---- LANDING: edit fixed node, swap body only ----
    if (!blogOnly) {
      const landingBody = landingWithHostedPicture(c, bodyHtml, pic, alias, dryRun);
      const lf = c.getForm(LANDING_URL);
      const fields = extractFormFields(lf.html);
      delete fields['edit[body]'];
      fields['edit[format]'] = BODY_FORMAT;       // ensure script-allowing (already 3)
      fields['op'] = 'Submit';                    // title / path / nodewords preserved as-scraped
      if (!fields['edit[form_token]'] && lf.formToken) fields['edit[form_token]'] = lf.formToken;
      if (dryRun) {
        summarize('LANDING', LANDING_URL, fields, landingBody);
      } else {
        const r = c.postNode(LANDING_URL, fields, landingBody);
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
