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
const COLORS = {
  'Fremont': '#FF6B6B', 'Union City': '#4ECDC4', 'Castro Valley': '#2E86AB',
  'Danville': '#FFA07A', 'Hayward': '#A23B72', 'Livermore': '#F7DC6F',
  'Newark': '#BB8FCE', 'Pleasanton': '#E8611A', 'San Ramon': '#3DDC84',
  'Dublin': '#5C6BC0', 'San Leandro': '#FF8A65', 'Milpitas': '#00BFA5',
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
    marker: { color: COLORS[city] || '#888', line: { width: 1.5, color: 'rgba(255,255,255,0.3)' } },
    hovertemplate: `<b>${city}</b><br>%{x}: %{y}<extra></extra>`,
  }));
  const layout = {
    title: { text: '🏠 Real Estate Inventory Dashboard', font: { size: 22, color: '#2c3e50', family: 'Arial, sans-serif' }, x: 0.5, xanchor: 'center' },
    xaxis: { title: 'Listing Category', titlefont: { size: 14, color: '#34495e' }, tickfont: { size: 12, color: '#34495e' }, gridcolor: 'rgba(0,0,0,0.05)', showgrid: true },
    yaxis: { title: 'Count', titlefont: { size: 14, color: '#34495e' }, tickfont: { size: 12, color: '#34495e' }, gridcolor: 'rgba(0,0,0,0.1)', showgrid: true },
    height: 700, plot_bgcolor: 'rgba(250,250,250,0.8)', paper_bgcolor: 'white', hovermode: 'closest', showlegend: true,
    legend: { title: { text: '<b>Cities (click to toggle)</b>', font: { size: 13 } }, font: { size: 11 }, bgcolor: 'rgba(255,255,255,0.9)', bordercolor: '#bdc3c7', borderwidth: 1, orientation: 'h', x: 0.5, y: -0.18, xanchor: 'center', yanchor: 'top' },
    barmode: 'group', bargap: 0.15, bargroupgap: 0.1, margin: { l: 60, r: 20, t: 70, b: 120 }, font: { family: 'Arial, sans-serif' }, transition: { duration: 500, easing: 'cubic-in-out' },
  };
  const config = { displayModeBar: true, displaylogo: false, modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'], toImageButtonOptions: { format: 'png', filename: 'realty_experts_inventory', height: 800, width: 1400, scale: 2 }, responsive: true };
  // Emitted to an EXTERNAL .js file (alameda-chart-MMDDYY.js) and referenced via
  // <script src>. Drupal strips INLINE <script> from the node body but keeps
  // external src tags — so the chart only renders when its data lives in a
  // hosted file. No HTML-escaping needed here (the file is never HTML-filtered).
  return `var data = ${JSON.stringify(traces)};
var layout = ${JSON.stringify(layout)};
var config = ${JSON.stringify(config)};
function getResponsiveLayout(){var w=window.innerWidth;var u=JSON.parse(JSON.stringify(layout));if(w<600){u.height=500;u.margin={l:40,r:10,t:50,b:140};u.title.font.size=16;u.xaxis.tickfont={size:10};u.yaxis.tickfont={size:10};u.legend.font={size:9};u.legend.y=-0.28;u.bargap=0.1;u.bargroupgap=0.05;}else if(w<900){u.height=600;u.margin={l:50,r:15,t:60,b:130};u.title.font.size=20;u.legend.font={size:10};u.legend.y=-0.22;}return u;}
function drawChart(){Plotly.newPlot('chart', data, getResponsiveLayout(), config).then(function(){var el=document.getElementById('chart');if(el&&el.on){el.on('plotly_legendclick',function(d){return true;});}});window.addEventListener('resize',function(){Plotly.relayout('chart', getResponsiveLayout());});}
if(window.Plotly){drawChart();}else{document.addEventListener('DOMContentLoaded',drawChart);}`;
}

const STYLE_BLOCK = `<style type="text/css">* { box-sizing: border-box; }
        body { margin: 0; padding: 10px; font-family: 'Arial', sans-serif; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); color: #333333; }
        #chart { background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); padding: 10px; max-width: 100%; margin: 0 auto; min-height: 500px; }
        .info-banner { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 10px 16px; border-radius: 8px; margin-bottom: 12px; text-align: center; font-size: 13px; }
        .date-badge { text-align: center; margin-bottom: 16px; }
        .date-badge span { display: inline-block; background: linear-gradient(135deg, #1e3a5f, #2563eb); color: white; padding: 8px 24px; border-radius: 50px; font-size: 14px; font-weight: 600; letter-spacing: 0.5px; }
        .newsletter-container { background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); max-width: 1000px; margin: 30px auto; padding: 30px; line-height: 1.6; }
        .newsletter-container h3 { color: #34495e; margin-top: 24px; margin-bottom: 8px; }
        .newsletter-container ul { margin: 8px 0 16px 0; padding-left: 22px; }
        .newsletter-container li { margin-bottom: 4px; }
        .newsletter-container hr { border: 0; height: 1px; background: #ecf0f1; margin: 28px 0; }
        .stat-line { font-size: 15px; font-weight: 600; color: #1e293b; margin: 10px 0 16px 0; }
        .section-bar-re, .section-bar-stocks, .section-bar-economy, .section-bar-crypto { color: white; padding: 10px 18px; font-size: 17px; font-weight: 700; border-radius: 6px; margin-top: 10px; margin-bottom: 12px; }
        .section-bar-re { background-color: #ea580c; }
        .section-bar-stocks { background-color: #2563eb; }
        .section-bar-economy { background-color: #16a34a; }
        .section-bar-crypto { background-color: #f59e0b; }
        .sources-box { background-color: #f8fafc; border-radius: 8px; padding: 18px; margin-top: 20px; }
        .sources-box h3 { color: #64748b; font-size: 14px; margin-top: 0; }
        .sources-box li { font-size: 13px; color: #64748b; }
        .sources-box a { color: #2563eb; text-decoration: none; }
        .disclaimer { background-color: #f9f9f9; border-left: 4px solid #bdc3c7; padding: 15px; font-style: italic; font-size: 0.9em; color: #7f8c8d; margin-top: 20px; }
        @media (max-width: 600px) { body { padding: 5px; } #chart { padding: 5px; } .newsletter-container { padding: 18px; margin: 15px auto; } }
</style>`;

/** Assemble the full standalone CMS page. `newsletterInner` is the inner HTML of .newsletter-container. */
function buildCmsHtml({ dateLabel, chartSrc, newsletterInner }) {
  const banner = DEFAULT_VISIBLE.join(', ');
  return `<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title></title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
${STYLE_BLOCK}

<div class="date-badge"><span>${dateLabel} - Alameda County Market Dashboard</span></div>

<div class="info-banner"><strong>Tip:</strong> Click on city names in the legend to show/hide data &bull; Default view: ${banner}</div>

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
  const html = buildCmsHtml({ dateLabel: label, chartSrc, newsletterInner: content.newsletter_html });
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
