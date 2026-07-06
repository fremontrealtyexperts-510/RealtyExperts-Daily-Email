/**
 * HTML building blocks for Agent Hub posts.
 * Dark-mode-safe white card layout with colored header bars.
 */

// --- Text formatting utilities (shared with generate-daily-email.js) ---

function formatCommentary(text) {
  if (!text) return '';
  const paragraphs = text.split('\n\n');

  return paragraphs.map(para => {
    if (para.includes('\u2022')) {
      const lines = para.split('\n');
      let html = '';
      lines.forEach(line => {
        const trimmed = line.trim();
        if (trimmed.startsWith('\u2022')) {
          const colonMatch = trimmed.match(/^\u2022 ([^:]+):(.*)/);
          if (colonMatch) {
            html += `<div style="margin: 10px 0 6px 0; line-height: 1.8;"><strong style="color: #1e293b;">\u2022 ${colonMatch[1]}:</strong>${colonMatch[2]}</div>`;
          } else {
            html += `<div style="margin: 6px 0; padding-left: 0; line-height: 1.8;">${trimmed}</div>`;
          }
        } else if (trimmed.startsWith('\ud83d\udccd')) {
          html += `<div style="margin: 20px 0 12px 0; font-weight: 700; font-size: 16px; line-height: 1.6; color: #1e293b;">${trimmed}</div>`;
        } else if (trimmed.startsWith('o ')) {
          html += `<div style="margin: 6px 0; padding-left: 20px; line-height: 1.8; color: #334155;">${trimmed}</div>`;
        } else if (trimmed) {
          if (trimmed.endsWith(':')) {
            html += `<div style="margin: 0 0 10px 0; line-height: 1.8; font-weight: 700; color: #1e293b;">${trimmed}</div>`;
          } else {
            html += `<div style="margin: 10px 0; line-height: 1.8; font-weight: 600;">${trimmed}</div>`;
          }
        }
      });
      return html;
    } else {
      const trimmed = para.trim();
      if (trimmed.startsWith('\ud83d\udccd')) {
        return `<div style="margin: 20px 0 12px 0; font-weight: 700; font-size: 16px; line-height: 1.6; color: #1e293b;">${trimmed}</div>`;
      } else if (trimmed.endsWith(':')) {
        return `<div style="margin: 0 0 10px 0; line-height: 1.8; font-weight: 700; color: #1e293b;">${trimmed}</div>`;
      }
      return `<div style="margin: 0 0 16px 0; line-height: 1.8;">${trimmed}</div>`;
    }
  }).join('');
}

function addArrow(value) {
  if (value.includes('+')) return '\u25b2 ' + value;
  if (value.includes('-')) return '\u25bc ' + value;
  return value;
}

function valueColor(value) {
  if (value.includes('+')) return '#16a34a';
  if (value.includes('-')) return '#dc2626';
  return '#1e293b';
}

// --- Agent Hub post HTML builders ---

function card(emoji, title, color, content) {
  return `<div style="background:#ffffff;border-radius:14px;overflow:hidden;margin-bottom:28px;border:1px solid #e2e8f0;box-shadow:0 1px 3px rgba(15,23,42,0.04);">
  <div style="background:${color};padding:16px 26px;">
    <span style="color:#ffffff;font-size:18px;font-weight:700;letter-spacing:0.3px;">${emoji} ${title}</span>
  </div>
  <div style="padding:26px 26px 16px;background:#ffffff;">
    ${content}
  </div>
</div>`;
}

const p = (t) => `<p style="color:#243244;margin:0 0 18px;font-size:16.5px;line-height:1.78;">${t}</p>`;
const sm = (t) => `<p style="color:#64748b;font-size:13px;margin:0 0 18px;font-style:italic;line-height:1.6;">${t}</p>`;
const b = (l) => `<strong style="color:#1e293b;">${l}</strong>`;
const a = (href, label) => `<a href="${href}" target="_blank" rel="noopener noreferrer" style="color:#2563eb;text-decoration:none;">${label}</a>`;

function banner(dateStr, emailUrl) {
  // Format date for display (e.g., "Mar 2, 2026" from "03/02/26")
  const parts = dateStr.split('/');
  const dateObj = new Date(2000 + parseInt(parts[2]), parseInt(parts[0]) - 1, parseInt(parts[1]));
  const displayDate = dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });

  return `<div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);border-radius:12px;padding:32px 24px;text-align:center;margin-bottom:24px;">
  <div style="color:rgba(255,255,255,0.85);font-size:13px;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px;">REALTY EXPERTS\u00ae</div>
  <div style="color:#ffffff;font-size:26px;font-weight:700;margin-bottom:8px;">Daily Market Glance</div>
  <div style="color:rgba(255,255,255,0.8);font-size:14px;margin-bottom:20px;">${displayDate} \u00b7 Real Estate \u00b7 Stocks \u00b7 Economy \u00b7 Crypto</div>
  <a href="${emailUrl}" target="_blank" rel="noopener noreferrer" style="display:inline-block;background:white;color:#667eea;font-weight:700;font-size:14px;padding:12px 28px;border-radius:8px;text-decoration:none;">Open Email in Browser</a>
</div>`;
}

function images(img1Url, img2Url) {
  // Each image links to its full-size file so a click opens it enlarged in a new
  // tab — works on the share page and in email clients that strip JS lightboxes.
  const tile = (url, alt, mb) => `<a href="${url}" target="_blank" rel="noopener noreferrer" style="display:block;text-decoration:none;cursor:zoom-in;max-width:650px;margin:0 auto ${mb};">
    <img src="${url}" alt="${alt}" style="width:100%;display:block;border-radius:10px;border:1px solid #e2e8f0;" />
  </a>`;
  return `<div style="margin-bottom:28px;">
  ${tile(img1Url, 'Daily Market Data Table', '12px')}
  ${tile(img2Url, 'Market Chart', '8px')}
  <div style="text-align:center;font-size:12.5px;color:#94a3b8;margin:4px 0 0;">🔍 Click an image to open it full-size</div>
</div>`;
}

// --- Section builders ---

function realEstateSection(data) {
  const re = data.real_estate;
  let content = '';
  content += p(`${b('30-Year Rate:')} ${re.rate_30year} &nbsp;|&nbsp; ${b('15-Year Rate:')} ${re.rate_15year}`);

  // homebuilder content — split paragraphs and format each
  if (re.homebuilder) {
    const paras = re.homebuilder.split('\n\n');
    paras.forEach(para => {
      const trimmed = para.trim();
      // Check for bold label pattern "Label: description"
      const colonMatch = trimmed.match(/^([^:]+):(.*)/s);
      if (colonMatch && colonMatch[1].length < 60) {
        content += p(`${b(colonMatch[1] + ':')} ${colonMatch[2].trim()}`);
      } else {
        content += p(trimmed);
      }
    });
  }

  // commentary
  if (re.commentary) {
    const paras = re.commentary.split('\n\n');
    paras.forEach(para => {
      const trimmed = para.trim();
      if (trimmed.startsWith('\ud83c\udfe1') || trimmed.startsWith('\ud83d\udcf0')) {
        // Emoji-prefixed items: bold the label portion
        const colonMatch = trimmed.match(/^([^\n:]+):(.*)/s);
        if (colonMatch) {
          content += p(`${b(colonMatch[1] + ':')} ${colonMatch[2].trim()}`);
        } else {
          content += p(`${b(trimmed)}`);
        }
      } else if (trimmed.endsWith(':')) {
        content += p(b(trimmed));
      } else {
        content += p(trimmed);
      }
    });
  }

  content += featureImagesHtml(re);

  return card('\ud83c\udfe0', 'Real Estate', '#ea580c', content);
}

// Render 0, 1, or N feature images for a section (clickable -> full size), shared
// by Stocks (e.g. the "AI Spending" chart) and Economy (e.g. the gold/NAHB charts).
function featureImagesHtml(section) {
  const imgs = Array.isArray(section.feature_images) ? section.feature_images
             : (section.feature_image ? [section.feature_image] : []);
  let out = '';
  imgs.filter(fi => fi && fi.url).forEach(fi => {
    out += `<a href="${fi.url}" target="_blank" rel="noopener noreferrer" style="display:block;text-decoration:none;cursor:zoom-in;margin:8px 0 4px;">
    <img src="${fi.url}" alt="${fi.alt || ''}" style="width:100%;display:block;border-radius:10px;border:1px solid #e2e8f0;" />
  </a>`;
    if (fi.caption) out += `<p style="color:#475569;font-size:13.5px;font-style:italic;line-height:1.6;margin:10px 0 4px;">${fi.caption}</p>`;
    if (fi.source) out += `<p style="color:#94a3b8;font-size:11.5px;margin:0 0 6px;">${fi.source}</p>`;
  });
  return out;
}

function stocksSection(data) {
  const s = data.stocks;
  let content = '';
  content += p(`${b('S&amp;P 500:')} ${s.sp500} &nbsp;|&nbsp; ${b('DOW:')} ${s.dow} &nbsp;|&nbsp; ${b('NASDAQ:')} ${s.nasdaq}`);
  if (s.note) content += sm(s.note);

  if (s.news) {
    const paras = s.news.split('\n\n');
    paras.forEach(para => {
      const trimmed = para.trim();
      const colonMatch = trimmed.match(/^([^:]+):(.*)/s);
      if (colonMatch && colonMatch[1].length < 60) {
        content += p(`${b(colonMatch[1] + ':')} ${colonMatch[2].trim()}`);
      } else {
        content += p(trimmed);
      }
    });
  }

  content += featureImagesHtml(s);

  return card('\ud83d\udcc8', 'Stocks', '#2563eb', content);
}

function economySection(data) {
  const e = data.economy;
  let content = '';
  // Gold AND Silver are MANDATORY in every report (live-search them when the
  // newsletter omits them — see CLAUDE.md "Gold + Silver" rule). A 4th metric
  // (Brent Crude via wti/oil_label, or CPI via cpi/cpi_label) is an optional
  // rotating extra and must never replace gold or silver.
  const metrics = [
    ['10-Year Treasury', e.us10year],
    [e.gold_label || 'Gold', e.gold],
    [e.silver_label || 'Silver', e.silver],
  ];
  if (e.wti) metrics.push([e.oil_label || 'WTI Crude', e.wti]);
  else if (e.cpi) metrics.push([e.cpi_label || 'CPI (YoY)', e.cpi]);
  content += p(metrics.filter(([, v]) => v).map(([l, v]) => `${b(l + ':')} ${v}`).join(' &nbsp;|&nbsp; '));
  if (e.note) content += sm(e.note);

  if (e.commentary) {
    const paras = e.commentary.split('\n\n');
    paras.forEach(para => {
      const trimmed = para.trim();
      const colonMatch = trimmed.match(/^([^:]+):(.*)/s);
      if (colonMatch && colonMatch[1].length < 60) {
        content += p(`${b(colonMatch[1] + ':')} ${colonMatch[2].trim()}`);
      } else {
        content += p(trimmed);
      }
    });
  }

  // Optional Market Briefs graphics (e.g. the gold "Looking Dull" / NAHB charts in
  // Economy, or the "AI Spending" chart in Stocks), shown in the broadcast post as
  // well as the email. Use `feature_images` (array) for several, or `feature_image`
  // (single) for one. Each clickable -> full size.
  content += featureImagesHtml(e);

  return card('\ud83c\udfe6', 'Economy', '#16a34a', content);
}

function cryptoSection(data) {
  if (!data.crypto) return '';
  const c = data.crypto;
  let content = '';
  content += p(`${b('BTC:')} ${c.btc} &nbsp;|&nbsp; ${b('ETH:')} ${c.eth} &nbsp;|&nbsp; ${b('XRP:')} ${c.xrp}`);
  if (c.note) content += sm(c.note);

  if (c.commentary) {
    const paras = c.commentary.split('\n\n');
    paras.forEach(para => {
      const trimmed = para.trim();
      const colonMatch = trimmed.match(/^([^:]+):(.*)/s);
      if (colonMatch && colonMatch[1].length < 60) {
        content += p(`${b(colonMatch[1] + ':')} ${colonMatch[2].trim()}`);
      } else {
        content += p(trimmed);
      }
    });
  }

  content += featureImagesHtml(c);

  return card('\u20bf', 'Crypto', '#f59e0b', content);
}

function sourcesBlock(sources) {
  if (!sources || sources.length === 0) return '';

  function labelFromUrl(url) {
    try {
      const u = new URL(url);
      const host = u.hostname.replace('www.', '');
      const publishers = {
        'bloomberg.com': 'Bloomberg',
        'cnbc.com': 'CNBC',
        'reuters.com': 'Reuters',
        'wsj.com': 'WSJ',
        'coindesk.com': 'CoinDesk',
        'tradingeconomics.com': 'Trading Economics',
        'mortgagenewsdaily.com': 'Mortgage News Daily',
        'bankrate.com': 'Bankrate',
        'yahoo.com': 'Yahoo Finance',
        'finance.yahoo.com': 'Yahoo Finance',
        'fool.com': 'Motley Fool',
        'decrypt.co': 'Decrypt',
        'tricityvoice.com': 'Tri-City Voice',
        'wrenews.com': 'WRE News',
      };
      const publisher = publishers[host] || host.split('.')[0].charAt(0).toUpperCase() + host.split('.')[0].slice(1);
      const pathParts = u.pathname.split('/').filter(Boolean);
      const slug = pathParts[pathParts.length - 1] || '';
      const topic = slug
        .replace(/\.html?$/, '')
        .replace(/\d{4}-\d{2}-\d{2}/, '')
        .replace(/-+/g, ' ')
        .replace(/\b\w/g, c => c.toUpperCase())
        .trim()
        .slice(0, 40);
      return topic ? `${publisher} \u2014 ${topic}` : publisher;
    } catch {
      return url.slice(0, 50);
    }
  }

  const links = sources.map(url =>
    `<p style="font-size:12px;margin:0 0 3px;">${a(url, labelFromUrl(url))}</p>`
  ).join('\n  ');

  return `<div style="background:#f8fafc;border-radius:10px;padding:16px 18px;margin-bottom:16px;border:1px solid #e2e8f0;">
  <p style="color:#475569;font-size:13px;font-weight:600;margin:0 0 8px;">Sources</p>
  ${links}
</div>
<p style="color:#94a3b8;font-size:11px;margin:0;"><em>Market data is for informational purposes only. Always verify with your lender or financial advisor before making decisions.</em></p>`;
}

/**
 * Build the complete Agent Hub post body HTML from JSON data.
 */
function buildPostBody(data, emailUrl, img1Url, img2Url) {
  const parts = [
    banner(data.date, emailUrl),
    images(img1Url, img2Url),
    realEstateSection(data),
    stocksSection(data),
    economySection(data),
    cryptoSection(data),
    sourcesBlock(data.sources),
  ].filter(Boolean);

  // Constrain to a comfortable reading column (long lines on the wide share
  // page were the main "too packed" culprit) + a modern system font stack.
  return `<div style="max-width:680px;margin:0 auto;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
${parts.join('\n')}
</div>`;
}

// ── Meridian responsive body (Agent Hub note + web) ───────────────────────────
// A phone-first, DOMPurify-safe body in Harv's Meridian Dial language, emitted from
// the SAME JSON as the Outlook email. Inline styles only (DOMPurify strips
// <style>/<script>/<link> from note bodies); flex-wrap for fluid reflow so it needs
// no @media rules; the muted-directional up/down signal (sage/clay, approved
// 2026-07-06) replaces saturated green/red. Serif numerals use Georgia (no web font
// is loadable inside a sanitized note body). update-note-body.js can point the
// broadcast at this instead of the email HTML; the Outlook email path is untouched.
const M_SERIF = "Georgia,'Times New Roman',serif";
const M_SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif";
const M = {
  paper: '#FAF7F0', ink: '#2E2E2E', soft: '#4A4640', gold: '#D4AF37', goldDark: '#B08C1E',
  hair: '#E8E4DA', up: '#5B7551', down: '#A65A44',
  re: '#B08C1E', stocks: '#3E5C76', economy: '#5B7551', crypto: '#8A5A2B',
};

// "$4,112 (+2.01%)" -> { main:"$4,112", change:"+2.01%" }
function mSplit(v) {
  const s = String(v == null ? '' : v);
  const m = s.match(/^(.*?)\s*\(([^)]*)\)\s*$/);
  return m ? { main: m[1].trim(), change: m[2].trim() } : { main: s.trim(), change: '' };
}
// Muted directional signal: up=sage, down=clay, flat (0.00%)=ink-soft with no arrow.
function mDir(change) {
  const c = String(change).trim();
  if (/^[+-]0(\.0+)?%?$/.test(c)) return { arrow: '', color: M.soft };
  if (/^\+/.test(c)) return { arrow: '▲', color: M.up };
  if (/^-/.test(c)) return { arrow: '▼', color: M.down };
  return { arrow: '', color: M.soft };
}
function mDelta(change) {
  if (!change) return '';
  const { arrow, color } = mDir(change);
  return `<span style="font-family:${M_SANS};font-size:12px;font-weight:600;color:${color};white-space:nowrap;">${arrow ? arrow + ' ' : ''}${change}</span>`;
}
function mCell(label, value) {
  const { main, change } = mSplit(value);
  return `<div style="box-sizing:border-box;flex:1 1 132px;min-width:120px;border:1px solid ${M.hair};border-radius:12px;padding:12px 13px;background:${M.paper};">
    <div style="font-family:${M_SANS};font-size:9.5px;text-transform:uppercase;letter-spacing:.12em;color:${M.soft};font-weight:600;">${label}</div>
    <div style="font-family:${M_SERIF};font-size:22px;font-weight:600;color:${M.ink};margin:4px 0 1px;line-height:1.05;">${main}</div>
    ${change ? mDelta(change) : ''}
  </div>`;
}
function mGrid(pairs) {
  const cells = pairs.filter(([, v]) => v).map(([l, v]) => mCell(l, v));
  return cells.length ? `<div style="display:flex;flex-wrap:wrap;gap:10px;">${cells.join('')}</div>` : '';
}
function mNote(t) {
  return `<div style="font-family:${M_SANS};font-size:12px;color:${M.soft};font-style:italic;margin:10px 0 2px;line-height:1.55;">${t}</div>`;
}
function mProse(text) {
  if (!text) return '';
  const para = (html) => `<div style="font-family:${M_SANS};font-size:14px;color:${M.soft};line-height:1.66;margin:0 0 12px;">${html}</div>`;
  return text.split('\n\n').map(block => {
    const t = block.trim();
    if (!t) return '';
    if (t.startsWith('📍')) { // 📍 location line
      const body = t.slice(2).trim();
      const cm = body.match(/^([^:]+):(.*)/s);
      if (cm) { // "City: 30 new / 741 active" -> compact hairline row
        return `<div style="display:flex;justify-content:space-between;gap:12px;font-family:${M_SANS};font-size:12.5px;color:${M.soft};padding:5px 0;border-top:1px solid ${M.hair};"><span style="font-weight:600;color:${M.ink};">${cm[1].trim()}</span><span style="font-family:${M_SERIF};text-align:right;">${cm[2].trim()}</span></div>`;
      }
      return `<div style="font-family:${M_SANS};font-size:10.5px;text-transform:uppercase;letter-spacing:.12em;color:${M.goldDark};font-weight:700;margin:16px 0 3px;">${body}</div>`;
    }
    if (t.includes('•')) { // bullet block
      return t.split('\n').map(line => {
        const l = line.trim();
        if (!l) return '';
        const bm = l.replace(/^•\s*/, '');
        const cm = bm.match(/^([^:]{1,60}):(.*)/s);
        const inner = cm ? `<strong style="color:${M.ink};">${cm[1].trim()}:</strong>${cm[2]}` : bm;
        return `<div style="font-family:${M_SANS};font-size:13.5px;color:${M.soft};line-height:1.6;margin:5px 0;padding-left:14px;position:relative;"><span style="position:absolute;left:0;top:8px;width:5px;height:5px;border-radius:50%;background:${M.gold};display:inline-block;"></span>${inner}</div>`;
      }).join('');
    }
    const cm = t.match(/^([^:\n]{1,60}):(.*)/s);
    if (cm) return para(`<strong style="color:${M.ink};">${cm[1].trim()}:</strong>${cm[2]}`);
    return para(t);
  }).join('');
}
function mFeatureImages(section) {
  const imgs = Array.isArray(section.feature_images) ? section.feature_images
    : (section.feature_image ? [section.feature_image] : []);
  return imgs.filter(fi => fi && fi.url).map(fi => {
    let o = `<a href="${fi.url}" target="_blank" rel="noopener noreferrer" style="display:block;text-decoration:none;margin:12px 0 4px;"><img src="${fi.url}" alt="${fi.alt || ''}" style="width:100%;display:block;border-radius:12px;border:1px solid ${M.hair};" /></a>`;
    if (fi.caption) o += `<div style="font-family:${M_SANS};font-size:12.5px;color:${M.soft};font-style:italic;line-height:1.55;margin:8px 0 2px;">${fi.caption}</div>`;
    if (fi.source) o += `<div style="font-family:${M_SANS};font-size:11px;color:${M.soft};margin:0 0 4px;">${fi.source}</div>`;
    return o;
  }).join('');
}
function mCard(label, accent, inner) {
  if (!inner) return '';
  return `<div style="background:#FFFFFF;border:1px solid ${M.hair};border-radius:14px;padding:17px 17px 15px;margin-bottom:15px;">
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:13px;">
    <span style="display:inline-block;width:5px;height:14px;border-radius:2px;background:${accent};"></span>
    <span style="font-family:${M_SANS};font-size:10.5px;text-transform:uppercase;letter-spacing:.16em;color:${accent};font-weight:700;">${label}</span>
  </div>
  ${inner}
</div>`;
}
function mHeader(dateStr, emailUrl) {
  const parts = String(dateStr).split('/');
  const dateObj = new Date(2000 + parseInt(parts[2], 10), parseInt(parts[0], 10) - 1, parseInt(parts[1], 10));
  const displayDate = dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  return `<div style="text-align:center;padding:4px 0 18px;border-bottom:1px solid ${M.hair};margin-bottom:18px;">
  <div style="font-family:${M_SANS};font-size:10px;text-transform:uppercase;letter-spacing:.2em;color:${M.goldDark};font-weight:700;">REALTY EXPERTS®</div>
  <div style="font-family:${M_SERIF};font-size:26px;font-weight:600;color:${M.ink};margin:8px 0 4px;">Daily Market Glance</div>
  <div style="font-family:${M_SANS};font-size:12px;color:${M.soft};">${displayDate} · Real Estate · Stocks · Economy · Crypto</div>
  <div style="margin-top:13px;"><a href="${emailUrl}" target="_blank" rel="noopener noreferrer" style="display:inline-block;border:1px solid ${M.gold};color:${M.goldDark};text-decoration:none;font-family:${M_SANS};font-size:12px;font-weight:600;padding:8px 18px;border-radius:40px;">Open Email in Browser</a></div>
</div>`;
}
function mImages(img1Url, img2Url) {
  const tile = (u, alt, mb) => `<a href="${u}" target="_blank" rel="noopener noreferrer" style="display:block;text-decoration:none;margin:0 0 ${mb};"><img src="${u}" alt="${alt}" style="width:100%;display:block;border-radius:12px;border:1px solid ${M.hair};" /></a>`;
  return `<div style="margin-bottom:18px;">
  ${tile(img1Url, 'Daily Market Data Table', '10px')}
  ${tile(img2Url, 'Market Chart', '6px')}
  <div style="text-align:center;font-family:${M_SANS};font-size:11.5px;color:${M.soft};margin-top:4px;">Tap an image to open it full size</div>
</div>`;
}
// Module-level publisher labeler (mirrors the closure in sourcesBlock).
function mLabelFromUrl(url) {
  try {
    const u = new URL(url);
    const host = u.hostname.replace('www.', '');
    const pub = {
      'bloomberg.com': 'Bloomberg', 'cnbc.com': 'CNBC', 'reuters.com': 'Reuters', 'wsj.com': 'WSJ',
      'coindesk.com': 'CoinDesk', 'tradingeconomics.com': 'Trading Economics',
      'mortgagenewsdaily.com': 'Mortgage News Daily', 'bankrate.com': 'Bankrate',
      'finance.yahoo.com': 'Yahoo Finance', 'yahoo.com': 'Yahoo Finance', 'fool.com': 'Motley Fool',
      'decrypt.co': 'Decrypt', 'market.briefs.co': 'Market Briefs', 'briefs.co': 'Market Briefs',
    };
    const publisher = pub[host] || host.split('.')[0].charAt(0).toUpperCase() + host.split('.')[0].slice(1);
    const parts = u.pathname.split('/').filter(Boolean);
    const slug = parts[parts.length - 1] || '';
    const topic = slug.replace(/\.html?$/, '').replace(/\d{4}-\d{2}-\d{2}/, '').replace(/-+/g, ' ')
      .replace(/\b\w/g, c => c.toUpperCase()).trim().slice(0, 40);
    return topic ? `${publisher}, ${topic}` : publisher;
  } catch { return String(url).slice(0, 50); }
}
function mSources(sources) {
  const links = (sources || []).map(u =>
    `<div style="font-family:${M_SANS};font-size:12.5px;margin:0 0 4px;"><a href="${u}" target="_blank" rel="noopener noreferrer" style="color:${M.goldDark};text-decoration:none;">${mLabelFromUrl(u)}</a></div>`
  ).join('');
  const box = links ? `<div style="background:${M.paper};border:1px solid ${M.hair};border-radius:12px;padding:15px 17px;margin-bottom:12px;">
  <div style="font-family:${M_SANS};font-size:10.5px;text-transform:uppercase;letter-spacing:.16em;color:${M.goldDark};font-weight:700;margin-bottom:8px;">Sources</div>${links}</div>` : '';
  return `${box}<div style="font-family:${M_SANS};font-size:11.5px;color:${M.soft};font-style:italic;line-height:1.6;">Market data is for informational purposes only. Always verify with your lender or financial advisor before making decisions.</div>`;
}

function mRealEstate(data) {
  const re = data.real_estate; if (!re) return '';
  let inner = '';
  if (re.homebuilder) inner += `<div style="font-family:${M_SERIF};font-size:15px;font-weight:600;color:${M.ink};line-height:1.42;margin-bottom:13px;">${re.homebuilder}</div>`;
  inner += mGrid([['30-Year Fixed', re.rate_30year], ['15-Year Fixed', re.rate_15year]]);
  if (re.commentary) inner += `<div style="margin-top:13px;">${mProse(re.commentary)}</div>`;
  inner += mFeatureImages(re);
  return mCard('Real Estate', M.re, inner);
}
function mStocks(data) {
  const s = data.stocks; if (!s) return '';
  let inner = mGrid([['S&amp;P 500', s.sp500], ['DOW', s.dow], ['NASDAQ', s.nasdaq]]);
  if (s.note) inner += mNote(s.note);
  if (s.news) inner += `<div style="margin-top:12px;">${mProse(s.news)}</div>`;
  inner += mFeatureImages(s);
  return mCard('Stocks', M.stocks, inner);
}
function mEconomy(data) {
  const e = data.economy; if (!e) return '';
  const pairs = [['10-Year', e.us10year], [e.gold_label || 'Gold', e.gold], [e.silver_label || 'Silver', e.silver]];
  if (e.wti) pairs.push([e.oil_label || 'WTI Crude', e.wti]);
  else if (e.cpi) pairs.push([e.cpi_label || 'CPI (YoY)', e.cpi]);
  let inner = mGrid(pairs);
  if (e.note) inner += mNote(e.note);
  if (e.commentary) inner += `<div style="margin-top:12px;">${mProse(e.commentary)}</div>`;
  inner += mFeatureImages(e);
  return mCard('Economy', M.economy, inner);
}
function mCrypto(data) {
  const c = data.crypto; if (!c) return '';
  let inner = mGrid([['BTC', c.btc], ['ETH', c.eth], ['XRP', c.xrp]]);
  if (c.note) inner += mNote(c.note);
  if (c.commentary) inner += `<div style="margin-top:12px;">${mProse(c.commentary)}</div>`;
  inner += mFeatureImages(c);
  return mCard('Crypto', M.crypto, inner);
}

/**
 * Build the Meridian responsive note body (Agent Hub + web) from JSON data.
 * DOMPurify-safe (inline styles only). Same content as the email, phone-first look.
 */
function buildResponsiveBody(data, emailUrl, img1Url, img2Url) {
  const parts = [
    mHeader(data.date, emailUrl),
    mImages(img1Url, img2Url),
    mRealEstate(data),
    mStocks(data),
    mEconomy(data),
    mCrypto(data),
    mSources(data.sources),
  ].filter(Boolean);
  return `<div style="max-width:680px;margin:0 auto;background:${M.paper};border:1px solid ${M.hair};border-radius:16px;padding:22px 18px;font-family:${M_SANS};color:${M.ink};">
${parts.join('\n')}
</div>`;
}

module.exports = {
  // Text formatting (shared with generate-daily-email.js)
  formatCommentary,
  addArrow,
  valueColor,
  // Meridian responsive body (Agent Hub note + web)
  buildResponsiveBody,
  // Agent Hub post builders
  card,
  p,
  sm,
  b,
  a,
  banner,
  images,
  realEstateSection,
  stocksSection,
  economySection,
  cryptoSection,
  sourcesBlock,
  buildPostBody,
};
