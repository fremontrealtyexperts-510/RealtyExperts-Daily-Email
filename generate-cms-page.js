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
// LEGACY (pre-2026-07-19 Plotly grouped-bar era): 12-series categorical palette
// and the default-visible city set. The ranked-bar chart uses a single gold and
// shows all 12 cities, so nothing here reads these any more — kept only because
// they are exported and the values document the old design. Do not re-adopt the
// 12-color map: three golds / two sages / two slates are not distinguishable.
const COLORS = {
  'Fremont': '#B08C1E', 'Union City': '#3E5C76', 'Castro Valley': '#6E7B5B',
  'Danville': '#9C6B4A', 'Hayward': '#7E5A73', 'Livermore': '#C9A227',
  'Newark': '#4E7C6E', 'Pleasanton': '#A65A44', 'San Ramon': '#5B7551',
  'Dublin': '#4A6E8A', 'San Leandro': '#8A6D3B', 'Milpitas': '#2E6E6A',
};
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
 * Parse RE-v2 rows into the chart cities. RE-v2 columns (the per-city "Total"
 * column was removed in the 2026-07-10 table redesign, so All CS / All New moved
 * left by one — indices below reflect the CURRENT layout):
 * [City, TH-Active, TH-Pend, CO-Active, CO-Pend, DU/DE/PH-Active, DU/DE/PH-Pend, All CS, All New]
 * Chart cats map: CO=CO-Active, DE=DU/DE/PH-Active, TH=TH-Active,
 *   Active All = TH+CO+DE actives, New=All New, CS=All CS, PEND = sum of the three pendings.
 * Pure (no IO) so it is unit-testable. Returns [{city, values:[...CATS]}] in CITY_ORDER.
 */
function parseRev2(rows) {
  if (!rows || rows.length < 2) throw new Error('RE-v2 returned no data rows');
  // Locate the "All CS" / "All New" columns by header name rather than a fixed
  // index: those two shift whenever a summary column (e.g. the per-city Total,
  // dropped 2026-07-10) is added/removed. Fail loudly if they are gone so the
  // chart never again silently renders New=0. The six type columns (1..6) keep
  // their stable positions.
  const header = (rows[0] || []).map(h => String(h || '').trim().toLowerCase());
  const csIdx = header.findIndex(h => h.includes('all cs'));
  const nwIdx = header.findIndex(h => h.includes('all new'));
  if (csIdx === -1 || nwIdx === -1) {
    throw new Error(`RE-v2 header missing "All CS"/"All New" (got: ${(rows[0] || []).join(' | ')})`);
  }
  const byCity = {};
  for (const row of rows.slice(1)) {
    const city = String(row[0] || '').trim();
    if (!city) continue;
    const n = i => parseInt(row[i], 10) || 0;
    const th = n(1), thp = n(2), co = n(3), cop = n(4), de = n(5), dep = n(6), cs = n(csIdx), nw = n(nwIdx);
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

function chartInnerJs(inventory, dateLabel) {
  // ── DATA CONTRACT (do not change the shape) ──────────────────────────────
  // verify-cms-publish.js regex-parses this file: it splits on `var baseLayout`
  // and requires `var data = [...]` (each series {name, x, y}, the legacy Plotly
  // trace shape) to be the LAST statement before it. That parse feeds the Stage 5
  // value-check that cross-checks every plotted number against an independent
  // RE-v2 read (the gate that caught the silent all-zero "New" column, 07-17).
  // Rendering below is free to change; the first two statements are not.
  const traces = inventory.map(({ city, values }) => ({ name: city, x: CATS, y: values }));
  // Emitted to an EXTERNAL .js file (alameda-chart-MMDDYY.js) and referenced via
  // <script src>. Drupal strips INLINE <script> from the node body but keeps
  // external src tags — so the chart only renders when its code lives in a
  // hosted file. No HTML-escaping needed here (the file is never HTML-filtered).
  // Since 2026-07-19 the chart is SELF-RENDERING (no Plotly): a category picker
  // plus all 12 cities as ranked horizontal bars with the count printed on every
  // row. That removes the 1.09MB Plotly payload, the touch scroll trap
  // (dragmode zoom), the hover-only values, and the 12-entry legend in one move.
  // All DOM is built with createElement/textContent (no HTML parsing of data).
  // The chart is ALWAYS light (white paper): the report embeds in the light InCom
  // page, so a prefers-color-scheme dark chart reads as broken there (2026-07-06).
  // The click-to-enlarge lightbox for NEWSLETTER images also lives here for the
  // same strip-inline reason — it is not part of the chart; keep it.
  return `var data = ${JSON.stringify(traces)};
var baseLayout = {};
var chartMeta = ${JSON.stringify({ dateLabel: dateLabel || '' })};
(function(){
var root=document.getElementById('chart');
if(!root)return;
var LABEL={'Active All':'Active All','New':'New','CS':'Coming Soon','PEND':'Pending','DE':'Detached','CO':'Condo','TH':'Townhouse'};
var SUB={'Active All':'total active listings','New':'new listings','CS':'coming soon listings','PEND':'pending sales','DE':'active detached homes','CO':'active condos','TH':'active townhouses'};
var GROUPS=[{label:'Market status',cats:['Active All','New','CS','PEND']},{label:'Active by home type',cats:['DE','CO','TH']}];
var FLAGSHIP='Fremont';
var css=''+
'#chart .rr-wrap{max-width:640px;margin:0 auto;}'+
'#chart .rr-title{font-family:var(--serif,Georgia,serif);font-size:19px;font-weight:700;color:var(--ink,#2E2E2E);text-align:center;margin:8px 0 2px;letter-spacing:-0.01em;}'+
'#chart .rr-sub{font-family:var(--sans,Arial,sans-serif);font-size:12.5px;color:var(--muted,#6B6459);text-align:center;margin:0 0 14px;}'+
'#chart .rr-groups{display:flex;flex-wrap:wrap;gap:10px 26px;justify-content:center;margin:0 0 16px;}'+
'#chart .rr-group-label{font-family:var(--sans,Arial,sans-serif);font-size:10px;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:var(--muted,#6B6459);margin:0 0 6px;}'+
'#chart .rr-chips{display:flex;flex-wrap:wrap;gap:8px;}'+
'#chart .rr-chip{min-height:44px;padding:10px 14px;border-radius:9px;border:1px solid var(--hairline,#E8E4DA);background:#FFFFFF;color:var(--ink-soft,#4A4640);font-family:var(--sans,Arial,sans-serif);font-size:13px;font-weight:600;line-height:1.15;cursor:pointer;}'+
'#chart .rr-chip[aria-pressed="true"]{background:var(--gold,#D4AF37);border-color:var(--gold-dark,#B08C1E);color:#2E2E2E;font-weight:700;}'+
'#chart .rr-chip:focus-visible{outline:2px solid var(--gold-dark,#B08C1E);outline-offset:2px;}'+
'#chart .rr-rows{list-style:none;margin:0;padding:0;}'+
'#chart .rr-rows li{display:grid;grid-template-columns:100px 1fr 46px;gap:8px;align-items:center;min-height:29px;padding:0;margin:0;}'+
'#chart .rr-city{font-family:var(--sans,Arial,sans-serif);font-size:12px;color:var(--ink-soft,#4A4640);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;text-align:left;}'+
'#chart li.rr-flag .rr-city{font-weight:700;color:var(--ink,#2E2E2E);}'+
'#chart .rr-track{height:16px;background:var(--track,#F2EFE7);border-radius:3px;overflow:hidden;}'+
'#chart .rr-fill{display:block;height:100%;width:0;background:var(--gold-dark,#B08C1E);border-radius:3px;transition:width 0.32s cubic-bezier(0.22,1,0.36,1);}'+
'#chart li.rr-flag .rr-fill{background:var(--gold,#D4AF37);box-shadow:inset 0 0 0 1px var(--gold-dark,#B08C1E);}'+
'#chart .rr-val{font-family:var(--serif,Georgia,serif);font-size:14px;font-weight:600;color:var(--ink,#2E2E2E);text-align:right;font-variant-numeric:tabular-nums;}'+
'#chart .rr-note{font-family:var(--sans,Arial,sans-serif);font-size:11.5px;color:var(--muted,#6B6459);line-height:1.55;margin:16px auto 4px;max-width:560px;text-align:center;}'+
'@media (max-width:599px){#chart .rr-rows li{grid-template-columns:88px 1fr 40px;}#chart .rr-groups{justify-content:flex-start;gap:12px 18px;}}'+
'@media (prefers-reduced-motion:reduce){#chart .rr-fill{transition:none;}}';
function el(tag,cls){var n=document.createElement(tag);if(cls)n.className=cls;return n;}
function valueOf(series,cat){var i=series.x.indexOf(cat);return i>=0?(Number(series.y[i])||0):0;}
while(root.firstChild){root.removeChild(root.firstChild);}
var style=document.createElement('style');
style.textContent=css;
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
c.textContent=d.name;
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
note.textContent='Active All is Detached plus Condo plus Townhouse. Pending and Coming Soon are counted separately. Source: REALTY EXPERTS\\u00AE MLS export, '+(chartMeta.dateLabel||'')+'.';
wrap.appendChild(title);wrap.appendChild(sub);wrap.appendChild(groups);wrap.appendChild(rows);wrap.appendChild(note);
root.appendChild(style);root.appendChild(wrap);
function update(cat){
buttons.forEach(function(b){b.setAttribute('aria-pressed',String(b.getAttribute('data-cat')===cat));});
var list=data.map(function(d,i){return {city:d.name,v:valueOf(d,cat),i:i};}).sort(function(a,b){return b.v-a.v||a.i-b.i;});
var max=1;
list.forEach(function(r){if(r.v>max)max=r.v;});
sub.textContent='All 12 cities, ranked by '+SUB[cat]+'. Tap a category to re-rank.';
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
(function(){
var open=null;
function close(){if(open){if(open.parentNode){open.parentNode.removeChild(open);}open=null;document.body.style.overflow='';}}
function show(src,alt){close();var o=document.createElement('div');o.className='re-lightbox';o.setAttribute('role','dialog');o.setAttribute('aria-modal','true');o.setAttribute('aria-label',alt||'Enlarged image');var im=document.createElement('img');im.src=src;im.alt=alt||'';var x=document.createElement('span');x.className='re-lightbox-close';x.setAttribute('aria-hidden','true');x.textContent='\\u00D7';o.appendChild(im);o.appendChild(x);document.body.appendChild(o);document.body.style.overflow='hidden';open=o;}
document.addEventListener('click',function(e){if(open){var t=e.target;if(t===open||(t&&t.className&&String(t.className).indexOf('re-lightbox-close')>-1)){close();}return;}var t2=e.target;if(t2&&t2.tagName==='IMG'&&t2.closest&&t2.closest('.newsletter-container')){e.preventDefault();show(t2.currentSrc||t2.src,t2.alt);}});
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
        .re-report #chart { background: var(--card); border: 1px solid var(--hairline); border-radius: 14px; box-shadow: 0 1px 3px rgba(46,46,46,0.04), 0 14px 34px -22px rgba(46,46,46,0.20); padding: 14px; max-width: 1000px; margin: 0 auto; min-height: 560px; }
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
        .re-lightbox-close { position: fixed; top: 8px; top: max(8px, env(safe-area-inset-top)); right: 10px; padding: 12px 14px; color: #fff; font: 700 36px/1 Arial, sans-serif; cursor: pointer; }
        @media (max-width: 900px) { .re-report .newsletter-container { max-width: 100%; padding: 28px 22px; } }
        @media (max-width: 600px) { .re-report { font-size: 15.5px; } .re-report #chart { padding: 8px; border-radius: 12px; } .re-report .newsletter-container { padding: 22px 16px; border-radius: 12px; } .re-report .stat-line { padding: 13px 14px; font-size: 14px; } .re-report .stat-line strong { font-size: 17px; } .re-lightbox { padding: 12px; } }
</style>`;

/** Assemble the full standalone CMS page. `newsletterInner` is the inner HTML of .newsletter-container. */
function buildCmsHtml({ dateLabel, chartSrc, newsletterInner, pageTitle = '', description = '' }) {
  // Attribute-safe escape for the head meta. NOTE: no inline <script> (e.g.
  // JSON-LD) may go in this document — Drupal strips inline scripts and truncates
  // everything after the first one, which would eat the newsletter. og/twitter
  // are <meta> tags (safe); Drupal owns the canonical SEO via the cms-meta sidecar.
  // The whole head prelude is emitted as ONE line: Drupal's line-break filter
  // turns every newline into a <br />, and a stack of ~10 breaks from invisible
  // meta tags rendered as a big empty gap under the page title (2026-07-06).
  const esc = s => String(s || '').replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const t = esc(pageTitle), d = esc(description);
  // No Plotly since 2026-07-19 — the chart JS is self-rendering (ranked bars),
  // which drops ~1.09MB of render-blocking library from every page view.
  return `<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>${t}</title><meta name="description" content="${d}"><meta property="og:type" content="article"><meta property="og:title" content="${t}"><meta property="og:description" content="${d}"><meta property="og:site_name" content="REALTY EXPERTS&reg;"><meta name="twitter:card" content="summary"><meta name="twitter:title" content="${t}"><meta name="twitter:description" content="${d}">${STYLE_BLOCK}
<div class="re-report">
<div class="date-badge"><span>${dateLabel} &middot; Alameda County Market Dashboard</span></div>
<div class="info-banner"><strong>Tip:</strong> Tap a category to re-rank all 12 cities &bull; Every count is printed on its bar &bull; Tap any chart image below to enlarge</div>
<div id="chart">&nbsp;</div>
<div style="max-width:760px;margin:22px auto 0;background:var(--card);border:1px solid var(--hairline);border-left:3px solid var(--gold);border-radius:12px;padding:20px 24px;">
<div style="font-size:11px;font-weight:700;letter-spacing:2.2px;color:#B08C1E;margin-bottom:8px;">TODAY'S LIVE INVENTORY</div>
<div style="font-size:14.5px;line-height:1.6;color:var(--ink-soft);margin-bottom:12px;">Behind these county totals: <strong id="hb-li-total" style="color:var(--ink);">hundreds of</strong> homes still for sale in <strong>Fremont, Hayward, Union City, Newark and Milpitas</strong>, one live ledger with prices, sizes and a market read, refreshed each morning from the same MLS export.</div>
<a href="https://harvrealtor.net/live-inventory?utm_source=harvrealtor.com&amp;utm_medium=referral&amp;utm_campaign=com-crosslink&amp;utm_content=daily-post-live-inventory" style="display:inline-block;background:var(--gold);color:var(--ink);font-weight:700;text-decoration:none;padding:13px 20px;border-radius:8px;font-size:14px;">Browse the live ledger &rarr;</a>
</div>
<div class="newsletter-container">
${newsletterInner}</div>
</div>
<script src="${chartSrc}"></script>
<script src="${GITHUB_PAGES_BASE}/live-inventory-teaser.js"></script>
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
  fs.writeFileSync(chartJsPath, chartInnerJs(inv, label));
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
