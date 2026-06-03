#!/usr/bin/env node
/**
 * build-interactive-chart.js  [outfile]  [--date MM/DD/YY]  [--email-url URL]
 *
 * Generates latest_inventory_chart.html — the Plotly dashboard pushed to the
 * teamrealtyexperts.com todays-inventory `html_display` slot — by reading the
 * master sheet's "Interactive" tab LIVE via the service account.
 *
 * Interactive tab layout (transposed): column A holds category labels
 * (CO, DU, DE, TH, Active All, New, CS, PEND, ...), row 0 holds city headers
 * across columns B+. Whatever cities are present render automatically — e.g.
 * Milpitas appears the moment it is added as a column to that tab.
 *
 * Exported as buildInteractiveChart({date, outFile, emailUrl}) for the daily
 * pipeline (update-inventory.js calls it before pushing html_display); also
 * runnable standalone for previews.
 */

const fs = require('fs');
const { getAccessToken, getSheetValues, SCOPES } = require('../lib/google-sa');
const { GITHUB_PAGES_BASE, CHART_HTML_PATH, TEMPLATE_PATH } = require('../lib/config');

const SHEET_ID = '1YxbK29giJO6XDQAV3RHXml2vjMejmtBpZfD3ICW_gTw';
const TAB_RANGE = 'Interactive!A1:Z30';

// Chart category columns (display order), matched against the tab's col-A labels.
const CATS = ['CO', 'DU', 'DE', 'TH', 'Active All', 'New', 'CS', 'PEND'];

// Per-city bar colors, keyed by clean display name. Milpitas pre-seeded so it
// renders with a stable color as soon as it joins the Interactive tab.
const COLORS = {
  'FREMONT': '#FF6B6B', 'UNION CITY': '#4ECDC4', 'CASTRO VALLEY': '#2E86AB',
  'DANVILLE': '#FFA07A', 'HAYWARD': '#A23B72', 'LIVERMORE': '#F7DC6F',
  'NEWARK': '#BB8FCE', 'PLEASANTON': '#E8611A', 'SAN RAMON': '#3DDC84',
  'DUBLIN': '#5C6BC0', 'SAN LEANDRO': '#FF8A65', 'MILPITAS': '#00BFA5',
};

// Cities shown by default; everything else starts collapsed to "legendonly".
const DEFAULT_VISIBLE = new Set(['FREMONT', 'UNION CITY', 'HAYWARD', 'NEWARK', 'MILPITAS']);

// The Interactive-tab header occasionally carries mangled spellings — map the
// raw header cell (spaces stripped, upper-cased) to a clean display name.
// Unmapped names pass through trimmed + upper-cased.
const CITY_ALIASES = {
  'CASTROVAEY': 'CASTRO VALLEY',
  'CASTROVALLEY': 'CASTRO VALLEY',
  'SANLEANDRO': 'SAN LEANDRO',
  'UNIONCITY': 'UNION CITY',
  'SANRAMON': 'SAN RAMON',
};

const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'];

function normCity(raw) {
  const key = String(raw).trim().toUpperCase().replace(/\s+/g, '');
  return CITY_ALIASES[key] || String(raw).trim().toUpperCase();
}

function titleCase(name) {
  return name.split(' ')
    .map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(' ');
}

/** "MM/DD/YY" -> { label: "June 2, 2026", short: "060226" } */
function parseDate(mmddyy) {
  const [mm, dd, yy] = String(mmddyy).split('/').map(s => parseInt(s, 10));
  if (!mm || !dd || isNaN(yy)) throw new Error(`bad date "${mmddyy}" (want MM/DD/YY)`);
  return {
    label: `${MONTHS[mm - 1]} ${dd}, 20${String(yy).padStart(2, '0')}`,
    short: String(mmddyy).replace(/\//g, ''),
  };
}

/**
 * Parse raw Interactive-tab rows into an ordered list of
 * { city, values: [CO, DU, DE, TH, Active All, New, CS, PEND] }, one per city
 * column, in the tab's left-to-right order. Pure (no IO) so it can be tested
 * against synthetic sheets — e.g. to confirm a newly-added Milpitas column.
 */
function parseInventory(rows) {
  if (!rows || !rows.length) throw new Error('Interactive tab returned no rows');

  const cities = (rows[0] || []).slice(1).map(normCity);  // drop corner cell
  if (!cities.length) throw new Error('Interactive tab header has no city columns');

  // category label (trimmed) -> array of per-city cells
  const byCat = {};
  for (const row of rows.slice(1)) {
    const label = String(row[0] || '').trim();
    if (label) byCat[label] = row.slice(1);
  }
  const missing = CATS.filter(c => !byCat[c]);
  if (missing.length) throw new Error(`Interactive tab missing category rows: ${missing.join(', ')}`);

  return cities.map((city, i) => ({
    city,
    values: CATS.map(cat => parseInt(byCat[cat][i], 10) || 0),
  }));
}

/** Fetch the Interactive tab live and parse it. */
async function readInventory() {
  const token = await getAccessToken(SCOPES.SHEETS_RO);
  const rows = await getSheetValues(SHEET_ID, TAB_RANGE, token);
  return parseInventory(rows);
}

function renderHtml(inventory, dateLabel, emailUrl) {
  const traces = inventory.map(({ city, values }) => ({
    name: city,
    x: CATS,
    y: values,
    type: 'bar',
    visible: DEFAULT_VISIBLE.has(city) ? true : 'legendonly',
    marker: { color: COLORS[city] || '#888', line: { width: 1.5, color: 'rgba(255,255,255,0.3)' } },
    hovertemplate: `<b>${city}</b><br>%{x}: %{y}<extra></extra>`,
  }));

  const layout = {
    title: { text: 'Real Estate Inventory Dashboard', font: { size: 22, color: '#2c3e50', family: 'Arial, sans-serif' }, x: 0.5, xanchor: 'center' },
    xaxis: { title: 'Listing Category', titlefont: { size: 14, color: '#34495e' }, tickfont: { size: 12, color: '#34495e' }, gridcolor: 'rgba(0,0,0,0.05)', showgrid: true },
    yaxis: { title: 'Count', titlefont: { size: 14, color: '#34495e' }, tickfont: { size: 12, color: '#34495e' }, gridcolor: 'rgba(0,0,0,0.1)', showgrid: true },
    height: 700, plot_bgcolor: 'rgba(250,250,250,0.8)', paper_bgcolor: 'white', hovermode: 'closest', showlegend: true,
    legend: { title: { text: '<b>Cities (click to toggle)</b>', font: { size: 13 } }, font: { size: 11 }, bgcolor: 'rgba(255,255,255,0.9)', bordercolor: '#bdc3c7', borderwidth: 1, orientation: 'h', x: 0.5, y: -0.18, xanchor: 'center', yanchor: 'top' },
    barmode: 'group', bargap: 0.15, bargroupgap: 0.1, margin: { l: 60, r: 20, t: 70, b: 120 }, font: { family: 'Arial, sans-serif' }, transition: { duration: 500, easing: 'cubic-in-out' },
  };
  const config = { displayModeBar: true, displaylogo: false, modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'], toImageButtonOptions: { format: 'png', filename: 'realty_experts_inventory', height: 800, width: 1400, scale: 2 }, responsive: true };

  // Banner lists the default-visible cities that actually exist, in tab order.
  const defaultCities = inventory.map(t => t.city)
    .filter(c => DEFAULT_VISIBLE.has(c)).map(titleCase).join(', ');

  return `<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<style>
.date-badge{text-align:center;margin:6px 0;}
.date-badge span{display:inline-block;background:#1e5bb8;color:#fff;font:600 15px Arial,sans-serif;padding:8px 22px;border-radius:20px;}
.info-banner{background:linear-gradient(135deg,#4f46e5,#7c3aed);color:#fff;font:13px Arial,sans-serif;padding:10px 16px;border-radius:8px;margin:10px auto;max-width:1200px;text-align:center;}
#chart{background:#fff;border-radius:12px;padding:10px;max-width:1300px;margin:0 auto;}
</style>
<div class="date-badge"><span>${dateLabel} - Alameda County Market Dashboard</span></div>
<div class="info-banner"><strong>Tip:</strong> Click on city names in the legend to show/hide data &bull; Default view: ${defaultCities}</div>
<div id="chart">&nbsp;</div>
<h2 style="text-align:center;"><a href="${emailUrl}" target="_blank"><span style="color:#0000FF;">View Full Email Version</span></a></h2>
<script>
var data = ${JSON.stringify(traces)};
var layout = ${JSON.stringify(layout)};
var config = ${JSON.stringify(config)};
function getResponsiveLayout(){var w=window.innerWidth;var L=JSON.parse(JSON.stringify(layout));if(w<600){L.height=500;L.margin={l:40,r:10,t:50,b:140};L.title.font.size=16;L.xaxis.tickfont={size:10};L.yaxis.tickfont={size:10};L.legend.font={size:9};L.legend.y=-0.28;L.bargap=0.1;L.bargroupgap=0.05;}else if(w<900){L.height=600;L.margin={l:50,r:15,t:60,b:130};L.title.font.size=20;L.legend.font={size:10};L.legend.y=-0.22;}return L;}
Plotly.newPlot('chart',data,getResponsiveLayout(),config);
window.addEventListener('resize',function(){Plotly.relayout('chart',getResponsiveLayout());});
document.getElementById('chart').on('plotly_legendclick',function(d){return true;});
</script>
`;
}

/**
 * Build the interactive chart HTML and write it to `outFile`.
 * @param {object} opts
 * @param {string} opts.date     today's date as "MM/DD/YY" (drives badge + email URL)
 * @param {string} [opts.outFile]  where to write (default: CHART_HTML_PATH)
 * @param {string} [opts.emailUrl] override the "View Full Email Version" link
 * @returns {Promise<{cities:number, bytes:number, path:string}>}
 */
async function buildInteractiveChart({ date, outFile, emailUrl } = {}) {
  if (!date) throw new Error('buildInteractiveChart requires a date (MM/DD/YY)');
  const { label, short } = parseDate(date);
  const url = emailUrl || `${GITHUB_PAGES_BASE}/daily-market-glance-${short}.html`;
  const out = outFile || CHART_HTML_PATH;
  const inventory = await readInventory();
  const html = renderHtml(inventory, label, url);
  fs.writeFileSync(out, html);
  return { cities: inventory.length, bytes: html.length, path: out };
}

// ── CLI ──────────────────────────────────────────────────────────────────────

if (require.main === module) {
  const argv = process.argv.slice(2);
  let date = null, emailUrl, outFile;
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--date') date = argv[++i];
    else if (a === '--email-url') emailUrl = argv[++i];
    else if (!a.startsWith('--') && outFile === undefined) outFile = a;
  }

  if (!date) {
    try { date = JSON.parse(fs.readFileSync(TEMPLATE_PATH, 'utf8')).date; } catch (_) { /* none */ }
  }
  if (!date) {
    console.error('No date — pass --date MM/DD/YY or ensure daily-market-template.json exists.');
    process.exit(1);
  }

  buildInteractiveChart({ date, outFile, emailUrl })
    .then(res => console.log(`wrote ${res.path} (${res.cities} cities, ${res.bytes} bytes)`))
    .catch(err => { console.error('Error:', err.message); process.exit(1); });
}

module.exports = { buildInteractiveChart, readInventory, parseInventory, renderHtml };
