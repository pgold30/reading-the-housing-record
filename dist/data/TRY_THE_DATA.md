# Try the linked data

Download nyc_linked_dataset_v1_2_0.zip from the version 1.2.0 record at https://doi.org/10.5281/zenodo.23557585. Python 3.10 or newer is sufficient; no extra packages or registry account are needed.

```sh
python3 -m zipfile -e nyc_linked_dataset_v1_2_0.zip .
cd nyc_linked_dataset_v1_2_0
python3 examples/recorded_mortgage_example.py build --output annual_condo_coverage.csv
python3 examples/condo_selection.py build --output selection
```

In 2021, 16,736 of 17,734 eligible condominium sales link to a deed (94.4%). Of those links, 11,106 have a base-window mortgage match (66.4%). The second example compares linked and unlinked condominium records. Read the denominators before comparing shares: an unmeasured financing field is not a cash purchase, and a mortgage match is not verified purchase finance. These medians are not an appreciation index.

If you try the example, email loschi.pablo@gmail.com with the release, Python version, command and whether it reproduced. An error message without names or property addresses is enough. External users have not yet validated this release; an invitation is not a completed use report.
