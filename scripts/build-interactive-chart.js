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

// LEGACY (pre-2026-07-19 Plotly grouped-bar era): per-city colors and the
// default-visible subset. The ranked-bar renderer shows every city in one gold
// and needs neither — kept only for reference/rollback.
const COLORS = {
  'FREMONT': '#FF6B6B', 'UNION CITY': '#4ECDC4', 'CASTRO VALLEY': '#2E86AB',
  'DANVILLE': '#FFA07A', 'HAYWARD': '#A23B72', 'LIVERMORE': '#F7DC6F',
  'NEWARK': '#BB8FCE', 'PLEASANTON': '#E8611A', 'SAN RAMON': '#3DDC84',
  'DUBLIN': '#5C6BC0', 'SAN LEANDRO': '#FF8A65', 'MILPITAS': '#00BFA5',
};
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
  // Same {name, x, y} series shape as the harvrealtor.com chart JS — no verifier
  // reads this surface today, but keeping the two forks shape-identical keeps a
  // future shared value-check trivial.
  const traces = inventory.map(({ city, values }) => ({ name: city, x: CATS, y: values }));

  // 2026-07-19 redesign (mirrors the harvrealtor.com daily chart): self-rendering
  // ranked horizontal bars, no Plotly (was a 1.09MB render-blocking load), every
  // count printed, category chips at 44px touch size, all cities always shown.
  // This surface (glance-api html_display) allows inline <script>, so the whole
  // chart ships self-contained: data + styles + renderer in this one fragment.
  // Categories here are the 8-cat Interactive-tab set (adds DU = Duet vs .com).
  // All DOM is built with createElement/textContent.
  return `<style>
.date-badge{text-align:center;margin:6px 0;}
.date-badge span{display:inline-block;background:#1e5bb8;color:#fff;font:600 15px Arial,sans-serif;padding:8px 22px;border-radius:20px;}
.info-banner{background:linear-gradient(135deg,#4f46e5,#7c3aed);color:#fff;font:13px Arial,sans-serif;padding:10px 16px;border-radius:8px;margin:10px auto;max-width:1200px;text-align:center;}
#chart{background:#fff;border-radius:12px;padding:14px;max-width:1300px;margin:0 auto;}
#chart .rr-wrap{max-width:640px;margin:0 auto;}
#chart .rr-title{font-family:Georgia,'Times New Roman',serif;font-size:19px;font-weight:700;color:#2E2E2E;text-align:center;margin:8px 0 2px;letter-spacing:-0.01em;}
#chart .rr-sub{font-family:Arial,sans-serif;font-size:12.5px;color:#6B6459;text-align:center;margin:0 0 14px;}
#chart .rr-groups{display:flex;flex-wrap:wrap;gap:10px 26px;justify-content:center;margin:0 0 16px;}
#chart .rr-group-label{font-family:Arial,sans-serif;font-size:10px;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:#6B6459;margin:0 0 6px;}
#chart .rr-chips{display:flex;flex-wrap:wrap;gap:8px;}
#chart .rr-chip{min-height:44px;padding:10px 14px;border-radius:9px;border:1px solid #E8E4DA;background:#FFFFFF;color:#4A4640;font-family:Arial,sans-serif;font-size:13px;font-weight:600;line-height:1.15;cursor:pointer;}
#chart .rr-chip[aria-pressed="true"]{background:#D4AF37;border-color:#B08C1E;color:#2E2E2E;font-weight:700;}
#chart .rr-chip:focus-visible{outline:2px solid #B08C1E;outline-offset:2px;}
#chart .rr-rows{list-style:none;margin:0;padding:0;}
#chart .rr-rows li{display:grid;grid-template-columns:100px 1fr 46px;gap:8px;align-items:center;min-height:29px;padding:0;margin:0;}
#chart .rr-city{font-family:Arial,sans-serif;font-size:12px;color:#4A4640;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;text-align:left;}
#chart li.rr-flag .rr-city{font-weight:700;color:#2E2E2E;}
#chart .rr-track{height:16px;background:#F2EFE7;border-radius:3px;overflow:hidden;}
#chart .rr-fill{display:block;height:100%;width:0;background:#B08C1E;border-radius:3px;transition:width 0.32s cubic-bezier(0.22,1,0.36,1);}
#chart li.rr-flag .rr-fill{background:#D4AF37;box-shadow:inset 0 0 0 1px #B08C1E;}
#chart .rr-val{font-family:Georgia,'Times New Roman',serif;font-size:14px;font-weight:600;color:#2E2E2E;text-align:right;font-variant-numeric:tabular-nums;}
#chart .rr-note{font-family:Arial,sans-serif;font-size:11.5px;color:#6B6459;line-height:1.55;margin:16px auto 4px;max-width:560px;text-align:center;}
@media (max-width:599px){#chart .rr-rows li{grid-template-columns:88px 1fr 40px;}#chart .rr-groups{justify-content:flex-start;gap:12px 18px;}}
@media (prefers-reduced-motion:reduce){#chart .rr-fill{transition:none;}}
</style>
<div class="date-badge"><span>${dateLabel} - Alameda County Market Dashboard</span></div>
<div class="info-banner"><strong>Tip:</strong> Tap a category to re-rank the cities &bull; Every count is printed on its bar</div>
<div id="chart">&nbsp;</div>
<h2 style="text-align:center;"><a href="${emailUrl}" target="_blank"><span style="color:#0000FF;">View Full Email Version</span></a></h2>
<script>
var data = ${JSON.stringify(traces)};
var chartMeta = ${JSON.stringify({ dateLabel })};
(function(){
var root=document.getElementById('chart');
if(!root)return;
var LABEL={'Active All':'Active All','New':'New','CS':'Coming Soon','PEND':'Pending','DE':'Detached','CO':'Condo','TH':'Townhouse','DU':'Duet'};
var SUB={'Active All':'active listings','New':'new listings','CS':'coming soon listings','PEND':'pending sales','DE':'detached homes','CO':'condos','TH':'townhouses','DU':'duets'};
var GROUPS=[{label:'Market status',cats:['Active All','New','CS','PEND']},{label:'By home type',cats:['DE','CO','TH','DU']}];
var FLAGSHIP='FREMONT';
function titleCase(s){return String(s).split(' ').map(function(w){return w.charAt(0).toUpperCase()+w.slice(1).toLowerCase();}).join(' ');}
function el(tag,cls){var n=document.createElement(tag);if(cls)n.className=cls;return n;}
function valueOf(series,cat){var i=series.x.indexOf(cat);return i>=0?(Number(series.y[i])||0):0;}
while(root.firstChild){root.removeChild(root.firstChild);}
var wrap=el('div','rr-wrap');
var title=el('div','rr-title');
title.textContent='Real Estate Inventory by City';
var sub=el('p','rr-sub');
sub.setAttribute('aria-live','polite');
var groups=el('div','rr-groups');
var buttons=[];
GROUPS.forEach(function(g){
var box=el('div','rr-group');
var lab=el('div','rr-group-label');
lab.textContent=g.label;
var chips=el('div','rr-chips');
g.cats.forEach(function(cat){
var b=el('button','rr-chip');
b.type='button';
b.textContent=LABEL[cat];
b.setAttribute('data-cat',cat);
b.setAttribute('aria-pressed','false');
b.addEventListener('click',function(){update(cat);});
chips.appendChild(b);
buttons.push(b);
});
box.appendChild(lab);
box.appendChild(chips);
groups.appendChild(box);
});
var rows=document.createElement('ol');
rows.className='rr-rows';
var rowByCity={};
data.forEach(function(d){
var li=document.createElement('li');
if(d.name===FLAGSHIP)li.className='rr-flag';
var c=el('span','rr-city');
c.textContent=titleCase(d.name);
var t=el('span','rr-track');
t.setAttribute('aria-hidden','true');
var f=el('span','rr-fill');
t.appendChild(f);
var v=el('span','rr-val');
li.appendChild(c);li.appendChild(t);li.appendChild(v);
rows.appendChild(li);
rowByCity[d.name]={li:li,fill:f,val:v};
});
var note=el('p','rr-note');
note.textContent='Each category is counted from the day\\u0027s MLS export; categories overlap and do not sum. Source: REALTY EXPERTS\\u00AE MLS export, '+(chartMeta.dateLabel||'')+'.';
wrap.appendChild(title);wrap.appendChild(sub);wrap.appendChild(groups);wrap.appendChild(rows);wrap.appendChild(note);
root.appendChild(wrap);
function update(cat){
buttons.forEach(function(b){b.setAttribute('aria-pressed',String(b.getAttribute('data-cat')===cat));});
var list=data.map(function(d,i){return {city:d.name,v:valueOf(d,cat),i:i};}).sort(function(a,b){return b.v-a.v||a.i-b.i;});
var max=1;
list.forEach(function(r){if(r.v>max)max=r.v;});
sub.textContent='All '+data.length+' cities, ranked by '+SUB[cat]+'. Tap a category to re-rank.';
rows.setAttribute('aria-label','Cities ranked by '+LABEL[cat]+' count, highest first');
list.forEach(function(r){
var n=rowByCity[r.city];
n.val.textContent=String(r.v);
n.fill.style.width=(r.v/max*100).toFixed(1)+'%';
rows.appendChild(n.li);
});
}
update('Active All');
})();
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
