#!/usr/bin/env node
/**
 * generate-app-report.js  [--date MM/DD/YY] [--out daily-report.json] [--dry-run]
 *
 * Builds daily-report.json, the HarvRealtor-branded feed read by the HarvRealtor
 * mobile app (Today's Report) and by harvrealtor.net/today. Added 2026-08-21 at
 * Harv's direction: the app must show HIS report in HIS brand, never the REALTY
 * EXPERTS team email, and must never read harvrealtor.com (InCom) for it.
 *
 * Sources, all already produced by the morning run (no new authoring step):
 *   daily-market-template.json   every number + the email commentary (always)
 *   cms-content.json             the HarvRealtor-voice body written for the .com
 *                                blog + its meta description (preferred voice)
 *   live-inventory.json          the five-city ledger counts (same-day only)
 *
 * Voice rule: when cms-content.json is TODAY's (its meta description names the
 * template date) the sections carry that prose. Otherwise the generator falls
 * back to the template commentary (rendered to clean HTML) and prints a loud
 * warning, so a stale or missing cms-content can never silently ship old prose.
 *
 * Publishing: this is a SINGLETON, one file rewritten each run and pushed by
 * push-to-github.sh. Nothing accumulates; the app and the .net page only ever
 * show the latest edition. Git history keeps old versions (a few KB a day).
 *
 * Gates: the file is only written when every gate passes (date shape, both
 * rates numeric, at least three sections with real text, no dashes in any
 * spelling, no REALTY EXPERTS branding in the prose, https-only images and
 * links, headline and teaser present). A failed run exits 1 and leaves
 * yesterday's file alone. Non-https images are dropped with a WARN, not fatal.
 *
 * Freshness: GitHub Pages serves max-age=600 and ignores query strings, and
 * harvrealtor.net/api/daily adds s-maxage=900, so a pushed edition can take up
 * to ~25 minutes to reach every consumer. By design for a daily feed; the app
 * and the page print the edition's date.
 *
 * No dependencies (fs + path only), like the other generators here.
 */

const fs = require('fs');
const path = require('path');
const { TEMPLATE_PATH, GITHUB_PAGES_BASE } = require('./lib/config');

const ROOT = __dirname;
const CMS_CONTENT_PATH = path.join(ROOT, 'cms-content.json');
const LIVE_INVENTORY_PATH = path.join(ROOT, 'live-inventory.json');
const DEFAULT_OUT = path.join(ROOT, 'daily-report.json');

const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'];

// Section order and labels for the app. The .com body uses the same four.
const SECTIONS = [
  { key: 'real_estate', marker: 'REAL ESTATE', label: 'Real estate' },
  { key: 'economy', marker: 'ECONOMY', label: 'Economy' },
  { key: 'stocks', marker: 'STOCKS', label: 'Stocks' },
  { key: 'crypto', marker: 'CRYPTO', label: 'Crypto' },
];

// The one REALTY EXPERTS label inside the .com sources box. The app is the
// HarvRealtor brand, so the ledger is named for where it lives.
const LEDGER_LABEL_RE = /^REALTY\s*EXPERTS\s*®?\s*Live\s+Inventory$/i;
const LEDGER_LABEL = 'Live Inventory ledger, harvrealtor.net';
// The app is the HarvRealtor brand: any other REALTY EXPERTS mention in the
// prose is a hard gate failure (fix the source body, re-run), never a silent ship.
const BRAND_RE = /REALTY\s*EXPERTS/i;

// House style: no em/en dashes, in any spelling (literal, named or numeric entity).
const DASH_RE = /[—–]|&(?:mdash|ndash|#0*(?:8212|8211)|#x0*(?:2014|2013));/i;

// Non-https images are dropped at parse time (both renderers strip them anyway),
// and reported as warnings so the operator sees the bad src.
const PARSE_WARNINGS = [];

// ---------------------------------------------------------------------------
// small helpers
// ---------------------------------------------------------------------------

function parseDate(mmddyy) {
  const m = String(mmddyy || '').match(/^(\d{2})\/(\d{2})\/(\d{2})$/);
  if (!m) throw new Error(`bad date "${mmddyy}" (want MM/DD/YY)`);
  const mm = Number(m[1]), dd = Number(m[2]), year = 2000 + Number(m[3]);
  return {
    slash: mmddyy,
    short: `${m[1]}${m[2]}${m[3]}`,
    iso: `${year}-${m[1]}-${m[2]}`,
    label: `${MONTHS[mm - 1]} ${dd}, ${year}`,
    year,
  };
}

const decode = (s) => String(s == null ? '' : s)
  .replace(/&#(\d+);/g, (_, n) => String.fromCodePoint(Number(n)))
  .replace(/&#x([0-9a-f]+);/gi, (_, h) => String.fromCodePoint(parseInt(h, 16)))
  .replace(/&nbsp;/g, ' ')
  .replace(/&amp;/g, '&')
  .replace(/&lt;/g, '<')
  .replace(/&gt;/g, '>')
  .replace(/&quot;/g, '"')
  .replace(/&#0?39;|&apos;|&rsquo;|&lsquo;/g, "'")
  .replace(/&ldquo;|&rdquo;/g, '"')
  .replace(/&#9650;|&#9660;|[▲▼]/g, '')
  .replace(/&reg;/g, '®');

const stripTags = (html) => decode(String(html || '').replace(/<[^>]+>/g, ' ')).replace(/\s+/g, ' ').trim();

const escapeHtml = (s) => String(s == null ? '' : s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

// Defense in depth at publish time: the app sanitizes again at render time.
function sanitizeHtml(html) {
  return String(html || '')
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/<iframe[\s\S]*?<\/iframe>/gi, '')
    .replace(/<(object|embed|link|meta|style)[^>]*>/gi, '')
    .replace(/\son[a-z]+\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)/gi, '')
    .replace(/(href|src)\s*=\s*("|')\s*javascript:[^"']*("|')/gi, '$1="#"');
}

/** Remove <img> tags whose src is not https (consumers strip them anyway); warn. */
function dropNonHttpsImages(html) {
  return String(html || '').replace(/<img\b[^>]*>/gi, (tag) => {
    const src = (tag.match(/\bsrc="([^"]*)"/i) || [])[1] || '';
    if (/^https:\/\//.test(src)) return tag;
    PARSE_WARNINGS.push(`dropped non-https image: ${src || '(no src)'}`);
    return '';
  });
}

// "7,707 (+0.21%)" -> { value: "7,707", change: "+0.21%" }
function splitValue(v) {
  const s = String(v == null ? '' : v).trim();
  const m = s.match(/^(.*?)\s*\(([^)]*)\)\s*$/);
  return m ? { value: m[1].trim(), change: m[2].trim() } : { value: s, change: null };
}

function dirOfChange(change) {
  if (change == null || change === '') return null;
  const c = String(change).trim();
  if (/^[+-]?0(\.0+)?%?$/.test(c) || /^(unch|flat)/i.test(c)) return 'flat';
  if (/^\+/.test(c)) return 'up';
  if (/^-/.test(c)) return 'down';
  return null;
}

function numOf(s) {
  const n = parseFloat(String(s == null ? '' : s).replace(/[^0-9.+-]/g, ''));
  return Number.isFinite(n) ? n : null;
}

function readJson(p, required) {
  try {
    return JSON.parse(fs.readFileSync(p, 'utf8'));
  } catch (e) {
    if (required) throw new Error(`cannot read ${path.basename(p)}: ${e.message}`);
    return null;
  }
}

// ---------------------------------------------------------------------------
// cms-content.json (HarvRealtor voice) parsing
// ---------------------------------------------------------------------------

/** Does the cms meta description name this date? ("... recap for August 20, 2026: ...") */
function cmsMatchesDate(cms, date) {
  const desc = cms && cms.meta && cms.meta.description ? String(cms.meta.description) : '';
  const m = desc.match(/for\s+([A-Z][a-z]+)\s+(\d{1,2}),\s+(\d{4})/);
  if (!m) return false;
  return `${m[1]} ${Number(m[2])}, ${m[3]}` === date.label;
}

/** Split the .com body on its <!-- SECTION --> markers. */
function splitCmsSections(html) {
  const out = {};
  const re = /<!--\s*([A-Z ]+?)\s*-->/g;
  const marks = [];
  let m;
  while ((m = re.exec(html))) marks.push({ name: m[1].trim(), start: m.index, end: m.index + m[0].length });
  for (let i = 0; i < marks.length; i++) {
    const from = marks[i].end;
    const to = i + 1 < marks.length ? marks[i + 1].start : html.length;
    out[marks[i].name] = html.slice(from, to);
  }
  return out;
}

/** "30-Year Fixed: <strong>6.76%</strong> <span class="up">&#9650; 0.04%</span> | ..." -> stats[] */
function parseStatLine(inner) {
  const chunks = String(inner).split(/&nbsp;\|&nbsp;|\s\|\s/);
  const stats = [];
  for (const chunk of chunks) {
    const mm = chunk.match(/^\s*(.*?):\s*<strong>([\s\S]*?)<\/strong>\s*(?:<span class="(up|down|flat)">([\s\S]*?)<\/span>)?/);
    if (!mm) continue;
    const label = stripTags(mm[1]);
    const value = stripTags(mm[2]);
    const dir = mm[3] || null;
    let change = mm[4] != null ? stripTags(mm[4]) : null;
    if (change) {
      change = change.replace(/^[+-]/, '');
      if (dir === 'up') change = `+${change}`;
      else if (dir === 'down') change = `-${change}`;
    }
    if (label && value) stats.push({ label, value, change: change || null, dir });
  }
  return stats;
}

function parseCmsSection(raw) {
  let html = String(raw || '');
  const bar = html.match(/<div class="section-bar-[a-z]+">([\s\S]*?)<\/div>/);
  if (bar) html = html.replace(bar[0], '');
  const stat = html.match(/<p class="stat-line">([\s\S]*?)<\/p>/);
  const stats = stat ? parseStatLine(stat[1]) : [];
  if (stat) html = html.replace(stat[0], '');
  html = html.replace(/<hr\s*\/?>\s*$/i, '').trim();
  // Block-first: match each <figure>...</figure>, then read img + figcaption
  // inside it (a single lazy regex silently dropped every caption).
  const images = [];
  const figBlock = /<figure[^>]*>[\s\S]*?<\/figure>/g;
  let b;
  while ((b = figBlock.exec(html))) {
    const img = b[0].match(/<img[^>]*src="([^"]+)"[^>]*alt="([^"]*)"/);
    if (!img) continue;
    const cap = b[0].match(/<figcaption[^>]*>([\s\S]*?)<\/figcaption>/);
    images.push({ url: img[1], alt: decode(img[2]), caption: cap ? stripTags(cap[1]) : null });
  }
  html = dropNonHttpsImages(html);
  const kept = images.filter((i) => /^https:\/\//.test(i.url));
  return { stats, html: sanitizeHtml(html), images: kept, text: stripTags(html) };
}

function parseCmsSources(raw) {
  const out = [];
  const liRe = /<li>\s*<a href="([^"]+)"[^>]*>([\s\S]*?)<\/a>\s*([\s\S]*?)<\/li>/g;
  let m;
  while ((m = liRe.exec(String(raw || '')))) {
    let label = stripTags(m[2]);
    if (LEDGER_LABEL_RE.test(label)) label = LEDGER_LABEL;
    const note = stripTags(m[3]).replace(/^\(|\)$/g, '').trim() || null;
    out.push({ label, url: m[1], note });
  }
  return out;
}

function parseCmsDisclaimer(raw) {
  const m = String(raw || '').match(/<blockquote class="disclaimer">([\s\S]*?)<\/blockquote>/);
  if (!m) return null;
  return stripTags(m[1]).replace(/^Disclaimer:\s*/i, '');
}

/** "Daily Bay Area housing recap for August 20, 2026: mortgage rates ..." -> "Mortgage rates ..." */
function teaserFromDescription(desc) {
  const s = String(desc || '').replace(/^Daily [^:]*:\s*/, '').trim();
  return s ? s.charAt(0).toUpperCase() + s.slice(1) : null;
}

// ---------------------------------------------------------------------------
// template fallback (the email commentary, rendered to clean semantic HTML)
// ---------------------------------------------------------------------------

function commentaryToHtml(text) {
  if (!text) return '';
  const paras = String(text).split('\n\n');
  const out = [];
  for (const para of paras) {
    const t = para.trim();
    if (!t) continue;
    if (t.includes('•') || t.startsWith('📍')) {
      const lines = t.split('\n').map((l) => l.trim()).filter(Boolean);
      let list = [];
      const flush = () => { if (list.length) { out.push(`<ul>${list.join('')}</ul>`); list = []; } };
      for (const line of lines) {
        if (line.startsWith('•')) {
          const body = line.replace(/^•\s*/, '');
          const cm = body.match(/^([^:]+):(.*)$/s);
          list.push(cm ? `<li><strong>${escapeHtml(cm[1].trim())}:</strong>${escapeHtml(cm[2])}</li>` : `<li>${escapeHtml(body)}</li>`);
        } else if (line.startsWith('📍')) {
          flush();
          const body = line.replace(/^📍\s*/, '');
          const cm = body.match(/^([^:]+):(.*)$/s);
          if (cm) list.push(`<li><strong>${escapeHtml(cm[1].trim())}:</strong>${escapeHtml(cm[2])}</li>`);
          else out.push(`<h4>${escapeHtml(body)}</h4>`);
        } else if (line.endsWith(':')) {
          flush();
          out.push(`<p><strong>${escapeHtml(line)}</strong></p>`);
        } else {
          flush();
          out.push(`<p>${escapeHtml(line)}</p>`);
        }
      }
      flush();
    } else if (t.endsWith(':')) {
      out.push(`<p><strong>${escapeHtml(t)}</strong></p>`);
    } else {
      out.push(`<p>${escapeHtml(t)}</p>`);
    }
  }
  return out.join('\n');
}

function imagesOf(section) {
  const arr = Array.isArray(section.feature_images) ? section.feature_images
    : (section.feature_image ? [section.feature_image] : []);
  return arr.filter((i) => i && i.url).filter((i) => {
    if (/^https:\/\//.test(String(i.url))) return true;
    PARSE_WARNINGS.push(`dropped non-https image: ${i.url}`);
    return false;
  }).map((i) => ({
    url: i.url, alt: i.alt || '', caption: i.caption || null, source: i.source || null,
  }));
}

function figuresHtml(images) {
  return images.map((i) =>
    `<figure><img src="${escapeHtml(i.url)}" alt="${escapeHtml(i.alt)}" loading="lazy" />` +
    (i.caption || i.source ? `<figcaption>${escapeHtml([i.caption, i.source].filter(Boolean).join(' '))}</figcaption>` : '') +
    `</figure>`).join('\n');
}

function templateSections(t) {
  const mk = (key, label, stats, text, section) => {
    const images = imagesOf(section || {});
    const html = sanitizeHtml(commentaryToHtml(text) + (images.length ? '\n' + figuresHtml(images) : ''));
    return { key, label, stats, html, images, text: stripTags(html) };
  };
  const re = t.real_estate || {}, ec = t.economy || {}, st = t.stocks || {}, cr = t.crypto || {};
  const sv = (label, raw) => { const { value, change } = splitValue(raw); return { label, value, change, dir: dirOfChange(change) }; };
  const ecStats = [sv('US 10-Year', ec.us10year), sv(ec.gold_label || 'Gold', ec.gold), sv(ec.silver_label || 'Silver', ec.silver)];
  if (ec.wti) ecStats.push(sv(ec.oil_label || 'Oil', ec.wti));
  else if (ec.cpi) ecStats.push(sv(ec.cpi_label || 'CPI', ec.cpi));
  return [
    mk('real_estate', 'Real estate',
      [{ label: '30-Year Fixed', value: String(re.rate_30year || ''), change: null, dir: null },
       { label: '15-Year Fixed', value: String(re.rate_15year || ''), change: null, dir: null }],
      re.commentary, re),
    mk('economy', 'Economy', ecStats.filter((s) => s.value), ec.commentary, ec),
    mk('stocks', 'Stocks', [sv('S&P 500', st.sp500), sv('DOW', st.dow), sv('NASDAQ', st.nasdaq)].filter((s) => s.value), st.news, st),
    mk('crypto', 'Crypto', [sv('BTC', cr.btc), sv('ETH', cr.eth), sv('XRP', cr.xrp)].filter((s) => s.value), cr.commentary, cr),
  ];
}

function templateSources(t) {
  return (Array.isArray(t.sources) ? t.sources : []).map((s) => {
    const str = String(s);
    if (/^https?:\/\//.test(str)) {
      let label = str;
      try { label = new URL(str).hostname.replace(/^www\./, ''); } catch (_) { /* keep */ }
      return { label, url: str, note: null };
    }
    return { label: str, url: null, note: null };
  });
}

// ---------------------------------------------------------------------------
// numbers that always come from the template / live feed
// ---------------------------------------------------------------------------

function boardFromText(text) {
  const s = String(text || '');
  // "Board wide: N active ..." was the original phrasing. Since 08/26/26 the copy says
  // "Board wide: N listings ...", because N is active PLUS in contract and calling it
  // active alone was wrong. Accept either. (The board.active FIELD name in the app
  // contract still carries that same total; renaming it is an app side change.)
  const active = s.match(/Board wide:\s*([\d,]+)\s+(?:active|listings)/i) || s.match(/carrying\s+(?:<strong>)?([\d,]+)(?:<\/strong>)?\s+active/i);
  const cs = s.match(/(\d[\d,]*)\s+coming soon/i);
  const nw = s.match(/(\d[\d,]*)\s+brand new/i) || s.match(/(\d[\d,]*)\s+new today/i);
  if (!active) return null;
  return {
    active: numOf(active[1]),
    comingSoon: cs ? numOf(cs[1]) : null,
    newToday: nw ? numOf(nw[1]) : null,
  };
}

function localFromLiveInventory(live, date) {
  if (!live || live.date !== date.slash || !live.counts) return null;
  const cities = Object.entries(live.counts).map(([city, c]) => ({
    city,
    total: c.total || 0,
    active: c.ACTV || 0,
    new: c.NEW || 0,
    comingSoon: c.CS || 0,
    backOnMarket: c.BOMK || 0,
  })).sort((a, b) => b.total - a.total || a.city.localeCompare(b.city));
  const total = cities.reduce((n, c) => n + c.total, 0);
  return { date: live.date, total, cities, source: 'live-inventory.json' };
}

function localFromCms(html, date) {
  const cities = [];
  const re = /<li>\s*<strong>([A-Za-z ]+):<\/strong>\s*([\d,]+)\s+available\s*\(([\d,]+)\s+active,\s*([\d,]+)\s+new,\s*([\d,]+)\s+coming soon\)/g;
  let m;
  while ((m = re.exec(String(html || '')))) {
    cities.push({ city: m[1].trim(), total: numOf(m[2]), active: numOf(m[3]), new: numOf(m[4]), comingSoon: numOf(m[5]), backOnMarket: null });
  }
  if (!cities.length) return null;
  cities.sort((a, b) => b.total - a.total);
  return { date: date.slash, total: cities.reduce((n, c) => n + (c.total || 0), 0), cities, source: 'cms-content.json' };
}

function localFromTemplate(text, date) {
  const s = String(text || '');
  const m = s.match(/Live ledger:[^.]*?([\d,]+)\s+listings\.\s*([^\n]*)/i);
  if (!m) return null;
  const cities = [];
  const re = /([A-Z][A-Za-z ]+?)\s+([\d,]+)(?=,| and|\.|$)/g;
  let c;
  while ((c = re.exec(m[2]))) cities.push({ city: c[1].trim(), total: numOf(c[2]), active: null, new: null, comingSoon: null, backOnMarket: null });
  return { date: date.slash, total: numOf(m[1]), cities, source: 'daily-market-template.json' };
}

// ---------------------------------------------------------------------------
// build
// ---------------------------------------------------------------------------

function build({ template, cms, live, date }) {
  const warnings = [];
  PARSE_WARNINGS.length = 0;
  const re = template.real_estate || {};

  const cmsFresh = !!(cms && cms.newsletter_html && cmsMatchesDate(cms, date));
  let voice, sections = [], sources, disclaimer;

  if (cmsFresh) {
    const parts = splitCmsSections(cms.newsletter_html);
    sections = SECTIONS.map((s) => {
      const raw = parts[s.marker];
      if (!raw) return null;
      const p = parseCmsSection(raw);
      return { key: s.key, label: s.label, stats: p.stats, html: p.html, images: p.images, text: p.text };
    }).filter(Boolean);
    sources = parseCmsSources(parts.SOURCES);
    disclaimer = parseCmsDisclaimer(parts.SOURCES || cms.newsletter_html);
    voice = 'harv';
    if (sections.length < 3) {
      warnings.push(`cms-content.json parsed into only ${sections.length} sections; falling back to the template`);
    }
  }
  if (!cmsFresh || sections.length < 3) {
    if (!cmsFresh) {
      warnings.push(cms
        ? `cms-content.json is NOT ${date.label} (meta says "${String((cms.meta || {}).description || '').slice(0, 60)}..."); using template commentary`
        : 'cms-content.json missing; using template commentary');
    }
    sections = templateSections(template);
    sources = templateSources(template);
    disclaimer = 'The market data, rates, and information provided are for informational purposes only and should not be considered financial advice. Always verify rates and data with your lender or financial advisor before making any decisions.';
    voice = 'template';
  }

  // Rates: the number from the template, the day's change from the .com stat
  // line when today's body is available (the template carries no change).
  const reStats = (sections.find((s) => s.key === 'real_estate') || {}).stats || [];
  const s30 = reStats.find((s) => /30/.test(s.label)) || {};
  const s15 = reStats.find((s) => /15/.test(s.label)) || {};
  const rates = {
    r30: numOf(re.rate_30year),
    r30Change: s30.change != null ? numOf(s30.change) : null,
    r15: numOf(re.rate_15year),
    r15Change: s15.change != null ? numOf(s15.change) : null,
    source: 'Mortgage News Daily',
    sourceUrl: 'https://www.mortgagenewsdaily.com/mortgage-rates',
  };

  const board = boardFromText(re.commentary) || (cmsFresh ? boardFromText(cms.newsletter_html) : null);
  if (!board) warnings.push('board totals not found in the commentary; board omitted');

  const local = localFromLiveInventory(live, date)
    || (cmsFresh ? localFromCms(cms.newsletter_html, date) : null)
    || localFromTemplate(re.commentary, date);
  if (!local) warnings.push('five-city ledger not found; local omitted');
  else if (local.source !== 'live-inventory.json') warnings.push(`five-city ledger came from ${local.source} (live-inventory.json is not ${date.slash})`);

  const teaser = (cmsFresh && teaserFromDescription(cms.meta.description))
    || stripTags(commentaryToHtml(String(re.commentary || '').split('\n\n')[0])) || null;

  const headline = String(re.homebuilder || '').trim() || null;

  const allImages = sections.flatMap((s) => s.images);
  warnings.push(...PARSE_WARNINGS);

  const payload = {
    version: 1,
    brand: 'HarvRealtor',
    name: "Today's Report",
    date: date.slash,
    dateISO: date.iso,
    dateLabel: date.label,
    time: template.time || null,
    generatedAt: new Date().toISOString(),
    voice,
    headline,
    teaser,
    rates,
    board,
    local,
    sections,
    images: allImages,
    sources,
    links: {
      web: 'https://harvrealtor.net/today',
      blog: `https://www.harvrealtor.com/HarvRealtor-daily-market-glance-${date.short}`,
      liveInventory: 'https://harvrealtor.net/live-inventory',
      glance: `${GITHUB_PAGES_BASE}/daily-market-glance-${date.short}.html`,
    },
    disclaimer,
  };
  return { payload, warnings };
}

// ---------------------------------------------------------------------------
// gates
// ---------------------------------------------------------------------------

function validate(p) {
  const errs = [];
  if (!/^\d{2}\/\d{2}\/\d{2}$/.test(p.date)) errs.push(`date "${p.date}" malformed`);
  if (!(p.rates.r30 > 2 && p.rates.r30 < 12)) errs.push(`30-year rate ${p.rates.r30} out of range`);
  if (!(p.rates.r15 > 2 && p.rates.r15 < 12)) errs.push(`15-year rate ${p.rates.r15} out of range`);
  if (!p.headline) errs.push('headline missing');
  if (!p.teaser || p.teaser.length < 40) errs.push('teaser missing or too short');
  if (p.sections.length < 3) errs.push(`only ${p.sections.length} sections`);
  for (const s of p.sections) {
    if (!s.text || s.text.length < 80) errs.push(`section ${s.key} has too little text (${(s.text || '').length} chars)`);
    if (/<script|onerror=|onload=|javascript:/i.test(s.html)) errs.push(`section ${s.key} failed sanitization`);
  }
  // House style: no em or en dashes anywhere in prose (URLs excluded).
  const walk = (v, where) => {
    if (typeof v === 'string') {
      if (/^https?:\/\//.test(v)) return;
      if (DASH_RE.test(v)) errs.push(`dash in ${where}`);
      if (BRAND_RE.test(v)) errs.push(`REALTY EXPERTS branding in ${where} (the app is the HarvRealtor brand; fix the source body)`);
    } else if (Array.isArray(v)) v.forEach((x, i) => walk(x, `${where}[${i}]`));
    else if (v && typeof v === 'object') Object.entries(v).forEach(([k, x]) => walk(x, `${where}.${k}`));
  };
  walk({ headline: p.headline, teaser: p.teaser, sections: p.sections, sources: p.sources, disclaimer: p.disclaimer }, 'report');
  if (p.local && p.local.cities.length && p.local.total !== p.local.cities.reduce((n, c) => n + (c.total || 0), 0)) {
    errs.push('local.total does not equal the sum of city totals');
  }
  // Parity with the consumers (app isReport, .net isDailyReport): they refuse the
  // WHOLE edition on any non-https image or link, so refuse it here, loudly.
  for (const s of p.sections) {
    for (const im of s.images || []) {
      if (!/^https:\/\//.test(String(im.url || ''))) errs.push(`section ${s.key} image url is not https: ${im.url}`);
    }
  }
  for (const k of ['web', 'blog', 'liveInventory']) {
    if (!/^https:\/\//.test(String((p.links || {})[k] || ''))) errs.push(`links.${k} is not https`);
  }
  return errs;
}

// ---------------------------------------------------------------------------
// CLI
// ---------------------------------------------------------------------------

function main() {
  const argv = process.argv.slice(2);
  const opt = (name) => { const i = argv.indexOf(name); return i >= 0 ? argv[i + 1] : undefined; };
  const dryRun = argv.includes('--dry-run');
  const out = opt('--out') || DEFAULT_OUT;

  const template = readJson(TEMPLATE_PATH, true);
  const date = parseDate(opt('--date') || template.date);
  if (template.date !== date.slash) {
    console.error(`template date ${template.date} != requested ${date.slash}; refusing (the template IS the day)`);
    process.exit(1);
  }
  const cms = readJson(CMS_CONTENT_PATH, false);
  const live = readJson(LIVE_INVENTORY_PATH, false);

  const { payload, warnings } = build({ template, cms, live, date });
  const errs = validate(payload);

  for (const w of warnings) console.warn(`WARN ${w}`);
  if (errs.length) {
    console.error('GATE FAILED, not writing:');
    for (const e of errs) console.error(`  - ${e}`);
    process.exit(1);
  }

  const json = JSON.stringify(payload);
  if (dryRun) {
    console.log(`[dry-run] daily-report.json for ${payload.date}: voice=${payload.voice}, ${payload.sections.length} sections, ${payload.images.length} images, ${payload.sources.length} sources, ${json.length} bytes`);
    console.log(JSON.stringify({ ...payload, sections: payload.sections.map((s) => ({ ...s, html: `[${s.html.length} chars]`, text: `[${s.text.length} chars]` })) }, null, 2));
    return;
  }
  const tmp = out + '.tmp';
  fs.writeFileSync(tmp, json);
  fs.renameSync(tmp, out);
  console.log(`wrote ${path.basename(out)} for ${payload.date}: voice=${payload.voice}, ${payload.sections.length} sections, ${payload.images.length} images, ${payload.sources.length} sources, ${json.length} bytes${warnings.length ? `, ${warnings.length} warning(s)` : ''}`);
}

if (require.main === module) {
  try { main(); } catch (e) { console.error(`Error: ${e.message}`); process.exit(1); }
}

module.exports = { build, validate, parseDate, splitCmsSections, parseStatLine, commentaryToHtml };
