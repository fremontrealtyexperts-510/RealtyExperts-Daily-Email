/*
 * live-inventory-teaser.js
 *
 * Keeps the harvrealtor.com "Live Inventory" teaser page's counts current.
 * Loaded via <script src> from the teaser body (Drupal strips inline
 * scripts; external files from this GitHub Pages origin are the established
 * pattern, same as alameda-chart-*.js).
 *
 * Reads live-inventory.json from this same origin and swaps the baked
 * counts and as-of date in place. Every failure path leaves the baked
 * numbers (which carry their own honest as-of date) untouched.
 */
(function () {
  "use strict";

  var FEED = "https://fremontrealtyexperts-510.github.io/RealtyExperts-Daily-Email/live-inventory.json";
  var MONTHS = ["January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"];

  function setText(id, text) {
    var el = document.getElementById(id);
    if (el) el.textContent = text;
  }

  function label(mdy) {
    var m = /^(\d{2})\/(\d{2})\/(\d{2})$/.exec(String(mdy || ""));
    if (!m) return null;
    var mo = parseInt(m[1], 10);
    if (mo < 1 || mo > 12) return null;
    return MONTHS[mo - 1] + " " + parseInt(m[2], 10) + ", 20" + m[3];
  }

  function apply(data) {
    if (!data || data.version !== 1 || !Array.isArray(data.listings)) return;
    // Count EVERY city the feed carries; do not hardcode the roster. Milpitas was
    // added to live-inventory.json on 2026-07-18 but this list was not updated, so
    // the strip read 627 while harvrealtor.net/live-inventory and the daily report
    // both said 733 (caught 2026-07-20). Deriving the roster from the feed means the
    // next city added cannot silently desync the total again.
    //
    // The totals come from the feed's per-city `counts` (every live status,
    // Coming Soon included). Since 2026-09-02 the `listings` array itemizes only
    // the rows the MLS rules allow on a public page (no Coming Soon), so counting
    // the array would understate the market by the Coming Soon homes. The row
    // count is only a fallback for a feed without `counts`.
    var counts = {};
    var fed = data.counts && typeof data.counts === "object" ? data.counts : null;
    if (fed) {
      for (var k0 in fed) {
        if (fed.hasOwnProperty(k0) && fed[k0] && typeof fed[k0].total === "number") {
          counts[k0] = fed[k0].total;
        }
      }
    } else {
      for (var i = 0; i < data.listings.length; i++) {
        var city = data.listings[i] && data.listings[i].city;
        if (!city) continue;
        counts[city] = (counts[city] || 0) + 1;
      }
    }
    var total = 0;
    for (var k in counts) { if (counts.hasOwnProperty(k)) total += counts[k]; }
    if (total < 50) return;
    var asOf = label(data.date);

    setText("hb-li-total", String(total));
    setText("hb-li-fremont", String(counts.Fremont || 0));
    setText("hb-li-hayward", String(counts.Hayward || 0));
    setText("hb-li-unioncity", String(counts["Union City"] || 0));
    setText("hb-li-newark", String(counts.Newark || 0));
    setText("hb-li-milpitas", String(counts.Milpitas || 0));
    if (asOf) setText("hb-li-asof", asOf);
  }

  function run() {
    try {
      var xhr = new XMLHttpRequest();
      xhr.open("GET", FEED, true);
      xhr.timeout = 8000;
      xhr.onload = function () {
        if (xhr.status !== 200) return;
        try { apply(JSON.parse(xhr.responseText)); } catch (e) { /* keep baked */ }
      };
      xhr.send();
    } catch (e) { /* keep baked */ }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }
})();
