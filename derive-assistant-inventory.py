#!/usr/bin/env python3
"""
derive-assistant-inventory.py

Derives assistant-inventory.json (compact, ~3KB) from live-inventory.json.
Consumed by the harvbalu.homes AI assistant's n8n get_inventory tool, which
feeds it directly into an LLM prompt, hence the compaction.

Since 2026-09-02 the source feed is version 2, statistics only (no
per-listing rows: the Bay East MLS Rules keep the per-listing compilation
off public surfaces), so everything here is read from the feed's per-city
`counts` and `market` blocks. Called by refresh-live-inventory.sh after
generate-live-inventory.js on every publish run. Safe to run by hand:
./derive-assistant-inventory.py. Reads ./live-inventory.json, writes
./assistant-inventory.json. Exits non-zero without writing anything if the
source looks wrong, so a bad run can never replace a good published file.
"""
import json
import sys
from datetime import datetime, timezone

TYPE_LABELS = {"DE": "detached", "CO": "condo", "TH": "townhouse", "DU": "duplex/multi"}


def main():
    src = json.load(open("live-inventory.json"))
    if src.get("version") != 2:
        print("ERROR: live-inventory.json is not the version 2 statistics feed — not writing", file=sys.stderr)
        return 1
    counts = src.get("counts") or {}
    blocks = src.get("cities") or {}
    band_labels = src.get("bandLabels") or []
    if not counts or not blocks:
        print("ERROR: live-inventory.json missing counts/cities — not writing", file=sys.stderr)
        return 1

    cities = {}
    for city, c in counts.items():
        m = (blocks.get(city) or {}).get("market") or {}
        by_type = {}
        for code, n in (m.get("types") or {}).items():
            if n:
                by_type[TYPE_LABELS.get(code, code)] = n
        bands = {}
        for label, n in zip(band_labels, m.get("bands") or []):
            if n:
                bands[label] = n
        cities[city] = {
            "total_for_sale": c.get("total"),
            "by_status": {
                "active": c.get("ACTV", 0),
                "new_this_period": c.get("NEW", 0),
                "coming_soon": c.get("CS", 0),
                "back_on_market": c.get("BOMK", 0),
            },
            "on_market": m.get("count"),
            "by_type": by_type,
            "by_price_band": bands,
            "median_list_price": m.get("medianPrice"),
            "median_price_per_sqft": m.get("medianPpsf"),
            "median_days_on_market": m.get("medianDom"),
            "new_in_last_7_days": m.get("newThisWeek"),
            "asking_under_1m": m.get("underMillion"),
        }

    out = {
        "data_date": src.get("date"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "MLS export via RealtyExperts daily feed (same statistics as harvrealtor.net/live-inventory)",
        "coverage": sorted(cities.keys()),
        "note": ("total_for_sale and by_status include active, new, coming-soon and back-on-market listings. "
                 "on_market, by_type, by_price_band and the medians cover the homes on the market (active, new, "
                 "back on market); coming-soon homes are counted, never itemized. No per-listing data is available "
                 "here; point people to the harvrealtor.com map search for individual homes. Refreshed up to 3x "
                 "daily on business days."),
        "cities": cities,
    }
    json.dump(out, open("assistant-inventory.json", "w"), indent=1)
    print(f"assistant-inventory.json written for {out['data_date']} "
          f"({sum(c['total_for_sale'] or 0 for c in cities.values())} listings across {len(cities)} cities)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
