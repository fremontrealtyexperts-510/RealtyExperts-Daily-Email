#!/usr/bin/env node
/**
 * sync-app-report-rates.mjs — keep the HarvRealtor app's rate tiles on the day's
 * own figure.
 *
 * WHY THIS EXISTS: daily-report.json is written at about 8:45 AM PT, and at that
 * hour Mortgage News Daily has only published the PREVIOUS business day's figure.
 * The app's Today's Report screen (App Store build 12) renders the report's own
 * rates block, so it printed September 16's 7.24% under a September 17 masthead
 * all day while Home and Tools, which read harvrealtor.net/api/mortgage-rates,
 * showed 7.19%. Harv caught it on launch day, 2026-09-17. Build 13 fixes it
 * inside the app; this keeps the LIVE build right without an App Store review.
 *
 * WHAT IT DOES: once MND posts the figure for the report's OWN date, it rewrites
 * the two tiles and the one line under them. Harv's headline, teaser, prose and
 * stat chips are NEVER touched: they quote the pair the report was written at,
 * and the line under the tiles says so. That is the same rule build 13 ships
 * (src/lib/reportRates.ts in the app repo), so the two agree.
 *
 * SAFE TO RUN ANY TIME. It exits without writing unless every one of these holds:
 *   - the published report is for today, Pacific
 *   - MND's own figure is for that same day
 *   - both rates parse and sit in a plausible mortgage band
 *   - the numbers actually differ from what the file already carries
 * Every other outcome is a no-op, so a scheduled run costs one HTTP GET.
 *
 * Writes `changed=true|false` to $GITHUB_OUTPUT when running under Actions.
 */

import { readFileSync, writeFileSync, renameSync, appendFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

const REPORT_PATH = fileURLToPath(new URL('../daily-report.json', import.meta.url))

const MND_URL = 'https://widgets.mortgagenewsdaily.com/Widget/Rates?user=2101&type=smallrates'
const MND_REFERER = 'https://widgets.mortgagenewsdaily.com/widget/f/rates'
const SOURCE_NAME = 'Mortgage News Daily'
const FETCH_TIMEOUT_MS = 10000

/* ---- Pacific time. Harv's rule: every date and time is California time. ---- */

/** Today in Pacific as "2026-09-17". en-CA formats ISO order, which is why it is used here. */
function pacificISO(now = new Date()) {
  return new Intl.DateTimeFormat('en-CA', {
    timeZone: 'America/Los_Angeles',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(now)
}

/** "September 17", for the line under the tiles. */
function pacificLongDay(iso) {
  const [y, m, d] = iso.split('-').map(Number)
  const MONTHS = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December',
  ]
  return `${MONTHS[m - 1]} ${d}`
}

/** "10:15 AM PT". */
function pacificClock(now = new Date()) {
  const t = new Intl.DateTimeFormat('en-US', {
    timeZone: 'America/Los_Angeles',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  }).format(now)
  return `${t} PT`
}

/** MND writes "9/17/2026 12:00:00 AM"; this returns "2026-09-17", or null. */
function mndDateToISO(v) {
  const m = String(v || '').match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})/)
  if (!m) return null
  const [, mo, d, y] = m
  if (Number(mo) < 1 || Number(mo) > 12 || Number(d) < 1 || Number(d) > 31) return null
  return `${y}-${String(mo).padStart(2, '0')}-${String(d).padStart(2, '0')}`
}

/* ---- The source ---- */

async function fetchMnd() {
  const ctrl = new AbortController()
  const timer = setTimeout(() => ctrl.abort(), FETCH_TIMEOUT_MS)
  try {
    const res = await fetch(MND_URL, {
      signal: ctrl.signal,
      headers: {
        'User-Agent':
          'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 ' +
          '(KHTML, like Gecko) Chrome/126.0 Safari/537.36 HarvRealtorRates/1.0',
        Accept: 'application/json,text/javascript,*/*',
        Referer: MND_REFERER,
      },
    })
    if (!res.ok) throw new Error(`MND HTTP ${res.status}`)
    const json = await res.json()
    if (!Array.isArray(json)) throw new Error('MND payload is not an array')
    return json
  } finally {
    clearTimeout(timer)
  }
}

/**
 * The one row for a product key, checked hard. `change` keeps MND's sign: the
 * app's deltaOf() reads the sign to pick the arrow, so an unsigned value would
 * point every move upward.
 */
function row(items, productKey) {
  const it = items.find((x) => x && String(x.productKey || '').toUpperCase() === productKey)
  if (!it) return null
  const rate = Number(it.rate)
  if (!Number.isFinite(rate) || rate <= 2 || rate >= 12) return null
  const changeRaw = Number(it.change)
  const change = Number.isFinite(changeRaw) && Math.abs(changeRaw) < 2 ? Number(changeRaw.toFixed(2)) : null
  return { rate: Number(rate.toFixed(2)), change, dateISO: mndDateToISO(it.date || it.RateDate) }
}

/* ---- Harv's copy rules ---- */

/** No em dashes and no en dashes in anything a client reads. */
function assertNoDashes(s) {
  if (/[—–]/.test(s)) throw new Error(`dash in user facing copy: ${s}`)
  return s
}

const same = (a, b) => Number(a).toFixed(2) === Number(b).toFixed(2)

function out(changed, why) {
  console.log(`${changed ? 'CHANGED' : 'no change'}: ${why}`)
  if (process.env.GITHUB_OUTPUT) {
    appendFileSync(process.env.GITHUB_OUTPUT, `changed=${changed ? 'true' : 'false'}\n`)
  }
}

async function main() {
  const report = JSON.parse(readFileSync(REPORT_PATH, 'utf8'))
  const today = pacificISO()

  if (report.dateISO !== today) {
    out(false, `published report is ${report.dateISO}, today is ${today} PT`)
    return
  }

  const items = await fetchMnd()
  const r30 = row(items, '30YRFRM')
  const r15 = row(items, '15YRFRM')
  if (!r30 || !r15) {
    out(false, 'MND did not return a usable 30 year and 15 year row')
    return
  }
  if (r30.dateISO !== today || r15.dateISO !== today) {
    out(false, `MND is still on ${r30.dateISO}, waiting for ${today}`)
    return
  }

  const b = report.rates
  if (!b || !Number.isFinite(b.r30) || !Number.isFinite(b.r15)) {
    throw new Error('daily-report.json has no usable rates block; refusing to touch it')
  }
  if (same(b.r30, r30.rate) && same(b.r15, r15.rate)) {
    out(false, `tiles already carry MND's ${today} figure (${r30.rate}% and ${r15.rate}%)`)
    return
  }

  /* The pair the report was WRITTEN at, kept once so a second run of the day
     still credits the prose correctly, and so build 13's pickRates can read it
     instead of re-deriving it. */
  const written = report.rates.written || {
    r30: b.r30,
    r30Change: b.r30Change ?? null,
    r15: b.r15,
    r15Change: b.r15Change ?? null,
  }

  const note = `${SOURCE_NAME}, the latest for ${pacificLongDay(today)}, updated ${pacificClock()}.`
  const writtenNote = ` This report was written before that update, at ${written.r30.toFixed(2)}% and ${written.r15.toFixed(2)}%`
  const source = assertNoDashes(note + writtenNote)

  report.rates = {
    ...b,
    r30: r30.rate,
    r30Change: r30.change,
    r15: r15.rate,
    r15Change: r15.change,
    source,
    sourceUrl: b.sourceUrl,
    asOf: today,
    updatedAt: new Date().toISOString(),
    written,
  }

  /* The app refuses a payload that fails its own validator, and then silently
     shows a baked seed. Re-check the fields it reads before writing. */
  const r = report.rates
  const ok =
    Number.isFinite(r.r30) &&
    Number.isFinite(r.r15) &&
    (r.r30Change === null || Number.isFinite(r.r30Change)) &&
    (r.r15Change === null || Number.isFinite(r.r15Change)) &&
    typeof r.source === 'string' &&
    typeof r.sourceUrl === 'string'
  if (!ok) throw new Error('patched rates block would fail the app validator')

  /* Byte for byte the shape generate-app-report.js writes: minified, no trailing
     newline, written to a temp file and renamed so a reader never sees half a
     file. Anything else would churn the whole file on every run and flip back and
     forth with the generator. */
  const json = JSON.stringify(report)
  JSON.parse(json)
  writeFileSync(`${REPORT_PATH}.tmp`, json)
  renameSync(`${REPORT_PATH}.tmp`, REPORT_PATH)
  out(true, `${written.r30.toFixed(2)}% -> ${r30.rate.toFixed(2)}%, ${written.r15.toFixed(2)}% -> ${r15.rate.toFixed(2)}%`)
}

main().catch((err) => {
  console.error(`rate sync failed: ${err && err.message ? err.message : err}`)
  process.exit(1)
})
