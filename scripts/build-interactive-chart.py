#!/usr/bin/env python3
"""
build-interactive-chart.py  [outfile]  [--date MM/DD/YY]  [--email-url URL]

Generates latest_inventory_chart.html (the Plotly interactive dashboard pushed to
the teamrealtyexperts.com todays-inventory html_display slot) from the master
sheet's "Interactive" tab data model: cities x [CO, DU, DE, TH, Active All, New, CS, PEND].

For now the data is embedded (today's, read from the Interactive tab). The wired-in
version will read the tab live via the service account. Keeps the exact look of the
prior chart: title, date badge, legend-toggle tip, per-city colored traces, 5-default view.
"""
import json, sys

DATE_LABEL = "June 2, 2026"        # badge date
EMAIL_URL = "https://fremontrealtyexperts-510.github.io/RealtyExperts-Daily-Email/daily-market-glance-060226.html"
CATS = ["CO", "DU", "DE", "TH", "Active All", "New", "CS", "PEND"]

# city -> [CO, DU, DE, TH, Active All, New, CS, PEND]  (from Interactive tab, 06/02)
DATA = {
  "FREMONT":      [112, 7, 231, 61, 213, 30, 46, 102],
  "UNION CITY":   [20, 3, 71, 11, 60, 10, 6, 26],
  "CASTRO VALLEY":[12, 0, 66, 14, 41, 6, 5, 33],
  "DANVILLE":     [16, 2, 160, 38, 108, 18, 15, 54],
  "HAYWARD":      [57, 3, 162, 49, 142, 29, 12, 77],
  "LIVERMORE":    [42, 5, 165, 23, 114, 25, 13, 70],
  "NEWARK":       [20, 6, 90, 21, 59, 6, 13, 49],
  "PLEASANTON":   [17, 4, 109, 24, 82, 9, 13, 35],
  "SAN RAMON":    [54, 3, 135, 24, 102, 28, 14, 47],
  "DUBLIN":       [68, 1, 118, 44, 118, 22, 24, 49],
  "SAN LEANDRO":  [22, 1, 74, 4, 46, 13, 1, 36],
}
COLORS = {
  "FREMONT":"#FF6B6B","UNION CITY":"#4ECDC4","CASTRO VALLEY":"#2E86AB","DANVILLE":"#FFA07A",
  "HAYWARD":"#A23B72","LIVERMORE":"#F7DC6F","NEWARK":"#BB8FCE","PLEASANTON":"#E8611A",
  "SAN RAMON":"#3DDC84","DUBLIN":"#5C6BC0","SAN LEANDRO":"#FF8A65","MILPITAS":"#00BFA5",
}
DEFAULT_VISIBLE = {"FREMONT","UNION CITY","HAYWARD","NEWARK","MILPITAS"}

traces = []
for city, ys in DATA.items():
    traces.append({
        "name": city, "x": CATS, "y": ys, "type": "bar",
        "visible": True if city in DEFAULT_VISIBLE else "legendonly",
        "marker": {"color": COLORS.get(city, "#888"), "line": {"width": 1.5, "color": "rgba(255,255,255,0.3)"}},
        "hovertemplate": f"<b>{city}</b><br>%{{x}}: %{{y}}<extra></extra>",
    })
layout = {"title":{"text":"Real Estate Inventory Dashboard","font":{"size":22,"color":"#2c3e50","family":"Arial, sans-serif"},"x":0.5,"xanchor":"center"},"xaxis":{"title":"Listing Category","titlefont":{"size":14,"color":"#34495e"},"tickfont":{"size":12,"color":"#34495e"},"gridcolor":"rgba(0,0,0,0.05)","showgrid":True},"yaxis":{"title":"Count","titlefont":{"size":14,"color":"#34495e"},"tickfont":{"size":12,"color":"#34495e"},"gridcolor":"rgba(0,0,0,0.1)","showgrid":True},"height":700,"plot_bgcolor":"rgba(250,250,250,0.8)","paper_bgcolor":"white","hovermode":"closest","showlegend":True,"legend":{"title":{"text":"<b>Cities (click to toggle)</b>","font":{"size":13}},"font":{"size":11},"bgcolor":"rgba(255,255,255,0.9)","bordercolor":"#bdc3c7","borderwidth":1,"orientation":"h","x":0.5,"y":-0.18,"xanchor":"center","yanchor":"top"},"barmode":"group","bargap":0.15,"bargroupgap":0.1,"margin":{"l":60,"r":20,"t":70,"b":120},"font":{"family":"Arial, sans-serif"},"transition":{"duration":500,"easing":"cubic-in-out"}}
config = {"displayModeBar":True,"displaylogo":False,"modeBarButtonsToRemove":["pan2d","lasso2d","select2d"],"toImageButtonOptions":{"format":"png","filename":"realty_experts_inventory","height":800,"width":1400,"scale":2},"responsive":True}

html = f"""<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<style>
.date-badge{{text-align:center;margin:6px 0;}}
.date-badge span{{display:inline-block;background:#1e5bb8;color:#fff;font:600 15px Arial,sans-serif;padding:8px 22px;border-radius:20px;}}
.info-banner{{background:linear-gradient(135deg,#4f46e5,#7c3aed);color:#fff;font:13px Arial,sans-serif;padding:10px 16px;border-radius:8px;margin:10px auto;max-width:1200px;text-align:center;}}
#chart{{background:#fff;border-radius:12px;padding:10px;max-width:1300px;margin:0 auto;}}
</style>
<div class="date-badge"><span>{DATE_LABEL} - Alameda County Market Dashboard</span></div>
<div class="info-banner"><strong>Tip:</strong> Click on city names in the legend to show/hide data &bull; Default view: Fremont, Union City, Hayward, Newark</div>
<div id="chart">&nbsp;</div>
<h2 style="text-align:center;"><a href="{EMAIL_URL}" target="_blank"><span style="color:#0000FF;">View Full Email Version</span></a></h2>
<script>
var data = {json.dumps(traces)};
var layout = {json.dumps(layout)};
var config = {json.dumps(config)};
function getResponsiveLayout(){{var w=window.innerWidth;var L=JSON.parse(JSON.stringify(layout));if(w<600){{L.height=500;L.margin={{l:40,r:10,t:50,b:140}};L.title.font.size=16;L.xaxis.tickfont={{size:10}};L.yaxis.tickfont={{size:10}};L.legend.font={{size:9}};L.legend.y=-0.28;L.bargap=0.1;L.bargroupgap=0.05;}}else if(w<900){{L.height=600;L.margin={{l:50,r:15,t:60,b:130}};L.title.font.size=20;L.legend.font={{size:10}};L.legend.y=-0.22;}}return L;}}
Plotly.newPlot('chart',data,getResponsiveLayout(),config);
window.addEventListener('resize',function(){{Plotly.relayout('chart',getResponsiveLayout());}});
document.getElementById('chart').on('plotly_legendclick',function(d){{return true;}});
</script>
"""
out = next((a for a in sys.argv[1:] if not a.startswith("--")), "latest_inventory_chart.html")
open(out, "w").write(html)
print(f"wrote {out} ({len(DATA)} cities, {len(html)} bytes)")
