# Dataset 1.2.0: outside-user test

Please try this without help from the author. Set aside about 15 minutes. You need Python 3.11 or later; no additional packages, account or data subscription are required.

1. Download `dataset_1_2_0_quickstart.zip` from https://nychousingdata.com/reproduce/#dataset and unzip it.
2. Open a terminal in the extracted `dataset` folder. Run `python3 run.py` (on Windows, use `py -3 run.py` if that is your Python command).
3. Find `results/RESULTS.json`. How many eligible condominium sales link to deeds? What is the percentage?
4. Open `results/annual_condo_coverage.csv` and `results/condo_group_summary.csv`. Identify the mortgage-match denominator and one difference between linked and unlinked sales. Does the example let you count unlinked sales as cash purchases?
5. Record the time taken, commands, errors and unclear instructions in `FEEDBACK.md`. Please return that file and your output JSON. Do not include personal file paths or transaction information in a public report.

Expected aggregate check: 121,263 links out of 126,251 eligible sales, or about 96.049%. The 4,988 unlinked sales have unmeasured financing. The exercise describes a fixed data extract; it does not validate documents or measure population linkage accuracy.

Please note any help you needed. This will count as an outside-user test only once an outside researcher has actually run it and returned feedback. The author's clean-folder check is a separate computational check.
