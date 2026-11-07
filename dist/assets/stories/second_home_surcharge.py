"""Second-home surcharge on a condo or co-op unit, first phase (July 2026 to June 2028).

Illustration for the story "New York's second-home tax starts at a cliff" (7 November 2026).
Rate: 4% of the Department of Finance value once that value reaches $1 million, applied to the
whole value, as in Greenberg Traurig's worked example (4% of $1 million = $40,000). The chart stops
below $3 million, where the next band starts, because published guides do not settle how the
higher bands apply. Writes second-home-surcharge.{svg,png,csv} next to this script.
"""
import csv, pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

OUT = pathlib.Path(__file__).resolve().parent
BLUE, INK, GRID = "#145f83", "#536774", "#d9e1e6"

def owed(v):
    return 0.04 * v if v >= 1_000_000 else 0.0

pts = [(0, 0.0), (500_000, 0.0), (999_999, 0.0), (1_000_000, 40_000.0), (2_000_000, 80_000.0), (2_999_999, owed(2_999_999))]
with open(OUT / "second-home-surcharge.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["dof_value_dollars", "annual_surcharge_dollars"])
    for v, s in pts:
        w.writerow([v, round(s, 2)])

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 13, "text.usetex": False, "text.parse_math": False})
fig, ax = plt.subplots(figsize=(9, 5.2), dpi=100)
ax.plot([0, 1_000_000], [0, 0], color=BLUE, lw=3, solid_capstyle="round")
ax.plot([1_000_000, 2_999_999], [40_000, owed(2_999_999)], color=BLUE, lw=3, solid_capstyle="round")
ax.plot([1_000_000, 1_000_000], [0, 40_000], color=BLUE, lw=1.4, ls=(0, (3, 3)))
ax.scatter([999_999], [0], s=90, facecolor="white", edgecolor=BLUE, lw=2.2, zorder=3)
ax.scatter([1_000_000], [40_000], s=90, color=BLUE, zorder=3)
ax.text(965_000, 44_000, "Valued at $1,000,000:\n$40,000 a year", color="#1d2b33", fontsize=13, ha="right", va="bottom", linespacing=1.3)
ax.text(965_000, 6_000, "Valued at $999,999: $0", color="#1d2b33", fontsize=13, ha="right", va="bottom")
ax.text(2_960_000, owed(2_999_999) + 4_000, "About $120,000\njust under $3M", color=INK, fontsize=12, ha="right", va="bottom", linespacing=1.3)
ax.set_xlim(0, 3_000_000)
ax.set_ylim(-4_000, 140_000)
ax.set_xticks([0, 500_000, 1_000_000, 1_500_000, 2_000_000, 2_500_000, 3_000_000])
ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"${x/1e6:g}M" if x >= 1e6 else (f"${x/1e3:.0f}k" if x else "$0")))
ax.set_yticks([0, 40_000, 80_000, 120_000])
ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"${y/1e3:.0f}k" if y else "$0"))
ax.set_xlabel("Department of Finance value of the unit", color=INK, fontsize=13, labelpad=8)
ax.set_ylabel("Surcharge per year", color=INK, fontsize=13, labelpad=8)
for s_ in ("top", "right"):
    ax.spines[s_].set_visible(False)
for s_ in ("left", "bottom"):
    ax.spines[s_].set_color(INK)
ax.tick_params(colors=INK, labelsize=12)
ax.grid(axis="y", color=GRID, lw=0.8)
ax.set_axisbelow(True)
ax.set_title("Condo or co-op that is not a primary residence, first phase", loc="left", color="#1d2b33", fontsize=15, pad=14)
fig.tight_layout()
fig.savefig(OUT / "second-home-surcharge.svg", metadata={"Date": None})
fig.savefig(OUT / "second-home-surcharge.png", dpi=150)
print("written")
