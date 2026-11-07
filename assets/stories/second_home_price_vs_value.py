"""Recent condo sale prices versus the city's 2026-27 market value of the same unit.

Story: "New York's second-home tax starts at a cliff" (7 November 2026).
Inputs:
  1. The linked dataset of NYC sales, deeds and mortgages, release 1.2.0 (Zenodo), build/ folder:
     sales.csv.gz, links.csv.gz, deed_flags.csv.gz. Pass the folder as the first argument.
  2. NYC Open Data, Property Valuation and Assessment Data (8y4t-faws): tax year 2026-27 final roll
     (year 2027, period 3), building classes R1 to R4 in tax class 2, final market value of $300,000
     or more. Downloaded by this script (or pass a saved CSV with columns bbl,dof_value as a second argument).
Sample: condominium sales in 2023-2025 at $100,000 or more with a unique deed match, an ordinary deed
(deed classifier) and no shared surname between buyer and seller; latest sale per unit.
Writes second-home-price-vs-value.csv (bins), second-home-price-vs-value.json (summary) and the chart.
First run: 7 November 2026.
"""
import csv, json, pathlib, sys, urllib.parse, urllib.request
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

OUT = pathlib.Path(__file__).resolve().parent
D = pathlib.Path(sys.argv[1])
BLUE, INK, GRID, LIGHT = "#145f83", "#536774", "#d9e1e6", "#7f9fb0"


def load_roll():
    if len(sys.argv) > 2:
        return pd.read_csv(sys.argv[2], dtype={"bbl": str})[["bbl", "dof_value"]]
    api = "https://data.cityofnewyork.us/resource/8y4t-faws.json"
    where = ("year='2027' and period='3' and bldg_class in('R1','R2','R3','R4') "
             "and curtaxclass='2' and finmkttot::number >= 300000")
    rows, off = [], 0
    while True:
        q = urllib.parse.urlencode({"$select": "boro,block,lot,finmkttot", "$where": where,
                                    "$order": "boro,block,lot", "$limit": 50000, "$offset": off})
        with urllib.request.urlopen(api + "?" + q, timeout=900) as r:
            page = json.load(r)
        rows += page
        if len(page) < 50000:
            break
        off += 50000
    return pd.DataFrame({"bbl": [f"{int(r['boro'])}{int(r['block']):05d}{int(r['lot']):04d}" for r in rows],
                         "dof_value": [int(float(r["finmkttot"])) for r in rows]})


roll = load_roll()
sales = pd.read_csv(D / "sales.csv.gz", usecols=["sale_id", "borough", "block", "lot", "property_group", "sale_price", "sale_date"])
links = pd.read_csv(D / "links.csv.gz", dtype={"linked_bbl": str, "deed_document_id": str}, low_memory=False,
                    usecols=["sale_id", "deed_match", "linked_bbl", "deed_document_id"])
flags = pd.read_csv(D / "deed_flags.csv.gz", dtype={"deed_document_id": str}, usecols=["deed_document_id", "same_surname", "deed_event"])

s = sales[(sales.property_group == "condo") & (sales.sale_price >= 100_000)].copy()
s["year"] = s.sale_date.str[:4].astype(int)
s = s[s.year >= 2023].merge(links, on="sale_id", how="left").merge(flags, on="deed_document_id", how="left")
s["unit_bbl"] = np.where(s.linked_bbl.notna(), s.linked_bbl,
                         s.borough.astype(str) + s.block.astype(int).map("{:05d}".format) + s.lot.astype(int).map("{:04d}".format))
s = s[s.unit_bbl.str[-4:].astype(int).between(1001, 6999)]
s = s[(s.deed_match == "unique") & (s.deed_event == "ORDINARY") & (s.same_surname != 1)]
s = s.sort_values("sale_date").drop_duplicates("unit_bbl", keep="last")
m = s.merge(roll, left_on="unit_bbl", right_on="bbl", how="inner")

edges = list(range(800_000, 1_200_001, 50_000))
rows = []
for lo, hi in zip(edges[:-1], edges[1:]):
    x = m[(m.dof_value >= lo) & (m.dof_value < hi)].sale_price
    rows.append([lo, hi, len(x), int(x.quantile(.25)), int(x.median()), int(x.quantile(.75))])
with open(OUT / "second-home-price-vs-value.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["dof_value_from", "dof_value_below", "sales", "price_p25", "price_median", "price_p75"])
    w.writerows(rows)

ge1 = m[m.dof_value >= 1_000_000]
near5 = m[(m.sale_price >= 4_500_000) & (m.sale_price < 5_500_000)]
summary = {
    "matched_sales": len(m),
    "below_line_900k_1m": {"n": int(((m.dof_value >= 900_000) & (m.dof_value < 1_000_000)).sum()),
                           "median_price": float(m[(m.dof_value >= 900_000) & (m.dof_value < 1_000_000)].sale_price.median())},
    "above_line_1m_1_1m": {"n": int(((m.dof_value >= 1_000_000) & (m.dof_value < 1_100_000)).sum()),
                           "median_price": float(m[(m.dof_value >= 1_000_000) & (m.dof_value < 1_100_000)].sale_price.median())},
    "sales_4_5m_5_5m_median_dof_value": float(near5.dof_value.median()),
    "sales_4_5m_5_5m_n": len(near5),
    "ratio_quartiles": [float(m.eval("sale_price/dof_value").quantile(q)) for q in (.25, .5, .75)],
    "valued_ge_1m_n": len(ge1),
    "valued_ge_1m_sold_under_5m": int((ge1.sale_price < 5_000_000).sum()),
    "valued_ge_1m_sold_under_5m_manhattan_share": float((ge1[ge1.unit_bbl.str[0] == "1"].sale_price < 5e6).mean()),
    "valued_ge_1m_sold_under_5m_brooklyn_share": float((ge1[ge1.unit_bbl.str[0] == "3"].sale_price < 5e6).mean()),
    "valued_under_1m_sold_ge_5m": int(((m.dof_value < 1_000_000) & (m.sale_price >= 5_000_000)).sum()),
}
json.dump(summary, open(OUT / "second-home-price-vs-value.json", "w"), indent=1)

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 13, "text.parse_math": False})
fig, ax = plt.subplots(figsize=(9, 5.2), dpi=100)
xs = np.arange(len(rows))
for i, r in enumerate(rows):
    color = BLUE if r[0] >= 1_000_000 else LIGHT
    ax.plot([i, i], [r[3], r[5]], color=color, lw=7, solid_capstyle="butt", alpha=0.35)
    ax.scatter([i], [r[4]], s=80, color=color, zorder=3)
ax.axvline(3.5, color=INK, lw=1.2, ls=(0, (3, 3)))
ax.text(3.45, 8_350_000, "Owes nothing", ha="right", va="top", color=INK, fontsize=12)
ax.text(3.55, 8_350_000, "Owes $40,000 a year or more", ha="left", va="top", color="#1d2b33", fontsize=12)
ax.text(7.4, 500_000, "Dot: median sale. Bar: middle half of sales.", ha="right", va="bottom", color=INK, fontsize=11)
ax.set_xticks(xs)
ax.set_xticklabels([(f"${r[0]/1e6:g}M" if r[0] % 100_000 == 0 else f"${r[0]/1e6:.2f}M") if r[0] >= 1e6 else f"${r[0]/1e3:.0f}k" for r in rows], rotation=0, fontsize=11)
ax.set_ylim(0, 8_500_000)
ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"${y/1e6:.0f}M" if y else "$0"))
ax.set_xlabel("City value of the unit, 2026-27 (bands of $50,000, starting at)", color=INK, fontsize=12, labelpad=8)
ax.set_ylabel("Sale price, 2023 to 2025", color=INK, fontsize=13, labelpad=8)
for s_ in ("top", "right"):
    ax.spines[s_].set_visible(False)
for s_ in ("left", "bottom"):
    ax.spines[s_].set_color(INK)
ax.tick_params(colors=INK)
ax.grid(axis="y", color=GRID, lw=0.8)
ax.set_axisbelow(True)
ax.set_title("Condos on either side of the $1 million line sell for about the same", loc="left", color="#1d2b33", fontsize=15, pad=14)
fig.tight_layout()
fig.savefig(OUT / "second-home-price-vs-value.svg", metadata={"Date": None})
fig.savefig(OUT / "second-home-price-vs-value.png", dpi=150)
print(json.dumps(summary, indent=1))
