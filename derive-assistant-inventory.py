#!/usr/bin/env python3
"""
derive-assistant-inventory.py

Derives assistant-inventory.json (compact, ~2KB) from live-inventory.json
(~175KB). Consumed by the harvbalu.homes AI assistant's n8n get_inventory
tool, which feeds it directly into an LLM prompt — hence the compaction.

Called by refresh-live-inventory.sh after generate-live-inventory.js on every
publish run. Safe to run by hand: ./derive-assistant-inventory.py
Reads ./live-inventory.json, writes ./assistant-inventory.json.
Exits non-zero without writing anything if the source looks wrong, so a bad
run can never replace a good published file.
"""
import json
import sys
from datetime import datetime, timezone
from statistics import median

BANDS = [
    ("under $800K", 0, 800_000),
    ("$800K-$1.2M", 800_000, 1_200_000),
    ("$1.2M-$1.6M", 1_200_000, 1_600_000),
    ("$1.6M-$2M", 1_600_000, 2_000_000),
    ("$2M+", 2_000_000, float("inf")),
]
TYPE_LABELS = {"DE": "detached", "CO": "condo", "TH": "townhouse", "DU": "duplex/multi"}


def main():
    src = json.load(open("live-inventory.json"))
    listings = src.get("listings") or []
    counts = src.get("counts") or {}
    if not listings or not counts:
        print("ERROR: live-inventory.json missing listings/counts — not writing", file=sys.stderr)
        return 1

    cities = {}
    for city, c in counts.items():
        rows = [l for l in listings if l.get("city") == city]
        prices = [l["price"] for l in rows if isinstance(l.get("price"), (int, float)) and l["price"] > 0]
        doms = [l["dom"] for l in rows if isinstance(l.get("dom"), (int, float))]
        by_type = {}
        for l in rows:
            t = TYPE_LABELS.get(l.get("type"), l.get("type") or "other")
            by_type[t] = by_type.get(t, 0) + 1
        bands = {}
        for label, lo, hi in BANDS:
            n = sum(1 for p in prices if lo <= p < hi)
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
            "by_type": by_type,
            "by_price_band": bands,
            "median_list_price": int(median(prices)) if prices else None,
            "median_days_on_market": int(median(doms)) if doms else None,
        }

    out = {
        "data_date": src.get("date"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "MLS export via RealtyExperts daily feed (same data as harvrealtor.net/live-inventory)",
        "coverage": sorted(cities.keys()),
        "note": "Counts include active, new, coming-soon, and back-on-market listings. Refreshed up to 3x daily on business days.",
        "cities": cities,
    }
    json.dump(out, open("assistant-inventory.json", "w"), indent=1)
    print(f"assistant-inventory.json written for {out['data_date']} "
          f"({sum(c['total_for_sale'] or 0 for c in cities.values())} listings across {len(cities)} cities)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
