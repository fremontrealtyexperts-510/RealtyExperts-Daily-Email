#!/usr/bin/env python3
"""
mls-csv-to-images.py  <input.csv>  [out_dir]

Reads the Paragon "MLS Defined Spread Sheet 4" CSV export and produces:
  RE-Daily-1.png  - per-city summary table (replaces the RE-v2 table screenshot)
  RE-Daily-2.png  - grouped bar chart        (replaces the RE-v2 chart screenshot)

Pivot logic reverse-engineered + validated cell-by-cell against the live
"Alameda-County-New Stats-Daily" master sheet (RE-v2 / 'REALTY EXPERTS' tabs)
on 2026-06-01: 14/15 cities exact. The 1 diff is Union City's All CS / All New,
which is a swapped-COUNTIFS bug in the sheet; this script computes them correctly
(so column totals come out CS 209 / New 223, not the sheet's bugged 216 / 216).
"""
import csv, sys, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ── pivot spec (validated) ───────────────────────────────────────────────────
# display label -> exact city string in MLS raw data (col F). Note the MLS data's
# own quirks: Castro Valley is stored "CASTROVAEY", and San Leandro/Lorenzo have no space.
CITIES = [
    ("Fremont", "FREMONT"), ("Union City", "UNION CITY"), ("Newark", "NEWARK"),
    ("Hayward", "HAYWARD"), ("Danville", "DANVILLE"), ("Milpitas", "MILPITAS"),
    ("Oakland", "OAKLAND"), ("Livermore", "LIVERMORE"), ("Castro Valley", "CASTROVAEY"),
    ("Pleasanton", "PLEASANTON"), ("San Ramon", "SAN RAMON"), ("Dublin", "DUBLIN"),
    ("Sunol", "SUNOL"), ("San Lorenzo", "SANLORENZO"), ("San Leandro", "SANLEANDRO"),
]
ACTIVE = {"ACTV", "PCH", "BOMK", "NEW"}     # "Active/BOMK/PCH/New" bucket
PENDING = {"PEND"}
TYPE_GROUPS = {"TH": {"TH"}, "CO": {"CO"}, "DD": {"DU", "DE", "PT"}}  # DU/DE/PH (PT unused in data)

def load_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        r = csv.reader(f)
        header = next(r)
        idx = {h.strip().lower(): i for i, h in enumerate(header)}
        ci = idx.get("city", 5); bi = idx.get("status", 1); ji = idx.get("bt", 9)
        rows = []
        for row in r:
            if len(row) <= max(ci, bi, ji):
                continue
            city = row[ci].strip().upper(); st = row[bi].strip().upper(); bt = row[ji].strip().upper()
            if city and st:
                rows.append((city, st, bt))
    return rows

def pivot(rows):
    """returns list of [TH_a,TH_p,CO_a,CO_p,DD_a,DD_p,Total,CS,New] per city + Total row."""
    out = []
    for _, key in CITIES:
        r = [x for x in rows if x[0] == key]
        def cnt(bts, sts): return sum(1 for c, s, b in r if b in bts and s in sts)
        th_a = cnt(TYPE_GROUPS["TH"], ACTIVE); th_p = cnt(TYPE_GROUPS["TH"], PENDING)
        co_a = cnt(TYPE_GROUPS["CO"], ACTIVE); co_p = cnt(TYPE_GROUPS["CO"], PENDING)
        dd_a = cnt(TYPE_GROUPS["DD"], ACTIVE); dd_p = cnt(TYPE_GROUPS["DD"], PENDING)
        total = th_a + th_p + co_a + co_p + dd_a + dd_p
        cs = sum(1 for c, s, b in r if s == "CS"); nw = sum(1 for c, s, b in r if s == "NEW")
        out.append([th_a, th_p, co_a, co_p, dd_a, dd_p, total, cs, nw])
    tot = [sum(col) for col in zip(*out)]
    return out, tot

# ── colors (match the Google-Sheets look) ───────────────────────────────────
BLUE = "#2f6df6"; DARKTXT = "#1f3864"; GRAY = "#808080"; BLACK = "#000000"
HDR_BLUE_TXT = "#5b9bd5"
SERIES = [("TH Active", "#4472C4"), ("TH Pending", "#ED7D31"), ("CO Active", "#C00000"),
          ("CO Pending", "#FFC000"), ("DU/DE/PH Active", "#5B9BD5"), ("DU/DE/PH Pending", "#70AD47")]

def render_table(rows_data, tot, out):
    headers = ["Cities", "TH\nActive/BOMK\n/PCH/New", "TH\nPending", "CO\nActive/BOMK\n/PCH/New",
               "CO\nPending", "DU/DE/PH\nActive/BOMK\n/PCH/New", "DU/DE/PH\nPending", "Total", "All CS", "All New"]
    blue_hdr_cols = {1, 3, 5}
    body = [[CITIES[i][0]] + [f"{v:,}" for v in rows_data[i]] for i in range(len(CITIES))]
    body.append(["Total"] + [f"{v:,}" for v in tot])
    fig, ax = plt.subplots(figsize=(13.5, 6.2)); ax.axis("off")
    tbl = ax.table(cellText=[headers] + body, cellLoc="center", loc="center")
    tbl.auto_set_font_size(False); tbl.set_fontsize(10.5); tbl.scale(1, 2.0)
    ncols = len(headers); nrows = len(body) + 1
    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor("#d9d9d9"); cell.set_linewidth(0.6)
        if r == 0:  # header
            cell.set_facecolor(GRAY if c == 7 else BLACK)
            cell.get_text().set_color(HDR_BLUE_TXT if c in blue_hdr_cols else "white")
            cell.get_text().set_fontweight("bold"); cell.set_height(0.13)
        elif r == nrows - 1:  # Total row
            cell.set_facecolor(BLACK); cell.get_text().set_color("white"); cell.get_text().set_fontweight("bold")
        else:
            band_blue = (r % 2 == 1)  # Fremont(r=1) blue, alternate
            if c == 7:  # Total column always gray
                cell.set_facecolor(GRAY); cell.get_text().set_color("white"); cell.get_text().set_fontweight("bold")
            elif band_blue:
                cell.set_facecolor(BLUE); cell.get_text().set_color("white")
            else:
                cell.set_facecolor("white"); cell.get_text().set_color(DARKTXT)
            if c == 0:
                cell.get_text().set_fontweight("bold")
    tbl.auto_set_column_width([0,1,2,3,4,5,6,7,8,9])
    fig.savefig(out, dpi=150, bbox_inches="tight", pad_inches=0.15); plt.close(fig)

CAP = 130  # y-axis ceiling; taller bars clip (so Oakland doesn't dominate) and get a value label
def render_chart(rows_data, out):
    labels = [c[0] for c in CITIES]
    x = np.arange(len(labels)); w = 0.14
    fig, ax = plt.subplots(figsize=(13.5, 6.8))
    for k, (name, color) in enumerate(SERIES):
        xs = x + (k - 2.5) * w
        vals = [rows_data[i][k] for i in range(len(labels))]
        ax.bar(xs, vals, w, label=name, color=color)
        for xi, v in zip(xs, vals):           # clipped bars: print true value vertically near the top
            if v > CAP:
                ax.text(xi, CAP - 4, str(v), ha="center", va="top", rotation=90,
                        fontsize=7.5, fontweight="bold", color="white")
    ax.set_title("www.TeamRealtyExperts.com", color="#1155cc", fontsize=18, fontweight="bold", pad=14)
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=8.5)
    ax.set_ylim(0, CAP); ax.set_yticks(np.arange(0, CAP + 1, 25))
    ax.tick_params(axis="y", labelsize=8); ax.grid(axis="y", color="#d9d9d9", linewidth=0.6)
    ax.set_axisbelow(True)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.06), ncol=6, fontsize=8.5, frameon=False)
    fig.savefig(out, dpi=150, bbox_inches="tight", pad_inches=0.2); plt.close(fig)

def main():
    if len(sys.argv) < 2:
        print("usage: mls-csv-to-images.py <input.csv> [out_dir]"); sys.exit(1)
    src = sys.argv[1]; out_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    rows = load_rows(src)
    rows_data, tot = pivot(rows)
    print(f"rows={len(rows)}  grand Total={tot[6]}  CS={tot[7]}  New={tot[8]}")
    render_table(rows_data, tot, os.path.join(out_dir, "RE-Daily-1.png"))
    render_chart(rows_data, os.path.join(out_dir, "RE-Daily-2.png"))
    print("wrote RE-Daily-1.png + RE-Daily-2.png to", out_dir)

if __name__ == "__main__":
    main()
