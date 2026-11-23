#!/usr/bin/env python3
"""Build static sharded JSON lookup data for nychousingdata.com/lookup/ from NYC linked dataset v1.2.0."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = Path(
    "/Users/pablo/Documents/ChatGPT/papers/dataset_release_2026-10-22/nyc_linked_dataset_v1_2_0/build"
)
NTA_LOOKUP_PATH = REPO_ROOT / "tools" / "nta2020_lookup.json"
OUT_DIR = REPO_ROOT / "assets" / "lookup"
SHARDS_DIR = OUT_DIR / "shards"

BOROUGH_NAMES = {
    1: "Manhattan",
    2: "Bronx",
    3: "Brooklyn",
    4: "Queens",
    5: "Staten Island",
}

MIN_PRICE = 10_000
MIN_GEO_SALES = 10
MIN_BLDG_SALES = 25
MIN_FLAGGED_FOR_SHARE = 10
MIN_VALID_LTV = 10
YEARS = list(range(2016, 2026))


def clean_address(raw: Any) -> str:
    if not isinstance(raw, str):
        return ""
    # Drop unit suffixes after comma if present in DOF rolling sales strings
    head = raw.split(",", 1)[0]
    head = re.sub(r"\s+", " ", head).strip()
    if not head:
        return ""
    tokens = []
    minor = {"OF", "AT", "IN", "ON", "THE", "AND"}
    for idx, tok in enumerate(head.split(" ")):
        up = tok.upper()
        if idx > 0 and up in minor:
            tokens.append(up.lower())
        elif re.match(r"^\d+(ST|ND|RD|TH)$", up):
            tokens.append(up.lower())
        elif up in {"NE", "NW", "SE", "SW"}:
            tokens.append(up)
        else:
            tokens.append(up.capitalize())
    return " ".join(tokens)


def normalize_search_text(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s\-]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def summarize_slice(df: pd.DataFrame) -> dict[str, Any]:
    n_sales = int(len(df))
    prices = df["sale_price"].to_numpy(dtype=np.float64)
    p25, p50, p75 = np.percentile(prices, [25, 50, 75])

    mix = {
        "house": int((df["property_group"] == "house").sum()),
        "condo": int((df["property_group"] == "condo").sum()),
        "coop": int((df["property_group"] == "coop").sum()),
    }

    flagged = df["financed_base"].isin([0.0, 1.0])
    flagged_n = int(flagged.sum())
    matched_n = int((df["financed_base"] == 1.0).sum())
    unmatched_n = int((df["financed_base"] == 0.0).sum())
    unmatched_pct = (
        round(100.0 * unmatched_n / flagged_n, 1)
        if flagged_n >= MIN_FLAGGED_FOR_SHARE
        else None
    )

    cema_n = int((df["cema_base"] == 1.0).sum())

    ltv = df.loc[df["valid_ltv"], "ltv"].to_numpy(dtype=np.float64)
    valid_ltv_n = int(len(ltv))
    if valid_ltv_n >= MIN_VALID_LTV:
        median_ltv = round(float(np.median(ltv) * 100.0), 1)
        high_ltv_pct = round(float(np.mean(ltv > 0.95) * 100.0), 1)
    else:
        median_ltv = None
        high_ltv_pct = None

    n_1m = int((prices >= 1_000_000).sum())
    n_2m = int((prices >= 2_000_000).sum())
    n_3m = int((prices >= 3_000_000).sum())

    return {
        "n_sales": n_sales,
        "mix": mix,
        "median_price": int(round(p50)),
        "p25_price": int(round(p25)),
        "p75_price": int(round(p75)),
        "flagged_n": flagged_n,
        "unmatched_n": unmatched_n,
        "matched_n": matched_n,
        "unmatched_pct": unmatched_pct,
        "cema_n": cema_n,
        "valid_ltv_n": valid_ltv_n,
        "median_ltv": median_ltv,
        "high_ltv_pct": high_ltv_pct,
        "n_1m_plus": n_1m,
        "share_1m_plus": round(100.0 * n_1m / n_sales, 1),
        "share_2m_plus": round(100.0 * n_2m / n_sales, 1),
        "share_3m_plus": round(100.0 * n_3m / n_sales, 1),
    }


def summarize_by_type(df: pd.DataFrame) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for ptype in ("house", "condo", "coop"):
        sub = df[df["property_group"] == ptype]
        if len(sub) == 0:
            continue
        prices = sub["sale_price"].to_numpy(dtype=np.float64)
        flagged_n = int(sub["financed_base"].isin([0.0, 1.0]).sum())
        unmatched_n = int((sub["financed_base"] == 0.0).sum())
        unmatched_pct = (
            round(100.0 * unmatched_n / flagged_n, 1)
            if flagged_n >= MIN_FLAGGED_FOR_SHARE
            else None
        )
        out[ptype] = {
            "n": int(len(sub)),
            "med": int(round(float(np.median(prices)))),
            "fn": flagged_n,
            "cp": unmatched_pct,
        }
    return out


def summarize_years(df: pd.DataFrame) -> list[list[Any]]:
    rows = []
    grouped = {int(yr): grp for yr, grp in df.groupby("sale_year", sort=True)}
    for yr in YEARS:
        sub = grouped.get(yr)
        if sub is None or len(sub) == 0:
            rows.append([yr, 0, None, 0, None])
            continue
        n = int(len(sub))
        med = int(round(float(np.median(sub["sale_price"].to_numpy(dtype=np.float64)))))
        fn = int(sub["financed_base"].isin([0.0, 1.0]).sum())
        unm = int((sub["financed_base"] == 0.0).sum())
        cp = round(100.0 * unm / fn, 1) if fn >= MIN_FLAGGED_FOR_SHARE else None
        rows.append([yr, n, med, fn, cp])
    return rows


def dominant_str(series: pd.Series) -> str:
    vc = series.dropna().astype(str).str.strip()
    vc = vc[vc != ""]
    if vc.empty:
        return ""
    return str(vc.value_counts().idxmax())


def dominant_int(series: pd.Series) -> int | None:
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        return None
    return int(s.astype(int).value_counts().idxmax())


def main() -> None:
    SHARDS_DIR.mkdir(parents=True, exist_ok=True)

    nta_raw = json.loads(NTA_LOOKUP_PATH.read_text())
    nta_names = {row["nta2020"]: row["ntaname"] for row in nta_raw}
    nta_boros = {row["nta2020"]: row.get("boroname", "") for row in nta_raw}

    sales_cols = [
        "sale_id",
        "bbl",
        "borough",
        "block",
        "lot",
        "property_group",
        "address",
        "zip_code",
        "year_built",
        "sale_price",
        "sale_date",
        "nta",
        "bin",
        "in_acris_borough",
    ]
    link_cols = [
        "sale_id",
        "deed_match",
        "financed_base",
        "mortgage_amount_base",
        "cema_base",
    ]

    sales = pd.read_csv(DATASET_DIR / "sales.csv.gz", usecols=sales_cols, low_memory=False)
    links = pd.read_csv(DATASET_DIR / "links.csv.gz", usecols=link_cols, low_memory=False)
    raw_rows = int(len(sales))
    pos_rows = int((sales["sale_price"] > 0).sum())

    df = sales.merge(links, on="sale_id", how="left")
    df = df[df["sale_price"] >= MIN_PRICE].copy()
    df["sale_year"] = df["sale_date"].astype(str).str.slice(0, 4).astype(int)
    df["zip_int"] = pd.to_numeric(df["zip_code"], errors="coerce")
    df["bin_int"] = pd.to_numeric(df["bin"], errors="coerce")
    df["ltv"] = np.where(
        (df["financed_base"] == 1.0) & (df["mortgage_amount_base"] > 0) & (df["sale_price"] > 0),
        df["mortgage_amount_base"] / df["sale_price"],
        np.nan,
    )
    df["valid_ltv"] = df["ltv"].notna() & (df["ltv"] > 0.05) & (df["ltv"] <= 1.05)

    # Benchmarks: NYC + each borough
    benchmarks: dict[str, Any] = {
        "meta": {
            "data_version": "1.2.0",
            "note_version": "1.2.2",
            "source_doi": "https://doi.org/10.5281/zenodo.24274709",
            "raw_input_rows": raw_rows,
            "positive_price_rows": pos_rows,
            "screened_10k_rows": int(len(df)),
            "min_price": MIN_PRICE,
            "years": YEARS,
        },
        "nyc": summarize_slice(df),
        "boroughs": {},
    }
    for boro, grp in df.groupby("borough", sort=True):
        b_int = int(boro)
        benchmarks["boroughs"][str(b_int)] = {
            "name": BOROUGH_NAMES.get(b_int, str(b_int)),
            **summarize_slice(grp),
        }

    index_rows: list[list[Any]] = []
    zip_shard: dict[str, Any] = {}
    nta_shard: dict[str, Any] = {}
    bldg_shards: dict[str, dict[str, Any]] = {f"b{i}": {} for i in range(10)}

    # 1. ZIP codes
    valid_zips = df[df["zip_int"].notna() & (df["zip_int"] >= 10000) & (df["zip_int"] <= 11699)]
    for zval, grp in valid_zips.groupby(valid_zips["zip_int"].astype(int), sort=True):
        if len(grp) < MIN_GEO_SALES:
            continue
        eid = f"zip-{zval}"
        boro = int(grp["borough"].value_counts().idxmax())
        bname = BOROUGH_NAMES.get(boro, "")
        top_ntas = [
            nta_names.get(code, code)
            for code in grp["nta"].dropna().value_counts().head(2).index.tolist()
        ]
        sub_label = " · ".join(dict.fromkeys([bname, *top_ntas]))
        summary = summarize_slice(grp)
        record = {
            "id": eid,
            "kind": "zip",
            "code": str(zval),
            "name": f"ZIP {zval}",
            "subtitle": sub_label,
            "borough": boro,
            "borough_name": bname,
            "nta_names": top_ntas,
            **summary,
            "by_type": summarize_by_type(grp),
            "years": summarize_years(grp),
        }
        zip_shard[eid] = record
        search_terms = normalize_search_text(f"{zval} {bname} {' '.join(top_ntas)}")
        index_rows.append(["z", eid, f"ZIP {zval}", sub_label, search_terms, summary["n_sales"]])

    # 2. NTAs (2020 Neighborhood Tabulation Areas)
    for nta_code, grp in df.dropna(subset=["nta"]).groupby("nta", sort=True):
        if len(grp) < MIN_GEO_SALES:
            continue
        eid = f"nta-{nta_code}"
        nta_title = nta_names.get(nta_code, nta_code)
        boro = int(grp["borough"].value_counts().idxmax())
        bname = nta_boros.get(nta_code) or BOROUGH_NAMES.get(boro, "")
        top_zips = [
            str(int(z))
            for z in grp.loc[(grp["zip_int"] >= 10000) & (grp["zip_int"] <= 11699), "zip_int"]
            .astype(int)
            .value_counts()
            .head(3)
            .index.tolist()
        ]
        sub_label = f"{bname} · {nta_code}" + (f" · ZIPs {', '.join(top_zips)}" if top_zips else "")
        summary = summarize_slice(grp)
        record = {
            "id": eid,
            "kind": "nta",
            "code": nta_code,
            "name": nta_title,
            "subtitle": sub_label,
            "borough": boro,
            "borough_name": bname,
            "top_zips": top_zips,
            **summary,
            "by_type": summarize_by_type(grp),
            "years": summarize_years(grp),
        }
        nta_shard[eid] = record
        search_terms = normalize_search_text(f"{nta_title} {nta_code} {bname} {' '.join(top_zips)}")
        index_rows.append(["n", eid, nta_title, sub_label, search_terms, summary["n_sales"]])

    # 3. Condo buildings (ACRIS boroughs, real BINs only, >= 25 condo sales)
    condos = df[
        (df["property_group"] == "condo")
        & (df["in_acris_borough"] == 1)
        & df["bin_int"].notna()
    ].copy()
    condos["bin_clean"] = condos["bin_int"].astype(np.int64)
    # Exclude NYC Department of Buildings placeholder BINs ending in 000000 (1000000, 3000000, etc.)
    condos = condos[(condos["bin_clean"] > 1_000_000) & (condos["bin_clean"] % 1_000_000 != 0)].copy()
    condos["addr_clean"] = condos["address"].map(clean_address)

    for bval, grp in condos.groupby("bin_clean", sort=True):
        if len(grp) < MIN_BLDG_SALES:
            continue
        addr_counts = grp.loc[grp["addr_clean"] != "", "addr_clean"].value_counts()
        primary_addr = str(addr_counts.index[0]) if len(addr_counts) else f"BIN {bval}"
        alias_addrs = [a for a in addr_counts.index[1:4].tolist() if a != primary_addr]
        boro = int(grp["borough"].value_counts().idxmax())
        bname = BOROUGH_NAMES.get(boro, "")
        z_dom = dominant_int(grp["zip_int"])
        nta_code = dominant_str(grp["nta"])
        nta_title = nta_names.get(nta_code, nta_code)
        yb_vals = pd.to_numeric(grp["year_built"], errors="coerce").dropna()
        yb_vals = yb_vals[(yb_vals >= 1800) & (yb_vals <= 2026)]
        year_built = int(yb_vals.median()) if len(yb_vals) else None

        block_dom = dominant_int(grp["block"])
        eid = f"bin-{bval}"
        sub_parts = [p for p in [nta_title or bname, bname, f"ZIP {z_dom}" if z_dom else "", f"BIN {bval}"] if p]
        sub_label = " · ".join(dict.fromkeys(sub_parts))
        summary = summarize_slice(grp)
        record = {
            "id": eid,
            "kind": "building",
            "bin": int(bval),
            "bbl_prefix": f"{boro}-{block_dom:05d}" if block_dom else None,
            "name": primary_addr,
            "aliases": alias_addrs,
            "subtitle": sub_label,
            "borough": boro,
            "borough_name": bname,
            "zip_code": str(z_dom) if z_dom else None,
            "nta_code": nta_code or None,
            "nta_name": nta_title or None,
            "year_built": year_built,
            **summary,
            "by_type": summarize_by_type(grp),
            "years": summarize_years(grp),
        }
        shard_key = f"b{bval % 10}"
        bldg_shards[shard_key][eid] = record
        search_terms = normalize_search_text(
            f"{primary_addr} {' '.join(alias_addrs)} {bval} {z_dom or ''} {nta_title} {bname}"
        )
        index_rows.append(["b", eid, primary_addr, sub_label, search_terms, summary["n_sales"]])

    # Sort index by descending sale count so high-activity entities rank naturally first on ties
    index_rows.sort(key=lambda r: (-r[5], r[2]))

    def dump_json(path: Path, payload: Any) -> int:
        txt = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
        path.write_text(txt, encoding="utf-8")
        return len(txt.encode("utf-8"))

    sizes: dict[str, int] = {}
    sizes["benchmarks.json"] = dump_json(OUT_DIR / "benchmarks.json", benchmarks)
    sizes["index.json"] = dump_json(OUT_DIR / "index.json", {"items": index_rows})
    sizes["shards/zip.json"] = dump_json(SHARDS_DIR / "zip.json", zip_shard)
    sizes["shards/nta.json"] = dump_json(SHARDS_DIR / "nta.json", nta_shard)
    for k, payload in bldg_shards.items():
        sizes[f"shards/{k}.json"] = dump_json(SHARDS_DIR / f"{k}.json", payload)

    total_bytes = sum(sizes.values())
    bldg_count = sum(len(v) for v in bldg_shards.values())
    print(f"Built lookup bundle cleanly: total={total_bytes / 1024:.1f} KB")
    print(f"  ZIPs: {len(zip_shard)} | NTAs: {len(nta_shard)} | Condo buildings: {bldg_count} | Total index items: {len(index_rows)}")
    for name, sz in sorted(sizes.items()):
        print(f"  {name}: {sz / 1024:.1f} KB")

    # Sanity assertions
    assert all(int(eid.split("-")[1]) % 1_000_000 != 0 for s in bldg_shards.values() for eid in s), "Placeholder BIN leaked!"
    assert zip_shard["zip-10301"]["unmatched_pct"] is None, "Staten Island ZIP should have null unmatched_pct!"
    assert zip_shard["zip-10013"]["unmatched_pct"] is not None
    print("Sanity assertions PASSED.")


if __name__ == "__main__":
    main()
