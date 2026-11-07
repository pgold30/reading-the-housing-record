"""Houses near the $5 million line, and bulk-price rows among high-end condo sales.

Story: "New York's second-home tax starts at a cliff" (7 November 2026).
Inputs: the linked dataset of NYC sales, deeds and mortgages, release 1.2.0, build/ folder (first argument),
and NYC Open Data 8y4t-faws, tax year 2026-27 final roll (year 2027, period 3), tax class 1 houses
(building classes A*, B* and C0) with a final market value of $2 million or more (downloaded, or pass a
saved CSV with columns bbl,dof_value as the second argument).
Houses: sales of $100,000 or more in 2023-2025 with a unique deed match, an ordinary deed and no shared
surname, latest sale per lot. Bulk rows: condo sales of $4 million or more in 2023-2025 (boroughs 1-4)
that share block, date and price with at least one other row in the DOF sales file.
Writes second-home-houses-and-bulk.json. First run: 7 November 2026.
"""
import json, pathlib, sys, urllib.parse, urllib.request
import pandas as pd

OUT = pathlib.Path(__file__).resolve().parent
D = pathlib.Path(sys.argv[1])


def load_roll():
    if len(sys.argv) > 2:
        return pd.read_csv(sys.argv[2], dtype={"bbl": str})[["bbl", "dof_value"]]
    api = "https://data.cityofnewyork.us/resource/8y4t-faws.json"
    where = ("year='2027' and period='3' and curtaxclass='1' and (starts_with(bldg_class,'A') or "
             "starts_with(bldg_class,'B') or bldg_class='C0') and finmkttot::number >= 2000000")
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
S = pd.read_csv(D / "sales.csv.gz", dtype={"bbl": str},
                usecols=["sale_id", "bbl", "borough", "block", "property_group", "sale_price", "sale_date"])
L = pd.read_csv(D / "links.csv.gz", dtype={"deed_document_id": str}, low_memory=False,
                usecols=["sale_id", "deed_match", "deed_document_id"])
F = pd.read_csv(D / "deed_flags.csv.gz", dtype={"deed_document_id": str},
                usecols=["deed_document_id", "same_surname", "deed_event", "legal_rule_amount"])
S["year"] = S.sale_date.str[:4].astype(int)

h = S[(S.property_group == "house") & (S.sale_price >= 100_000) & (S.year >= 2023)]
h = h.merge(L, on="sale_id", how="left").merge(F, on="deed_document_id", how="left")
h = h[(h.deed_match == "unique") & (h.deed_event == "ORDINARY") & (h.same_surname != 1)]
h = h.sort_values("sale_date").drop_duplicates("bbl", keep="last").merge(roll, on="bbl", how="inner")
band = lambda lo, hi: h[(h.dof_value >= lo) & (h.dof_value < hi)].sale_price
near = h[(h.sale_price >= 4.5e6) & (h.sale_price < 5.5e6)]
houses = {
    "roll_ge_5m": int((roll.dof_value >= 5e6).sum()),
    "roll_ge_5m_by_borough": {str(k): int(v) for k, v in roll[roll.dof_value >= 5e6].bbl.str[0].value_counts().items()},
    "roll_5_0_to_5_5m": int(((roll.dof_value >= 5e6) & (roll.dof_value < 5.5e6)).sum()),
    "matched_sales": len(h),
    "valued_4_5_to_5_0m": {"n": int(len(band(4.5e6, 5e6))), "median_price": float(band(4.5e6, 5e6).median())},
    "valued_5_0_to_5_5m": {"n": int(len(band(5e6, 5.5e6))), "median_price": float(band(5e6, 5.5e6).median())},
    "sold_4_5_to_5_5m_median_value": float(near.dof_value.median()),
    "price_to_value_quartiles": [float((h.sale_price / h.dof_value).quantile(q)) for q in (.25, .5, .75)],
}

c = S[(S.property_group == "condo") & S.year.between(2023, 2025) & S.borough.between(1, 4)].merge(L, on="sale_id", how="left")
c = c.merge(F, on="deed_document_id", how="left")
c["grp"] = c.borough.astype(str) + "-" + c.block.astype(str) + "-" + c.sale_date + "-" + c.sale_price.astype(str)
c["grp_n"] = c.groupby("grp").sale_id.transform("count")
x = c[c.sale_price >= 4e6]
rep = x[x.grp_n >= 2]
m = x[x.deed_match == "unique"]
bulk = {
    "condo_sales_ge_4m": len(x),
    "repeated_block_date_price_rows": len(rep),
    "of_which_no_single_unit_deed": int((rep.deed_match != "unique").sum()),
    "deals": int(rep.grp.nunique()),
    "largest_deals_rows": rep.drop_duplicates("grp").grp_n.sort_values(ascending=False).head(5).tolist(),
    "matched_same_surname": int(m.same_surname.sum()),
    "matched_legal_rule_amount": int(m.legal_rule_amount.sum()),
    "matched_n": len(m),
    "condo_rows_2023_2025_price_under_10k": int((c.sale_price < 10_000).sum()),
    "condo_rows_2023_2025": len(c),
}
json.dump({"houses": houses, "bulk_condo_rows": bulk}, open(OUT / "second-home-houses-and-bulk.json", "w"), indent=1)
print(json.dumps({"houses": houses, "bulk_condo_rows": bulk}, indent=1))
