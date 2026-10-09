Housing Stories graphics and chart data, 1 October 2026

Credit: Pablo Loschi, Reading the Housing Record.
Original graphics and new story text: CC BY 4.0, https://creativecommons.org/licenses/by/4.0/
State source, version, sample and dates when reusing. Indicate any edits.
Underlying paper and dataset releases retain their own terms.

Tax ratios: The Shape of the Tax v2.7, unchanged chart series, rounded reported values.
Tax step: 2019 buyer mansion/supplemental tax illustration only; other taxes excluded.
House contrasts: Who Gets the House? v3.6, unchanged headline series, 95% bootstrap intervals.
Deed index paths: v1.0.6 published sample. Indices use 2003 Q1 = 100.
Deed uncertainty: v1.0.6 BOTH-ENDPOINT house sample, definitions D0 and D4.
The uncertainty band is conditional on the labels and matching rules.
Condo coverage: dataset v1.0.1, frozen files rerun on 1 October 2026.
Mortgage linkage is not verified purchase financing; missing links are not cash.
Full source notes and paper links appear on each article.

Reproduce the new borough-by-price check with Python's standard library:
Download and extract the dataset v1.0.1 from https://zenodo.org/records/23047979
Keep the two included .py files together, then run:
python condo_coverage_check.py /path/to/dataset/build --output results
This produces the full price-band counts and annual Manhattan/Bronx coverage gap.
The published within-price comparison uses the 100k–<500k rows.

Website stories reviewed 9 October 2026. Chart data and graphics are unchanged.
Deed series from v1.0.6 remain unchanged in v1.0.9. Current fixed source releases:
House: https://zenodo.org/records/23258572
Tax: https://zenodo.org/records/23256513
Deed: https://zenodo.org/records/23257175
Dataset documentation: https://zenodo.org/records/23257216 (data unchanged).
The both-endpoint graphic's joint band differs from the main sample's per-definition
whole-path band. Preserve the sample and band definition when quoting either.
