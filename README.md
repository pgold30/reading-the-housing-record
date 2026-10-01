# Reading the Housing Record

Research website for Pablo Loschi's work on New York City housing records:

- *Who Gets the House? Related-Party Transfers and the Cash–Mortgage Price Gap in New York City* — [10.5281/zenodo.22421850](https://doi.org/10.5281/zenodo.22421850)
- *When a Deed Is Not a Market Sale: Foreclosure Transfers, Statutory Consideration, and Repeat-Sales House-Price Measurement* — [10.5281/zenodo.22925383](https://doi.org/10.5281/zenodo.22925383)
- *The Shape of the Tax: Transaction Shifting at New York City's 2019 Transfer-Tax Notches and the Mortgage Recording Tax* — [10.5281/zenodo.22925301](https://doi.org/10.5281/zenodo.22925301)
- *The Execution-Certainty Wedge* — model and replication links on its paper page.

Live site: https://pgold30.github.io/reading-the-housing-record/

Static HTML and CSS, no build step. Numbers on the site come from the public Zenodo versions named on each page.

## Housing Stories

The `stories/` section explains the research for general readers. Its initial order is an editorial estimate of reader appeal: tax thresholds, cash buyers, foreclosure deeds, condominium linkage. It is not a measured popularity ranking. Four articles link to their sources and offer eight downloadable graphics, CSV files and an Atom feed. Original new article text and graphics are CC BY 4.0; underlying releases keep their own terms.

The condominium article adds a descriptive borough-by-price comparison and annual coverage check on frozen dataset v1.0.1. Its runnable Python files are included in the graphics bundle. Coverage, agreement with earlier code and verified accuracy are separate concepts. Missing deed or mortgage links cannot establish cash financing.

Journal submission names and references were supplied by Pablo on 1 October 2026. They describe submissions, not accepted publications; citation metadata continues to identify the Zenodo preprints.

## Deployment

GitHub Pages serves `main` at the repository root. `dist/` mirrors the public files for the existing secondary hosting setup. Keep both copies in sync when editing. The website has no added tracking or contact form. Email links use Pablo's public address; preparing pitches does not send messages.
