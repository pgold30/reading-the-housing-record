"""Residential condo units by Department of Finance market value, 2026-27 final roll.

Story: "New York's second-home tax starts at a cliff" (7 November 2026).
Source: NYC Open Data, Property Valuation and Assessment Data (dataset 8y4t-faws),
fiscal year 2027 (tax year 2026-27), final roll (period 3), final market value (finmkttot).
Units: building classes R1, R2, R3 and R4 in tax class 2 (residential condominium units).
Co-op units are not in the count: the city values co-ops by building and imputes unit values
from share ratios. The roll does not say which units are primary residences.
Writes second-home-condo-values.csv next to this script. First run: 7 November 2026.
"""
import csv, json, pathlib, urllib.parse, urllib.request

OUT = pathlib.Path(__file__).resolve().parent
API = "https://data.cityofnewyork.us/resource/8y4t-faws.json"
BASE = "year='2027' and period='3' and bldg_class in('R1','R2','R3','R4') and curtaxclass='2'"
BANDS = [(0, 10**12), (800_000, 900_000), (900_000, 950_000), (950_000, 1_000_000),
         (1_000_000, 1_050_000), (1_050_000, 1_100_000), (1_100_000, 1_200_000),
         (1_000_000, 3_000_000), (2_850_000, 3_000_000), (3_000_000, 3_150_000),
         (3_000_000, 5_000_000), (5_000_000, 10**12)]


def count(lo, hi):
    where = f"{BASE} and finmkttot::number >= {lo} and finmkttot::number < {hi}"
    url = API + "?" + urllib.parse.urlencode({"$select": "count(*)", "$where": where})
    with urllib.request.urlopen(url, timeout=900) as r:
        return int(json.load(r)[0]["count"])


with open(OUT / "second-home-condo-values.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["value_from_dollars", "value_below_dollars", "condo_units"])
    for lo, hi in BANDS:
        w.writerow([lo, "" if hi == 10**12 else hi, count(lo, hi)])
print("written")
