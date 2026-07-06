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
  // Colors (paper/ink/grid) resolve at draw time from prefers-color-scheme via
  // themeC() below — these are just light-mode seeds so a no-JS view still reads.
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
  // Theme colors follow prefers-color-scheme so the chart tracks light/dark.
  return `var data = ${JSON.stringify(traces)};
var baseLayout = ${JSON.stringify(layout)};
var config = ${JSON.stringify(config)};
function themeC(){var d=window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches;return d?{paper:'#211F1B',ink:'#F3EFE6',soft:'#C9C2B4',grid:'rgba(243,239,230,0.10)'}:{paper:'#FFFFFF',ink:'#2E2E2E',soft:'#4A4640',grid:'rgba(46,46,46,0.07)'};}
function layoutFor(){var w=window.innerWidth,t=themeC(),u=JSON.parse(JSON.stringify(baseLayout));u.paper_bgcolor=t.paper;u.plot_bgcolor=t.paper;u.title.font.color=t.ink;u.xaxis.title.font.color=t.soft;u.xaxis.tickfont.color=t.soft;u.yaxis.title.font.color=t.soft;u.yaxis.tickfont.color=t.soft;u.yaxis.gridcolor=t.grid;u.legend.font.color=t.soft;u.legend.title.font.color=t.soft;u.font.color=t.soft;if(w<600){u.height=560;u.margin={l:42,r:10,t:46,b:176};u.title.font.size=17;u.xaxis.tickfont.size=10;u.yaxis.tickfont.size=10;u.legend.font.size=9;u.legend.x=0;u.legend.xanchor='left';u.legend.title.text='';u.legend.y=-0.26;u.bargap=0.22;}else if(w<900){u.height=580;u.margin={l:48,r:14,t:50,b:134};u.title.font.size=19;u.legend.font.size=10;u.legend.x=0;u.legend.xanchor='left';u.legend.y=-0.24;}return u;}
function drawChart(){Plotly.newPlot('chart', data, layoutFor(), config);window.addEventListener('resize',function(){Plotly.relayout('chart', layoutFor());});if(window.matchMedia){try{window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change',function(){Plotly.relayout('chart', layoutFor());});}catch(e){}}}
if(window.Plotly){drawChart();}else{document.addEventListener('DOMContentLoaded',drawChart);}`;
}

// Meridian-lite: the CSS-only interpretation of Harv's Meridian Dial system for
// the Drupal-embedded web report. Paper/ink/gold palette, Playfair serif numerals
// (via @import, Georgia fallback), hairline rules, one gold accent, a tablet
// breakpoint, and prefers-color-scheme dark mode. All theming runs through CSS
// custom properties so the dark block only re-declares :root.
const STYLE_BLOCK = `<style type="text/css">@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600;700&display=swap');
        :root { --paper:#FAF7F0; --ink:#2E2E2E; --ink-soft:#4A4640; --muted:#6B6459; --gold:#D4AF37; --gold-dark:#B08C1E; --hairline:#E8E4DA; --track:#F2EFE7; --card:#FFFFFF; --re:#B08C1E; --stocks:#3E5C76; --economy:#5B7551; --crypto:#8A5A2B; --serif:'Playfair Display',Georgia,'Times New Roman',serif; --sans:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif; }
        * { box-sizing: border-box; }
        body { margin: 0; padding: 22px 16px 40px; font-family: var(--sans); background: var(--paper); color: var(--ink); font-size: 16px; line-height: 1.65; -webkit-font-smoothing: antialiased; }
        #chart { background: var(--card); border: 1px solid var(--hairline); border-radius: 14px; box-shadow: 0 1px 3px rgba(46,46,46,0.04), 0 14px 34px -22px rgba(46,46,46,0.20); padding: 14px; max-width: 1000px; margin: 0 auto; min-height: 500px; }
        .date-badge { text-align: center; margin: 4px 0 16px; }
        .date-badge span { display: inline-block; border: 1px solid var(--gold); color: var(--gold-dark); background: transparent; padding: 7px 22px; border-radius: 40px; font-size: 12px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; }
        .info-banner { max-width: 1000px; margin: 0 auto 14px; background: var(--track); border: 1px solid var(--hairline); color: var(--ink-soft); padding: 10px 16px; border-radius: 10px; text-align: center; font-size: 12.5px; }
        .info-banner strong { color: var(--gold-dark); font-weight: 700; }
        .newsletter-container { background: var(--card); border: 1px solid var(--hairline); border-radius: 16px; box-shadow: 0 1px 3px rgba(46,46,46,0.04), 0 22px 50px -32px rgba(46,46,46,0.24); max-width: 760px; margin: 26px auto 0; padding: 36px 36px 30px; line-height: 1.72; font-variant-numeric: tabular-nums; }
        .newsletter-container p { margin: 0 0 15px; color: var(--ink-soft); }
        .newsletter-container strong { color: var(--ink); font-weight: 600; }
        .newsletter-container h3 { font-family: var(--serif); font-weight: 700; color: var(--ink); font-size: 18px; letter-spacing: -0.01em; margin: 26px 0 10px; padding-bottom: 7px; border-bottom: 1px solid var(--hairline); }
        .newsletter-container ul { margin: 8px 0 18px; padding-left: 0; list-style: none; }
        .newsletter-container li { margin-bottom: 7px; padding-left: 17px; position: relative; color: var(--ink-soft); font-size: 14.5px; }
        .newsletter-container li::before { content: ""; position: absolute; left: 0; top: 9px; width: 5px; height: 5px; border-radius: 50%; background: var(--gold); }
        .newsletter-container li strong { color: var(--ink); }
        .newsletter-container hr { border: 0; height: 1px; background: var(--hairline); margin: 30px 0; }
        .stat-line { font-family: var(--serif); font-size: 15px; color: var(--ink-soft); margin: 12px 0 20px; padding: 15px 18px; background: var(--paper); border: 1px solid var(--hairline); border-radius: 12px; line-height: 1.95; }
        .stat-line strong { font-family: var(--serif); color: var(--ink); font-weight: 600; font-size: 19px; font-variant-numeric: tabular-nums; }
        .section-bar-re, .section-bar-stocks, .section-bar-economy, .section-bar-crypto { font-family: var(--sans); font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.18em; padding: 0 0 8px 15px; margin: 32px 0 6px; position: relative; border-bottom: 1px solid var(--hairline); }
        .section-bar-re::before, .section-bar-stocks::before, .section-bar-economy::before, .section-bar-crypto::before { content: ""; position: absolute; left: 0; top: 1px; width: 5px; height: 13px; border-radius: 2px; }
        .section-bar-re { color: var(--re); } .section-bar-re::before { background: var(--re); }
        .section-bar-stocks { color: var(--stocks); } .section-bar-stocks::before { background: var(--stocks); }
        .section-bar-economy { color: var(--economy); } .section-bar-economy::before { background: var(--economy); }
        .section-bar-crypto { color: var(--crypto); } .section-bar-crypto::before { background: var(--crypto); }
        .sources-box { background: var(--paper); border: 1px solid var(--hairline); border-radius: 12px; padding: 18px 20px; margin-top: 26px; }
        .sources-box h3 { font-family: var(--sans); color: var(--gold-dark); font-size: 11px; text-transform: uppercase; letter-spacing: 0.16em; margin: 0 0 10px; padding: 0; border: 0; }
        .sources-box ul { margin: 0; padding: 0; list-style: none; }
        .sources-box li { font-size: 13px; color: var(--ink-soft); padding-left: 0; margin-bottom: 5px; }
        .sources-box li::before { display: none; }
        .sources-box a { color: var(--gold-dark); text-decoration: none; border-bottom: 1px solid var(--hairline); }
        .sources-box a:hover { border-bottom-color: var(--gold); }
        .disclaimer { background: transparent; border: 0; border-top: 1px solid var(--hairline); padding: 16px 0 0; font-style: normal; font-size: 12.5px; color: var(--muted); margin-top: 24px; line-height: 1.6; }
        .disclaimer strong { color: var(--ink-soft); }
        @media (max-width: 900px) { .newsletter-container { max-width: 100%; padding: 28px 22px; } }
        @media (max-width: 600px) { body { padding: 12px 10px 30px; font-size: 15.5px; } #chart { padding: 8px; border-radius: 12px; } .newsletter-container { padding: 22px 16px; border-radius: 12px; } .stat-line { padding: 13px 14px; font-size: 14px; } .stat-line strong { font-size: 17px; } }
        @media (prefers-color-scheme: dark) { :root { --paper:#1B1A17; --ink:#F3EFE6; --ink-soft:#C9C2B4; --muted:#9A9384; --gold:#E8C65A; --gold-dark:#D4AF37; --hairline:#34322C; --track:#232219; --card:#211F1B; --re:#D4AF37; --stocks:#7FA5C4; --economy:#9FC08F; --crypto:#D0A24E; } #chart, .newsletter-container { box-shadow: none; } }
</style>`;

/** Assemble the full standalone CMS page. `newsletterInner` is the inner HTML of .newsletter-container. */
function buildCmsHtml({ dateLabel, chartSrc, newsletterInner, pageTitle = '', description = '' }) {
  const banner = DEFAULT_VISIBLE.join(', ');
  // Attribute-safe escape for the head meta. NOTE: no inline <script> (e.g.
  // JSON-LD) may go in this document — Drupal strips inline scripts and truncates
  // everything after the first one, which would eat the newsletter. og/twitter
  // are <meta> tags (safe); Drupal owns the canonical SEO via the cms-meta sidecar.
  const esc = s => String(s || '').replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const t = esc(pageTitle), d = esc(description);
  return `<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${t}</title>
<meta name="description" content="${d}">
<meta property="og:type" content="article">
<meta property="og:title" content="${t}">
<meta property="og:description" content="${d}">
<meta property="og:site_name" content="REALTY EXPERTS&reg;">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="${t}">
<meta name="twitter:description" content="${d}">
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
${STYLE_BLOCK}

<div class="date-badge"><span>${dateLabel} &middot; Alameda County Market Dashboard</span></div>

<div class="info-banner"><strong>Tip:</strong> Tap a city in the legend to show or hide it &bull; Default view: ${banner}</div>

<div id="chart">&nbsp;</div>

<div class="newsletter-container">
${newsletterInner}</div>

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
