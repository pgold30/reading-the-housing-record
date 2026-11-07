"""Two charts for "New York's second-home tax starts at a cliff" (7 November 2026).

1. second-home-condo-counts: residential condo units (classes R1 to R4, tax class 2) by 2026-27 final
   market value in $25,000 bands from $700,000 to $1.3 million (NYC Open Data 8y4t-faws).
2. second-home-2028: condo units that sold in 2023-2025 (arm's-length sample of second_home_price_vs_value.py),
   by borough: valued at $1M or more and sold for $5M or more (stay in), valued at $1M or more but sold for
   less than $5M (drop out), valued under $1M but sold for $5M or more (come in).
Arguments: linked dataset 1.2.0 build/ folder; optional saved roll CSV (bbl,dof_value; condo units of
$300,000 or more). First run: 7 November 2026.
"""
import csv, json, pathlib, sys, urllib.parse, urllib.request
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

OUT = pathlib.Path(__file__).resolve().parent
D = pathlib.Path(sys.argv[1])
BLUE, MID, LIGHT, INK, GRID, TEXT = "#145f83", "#5e93ad", "#a9c3d1", "#536774", "#d9e1e6", "#1d2b33"


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


def style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(INK)
    ax.tick_params(colors=INK)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)


plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 13, "text.parse_math": False})
roll = load_roll()

# Chart 1: unit counts by value band
edges = np.arange(700_000, 1_300_001, 25_000)
counts = [int(((roll.dof_value >= lo) & (roll.dof_value < hi)).sum()) for lo, hi in zip(edges[:-1], edges[1:])]
with open(OUT / "second-home-condo-counts.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["dof_value_from", "dof_value_below", "condo_units"])
    w.writerows([[int(lo), int(hi), c] for lo, hi, c in zip(edges[:-1], edges[1:], counts)])
fig, ax = plt.subplots(figsize=(9, 5.2), dpi=100)
for lo, c in zip(edges[:-1], counts):
    ax.bar(lo + 12_500, c, width=22_000, color=BLUE if lo >= 1_000_000 else LIGHT)
ax.axvline(1_000_000, color=INK, lw=1.2, ls=(0, (3, 3)))
top = max(counts) * 1.18
ax.set_ylim(0, top)
ax.text(990_000, top * 0.97, "Owes nothing", ha="right", va="top", color=INK, fontsize=12)
ax.text(1_010_000, top * 0.97, "Owes $40,000 a year or more", ha="left", va="top", color=TEXT, fontsize=12)
ax.set_xlim(700_000, 1_300_000)
ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"${x/1e6:g}M" if x >= 1e6 else f"${x/1e3:.0f}k"))
ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:,.0f}"))
ax.set_xlabel("City value of the unit, 2026-27 (bands of $25,000)", color=INK, fontsize=12, labelpad=8)
ax.set_ylabel("Condo units", color=INK, fontsize=13, labelpad=8)
style(ax)
ax.set_title("No gap at the $1 million line yet", loc="left", color=TEXT, fontsize=15, pad=14)
fig.tight_layout()
fig.savefig(OUT / "second-home-condo-counts.svg", metadata={"Date": None})
fig.savefig(OUT / "second-home-condo-counts.png", dpi=150)
plt.close(fig)

# Chart 2: 2028 switch among sold units
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
m["boro"] = m.unit_bbl.str[0].map({"1": "Manhattan", "3": "Brooklyn"})
rows = []
for b in ["Manhattan", "Brooklyn"]:
    x = m[m.boro == b]
    stay = int(((x.dof_value >= 1e6) & (x.sale_price >= 5e6)).sum())
    out = int(((x.dof_value >= 1e6) & (x.sale_price < 5e6)).sum())
    inn = int(((x.dof_value < 1e6) & (x.sale_price >= 5e6)).sum())
    rows.append([b, stay, out, inn])
with open(OUT / "second-home-2028.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["borough", "stay_in", "drop_out", "come_in"])
    w.writerows(rows)

fig, axes = plt.subplots(1, 2, figsize=(9, 5.2), dpi=100, gridspec_kw={"wspace": 0.35})
for ax, (b, stay, out, inn) in zip(axes, rows):
    now, later = stay + out, stay + inn
    W = 0.72
    ax.bar(0, stay, width=W, color=BLUE)
    ax.bar(0, out, width=W, bottom=stay, color=LIGHT)
    ax.bar(1, stay, width=W, color=BLUE)
    ax.bar(1, inn, width=W, bottom=stay, color=MID)
    ymax = max(now, later) * 1.18
    ax.set_ylim(0, ymax)
    ax.text(0, now + ymax * 0.015, f"{now:,}", ha="center", va="bottom", color=TEXT, fontsize=12, fontweight="bold")
    ax.text(1, later + ymax * 0.015, f"{later:,}", ha="center", va="bottom", color=TEXT, fontsize=12, fontweight="bold")
    ax.text(0, stay + out / 2, f"{out:,}\ndrop out", ha="center", va="center", color=TEXT, fontsize=10.5, linespacing=1.15)
    ax.text(1, stay + inn / 2, f"{inn:,}\ncome in", ha="center", va="center", color="white", fontsize=10.5, linespacing=1.15)
    for xpos in (0, 1):
        ax.text(xpos, stay / 2, f"{stay:,}\nstay in", ha="center", va="center", color="white", fontsize=10.5, linespacing=1.15)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Now:\nvalued $1M+", "2028:\nsold $5M+"], fontsize=11)
    ax.set_xlim(-0.6, 1.6)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:,.0f}"))
    style(ax)
    ax.set_title(b, loc="left", color=TEXT, fontsize=13)
axes[0].set_ylabel("Condo units that sold, 2023 to 2025", color=INK, fontsize=12, labelpad=8)
fig.suptitle("If 2028 values follow sale prices, Brooklyn loses condos from the tax", x=0.02, ha="left", color=TEXT, fontsize=15)
fig.subplots_adjust(left=0.1, right=0.98, top=0.84, bottom=0.14, wspace=0.3)
fig.savefig(OUT / "second-home-2028.svg", metadata={"Date": None})
fig.savefig(OUT / "second-home-2028.png", dpi=150)
print(json.dumps({"counts_window": [int(edges[0]), int(edges[-1])], "counts": counts, "2028": rows}))
