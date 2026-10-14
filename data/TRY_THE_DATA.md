# Try the linked data

Download nyc_linked_dataset_v1.0.zip and the unchanged examples archive linked on the record. Use Python 3.10 or newer; no extra packages or account are needed. From the folder holding both downloads, extract them into the same location:

```sh
python3 -m zipfile -e nyc_linked_dataset_v1.0.zip .
python3 -m zipfile -e nyc_linked_dataset_v1.0.1_examples.zip .
cd nyc_linked_dataset_v1.0
python3 examples/recorded_mortgage_example.py build --output annual_condo_coverage.csv
python3 examples/condo_selection.py build --output selection
```

The first result separates annual condominium deed coverage from mortgage matches among uniquely linked sales. The second compares linked and unlinked condominium records. Read the output denominators before comparing shares. A blank financing flag is not a cash purchase; a mortgage match is not verified purchase finance. Neither table is an appreciation index.

If you try it, email loschi.pablo@gmail.com with your operating system, Python version, release used, command and whether the result reproduced. An error message without names or property addresses is enough. A useful next test is whether the documentation lets you make a borough comparison without help. External users have not yet validated this release; an invitation is not a completed use report.
