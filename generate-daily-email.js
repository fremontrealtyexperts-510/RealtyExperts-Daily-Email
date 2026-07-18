#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// ── Meridian palette (matches lib/html-builders.js + the harvrealtor.com report) ──
// paper/ink/gold with the muted directional signal (sage up, clay down) approved 2026-07-06.
const PAL = {
  paper: '#FAF7F0', ink: '#2E2E2E', soft: '#4A4640', faint: '#7C766B',
  gold: '#D4AF37', goldDark: '#B08C1E', hair: '#E8E4DA',
  up: '#5B7551', down: '#A65A44',
  re: '#B08C1E', stocks: '#3E5C76', economy: '#5B7551', crypto: '#8A5A2B',
  cardLabel: '#BEB9AE',
};
const SERIF = "Georgia, 'Times New Roman', serif";
const SANS = "'Segoe UI', Arial, Helvetica, sans-serif";

// Read JSON data
function loadData(jsonFile) {
  const data = JSON.parse(fs.readFileSync(jsonFile, 'utf8'));
  return data;
}

// Generate source links from JSON template sources array
function generateSourceLinks(sources) {
  if (!sources || sources.length === 0) return '';

  // Extract a short label from a URL
  function labelFromUrl(url) {
    try {
      const u = new URL(url);
      const host = u.hostname.replace('www.', '');
      // Get the publisher name
      const publishers = {
        'bloomberg.com': 'Bloomberg',
        'cnbc.com': 'CNBC',
        'reuters.com': 'Reuters',
        'wsj.com': 'WSJ',
        'whitehouse.gov': 'White House',
        'coindesk.com': 'CoinDesk',
        'tradingview.com': 'TradingView',
        'nytimes.com': 'NYT',
        'foxbusiness.com': 'Fox Business',
        'yahoo.com': 'Yahoo Finance',
        'bls.gov': 'U.S. Bureau of Labor Statistics',
        'fred.stlouisfed.org': 'FRED',
        'market.briefs.co': 'Market Briefs',
        'tradingeconomics.com': 'Trading Economics',
        'mortgagenewsdaily.com': 'Mortgage News Daily',
      };
      const publisher = publishers[host] || host.split('.')[0].charAt(0).toUpperCase() + host.split('.')[0].slice(1);

      // Extract a topic from the URL path
      const pathParts = u.pathname.split('/').filter(Boolean);
      const slug = pathParts[pathParts.length - 1] || '';
      // Clean up the slug: remove dates, file extensions, convert hyphens
      const topic = slug
        .replace(/\.html?$/, '')
        .replace(/\d{4}-\d{2}-\d{2}/, '')
        .replace(/-+/g, ' ')
        .replace(/\b\w/g, c => c.toUpperCase())
        .trim()
        .slice(0, 30)
        .replace(/\b(Cpi|Gdp|Wti|Btc|Eth|Xrp|Ytd|Yoy|Nahb|Us)\b/g, m => m.toUpperCase());

      return topic ? `${publisher}, ${topic}` : publisher;
    } catch {
      return url.slice(0, 40);
    }
  }

  return sources
    .map(url => `<a href="${url}" style="color: ${PAL.faint}; text-decoration: none;">${labelFromUrl(url)}</a>`)
    .join(' · \n                      ');
}

// Format commentary text with proper paragraphs and bullets
function formatCommentary(text) {
  if (!text) return '';
  // Split by double newlines for paragraphs
  const paragraphs = text.split('\n\n');

  const paraStyle = `margin: 0 0 14px 0; font-family: ${SANS}; font-size: 15px; color: ${PAL.soft}; line-height: 1.75;`;

  // A 📍 line: the snapshot header becomes a small-caps gold kicker; a
  // "📍 City: numbers" line becomes a hairline ledger row (pin stripped).
  function pinLine(trimmed) {
    const body = trimmed.replace(/^📍\s*/, '');
    const colonMatch = body.match(/^([^:]+):(.*)/s);
    if (colonMatch) {
      return `<div style="border-top: 1px solid ${PAL.hair}; padding: 7px 0; font-family: ${SANS}; font-size: 14px; color: ${PAL.soft}; line-height: 1.6;"><strong style="color: ${PAL.ink};">${colonMatch[1].trim()}:</strong>${colonMatch[2]}</div>`;
    }
    return `<div style="margin: 22px 0 8px 0; font-family: ${SANS}; font-size: 11px; font-weight: 700; letter-spacing: 1.6px; color: ${PAL.goldDark};">${body.toUpperCase()}</div>`;
  }

  return paragraphs.map(para => {
    // Check if paragraph contains bullet points
    if (para.includes('•')) {
      const lines = para.split('\n');
      let html = '';

      lines.forEach(line => {
        const trimmed = line.trim();
        if (trimmed.startsWith('•')) {
          // Check if this bullet point has a bold label (ends with :)
          const colonMatch = trimmed.match(/^• ([^:]+):(.*)/);
          if (colonMatch) {
            html += `<div style="margin: 10px 0 6px 0; font-family: ${SANS}; font-size: 15px; color: ${PAL.soft}; line-height: 1.7;"><strong style="color: ${PAL.ink};">• ${colonMatch[1]}:</strong>${colonMatch[2]}</div>`;
          } else {
            html += `<div style="margin: 6px 0; padding-left: 0; font-family: ${SANS}; font-size: 15px; color: ${PAL.soft}; line-height: 1.7;">${trimmed}</div>`;
          }
        } else if (trimmed.startsWith('📍')) {
          html += pinLine(trimmed);
        } else if (trimmed.startsWith('o ')) {
          // Nested list items (open houses, etc) - normal weight
          html += `<div style="margin: 6px 0; padding-left: 20px; font-family: ${SANS}; font-size: 15px; color: ${PAL.soft}; line-height: 1.7;">${trimmed}</div>`;
        } else if (trimmed) {
          // Headers ending with colon should be bold
          if (trimmed.endsWith(':')) {
            html += `<div style="margin: 0 0 10px 0; font-family: ${SANS}; font-size: 15px; line-height: 1.7; font-weight: 700; color: ${PAL.ink};">${trimmed}</div>`;
          } else {
            html += `<div style="margin: 10px 0; font-family: ${SANS}; font-size: 15px; color: ${PAL.soft}; line-height: 1.7; font-weight: 600;">${trimmed}</div>`;
          }
        }
      });
      return html;
    } else {
      // Check if this paragraph is a location marker or header
      const trimmed = para.trim();
      if (trimmed.startsWith('📍')) {
        return pinLine(trimmed);
      } else if (trimmed.endsWith(':')) {
        return `<div style="margin: 0 0 10px 0; font-family: ${SANS}; font-size: 15px; line-height: 1.7; font-weight: 700; color: ${PAL.ink};">${trimmed}</div>`;
      }
      return `<div style="${paraStyle}">${trimmed}</div>`;
    }
  }).join('');
}

// "$4,061 (+0.1%)" -> { main: "$4,061", change: "+0.1%" }
function splitValue(v) {
  const s = String(v == null ? '' : v);
  const m = s.match(/^(.*?)\s*\(([^)]*)\)\s*$/);
  return m ? { main: m[1].trim(), change: m[2].trim() } : { main: s.trim(), change: '' };
}

// Muted directional signal: up = sage, down = clay, flat = ink-soft, no arrow.
function dirOf(change) {
  const c = String(change).trim();
  if (/^[+-]0(\.0+)?%?$/.test(c)) return { arrow: '', color: PAL.soft };
  if (/^\+/.test(c)) return { arrow: '▲', color: PAL.up };
  if (/^-/.test(c)) return { arrow: '▼', color: PAL.down };
  return { arrow: '', color: PAL.soft };
}

// Add up/down arrow indicators to values with percentages (kept for compatibility)
function addArrow(value) {
  if (value.includes('+')) {
    return '▲ ' + value;
  } else if (value.includes('-')) {
    return '▼ ' + value;
  }
  return value;
}

// Get value color based on +/- indicator (muted Meridian signal)
function valueColor(value) {
  if (!value) return PAL.ink;
  if (value.includes('+')) return PAL.up;
  if (value.includes('-')) return PAL.down;
  return PAL.ink;
}

// One stat cell: uppercase label, serif numeral, stacked muted delta. Stacking the
// delta under the value (instead of one long nowrap line) keeps the minimum content
// width small, so phones no longer zoom the whole email out.
function statCellInner(label, value) {
  const { main, change } = splitValue(value || 'n/a');
  const d = change ? dirOf(change) : null;
  return `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="${PAL.paper}" style="background-color: ${PAL.paper}; border: 1px solid ${PAL.hair};">
                            <tr>
                              <td style="padding: 12px 14px;">
                                <div style="font-family: ${SANS}; font-size: 10px; font-weight: 600; color: ${PAL.soft}; letter-spacing: 1.4px;">${label}</div>
                                <div style="font-family: ${SERIF}; font-size: 21px; font-weight: 700; color: ${PAL.ink}; padding: 5px 0 2px 0; white-space: nowrap;">${main}</div>
                                ${d ? `<div style="font-family: ${SANS}; font-size: 12px; font-weight: 700; color: ${d.color}; white-space: nowrap;">${d.arrow ? d.arrow + ' ' : ''}${change}</div>` : ''}
                              </td>
                            </tr>
                          </table>`;
}

// A row of three stat cells (Stocks, Crypto).
function statRow3(cells) {
  const tds = cells.map(([label, value]) => `<td width="32%" style="vertical-align: top;">
                          ${statCellInner(label, value)}
                        </td>`);
  return `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 14px 0 10px 0;">
                      <tr>
                        ${tds.join(`\n                        <td width="2%"></td>\n                        `)}
                      </tr>
                    </table>`;
}

// Build the ECONOMY stat-card grid (2×2).
// Gold AND Silver are MANDATORY in every report (live-search them when the
// newsletter omits them — see CLAUDE.md "Gold + Silver" rule). A 4th card
// (Brent Crude via wti/oil_label, or CPI via cpi/cpi_label) is an optional
// rotating extra and must never replace gold or silver. Renders a 2×2 grid
// when there are 4 metrics (phone-safe), or a single row of 3.
function economyStatCards(e) {
  const cards = [
    ['US 10-YEAR', e.us10year],
    [(e.gold_label || 'Gold').toUpperCase(), e.gold],
    [(e.silver_label || 'Silver').toUpperCase(), e.silver],
  ];
  if (e.wti) cards.push([(e.oil_label || 'WTI Crude').toUpperCase(), e.wti]);
  else if (e.cpi) cards.push([(e.cpi_label || 'CPI (YoY)').toUpperCase(), e.cpi]);

  if (cards.length < 4) return statRow3(cards);

  const cell = ([label, value]) => `<td width="48%" style="vertical-align: top;">
                          ${statCellInner(label, value)}
                        </td>`;
  return `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 14px 0 10px 0;">
                      <tr>
                        ${cell(cards[0])}
                        <td width="4%"></td>
                        ${cell(cards[1])}
                      </tr>
                      <tr><td colspan="3" style="font-size: 10px; line-height: 10px;">&nbsp;</td></tr>
                      <tr>
                        ${cell(cards[2])}
                        <td width="4%"></td>
                        ${cell(cards[3])}
                      </tr>
                    </table>`;
}

// Editorial numbered section header: serif number in the section accent, spaced
// small-caps title, hairline rule running to the right edge.
function sectionHeader(num, title, accent) {
  return `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 0 0 16px 0;">
                      <tr>
                        <td style="white-space: nowrap; padding-right: 14px;">
                          <span style="font-family: ${SERIF}; font-size: 21px; font-weight: 600; color: ${accent};">${num}</span>
                          <h2 style="display: inline; margin: 0; font-family: ${SANS}; font-size: 13px; font-weight: 700; color: ${PAL.ink}; letter-spacing: 2.4px;">&nbsp; ${title}</h2>
                        </td>
                        <td width="100%" style="border-bottom: 1px solid ${PAL.hair}; font-size: 1px; line-height: 1px;">&nbsp;</td>
                      </tr>
                    </table>`;
}

// Vertical breathing room between sections.
function sectionGap() {
  return `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr><td style="font-size: 26px; line-height: 26px;">&nbsp;</td></tr>
              </table>`;
}

// Italic as-of note under a stat grid.
function asOfNote(text) {
  if (!text) return '';
  return `<div style="font-family: ${SANS}; font-size: 12px; color: ${PAL.faint}; font-style: italic; margin: 0 0 14px 0; line-height: 1.55;">${text}</div>`;
}

// Render 0, 1, or N feature images in a section (each click-to-enlarge,
// Outlook-safe). Use `<section>.feature_images` (array) for multiple — e.g. the
// Market Briefs "10 Most Valuable Companies" + "Top 5 Economies by GDP" infographics —
// or `<section>.feature_image` (single object) for one (back-compat, e.g. the gold
// chart in Economy, or the "AI Spending" chart in Stocks).
function featureImagesHtml(section) {
  const imgs = Array.isArray(section.feature_images) ? section.feature_images
             : (section.feature_image ? [section.feature_image] : []);
  if (!imgs.length) return '';
  return imgs.filter(fi => fi && fi.url).map(fi => `<!-- feature image -->
                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 18px 0 4px 0;">
                      <tr>
                        <td align="center">
                          <a href="${fi.url}" target="_blank" rel="noopener noreferrer" onclick="openLightbox(this.href); return false;" style="display: block; text-decoration: none; cursor: zoom-in;">
                            <img src="${fi.url}" alt="${fi.alt || ''}" width="100%" class="clickable-image" style="display: block; max-width: 100%; height: auto; border: 1px solid ${PAL.hair}; cursor: zoom-in;">
                          </a>
                        </td>
                      </tr>
                      ${fi.caption ? `<tr><td style="padding: 10px 4px 0 4px; font-family: ${SANS}; font-size: 13px; color: ${PAL.soft}; line-height: 1.55; font-style: italic;">${fi.caption}</td></tr>` : ''}
                      ${fi.source ? `<tr><td style="padding: 4px 4px 0 4px; font-family: ${SANS}; font-size: 11px; color: ${PAL.faint};">${fi.source}</td></tr>` : ''}
                    </table>`).join('\n');
}

// Generate HTML with inline styles for Outlook compatibility
function generateHTML(data) {
  // Format date for filenames (MMDDYY)
  const dateForFile = data.date.replace(/\//g, '');
  const htmlFileName = `daily-market-glance-${dateForFile}.html`;
  const githubBaseUrl = 'https://fremontrealtyexperts-510.github.io/RealtyExperts-Daily-Email';

  // Long-form date for the masthead (e.g. "Wednesday, July 15, 2026")
  const dParts = data.date.split('/');
  const dateObj = new Date(2000 + parseInt(dParts[2], 10), parseInt(dParts[0], 10) - 1, parseInt(dParts[1], 10));
  const longDate = dateObj.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });

  // Head metadata below is for the GitHub Pages "View in Browser" page ONLY.
  // The <head> never survives a copy-paste of the rendered body into Outlook,
  // so none of it can affect the email path. color-scheme declares the design
  // light-only so dark-mode clients that respect the hint do not force-invert
  // the palette (partial inversion mangles the section colors).
  const esc = (s) => String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
  const pageUrl = `${githubBaseUrl}/${htmlFileName}`;
  const ogImage = `https://raw.githubusercontent.com/fremontrealtyexperts-510/RealtyExperts-Daily-Email/main/RE-Daily-1-${dateForFile}.png`;
  const pageTitle = `"At a Glance" Local Housing STATS and News ${data.date}`;
  const metricBits = [
    data.real_estate && data.real_estate.rate_30year ? `30-year ${data.real_estate.rate_30year}` : '',
    data.real_estate && data.real_estate.rate_15year ? `15-year ${data.real_estate.rate_15year}` : '',
    data.stocks && data.stocks.sp500 ? `S&P 500 ${data.stocks.sp500}` : '',
    data.economy && data.economy.gold ? `gold ${data.economy.gold}` : '',
    data.economy && data.economy.silver ? `silver ${data.economy.silver}` : '',
  ].filter(Boolean).join(', ');
  const description = `Daily market glance for ${data.date}: ${metricBits}. Local East Bay housing stats and news from REALTY EXPERTS®.`;

  // Hidden preheader: what inbox list views show under the subject line.
  const preheader = [
    data.real_estate && data.real_estate.rate_30year ? `30-year ${data.real_estate.rate_30year}` : '',
    data.stocks && data.stocks.sp500 ? `S&P 500 ${splitValue(data.stocks.sp500).main}` : '',
    data.economy && data.economy.gold ? `Gold ${splitValue(data.economy.gold).main}` : '',
    data.crypto && data.crypto.btc ? `BTC ${splitValue(data.crypto.btc).main}` : '',
  ].filter(Boolean).join(' · ');

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="icon" type="image/png" href="https://raw.githubusercontent.com/fremontrealtyexperts-510/RealtyExperts-Daily-Email/main/Realty%20Experts%20-%20RE.png">
  <title>Daily Market Glance - ${data.date}</title>
  <meta name="description" content="${esc(description)}">
  <meta name="color-scheme" content="light">
  <meta name="supported-color-schemes" content="light">
  <link rel="canonical" href="${pageUrl}">
  <meta property="og:type" content="article">
  <meta property="og:title" content="${esc(pageTitle)}">
  <meta property="og:description" content="${esc(description)}">
  <meta property="og:url" content="${pageUrl}">
  <meta property="og:image" content="${ogImage}">
  <meta property="og:site_name" content="REALTY EXPERTS®">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="${esc(pageTitle)}">
  <meta name="twitter:description" content="${esc(description)}">
  <meta name="twitter:image" content="${ogImage}">
  <style>
    /* Lightbox styles */
    .lightbox-overlay {
      display: none;
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(0, 0, 0, 0.9);
      z-index: 9999;
      cursor: zoom-out;
    }
    .lightbox-overlay.active {
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .lightbox-image {
      max-width: 95%;
      max-height: 95%;
      object-fit: contain;
      box-shadow: 0 0 40px rgba(0, 0, 0, 0.5);
    }
    .lightbox-close {
      position: absolute;
      top: 20px;
      right: 30px;
      color: white;
      font-size: 40px;
      font-weight: bold;
      cursor: pointer;
      background: none;
      border: none;
      z-index: 10000;
    }
    .clickable-image {
      cursor: zoom-in;
      transition: opacity 0.2s;
    }
    .clickable-image:hover {
      opacity: 0.9;
    }
    /* Mobile responsive */
    @media only screen and (max-width: 680px) {
      .email-container {
        width: 100% !important;
        min-width: 0 !important;
        max-width: 100% !important;
      }
      .email-body {
        padding: 24px 16px !important;
      }
      .email-masthead {
        padding: 26px 16px 20px 16px !important;
      }
      .email-hub {
        padding: 16px !important;
      }
    }
  </style>
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Arial, Helvetica, sans-serif; background-color: ${PAL.paper};">
  <!-- Preheader (inbox preview text; hidden in the rendered email) -->
  <div style="display: none; font-size: 1px; line-height: 1px; max-height: 0; max-width: 0; opacity: 0; overflow: hidden; mso-hide: all;">${preheader}</div>
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="${PAL.paper}" style="background-color: ${PAL.paper};">
    <tr>
      <td align="center" style="padding: 16px 10px 0 10px;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" class="email-container" style="max-width: 650px;">
          <tr>
            <td align="center" style="padding: 0 0 12px 0;">
              <p style="margin: 0; font-family: ${SANS}; font-size: 12px; color: ${PAL.faint};">
                Having trouble viewing this email? <a href="${githubBaseUrl}/${htmlFileName}" style="color: ${PAL.goldDark}; text-decoration: none; font-weight: 700;">View in Browser</a>
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
    <tr>
      <td align="center" style="padding: 0 10px 32px 10px;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" class="email-container" bgcolor="#FFFFFF" style="background-color: #ffffff; max-width: 650px; border: 1px solid ${PAL.hair};">

          <!-- Masthead -->
          <tr>
            <td class="email-masthead" align="center" style="padding: 36px 40px 24px 40px; border-bottom: 1px solid ${PAL.hair};">
              <img src="https://raw.githubusercontent.com/fremontrealtyexperts-510/RealtyExperts-Daily-Email/main/2022_Logo_WhiteBox-Realtor.jpg" alt="REALTY EXPERTS®" width="230" data-no-lightbox style="display: block; margin: 0 auto; max-width: 100%; height: auto;">
              <h1 style="margin: 18px 0 12px 0; font-family: ${SERIF}; font-size: 31px; font-weight: 600; color: ${PAL.ink}; letter-spacing: 0.3px;">Daily Market Glance</h1>
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td width="50%" style="border-bottom: 1px solid ${PAL.gold}; font-size: 1px; line-height: 1px;">&nbsp;</td>
                  <td style="white-space: nowrap; padding: 0 14px; font-family: ${SANS}; font-size: 12px; font-weight: 600; color: ${PAL.soft}; letter-spacing: 1.6px;">${longDate.toUpperCase()} · ${data.time}</td>
                  <td width="50%" style="border-bottom: 1px solid ${PAL.gold}; font-size: 1px; line-height: 1px;">&nbsp;</td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Agent Hub strip -->
          <tr>
            <td class="email-hub" bgcolor="${PAL.paper}" style="background-color: ${PAL.paper}; padding: 18px 30px; border-bottom: 1px solid ${PAL.hair};">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td style="vertical-align: middle; padding-right: 18px;">
                    <div style="font-family: ${SANS}; font-size: 10px; font-weight: 700; color: ${PAL.goldDark}; letter-spacing: 2.2px; margin-bottom: 6px;">AGENT HUB</div>
                    <div style="font-family: ${SANS}; font-size: 15px; color: ${PAL.ink}; line-height: 1.5;">
                      <strong><a href="${data.agent_hub_link}" style="color: ${PAL.ink}; text-decoration: none;">View the full post on our Agent Hub &rarr;</a></strong>
                    </div>
                    <div style="margin-top: 6px; font-family: ${SANS}; font-size: 13px; color: ${PAL.soft}; line-height: 1.55;">
                      Scan the QR code or visit the Agent Hub for the complete market update. Contact the front desk for your access code.
                    </div>
                  </td>
                  <td width="104" style="vertical-align: middle;">
                    <table role="presentation" cellpadding="0" cellspacing="0" border="0" bgcolor="#FFFFFF" style="background-color: #ffffff; border: 1px solid ${PAL.hair};">
                      <tr>
                        <td style="padding: 5px;">
                          <img src="https://raw.githubusercontent.com/fremontrealtyexperts-510/RealtyExperts-Daily-Email/main/${data.qr_code_path}" alt="Agent Hub QR Code" width="92" data-no-lightbox style="display: block; max-width: 92px; height: auto;">
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Content -->
          <tr>
            <td class="email-body" style="padding: 32px 40px 36px 40px;">

              <!-- Local MLS snapshot images -->
              <div style="font-family: ${SANS}; font-size: 11px; font-weight: 700; color: ${PAL.goldDark}; letter-spacing: 2.2px; margin: 0 0 12px 0;">LOCAL MLS SNAPSHOT</div>
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 0 0 14px 0;">
                <tr>
                  <td align="center">
                    <a href="https://raw.githubusercontent.com/fremontrealtyexperts-510/RealtyExperts-Daily-Email/main/RE-Daily-1-${dateForFile}.png" target="_blank" rel="noopener noreferrer" onclick="openLightbox(this.href); return false;" style="display: block; text-decoration: none; cursor: zoom-in;">
                      <img src="https://raw.githubusercontent.com/fremontrealtyexperts-510/RealtyExperts-Daily-Email/main/RE-Daily-1-${dateForFile}.png" alt="Local Housing Statistics (click to enlarge)" width="100%" class="clickable-image" style="display: block; max-width: 100%; height: auto; border: 1px solid ${PAL.hair}; cursor: zoom-in;">
                    </a>
                  </td>
                </tr>
              </table>
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 0 0 8px 0;">
                <tr>
                  <td align="center">
                    <a href="https://raw.githubusercontent.com/fremontrealtyexperts-510/RealtyExperts-Daily-Email/main/RE-Daily-2-${dateForFile}.png" target="_blank" rel="noopener noreferrer" onclick="openLightbox(this.href); return false;" style="display: block; text-decoration: none; cursor: zoom-in;">
                      <img src="https://raw.githubusercontent.com/fremontrealtyexperts-510/RealtyExperts-Daily-Email/main/RE-Daily-2-${dateForFile}.png" alt="Market Analysis Chart (click to enlarge)" width="100%" class="clickable-image" style="display: block; max-width: 100%; height: auto; border: 1px solid ${PAL.hair}; cursor: zoom-in;">
                    </a>
                  </td>
                </tr>
              </table>
              <div style="text-align: center; font-family: ${SANS}; font-size: 12px; color: ${PAL.faint}; margin: 0 0 6px 0;">Click an image to enlarge it</div>

              <!-- LIVE INVENTORY strip: standing link to the harvrealtor.net
                   daily ledger (per Harv 2026-07-16: promote it inside the
                   daily post, not as a separate blog). Static and count-free
                   on purpose: emails cannot run scripts, and Stage 2 runs
                   before Stage 3 refreshes live-inventory.json. -->
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 14px 0 6px 0;">
                <tr>
                  <td style="background-color: ${PAL.paper}; border: 1px solid ${PAL.hair}; border-left: 3px solid ${PAL.gold}; padding: 18px 22px;">
                    <div style="font-family: ${SANS}; font-size: 11px; font-weight: 700; letter-spacing: 2.2px; color: ${PAL.goldDark}; margin-bottom: 8px;">TODAY'S LIVE INVENTORY</div>
                    <div style="font-family: ${SANS}; font-size: 14.5px; line-height: 1.6; color: ${PAL.soft}; margin-bottom: 12px;">Every home still for sale in Fremont, Hayward, Union City, Newark and Milpitas, one live ledger with prices, sizes and a market read, refreshed each morning from this same MLS export.</div>
                    <table role="presentation" cellpadding="0" cellspacing="0" border="0">
                      <tr>
                        <td bgcolor="${PAL.gold}" style="background-color: ${PAL.gold}; padding: 10px 18px;">
                          <a href="https://harvrealtor.net/live-inventory?utm_source=daily-email&amp;utm_medium=email&amp;utm_campaign=live-inventory" style="color: ${PAL.ink}; text-decoration: none; font-family: ${SANS}; font-weight: 700; font-size: 14px;">Browse the live ledger &rarr;</a>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>

              ${data.featured_promo ? `${sectionGap()}<!-- FEATURED PROMO -->
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 0 0 6px 0;">
                <tr>
                  <td bgcolor="${PAL.ink}" style="background-color: ${PAL.ink}; padding: 24px 26px; border-top: 3px solid ${PAL.gold};">
                    <div style="font-family: ${SANS}; font-size: 11px; font-weight: 700; letter-spacing: 2.2px; color: ${PAL.gold}; margin-bottom: 10px;">${String(data.featured_promo.eyebrow || '').toUpperCase()}</div>
                    <h2 style="margin: 0 0 12px 0; font-family: ${SERIF}; font-size: 23px; font-weight: 600; line-height: 1.3; color: #ffffff;">${data.featured_promo.title}</h2>
                    <div style="font-family: ${SANS}; font-size: 15px; line-height: 1.6; color: #EDEAE2; margin-bottom: 14px;">${data.featured_promo.body}</div>
                    ${data.featured_promo.quote ? `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 0 0 16px 0;"><tr><td style="border-left: 2px solid ${PAL.gold}; padding: 4px 0 4px 16px;"><div style="font-family: ${SERIF}; font-size: 15px; font-style: italic; line-height: 1.55; color: #ffffff;">"${data.featured_promo.quote}"</div><div style="font-family: ${SANS}; font-size: 12px; color: ${PAL.cardLabel}; margin-top: 6px;">${data.featured_promo.quote_attribution}</div></td></tr></table>` : ''}
                    <table role="presentation" cellpadding="0" cellspacing="0" border="0">
                      <tr>
                        <td bgcolor="${PAL.gold}" style="background-color: ${PAL.gold}; padding: 11px 20px;">
                          <a href="${data.featured_promo.primary_link}" style="color: ${PAL.ink}; text-decoration: none; font-family: ${SANS}; font-weight: 700; font-size: 14px;">${data.featured_promo.primary_label} &rarr;</a>
                        </td>
                        <td width="10"></td>
                        <td style="border: 1px solid ${PAL.gold}; padding: 10px 19px;">
                          <a href="${data.featured_promo.secondary_link}" style="color: ${PAL.gold}; text-decoration: none; font-family: ${SANS}; font-weight: 700; font-size: 14px;">${data.featured_promo.secondary_label} &rarr;</a>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>` : ''}

              ${sectionGap()}

              <!-- REAL ESTATE Section -->
              ${sectionHeader('01', 'REAL ESTATE', PAL.re)}
              ${data.real_estate.homebuilder ? `<div style="font-family: ${SERIF}; font-size: 18px; font-weight: 600; color: ${PAL.ink}; line-height: 1.45; margin: 0 0 16px 0;">${data.real_estate.homebuilder}</div>` : ''}
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 0 0 18px 0;">
                <tr>
                  <td width="48%" style="vertical-align: top;">
                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="${PAL.ink}" style="background-color: ${PAL.ink};">
                      <tr>
                        <td align="center" style="padding: 18px 12px;">
                          <div style="font-family: ${SANS}; font-size: 11px; font-weight: 600; color: ${PAL.cardLabel}; letter-spacing: 1.8px;">30-YEAR FIXED</div>
                          <div style="font-family: ${SERIF}; font-size: 34px; font-weight: 700; color: ${PAL.gold}; padding-top: 6px; white-space: nowrap;">${data.real_estate.rate_30year}</div>
                        </td>
                      </tr>
                    </table>
                  </td>
                  <td width="4%"></td>
                  <td width="48%" style="vertical-align: top;">
                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="${PAL.ink}" style="background-color: ${PAL.ink};">
                      <tr>
                        <td align="center" style="padding: 18px 12px;">
                          <div style="font-family: ${SANS}; font-size: 11px; font-weight: 600; color: ${PAL.cardLabel}; letter-spacing: 1.8px;">15-YEAR FIXED</div>
                          <div style="font-family: ${SERIF}; font-size: 34px; font-weight: 700; color: ${PAL.gold}; padding-top: 6px; white-space: nowrap;">${data.real_estate.rate_15year}</div>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
              ${formatCommentary(data.real_estate.commentary)}
              ${featureImagesHtml(data.real_estate)}

              ${sectionGap()}

              <!-- STOCKS Section -->
              ${sectionHeader('02', 'STOCKS', PAL.stocks)}
              ${statRow3([['S&amp;P 500', data.stocks.sp500], ['DOW', data.stocks.dow], ['NASDAQ', data.stocks.nasdaq]])}
              ${asOfNote(data.stocks.note)}
              ${formatCommentary(data.stocks.news)}
              ${featureImagesHtml(data.stocks)}

              ${sectionGap()}

              <!-- ECONOMY Section -->
              ${sectionHeader('03', 'ECONOMY', PAL.economy)}
              ${economyStatCards(data.economy)}
              ${asOfNote(data.economy.note)}
              ${formatCommentary(data.economy.commentary)}
              ${featureImagesHtml(data.economy)}

              ${data.crypto ? `${sectionGap()}

              <!-- CRYPTO Section -->
              ${sectionHeader('04', 'CRYPTO', PAL.crypto)}
              ${statRow3([['BTC', data.crypto.btc], ['ETH', data.crypto.eth], ['XRP', data.crypto.xrp]])}
              ${asOfNote(data.crypto.note)}
              ${formatCommentary(data.crypto.commentary)}
              ${featureImagesHtml(data.crypto)}` : ''}

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding: 0;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td bgcolor="${PAL.gold}" style="background-color: ${PAL.gold}; height: 2px; font-size: 1px; line-height: 1px;">&nbsp;</td>
                </tr>
              </table>
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="${PAL.paper}" style="background-color: ${PAL.paper};">
                <tr>
                  <td align="center" style="padding: 28px 30px;">
                    <p style="margin: 0 0 4px 0; font-family: ${SERIF}; font-size: 17px; font-weight: 600; color: ${PAL.ink}; letter-spacing: 0.5px;">REALTY EXPERTS®</p>
                    <p style="margin: 0 0 10px 0; font-family: ${SERIF}; font-style: italic; color: ${PAL.soft}; font-size: 13px;">"Our Experience is the Difference"</p>
                    <p style="margin: 0 0 12px 0; font-family: ${SANS}; color: ${PAL.faint}; font-size: 12px; letter-spacing: 0.8px;">DAILY MARKET GLANCE · ${new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }).toUpperCase()}</p>
                    <p style="margin: 0 0 18px 0; font-size: 13px;"><a href="https://TeamRealtyExperts.com" style="font-family: ${SANS}; color: ${PAL.goldDark}; text-decoration: none; font-weight: 700;">TeamRealtyExperts.com</a></p>
                    <p style="margin: 0; font-family: ${SANS}; color: ${PAL.faint}; font-size: 11px; line-height: 1.65; border-top: 1px solid ${PAL.hair}; padding-top: 14px;">Disclaimer: The market data, rates, and information provided in this email are for informational purposes only and should not be considered financial advice. Figures are sourced from third-party providers and may be delayed or subject to change. Always verify rates and data with your lender or financial advisor before making any decisions.</p>
                    <p style="margin: 10px 0 0 0; font-family: ${SANS}; color: ${PAL.faint}; font-size: 10px; line-height: 1.6;">
                      <em>Sources:</em><br>
                      ${generateSourceLinks(data.sources || [])}
                    </p>
                    <p style="margin: 10px 0 0 0; font-family: ${SANS}; color: ${PAL.faint}; font-size: 11px; line-height: 1.65;">If you would like to stop receiving this email, simply reply with <strong style="color: ${PAL.soft};">UNSUBSCRIBE</strong>.</p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

  <script>
    // Create lightbox overlay dynamically (prevents broken image in non-JS contexts)
    (function() {
      var overlay = document.createElement('div');
      overlay.id = 'lightbox';
      overlay.className = 'lightbox-overlay';
      overlay.setAttribute('role', 'dialog');
      overlay.setAttribute('aria-modal', 'true');
      overlay.setAttribute('aria-label', 'Enlarged image view');
      overlay.onclick = function() { closeLightbox(); };
      var btn = document.createElement('button');
      btn.className = 'lightbox-close';
      btn.setAttribute('aria-label', 'Close enlarged image');
      btn.onclick = function() { closeLightbox(); };
      btn.textContent = '×';
      var img = document.createElement('img');
      img.id = 'lightbox-img';
      img.className = 'lightbox-image';
      img.alt = 'Full screen view';
      overlay.appendChild(btn);
      overlay.appendChild(img);
      document.body.appendChild(overlay);
    })();

    function openLightbox(src) {
      document.getElementById('lightbox').classList.add('active');
      document.getElementById('lightbox-img').src = src;
      document.body.style.overflow = 'hidden';
    }

    function closeLightbox() {
      document.getElementById('lightbox').classList.remove('active');
      document.body.style.overflow = '';
    }

    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') {
        closeLightbox();
      }
    });
  </script>
</body>
</html>`;
}

// Main execution
const args = process.argv.slice(2);
const jsonFile = args[0] || 'daily-market-template.json';

if (!fs.existsSync(jsonFile)) {
  console.error(`Error: File "${jsonFile}" not found`);
  process.exit(1);
}

const data = loadData(jsonFile);
const html = generateHTML(data);
const dateForFile = data.date.replace(/\//g, '');
const outputFile = `daily-market-glance-${dateForFile}.html`;

fs.writeFileSync(outputFile, html);
console.log(`✅ Generated: ${outputFile}`);
console.log(`📧 Subject: "At a Glance" Local Housing STATS and News ${data.date}`);
console.log(`🌐 Web View: https://fremontrealtyexperts-510.github.io/RealtyExperts-Daily-Email/${outputFile}`);
