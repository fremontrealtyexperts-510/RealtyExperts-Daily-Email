#!/usr/bin/env node
/**
 * generate-cms-page.js  [--date MM/DD/YY] [--content cms-content.json]
 *                       [--out-html FILE] [--out-meta FILE]
 *
 * Builds the harvrealtor.com CMS artifacts that get posted to InCom:
 *   - alameda-interactive-MMDDYY.html  (standalone Plotly dashboard + newsletter)
 *   - cms-meta-MMDDYY.txt              (title / copyright / description / keywords / robots)
 *
 * The 12-city chart is read LIVE from the master sheet's "RE-v2" tab (reusing
 * lib/google-sa.js). The editorial newsletter body + meta description/keywords are
 * "composed each morning" and supplied via cms-content.json. Everything else
 * (date badge, default-city banner, title, copyright, robots) is derived.
 *
 * Replaces the throwaway /tmp/build-alameda.py.
 */

const fs = require('fs');
const path = require('path');
const { getAccessToken, getSheetValues, SCOPES } = require('./lib/google-sa');
const { TEMPLATE_PATH, GITHUB_PAGES_BASE } = require('./lib/config');

const SHEET_ID = '1YxbK29giJO6XDQAV3RHXml2vjMejmtBpZfD3ICW_gTw';
const REV2_RANGE = 'RE-v2!A1:Z40';
const DEFAULT_CONTENT = path.join(__dirname, 'cms-content.json');

// Chart category columns (display order) — derived from RE-v2's per-city columns.
const CATS = ['CO', 'DE', 'TH', 'Active All', 'New', 'CS', 'PEND'];

// The 12 chart cities, in display order (RE-v2 also has Oakland/Sunol/San Lorenzo
// which are intentionally excluded from this chart).
const CITY_ORDER = [
  'Fremont', 'Union City', 'Castro Valley', 'Danville', 'Hayward', 'Livermore',
  'Newark', 'Pleasanton', 'San Ramon', 'Dublin', 'San Leandro', 'Milpitas',
];
// Meridian-harmonized categorical palette: desaturated, earthy tones that sit
// inside the gold / ink / paper system while staying mutually distinguishable
// across 12 series. Fremont, the flagship, carries the brand gold.
const COLORS = {
  'Fremont': '#B08C1E', 'Union City': '#3E5C76', 'Castro Valley': '#6E7B5B',
  'Danville': '#9C6B4A', 'Hayward': '#7E5A73', 'Livermore': '#C9A227',
  'Newark': '#4E7C6E', 'Pleasanton': '#A65A44', 'San Ramon': '#5B7551',
  'Dublin': '#4A6E8A', 'San Leandro': '#8A6D3B', 'Milpitas': '#2E6E6A',
};
// Cities shown by default (also drives the info-banner text), in banner order.
const DEFAULT_VISIBLE = ['Fremont', 'Union City', 'Milpitas', 'Hayward', 'Newark'];

const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'];

/** "MM/DD/YY" -> { label:"June 2, 2026", short:"060226", year:2026 } */
function parseDate(mmddyy) {
  const [mm, dd, yy] = String(mmddyy).split('/').map(s => parseInt(s, 10));
  if (!mm || !dd || isNaN(yy)) throw new Error(`bad date "${mmddyy}" (want MM/DD/YY)`);
  const year = 2000 + yy;
  return { label: `${MONTHS[mm - 1]} ${dd}, ${year}`, short: String(mmddyy).replace(/\//g, ''), year };
}

/**
 * Parse RE-v2 rows into the chart cities. RE-v2 columns:
 * [City, TH-Active, TH-Pend, CO-Active, CO-Pend, DU/DE/PH-Active, DU/DE/PH-Pend, Total, All CS, All New]
 * Chart cats map: CO=CO-Active, DE=DU/DE/PH-Active, TH=TH-Active,
 *   Active All = TH+CO+DE actives, New=All New, CS=All CS, PEND = sum of the three pendings.
 * Pure (no IO) so it is unit-testable. Returns [{city, values:[...CATS]}] in CITY_ORDER.
 */
function parseRev2(rows) {
  if (!rows || rows.length < 2) throw new Error('RE-v2 returned no data rows');
  const byCity = {};
  for (const row of rows.slice(1)) {
    const city = String(row[0] || '').trim();
    if (!city) continue;
    const n = i => parseInt(row[i], 10) || 0;
    const th = n(1), thp = n(2), co = n(3), cop = n(4), de = n(5), dep = n(6), cs = n(8), nw = n(9);
    byCity[city.toLowerCase()] = {
      CO: co, DE: de, TH: th, 'Active All': th + co + de, New: nw, CS: cs, PEND: thp + cop + dep,
    };
  }
  const missing = CITY_ORDER.filter(c => !byCity[c.toLowerCase()]);
  if (missing.length) throw new Error(`RE-v2 missing chart cities: ${missing.join(', ')}`);
  return CITY_ORDER.map(city => ({
    city,
    values: CATS.map(cat => byCity[city.toLowerCase()][cat]),
  }));
}

/** Fetch RE-v2 live and parse it. */
async function readRev2() {
  const token = await getAccessToken(SCOPES.SHEETS_RO);
  const rows = await getSheetValues(SHEET_ID, REV2_RANGE, token);
  return parseRev2(rows);
}

function chartInnerJs(inventory) {
  const traces = inventory.map(({ city, values }) => ({
    name: city, x: CATS, y: values, type: 'bar',
    visible: DEFAULT_VISIBLE.includes(city) ? true : 'legendonly',
    marker: { color: COLORS[city] || '#8A6D3B' },
    hovertemplate: `<b>${city}</b><br>%{x}: %{y}<extra></extra>`,
  }));
  const SERIF = "'Playfair Display', Georgia, 'Times New Roman', serif";
  const SANS = "'Inter', -apple-system, 'Segoe UI', Arial, sans-serif";
  const layout = {
    title: { text: 'Real Estate Inventory by City', font: { size: 21, color: '#2E2E2E', family: SERIF }, x: 0.5, xanchor: 'center', y: 0.97 },
    xaxis: { title: { text: 'Listing Category', font: { size: 13, color: '#4A4640', family: SANS } }, tickfont: { size: 12, color: '#4A4640', family: SANS }, showgrid: false, zeroline: false },
    yaxis: { title: { text: 'Count', font: { size: 13, color: '#4A4640', family: SANS } }, tickfont: { size: 12, color: '#4A4640', family: SANS }, gridcolor: 'rgba(46,46,46,0.07)', showgrid: true, zeroline: false },
    height: 640, plot_bgcolor: '#FFFFFF', paper_bgcolor: '#FFFFFF', hovermode: 'closest', showlegend: true,
    legend: { title: { text: 'Cities (tap to toggle)', font: { size: 12, color: '#4A4640', family: SANS } }, font: { size: 11, color: '#4A4640', family: SANS }, bgcolor: 'rgba(0,0,0,0)', borderwidth: 0, orientation: 'h', x: 0.5, y: -0.2, xanchor: 'center', yanchor: 'top' },
    barmode: 'group', bargap: 0.28, bargroupgap: 0.08, margin: { l: 54, r: 18, t: 54, b: 116 }, font: { family: SANS, color: '#4A4640' }, transition: { duration: 600, easing: 'cubic-in-out' },
  };
  const config = { displayModeBar: false, displaylogo: false, responsive: true, toImageButtonOptions: { format: 'png', filename: 'realty_experts_inventory', height: 800, width: 1400, scale: 2 } };
  // Emitted to an EXTERNAL .js file (alameda-chart-MMDDYY.js) and referenced via
  // <script src>. Drupal strips INLINE <script> from the node body but keeps
  // external src tags — so the chart only renders when its data lives in a
  // hosted file. No HTML-escaping needed here (the file is never HTML-filtered).
  // The chart is ALWAYS light (white paper): the report embeds in the light InCom
  // page, so a prefers-color-scheme dark chart reads as broken there (2026-07-06).
  // The click-to-enlarge lightbox also lives here for the same strip-inline reason.
  return `var data = ${JSON.stringify(traces)};
var baseLayout = ${JSON.stringify(layout)};
var config = ${JSON.stringify(config)};
function layoutFor(){var w=window.innerWidth,u=JSON.parse(JSON.stringify(baseLayout));u.autosize=true;if(w<600){u.height=560;u.margin={l:42,r:10,t:46,b:176};u.title.font.size=17;u.xaxis.tickfont.size=10;u.yaxis.tickfont.size=10;u.legend.font.size=9;u.legend.x=0;u.legend.xanchor='left';u.legend.title.text='';u.legend.y=-0.26;u.bargap=0.22;}else if(w<900){u.height=580;u.margin={l:48,r:14,t:50,b:134};u.title.font.size=19;u.legend.font.size=10;u.legend.x=0;u.legend.xanchor='left';u.legend.y=-0.24;}return u;}
function drawChart(){Plotly.newPlot('chart', data, layoutFor(), config);window.addEventListener('resize',function(){Plotly.relayout('chart', layoutFor());});}
if(window.Plotly){drawChart();}else{document.addEventListener('DOMContentLoaded',drawChart);}
(function(){
var open=null;
function close(){if(open){if(open.parentNode){open.parentNode.removeChild(open);}open=null;document.body.style.overflow='';}}
function show(src,alt){close();var o=document.createElement('div');o.className='re-lightbox';o.setAttribute('role','dialog');o.setAttribute('aria-modal','true');o.setAttribute('aria-label',alt||'Enlarged image');var im=document.createElement('img');im.src=src;im.alt=alt||'';var x=document.createElement('span');x.className='re-lightbox-close';x.setAttribute('aria-hidden','true');x.textContent='\\u00D7';o.appendChild(im);o.appendChild(x);document.body.appendChild(o);document.body.style.overflow='hidden';open=o;}
document.addEventListener('click',function(e){if(open){close();return;}var t=e.target;if(t&&t.tagName==='IMG'&&t.closest&&t.closest('.newsletter-container')){e.preventDefault();show(t.currentSrc||t.src,t.alt);}});
document.addEventListener('keydown',function(e){if(e.key==='Escape'||e.keyCode===27){close();}});
})();`;
}

// Meridian-lite: the CSS-only interpretation of Harv's Meridian Dial system for
// the Drupal-embedded web report. Paper/ink/gold palette, Playfair serif numerals
// (via @import, Georgia fallback), hairline rules, one gold accent, and a tablet
// breakpoint. EVERY rule is scoped under the .re-report wrapper (plus the
// .re-lightbox overlay) so nothing leaks into the surrounding InCom page — an
// unscoped body/:root block once washed out the site's own sidebar (2026-07-06).
// No dark mode on purpose: the report always renders as a light paper sheet, and
// the up/down market signal uses classic green/red per Harv.
const STYLE_BLOCK = `<style type="text/css">@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600;700&display=swap');
        .re-report { --paper:#FAF7F0; --ink:#2E2E2E; --ink-soft:#4A4640; --muted:#6B6459; --gold:#D4AF37; --gold-dark:#B08C1E; --hairline:#E8E4DA; --track:#F2EFE7; --card:#FFFFFF; --up:#16a34a; --down:#dc2626; --re:#B08C1E; --stocks:#3E5C76; --economy:#5B7551; --crypto:#8A5A2B; --serif:'Playfair Display',Georgia,'Times New Roman',serif; --sans:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif; margin: 0; padding: 18px 12px 24px; background: var(--paper); border-radius: 14px; font-family: var(--sans); color: var(--ink); font-size: 16px; line-height: 1.65; -webkit-font-smoothing: antialiased; }
        .re-report *, .re-report *::before, .re-report *::after { box-sizing: border-box; }
        .re-report #chart { background: var(--card); border: 1px solid var(--hairline); border-radius: 14px; box-shadow: 0 1px 3px rgba(46,46,46,0.04), 0 14px 34px -22px rgba(46,46,46,0.20); padding: 14px; max-width: 1000px; margin: 0 auto; min-height: 500px; }
        .re-report .date-badge { text-align: center; margin: 4px 0 16px; }
        .re-report .date-badge span { display: inline-block; border: 1px solid var(--gold); color: var(--gold-dark); background: transparent; padding: 7px 22px; border-radius: 40px; font-size: 12px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; }
        .re-report .info-banner { max-width: 1000px; margin: 0 auto 14px; background: var(--track); border: 1px solid var(--hairline); color: var(--ink-soft); padding: 10px 16px; border-radius: 10px; text-align: center; font-size: 12.5px; }
        .re-report .info-banner strong { color: var(--gold-dark); font-weight: 700; }
        .re-report .newsletter-container { background: var(--card); border: 1px solid var(--hairline); border-radius: 16px; box-shadow: 0 1px 3px rgba(46,46,46,0.04), 0 22px 50px -32px rgba(46,46,46,0.24); max-width: 760px; margin: 26px auto 0; padding: 36px 36px 30px; line-height: 1.72; font-variant-numeric: tabular-nums; }
        .re-report .newsletter-container p { margin: 0 0 15px; color: var(--ink-soft); }
        .re-report .newsletter-container strong { color: var(--ink); font-weight: 600; }
        .re-report .newsletter-container h3 { font-family: var(--serif); font-weight: 700; color: var(--ink); font-size: 18px; letter-spacing: -0.01em; margin: 26px 0 10px; padding-bottom: 7px; border-bottom: 1px solid var(--hairline); }
        .re-report .newsletter-container ul { margin: 8px 0 18px; padding-left: 0; list-style: none; }
        .re-report .newsletter-container li { margin-bottom: 7px; padding-left: 17px; position: relative; color: var(--ink-soft); font-size: 14.5px; }
        .re-report .newsletter-container li::before { content: ""; position: absolute; left: 0; top: 9px; width: 5px; height: 5px; border-radius: 50%; background: var(--gold); }
        .re-report .newsletter-container li strong { color: var(--ink); }
        .re-report .newsletter-container hr { border: 0; height: 1px; background: var(--hairline); margin: 30px 0; }
        .re-report .newsletter-container img { cursor: zoom-in; }
        .re-report .stat-line { font-family: var(--serif); font-size: 15px; color: var(--ink-soft); margin: 12px 0 20px; padding: 15px 18px; background: var(--paper); border: 1px solid var(--hairline); border-radius: 12px; line-height: 1.95; }
        .re-report .stat-line strong { font-family: var(--serif); color: var(--ink); font-weight: 600; font-size: 19px; font-variant-numeric: tabular-nums; }
        .re-report .up { color: var(--up); } .re-report .down { color: var(--down); } .re-report .flat { color: var(--muted); }
        .re-report .stat-line .up, .re-report .stat-line .down, .re-report .stat-line .flat { font-family: var(--sans); font-size: 12.5px; font-weight: 700; white-space: nowrap; }
        .re-report .section-bar-re, .re-report .section-bar-stocks, .re-report .section-bar-economy, .re-report .section-bar-crypto { font-family: var(--sans); font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.18em; padding: 0 0 8px 15px; margin: 32px 0 6px; position: relative; border-bottom: 1px solid var(--hairline); }
        .re-report .section-bar-re::before, .re-report .section-bar-stocks::before, .re-report .section-bar-economy::before, .re-report .section-bar-crypto::before { content: ""; position: absolute; left: 0; top: 1px; width: 5px; height: 13px; border-radius: 2px; }
        .re-report .section-bar-re { color: var(--re); } .re-report .section-bar-re::before { background: var(--re); }
        .re-report .section-bar-stocks { color: var(--stocks); } .re-report .section-bar-stocks::before { background: var(--stocks); }
        .re-report .section-bar-economy { color: var(--economy); } .re-report .section-bar-economy::before { background: var(--economy); }
        .re-report .section-bar-crypto { color: var(--crypto); } .re-report .section-bar-crypto::before { background: var(--crypto); }
        .re-report .sources-box { background: var(--paper); border: 1px solid var(--hairline); border-radius: 12px; padding: 18px 20px; margin-top: 26px; }
        .re-report .sources-box h3 { font-family: var(--sans); color: var(--gold-dark); font-size: 11px; text-transform: uppercase; letter-spacing: 0.16em; margin: 0 0 10px; padding: 0; border: 0; }
        .re-report .sources-box ul { margin: 0; padding: 0; list-style: none; }
        .re-report .sources-box li { font-size: 13px; color: var(--ink-soft); padding-left: 0; margin-bottom: 5px; }
        .re-report .sources-box li::before { display: none; }
        .re-report .sources-box a { color: var(--gold-dark); text-decoration: none; border-bottom: 1px solid var(--hairline); }
        .re-report .sources-box a:hover { border-bottom-color: var(--gold); }
        .re-report .disclaimer { background: transparent; border: 0; border-top: 1px solid var(--hairline); padding: 16px 0 0; font-style: normal; font-size: 12.5px; color: var(--muted); margin-top: 24px; line-height: 1.6; }
        .re-report .disclaimer strong { color: var(--ink-soft); }
        .re-lightbox { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(28,26,21,0.9); z-index: 999999; display: flex; align-items: center; justify-content: center; padding: 28px; cursor: zoom-out; }
        .re-lightbox img { max-width: 94vw; max-height: 90vh; width: auto; height: auto; background: #fff; border-radius: 10px; box-shadow: 0 24px 80px rgba(0,0,0,0.55); }
        .re-lightbox-close { position: fixed; top: 12px; right: 20px; color: #fff; font: 700 36px/1 Arial, sans-serif; cursor: pointer; }
        @media (max-width: 900px) { .re-report .newsletter-container { max-width: 100%; padding: 28px 22px; } }
        @media (max-width: 600px) { .re-report { font-size: 15.5px; } .re-report #chart { padding: 8px; border-radius: 12px; } .re-report .newsletter-container { padding: 22px 16px; border-radius: 12px; } .re-report .stat-line { padding: 13px 14px; font-size: 14px; } .re-report .stat-line strong { font-size: 17px; } .re-lightbox { padding: 12px; } }
</style>`;

/** Assemble the full standalone CMS page. `newsletterInner` is the inner HTML of .newsletter-container. */
function buildCmsHtml({ dateLabel, chartSrc, newsletterInner, pageTitle = '', description = '' }) {
  const banner = DEFAULT_VISIBLE.join(', ');
  // Attribute-safe escape for the head meta. NOTE: no inline <script> (e.g.
  // JSON-LD) may go in this document — Drupal strips inline scripts and truncates
  // everything after the first one, which would eat the newsletter. og/twitter
  // are <meta> tags (safe); Drupal owns the canonical SEO via the cms-meta sidecar.
  // The whole head prelude is emitted as ONE line: Drupal's line-break filter
  // turns every newline into a <br />, and a stack of ~10 breaks from invisible
  // meta tags rendered as a big empty gap under the page title (2026-07-06).
  const esc = s => String(s || '').replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const t = esc(pageTitle), d = esc(description);
  return `<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>${t}</title><meta name="description" content="${d}"><meta property="og:type" content="article"><meta property="og:title" content="${t}"><meta property="og:description" content="${d}"><meta property="og:site_name" content="REALTY EXPERTS&reg;"><meta name="twitter:card" content="summary"><meta name="twitter:title" content="${t}"><meta name="twitter:description" content="${d}"><script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>${STYLE_BLOCK}
<div class="re-report">
<div class="date-badge"><span>${dateLabel} &middot; Alameda County Market Dashboard</span></div>
<div class="info-banner"><strong>Tip:</strong> Tap a city in the legend to show or hide it &bull; Default view: ${banner} &bull; Tap any chart image below to enlarge</div>
<div id="chart">&nbsp;</div>
<div class="newsletter-container">
${newsletterInner}</div>
</div>
<script src="${chartSrc}"></script>
`;
}

/** Build the cms-meta sidecar text. */
function buildMeta({ date, year, copyright, description, keywords, robots }) {
  const title = `"At a Glance" Local Housing STATS and News ${date}`;
  return `════════════════════════════════
HARVREALTOR.COM CMS METADATA — ${date}
Copy/paste into the InCom "Add Blog Page" form
═════════════════════════════════

TITLE:
${title}


META COPYRIGHT (Optional):
${copyright || `© ${year} REALTY EXPERTS®`}


META DESCRIPTION (Optional — ~20 words, no HTML, max 1024 chars):
${description}


META KEYWORDS (Optional — comma-separated, max 450 chars):
${keywords}


ROBOTS META TAG:
${robots || 'Use default setting (ALL=INDEX,FOLLOW)'}
`;
}

/**
 * Generate both CMS artifacts.
 * @param {object} opts
 * @param {string} opts.date     "MM/DD/YY"
 * @param {object} opts.content  { newsletter_html, meta:{ description, keywords, copyright?, robots? } }
 * @param {string} [opts.outHtml] default alameda-interactive-MMDDYY.html
 * @param {string} [opts.outMeta] default cms-meta-MMDDYY.txt
 * @param {Array}  [opts.inventory] pre-parsed RE-v2 (for tests); otherwise read live
 */
async function generateCmsPage({ date, content, outHtml, outMeta, inventory }) {
  const { label, short, year } = parseDate(date);
  const inv = inventory || await readRev2();
  const meta = (content && content.meta) || {};
  if (!content || !content.newsletter_html) throw new Error('cms content missing newsletter_html');
  if (!meta.description || !meta.keywords) throw new Error('cms content missing meta.description / meta.keywords');

  const chartJsName = `alameda-chart-${short}.js`;
  const chartSrc = `${GITHUB_PAGES_BASE}/${chartJsName}`;
  const pageTitle = `"At a Glance" Local Housing STATS and News ${date}`;
  const html = buildCmsHtml({ dateLabel: label, chartSrc, newsletterInner: content.newsletter_html, pageTitle, description: meta.description });
  const metaTxt = buildMeta({ date, year, copyright: meta.copyright, description: meta.description, keywords: meta.keywords, robots: meta.robots });

  const htmlPath = outHtml || path.join(__dirname, `alameda-interactive-${short}.html`);
  const metaPath = outMeta || path.join(__dirname, `cms-meta-${short}.txt`);
  const chartJsPath = path.join(path.dirname(htmlPath), chartJsName);
  fs.writeFileSync(htmlPath, html);
  fs.writeFileSync(metaPath, metaTxt);
  fs.writeFileSync(chartJsPath, chartInnerJs(inv));
  return { cities: inv.length, htmlBytes: html.length, htmlPath, metaPath, chartJsPath };
}

// ── CLI ──────────────────────────────────────────────────────────────────────

if (require.main === module) {
  const argv = process.argv.slice(2);
  const opt = (name) => { const i = argv.indexOf(name); return i >= 0 ? argv[i + 1] : undefined; };
  let date = opt('--date');
  const contentPath = opt('--content') || DEFAULT_CONTENT;
  const outHtml = opt('--out-html');
  const outMeta = opt('--out-meta');

  if (!date) {
    try { date = JSON.parse(fs.readFileSync(TEMPLATE_PATH, 'utf8')).date; } catch (_) { /* none */ }
  }
  if (!date) { console.error('No date — pass --date MM/DD/YY or ensure daily-market-template.json exists.'); process.exit(1); }
  let content;
  try { content = JSON.parse(fs.readFileSync(contentPath, 'utf8')); }
  catch (e) { console.error(`Could not read cms content at ${contentPath}: ${e.message}`); process.exit(1); }

  generateCmsPage({ date, content, outHtml, outMeta })
    .then(r => console.log(`wrote ${path.basename(r.htmlPath)} (${r.cities} cities, ${r.htmlBytes} bytes) + ${path.basename(r.metaPath)} + ${path.basename(r.chartJsPath)}`))
    .catch(err => { console.error('Error:', err.message); process.exit(1); });
}

module.exports = { generateCmsPage, parseRev2, readRev2, buildCmsHtml, buildMeta, parseDate, CATS, CITY_ORDER, DEFAULT_VISIBLE };
