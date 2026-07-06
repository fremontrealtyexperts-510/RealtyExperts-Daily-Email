#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

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
        .slice(0, 30);

      return topic ? `${publisher} - ${topic}` : publisher;
    } catch {
      return url.slice(0, 40);
    }
  }

  return sources
    .map(url => `<a href="${url}" style="color: #94a3b8; text-decoration: none;">${labelFromUrl(url)}</a>`)
    .join(' · \n                      ');
}

// Format commentary text with proper paragraphs and bullets
function formatCommentary(text) {
  // Split by double newlines for paragraphs
  const paragraphs = text.split('\n\n');

  return paragraphs.map(para => {
    // Check if paragraph contains bullet points
    if (para.includes('•')) {
      const lines = para.split('\n');
      let html = '';
      let isFirstLine = true;

      lines.forEach(line => {
        const trimmed = line.trim();
        if (trimmed.startsWith('•')) {
          // Check if this bullet point has a bold label (ends with :)
          const colonMatch = trimmed.match(/^• ([^:]+):(.*)/);
          if (colonMatch) {
            html += `<div style="margin: 10px 0 6px 0; line-height: 1.8;"><strong style="color: #1e293b;">• ${colonMatch[1]}:</strong>${colonMatch[2]}</div>`;
          } else {
            html += `<div style="margin: 6px 0; padding-left: 0; line-height: 1.8;">${trimmed}</div>`;
          }
        } else if (trimmed.startsWith('📍')) {
          const locColonMatch = trimmed.match(/^(📍[^:]+:)(.*)/);
          if (locColonMatch) {
            html += `<div style="margin: 20px 0 6px 0; line-height: 1.8; color: #1e293b;"><strong style="font-size: 16px;">${locColonMatch[1]}</strong>${locColonMatch[2]}</div>`;
          } else {
            html += `<div style="margin: 20px 0 12px 0; font-weight: 700; font-size: 16px; line-height: 1.6; color: #1e293b;">${trimmed}</div>`;
          }
        } else if (trimmed.startsWith('o ')) {
          // Nested list items (open houses, etc) - normal weight
          html += `<div style="margin: 6px 0; padding-left: 20px; line-height: 1.8; color: #334155;">${trimmed}</div>`;
        } else if (trimmed) {
          // Headers ending with colon should be bold
          if (trimmed.endsWith(':')) {
            html += `<div style="margin: 0 0 10px 0; line-height: 1.8; font-weight: 700; color: #1e293b;">${trimmed}</div>`;
          } else {
            html += `<div style="margin: 10px 0; line-height: 1.8; font-weight: 600;">${trimmed}</div>`;
          }
        }
        if (trimmed) isFirstLine = false;
      });
      return html;
    } else {
      // Check if this paragraph is a location marker or header
      const trimmed = para.trim();
      if (trimmed.startsWith('📍')) {
        const locColonMatch = trimmed.match(/^(📍[^:]+:)(.*)/);
        if (locColonMatch) {
          return `<div style="margin: 20px 0 6px 0; line-height: 1.8; color: #1e293b;"><strong style="font-size: 16px;">${locColonMatch[1]}</strong>${locColonMatch[2]}</div>`;
        }
        return `<div style="margin: 20px 0 12px 0; font-weight: 700; font-size: 16px; line-height: 1.6; color: #1e293b;">${trimmed}</div>`;
      } else if (trimmed.endsWith(':')) {
        return `<div style="margin: 0 0 10px 0; line-height: 1.8; font-weight: 700; color: #1e293b;">${trimmed}</div>`;
      }
      return `<div style="margin: 0 0 16px 0; line-height: 1.8;">${trimmed}</div>`;
    }
  }).join('');
}

// Add up/down arrow indicators to values with percentages
function addArrow(value) {
  if (value.includes('+')) {
    return '▲ ' + value;
  } else if (value.includes('-')) {
    return '▼ ' + value;
  }
  return value;
}

// Get value color based on +/- indicator
function valueColor(value) {
  if (!value) return '#1e293b';
  if (value.includes('+')) return '#16a34a';
  if (value.includes('-')) return '#dc2626';
  return '#1e293b';
}

// Build the ECONOMY stat-card row.
// Gold AND Silver are MANDATORY in every report (live-search them when the
// newsletter omits them — see CLAUDE.md "Gold + Silver" rule). A 4th card
// (Brent Crude via wti/oil_label, or CPI via cpi/cpi_label) is an optional
// rotating extra and must never replace gold or silver. Renders 3 or 4 cards.
function economyStatCards(e) {
  const cards = [
    { label: 'US 10-Year', value: e.us10year },
    { label: e.gold_label || 'Gold', value: e.gold },
    { label: e.silver_label || 'Silver', value: e.silver },
  ];
  if (e.wti) cards.push({ label: e.oil_label || 'WTI Crude', value: e.wti });
  else if (e.cpi) cards.push({ label: e.cpi_label || 'CPI (YoY)', value: e.cpi });

  const four = cards.length >= 4;
  const cellW = four ? '23%' : '32%';
  const spacerW = four ? '2.6%' : '2%';

  const cell = (c) => `<td width="${cellW}" style="vertical-align: top;">
                          <table role="presentation" width="100%" cellpadding="12" cellspacing="0" border="0" style="background-color: #f0fdf4; border-left: 4px solid #16a34a;">
                            <tr>
                              <td>
                                <div style="font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">${c.label}</div>
                                <div style="font-size: 17px; font-weight: 700; white-space: nowrap; color: ${valueColor(c.value || '')};">${addArrow(c.value || 'n/a')}</div>
                              </td>
                            </tr>
                          </table>
                        </td>`;

  const cells = cards.map(cell).join(`\n                        <td width="${spacerW}"></td>\n                        `);

  return `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 12px 0;">
                      <tr>
                        ${cells}
                      </tr>
                    </table>`;
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
                            <img src="${fi.url}" alt="${fi.alt || ''}" width="100%" class="clickable-image" style="display: block; max-width: 100%; height: auto; border: 1px solid #e2e8f0; cursor: zoom-in;">
                          </a>
                        </td>
                      </tr>
                      ${fi.caption ? `<tr><td style="padding: 10px 4px 0 4px; font-size: 13px; color: #475569; line-height: 1.55; font-style: italic;">${fi.caption}</td></tr>` : ''}
                      ${fi.source ? `<tr><td style="padding: 4px 4px 0 4px; font-size: 11px; color: #94a3b8;">${fi.source}</td></tr>` : ''}
                    </table>`).join('\n');
}

// Generate HTML with inline styles for Outlook compatibility
function generateHTML(data) {
  // Format date for filenames (MMDDYY)
  const dateForFile = data.date.replace(/\//g, '');
  const htmlFileName = `daily-market-glance-${dateForFile}.html`;
  const githubBaseUrl = 'https://fremontrealtyexperts-510.github.io/RealtyExperts-Daily-Email';

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
        padding: 16px !important;
      }
      .email-header {
        padding: 24px 16px !important;
      }
      .email-hub {
        padding: 16px !important;
      }
    }
  </style>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, Helvetica, sans-serif; background-color: #f0f4f8;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f0f4f8;">
    <tr>
      <td align="center" style="padding: 20px 0;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" class="email-container" style="background-color: #ffffff; max-width: 650px;">

          <!-- View in Browser Link -->
          <tr>
            <td style="background-color: #f1f5f9; padding: 12px 20px; text-align: center; border-bottom: 1px solid #e2e8f0;">
              <p style="margin: 0; font-size: 13px; color: #64748b;">
                Having trouble viewing this email? <a href="${githubBaseUrl}/${htmlFileName}" style="color: #2563eb; text-decoration: none; font-weight: 600;">View in Browser</a>
              </p>
            </td>
          </tr>

          <!-- Header -->
          <tr>
            <td class="email-header" style="background-color: #2563eb; padding: 30px 40px; text-align: center;">
              <img src="https://raw.githubusercontent.com/fremontrealtyexperts-510/RealtyExperts-Daily-Email/main/2022_Logo_WhiteBox-Realtor.jpg" alt="REALTY EXPERTS®" width="250" data-no-lightbox style="display: block; margin: 0 auto 15px; max-width: 100%; height: auto;">
              <h1 style="margin: 0 0 8px 0; font-size: 28px; font-weight: 700; color: #ffffff;">Daily Market Glance</h1>
              <p style="margin: 0; font-size: 14px; color: rgba(255,255,255,0.9);">${data.date} - ${data.time}</p>
            </td>
          </tr>

          <!-- Agent Hub Banner -->
          <tr>
            <td class="email-hub" style="background-color: #f8fafc; padding: 20px 40px; border-bottom: 2px solid #e2e8f0;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td width="70%" style="vertical-align: middle; padding-right: 20px;">
                    <div style="font-size: 15px; color: #1e293b; line-height: 1.6;">
                      <strong style="font-size: 16px;">📱 <a href="${data.agent_hub_link}" style="color: #2563eb; text-decoration: none;">View Full Post on Agent Hub</a></strong>
                      <div style="margin-top: 8px; color: #475569;">
                        Scan the QR code or visit our Agent Hub for the complete market update. Contact the front desk for your access code.
                      </div>
                    </div>
                  </td>
                  <td width="30%" style="vertical-align: middle; text-align: center;">
                    <img src="https://raw.githubusercontent.com/fremontrealtyexperts-510/RealtyExperts-Daily-Email/main/${data.qr_code_path}" alt="Agent Hub QR Code" width="100" data-no-lightbox style="display: block; margin: 0 auto; max-width: 100px; height: auto;">
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Content -->
          <tr>
            <td class="email-body" style="padding: 40px;">

              <!-- Image 1 -->
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 0 0 24px 0;">
                <tr>
                  <td align="center">
                    <a href="https://raw.githubusercontent.com/fremontrealtyexperts-510/RealtyExperts-Daily-Email/main/RE-Daily-1-${dateForFile}.png" target="_blank" rel="noopener noreferrer" onclick="openLightbox(this.href); return false;" style="display: block; text-decoration: none; cursor: zoom-in;">
                      <img src="https://raw.githubusercontent.com/fremontrealtyexperts-510/RealtyExperts-Daily-Email/main/RE-Daily-1-${dateForFile}.png" alt="Local Housing Statistics (click to enlarge)" width="100%" class="clickable-image" style="display: block; max-width: 100%; height: auto; cursor: zoom-in;">
                    </a>
                  </td>
                </tr>
              </table>

              <!-- Image 2 -->
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 0 0 35px 0;">
                <tr>
                  <td align="center">
                    <a href="https://raw.githubusercontent.com/fremontrealtyexperts-510/RealtyExperts-Daily-Email/main/RE-Daily-2-${dateForFile}.png" target="_blank" rel="noopener noreferrer" onclick="openLightbox(this.href); return false;" style="display: block; text-decoration: none; cursor: zoom-in;">
                      <img src="https://raw.githubusercontent.com/fremontrealtyexperts-510/RealtyExperts-Daily-Email/main/RE-Daily-2-${dateForFile}.png" alt="Market Analysis Chart (click to enlarge)" width="100%" class="clickable-image" style="display: block; max-width: 100%; height: auto; cursor: zoom-in;">
                    </a>
                  </td>
                </tr>
              </table>

              ${data.featured_promo ? `<!-- FEATURED PROMO -->
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 0 0 32px 0;">
                <tr>
                  <td style="background-color: #0d9488; padding: 22px 24px; border-left: 6px solid #f97316;">
                    <div style="font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #ffffff; opacity: 0.9; margin-bottom: 8px;">${data.featured_promo.eyebrow}</div>
                    <h2 style="margin: 0 0 12px 0; font-size: 22px; font-weight: 800; line-height: 1.25; color: #ffffff;">${data.featured_promo.title}</h2>
                    <div style="font-size: 15px; line-height: 1.6; color: #ffffff; margin-bottom: 14px;">${data.featured_promo.body}</div>
                    ${data.featured_promo.quote ? `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 0 0 16px 0;"><tr><td style="background-color: rgba(255,255,255,0.12); padding: 14px 18px; border-left: 3px solid #f97316;"><div style="font-size: 14px; font-style: italic; line-height: 1.55; color: #ffffff;">"${data.featured_promo.quote}"</div><div style="font-size: 12px; color: #fed7aa; margin-top: 6px;">${data.featured_promo.quote_attribution}</div></td></tr></table>` : ''}
                    <table role="presentation" cellpadding="0" cellspacing="0" border="0">
                      <tr>
                        <td style="background-color: #f97316; padding: 11px 20px;">
                          <a href="${data.featured_promo.primary_link}" style="color: #ffffff; text-decoration: none; font-weight: 700; font-size: 14px;">${data.featured_promo.primary_label} →</a>
                        </td>
                        <td width="10"></td>
                        <td style="background-color: #ffffff; padding: 11px 20px;">
                          <a href="${data.featured_promo.secondary_link}" style="color: #0d9488; text-decoration: none; font-weight: 700; font-size: 14px;">${data.featured_promo.secondary_label} →</a>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>` : ''}

              <!-- REAL ESTATE Section -->
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom: 10px;">
                <tr>
                  <td>
                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
                      <tr>
                        <td style="background-color: #ea580c; padding: 14px 20px;">
                          <h2 style="margin: 0; font-size: 20px; font-weight: 700; color: #ffffff;">
                            🏠 REAL ESTATE
                          </h2>
                        </td>
                      </tr>
                    </table>
                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 12px 0;">
                      <tr>
                        <td width="48%" style="vertical-align: top;">
                          <table role="presentation" width="100%" cellpadding="16" cellspacing="0" border="0" style="background-color: #ea580c; text-align: center;">
                            <tr>
                              <td>
                                <div style="font-size: 13px; font-weight: 600; color: rgba(255,255,255,0.85); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">30-Year Fixed</div>
                                <div style="font-size: 32px; font-weight: 700; color: #ffffff;">${data.real_estate.rate_30year}</div>
                              </td>
                            </tr>
                          </table>
                        </td>
                        <td width="4%"></td>
                        <td width="48%" style="vertical-align: top;">
                          <table role="presentation" width="100%" cellpadding="16" cellspacing="0" border="0" style="background-color: #ea580c; text-align: center;">
                            <tr>
                              <td>
                                <div style="font-size: 13px; font-weight: 600; color: rgba(255,255,255,0.85); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">15-Year Fixed</div>
                                <div style="font-size: 32px; font-weight: 700; color: #ffffff;">${data.real_estate.rate_15year}</div>
                              </td>
                            </tr>
                          </table>
                        </td>
                      </tr>
                    </table>
                    <table role="presentation" width="100%" cellpadding="16" cellspacing="0" border="0" style="background-color: #fff7ed; border-top: 4px solid #ea580c;">
                      <tr>
                        <td style="font-size: 15px; color: #334155;">
                          ${formatCommentary(data.real_estate.homebuilder)}
                          ${formatCommentary(data.real_estate.commentary)}
                        </td>
                      </tr>
                    </table>
                    ${featureImagesHtml(data.real_estate)}
                  </td>
                </tr>
              </table>

              <!-- Section Divider -->
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 10px 0;">
                <tr><td style="border-bottom: 1px solid #e2e8f0; font-size: 1px; height: 1px;">&nbsp;</td></tr>
              </table>

              <!-- STOCKS Section -->
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom: 10px;">
                <tr>
                  <td>
                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
                      <tr>
                        <td style="background-color: #2563eb; padding: 14px 20px;">
                          <h2 style="margin: 0; font-size: 20px; font-weight: 700; color: #ffffff;">
                            📈 STOCKS
                          </h2>
                        </td>
                      </tr>
                    </table>
                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 12px 0;">
                      <tr>
                        <td width="32%" style="vertical-align: top;">
                          <table role="presentation" width="100%" cellpadding="12" cellspacing="0" border="0" style="background-color: #eff6ff; border-left: 4px solid #2563eb;">
                            <tr>
                              <td>
                                <div style="font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">S&amp;P 500</div>
                                <div style="font-size: 17px; font-weight: 700; white-space: nowrap; color: ${valueColor(data.stocks.sp500)};">${addArrow(data.stocks.sp500)}</div>
                              </td>
                            </tr>
                          </table>
                        </td>
                        <td width="2%"></td>
                        <td width="32%" style="vertical-align: top;">
                          <table role="presentation" width="100%" cellpadding="12" cellspacing="0" border="0" style="background-color: #eff6ff; border-left: 4px solid #2563eb;">
                            <tr>
                              <td>
                                <div style="font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">DOW</div>
                                <div style="font-size: 17px; font-weight: 700; white-space: nowrap; color: ${valueColor(data.stocks.dow)};">${addArrow(data.stocks.dow)}</div>
                              </td>
                            </tr>
                          </table>
                        </td>
                        <td width="2%"></td>
                        <td width="32%" style="vertical-align: top;">
                          <table role="presentation" width="100%" cellpadding="12" cellspacing="0" border="0" style="background-color: #eff6ff; border-left: 4px solid #2563eb;">
                            <tr>
                              <td>
                                <div style="font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">NASDAQ</div>
                                <div style="font-size: 17px; font-weight: 700; white-space: nowrap; color: ${valueColor(data.stocks.nasdaq)};">${addArrow(data.stocks.nasdaq)}</div>
                              </td>
                            </tr>
                          </table>
                        </td>
                      </tr>
                    </table>
                    <div style="font-size: 12px; color: #64748b; font-style: italic; margin-bottom: 12px;">${data.stocks.note}</div>
                    <table role="presentation" width="100%" cellpadding="16" cellspacing="0" border="0" style="background-color: #eff6ff; border-top: 4px solid #2563eb;">
                      <tr>
                        <td style="font-size: 15px; color: #334155;">${formatCommentary(data.stocks.news)}</td>
                      </tr>
                    </table>
                    ${featureImagesHtml(data.stocks)}
                  </td>
                </tr>
              </table>

              <!-- Section Divider -->
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 10px 0;">
                <tr><td style="border-bottom: 1px solid #e2e8f0; font-size: 1px; height: 1px;">&nbsp;</td></tr>
              </table>

              <!-- ECONOMY Section -->
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom: 10px;">
                <tr>
                  <td>
                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
                      <tr>
                        <td style="background-color: #16a34a; padding: 14px 20px;">
                          <h2 style="margin: 0; font-size: 20px; font-weight: 700; color: #ffffff;">
                            💰 ECONOMY
                          </h2>
                        </td>
                      </tr>
                    </table>
                    ${economyStatCards(data.economy)}
                    ${data.economy.note ? `<div style="font-size: 12px; color: #64748b; font-style: italic; margin-bottom: 12px;">${data.economy.note}</div>` : ''}
                    <table role="presentation" width="100%" cellpadding="16" cellspacing="0" border="0" style="background-color: #f0fdf4; border-top: 4px solid #16a34a;">
                      <tr>
                        <td style="font-size: 15px; color: #334155;">${formatCommentary(data.economy.commentary)}</td>
                      </tr>
                    </table>
                    ${featureImagesHtml(data.economy)}
                  </td>
                </tr>
              </table>

              ${data.crypto ? `<!-- Section Divider -->
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 10px 0;">
                <tr><td style="border-bottom: 1px solid #e2e8f0; font-size: 1px; height: 1px;">&nbsp;</td></tr>
              </table>

              <!-- CRYPTO Section -->
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom: 10px;">
                <tr>
                  <td>
                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
                      <tr>
                        <td style="background-color: #f59e0b; padding: 14px 20px;">
                          <h2 style="margin: 0; font-size: 20px; font-weight: 700; color: #ffffff;">
                            ₿ CRYPTO
                          </h2>
                        </td>
                      </tr>
                    </table>
                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 12px 0;">
                      <tr>
                        <td width="32%" style="vertical-align: top;">
                          <table role="presentation" width="100%" cellpadding="12" cellspacing="0" border="0" style="background-color: #fffbeb; border-left: 4px solid #f59e0b;">
                            <tr>
                              <td>
                                <div style="font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">BTC</div>
                                <div style="font-size: 17px; font-weight: 700; white-space: nowrap; color: ${valueColor(data.crypto.btc)};">${addArrow(data.crypto.btc)}</div>
                              </td>
                            </tr>
                          </table>
                        </td>
                        <td width="2%"></td>
                        <td width="32%" style="vertical-align: top;">
                          <table role="presentation" width="100%" cellpadding="12" cellspacing="0" border="0" style="background-color: #fffbeb; border-left: 4px solid #f59e0b;">
                            <tr>
                              <td>
                                <div style="font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">ETH</div>
                                <div style="font-size: 17px; font-weight: 700; white-space: nowrap; color: ${valueColor(data.crypto.eth)};">${addArrow(data.crypto.eth)}</div>
                              </td>
                            </tr>
                          </table>
                        </td>
                        <td width="2%"></td>
                        <td width="32%" style="vertical-align: top;">
                          <table role="presentation" width="100%" cellpadding="12" cellspacing="0" border="0" style="background-color: #fffbeb; border-left: 4px solid #f59e0b;">
                            <tr>
                              <td>
                                <div style="font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">XRP</div>
                                <div style="font-size: 17px; font-weight: 700; white-space: nowrap; color: ${valueColor(data.crypto.xrp)};">${addArrow(data.crypto.xrp)}</div>
                              </td>
                            </tr>
                          </table>
                        </td>
                      </tr>
                    </table>
                    ${data.crypto.note ? `<div style="font-size: 12px; color: #64748b; font-style: italic; margin-bottom: 12px;">${data.crypto.note}</div>` : ''}
                    <table role="presentation" width="100%" cellpadding="16" cellspacing="0" border="0" style="background-color: #fffbeb; border-top: 4px solid #f59e0b;">
                      <tr>
                        <td style="font-size: 15px; color: #334155;">${formatCommentary(data.crypto.commentary)}</td>
                      </tr>
                    </table>
                    ${featureImagesHtml(data.crypto)}
                  </td>
                </tr>
              </table>` : ''}

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding: 0;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td style="background-color: #2563eb; height: 4px; font-size: 1px;">&nbsp;</td>
                </tr>
              </table>
              <table role="presentation" width="100%" cellpadding="24" cellspacing="0" border="0" style="background-color: #f8fafc;">
                <tr>
                  <td style="text-align: center;">
                    <p style="margin: 0 0 8px 0; font-weight: 600; color: #2563eb; font-size: 14px;">REALTY EXPERTS®</p>
                    <p style="margin: 0 0 8px 0; color: #64748b; font-size: 13px;">"Our Experience is the Difference"</p>
                    <p style="margin: 0 0 12px 0; color: #64748b; font-size: 13px;">Daily Market Glance · ${new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}</p>
                    <p style="margin: 0 0 16px 0; color: #2563eb; font-size: 13px;"><a href="https://TeamRealtyExperts.com" style="color: #2563eb; text-decoration: none; font-weight: 600;">TeamRealtyExperts.com</a></p>
                    <p style="margin: 0; color: #94a3b8; font-size: 11px; line-height: 1.6; border-top: 1px solid #e2e8f0; padding-top: 14px;">Disclaimer: The market data, rates, and information provided in this email are for informational purposes only and should not be considered financial advice. Figures are sourced from third-party providers and may be delayed or subject to change. Always verify rates and data with your lender or financial advisor before making any decisions.</p>
                    <p style="margin: 10px 0 0 0; color: #94a3b8; font-size: 10px; line-height: 1.5;">
                      <em>Sources:</em><br>
                      ${generateSourceLinks(data.sources || [])}
                    </p>
                    <p style="margin: 10px 0 0 0; color: #94a3b8; font-size: 11px; line-height: 1.6;">If you would like to stop receiving this email, simply reply with <strong style="color: #64748b;">UNSUBSCRIBE</strong>.</p>
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
      btn.textContent = '\u00D7';
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
