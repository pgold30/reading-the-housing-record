# Reading the Housing Record

Research website for Pablo Loschi's work on New York City housing records:

- *Who Gets the House? Related-Party Transfers and the Cash–Mortgage Price Gap in New York City* — [10.5281/zenodo.22421850](https://doi.org/10.5281/zenodo.22421850)
- *When a Deed Is Not a Market Sale: Foreclosure Transfers, Statutory Consideration, and Repeat-Sales House-Price Measurement* — [10.5281/zenodo.22925383](https://doi.org/10.5281/zenodo.22925383)
- *The Shape of the Tax: Round Prices and Bunching at New York City's 2019 Transfer-Tax Notches* — [10.5281/zenodo.22925301](https://doi.org/10.5281/zenodo.22925301)
- *The Execution-Certainty Wedge* — model and replication links on its paper page.

Live site: https://nychousingdata.com/

Static HTML and CSS, no build step. Numbers on the site come from the linked public paper releases. Release identifiers remain in citation metadata and download filenames; page summaries omit revision logs.

## Housing Stories

The `stories/` section explains the research for general readers. Its initial order is an editorial estimate of reader appeal: mortgage recording tax, tax thresholds, cash buyers, foreclosure deeds, condominium linkage. It is not a measured popularity ranking. Five articles link to their sources and offer nine downloadable graphics, CSV files and an Atom feed. The original eight-chart ZIP is retained; the mortgage comparison has separate downloads. Original new article text and graphics are CC BY 4.0; underlying releases keep their own terms.

The condominium article adds a descriptive borough-by-price comparison and annual coverage check on frozen dataset v1.0.1. Its runnable Python files are included in the graphics bundle. Coverage, agreement with earlier code and verified accuracy are separate concepts. Missing deed or mortgage links cannot establish cash financing.

Journal submission names and references were supplied by Pablo on 1 October 2026. They describe submissions, not accepted publications; citation metadata continues to identify the Zenodo preprints.

## Deployment

Paper and dataset findings use full-width rows so that their qualifications remain readable. Paper pages put the PDF and replication links below the title. The shared layout has been checked at 390, 768, 1024 and 1440 pixels; tables and citations scroll within their own containers. Keep long findings out of narrow statistic cards.

GitHub Pages serves `main` at the repository root. `dist/` mirrors the public files for the existing secondary hosting setup. Keep both copies in sync when editing. The website uses Cloudflare Web Analytics without tracking cookies; the local loader respects Do Not Track and Global Privacy Control. There is no contact form. Email links use Pablo's public address; preparing pitches does not send messages.

## Paper page conventions

Each paper page presents a short finding, one PDF action, one replication action and section navigation. Replication links identify the fixed public release behind the displayed findings. Citation metadata retains the paper DOI. Keep substantive interpretation limits in a short scope note; document audit detail and revision history belong in the linked manuscript/archive. Do not describe audit agreement as independently verified accuracy. New review scenarios remain off the public site until incorporated into a public paper release.

The primary navigation is Explore data, Stories, Research, Press and About. Paper sidebars link to the matching general-reader story and shared dataset page, avoiding repeated Zenodo links. LinkedIn, Medium and the generic Zenodo-profile link are omitted from the About links at Pablo's request.

## 9 October editorial correspondence update

The website links reviewed author-named PDFs for house, tax and deed, plus the
focused deed note and dataset article. These are website manuscript copies;
the Zenodo analysis archives and their numerical findings have not changed.
Keep the old PDF URLs for incoming citations. The older wedge page retains
its archived identity and distinguishes the separate benchmark-audit methods paper.
No anonymous journal manuscript is exposed as a public preprint.

House review counts from a mixed random/targeted queue are not population error
rates. Deed bands condition on classification; the narrower headline now shows
its whole-path band, while the stricter story graphic keeps its different joint
band definition. The tax landing card uses a local-density ratio instead of
counts over unequal periods. The featured story remains an editorial choice;
no private guest-post invitation is described as an accepted publication.

## 9 October public release refresh

The primary PDF actions and fixed archive links now use house 3.6, tax 2.7
(replication 1.10), deed 1.0.9 and dataset documentation 1.0.2. The benchmark
audit 1.0 is linked separately from the older wedge simulation. House 3.6
resolves the earlier cross-reference, reports the locked probability sample
and retains the headline series; two sampled financing corrections give 9.23
log points, with 18 endpoints still unresolved. No independent accuracy claim.

Preserve the story and paper landing-page paths for incoming Housing Notes
links. Old PDFs remain available but current downloads drive the sitemap.
Keep GitHub Pages and this static stack for any later custom-domain change;
configure and verify the owned domain before changing canonical URLs. The custom domain nychousingdata.com was purchased and verified on 9 October 2026. A guest-post invitation is not an
accepted or published article and must not be presented as one.

## Custom domain

The primary address is https://nychousingdata.com/. GitHub Pages serves the same repository and paths; keep both root and dist/CNAME set to nychousingdata.com. Canonical, citation, social-preview, sitemap and Atom URLs use the custom domain. Old download files remain in place. The domain uses Spaceship DNS, four GitHub Pages A records at the apex and a www CNAME to pgold30.github.io. Keep the GitHub ownership TXT record. Free GitHub Pages hosting continues.

## Public tools and search setup

NYC Housing Data is the site name; Reading the Housing Record remains the research series. The code-native SVG logo is shared by the header and favicon. Keep original paper, story and PDF paths.

`explore/` uses only aggregate cells built by `tools/build_explorer.py`. Rebuild with `python3 tools/build_explorer.py ../nyc_linked_dataset/build --archive ../zenodo_uploads/dataset_v1.0/nyc_linked_dataset_v1.0.zip`. The builder verifies sales/link file hashes against the published archive. No names, addresses, parcel identifiers or individual rows enter the browser asset. Positive recorded prices are included without a market-sale screen. Counts are sales-file rows, not deduplicated deeds. Medians pool records within the filters and are not a price index. Co-ops and Staten Island have no ACRIS linkage measure; condo mortgage flags require a unique deed link. Every percentage names its denominator.

`guide/` explains amounts, parcels, dates and candidate mortgage evidence with a clearly fictional example. `press/` consolidates reusable findings and existing chart assets. The historical tax illustration lives inside the existing tax story at `#tax-tool`, covers the $1m, $2m and $3m lines, and excludes seller taxes, mortgage charges, exemptions and grandfathering. Its source is TSB-M-19(1)R; do not present it as a current closing-cost calculator.

Cloudflare Web Analytics is configured for the owned domain. The public beacon token in `assets/analytics.js` is not an API credential. It runs only on the production domain and is skipped for DNT/GPC. Privacy details are in `privacy/`. No DNS proxy or paid analytics plan is needed. Google Search Console ownership is verified by the apex TXT record; retain that record and the separate GitHub ownership TXT. Submit the root sitemap after publishing new routes. Search-engine inclusion is not guaranteed.

GitHub approved the TLS certificate after a single documented provisioning restart on 9 October 2026. HTTPS enforcement is enabled. Check apex, www redirect and old GitHub paths when changing the domain configuration.

## Resource-page roles

Stories is the editorial index and keeps the full explanations. Press resources contains contact, the graphics pack and individual chart downloads grouped by topic; it does not repeat the findings or embed the same charts again. The old `/stories/#reporters` anchor remains as a compact pointer to `/press/`. Keep resource headings compact. Page shells use the available viewport with consistent responsive gutters; avoid reintroducing fixed page-width caps. The Explorer and historical tax tables become labelled rows on phones, while chart geometry is redrawn for the actual panel width.

Performance: the optional audio uses `preload="none"` so the 22 MB MP3 is requested when the reader starts playback. Cloudflare field metrics include development visits; interpret them separately from PageSpeed laboratory tests.

## Editorial voice

Stories lead with the concrete finding and explain what a buyer or data user can learn from it. Keep scope, unresolved evidence and incidence limits with the claims they qualify. The tax story raises the fairness of an additional statutory charge on borrowing; it does not describe double taxation as an established finding. Preserve source URLs, archived graphics and research estimates when editing site prose.

## Mortgage story and public change history

The mortgage-tax story leads Home and Stories as an editorial choice, not a measured popularity ranking. It uses the tax paper v2.7 Section 1 example: a $900,000 condo, $720,000 mortgage, 1.925% gross borrower schedule and $13,860 calculated charge. Sources, exclusions and the distinction from actual payments remain beside the calculation. Sample-average burdens of 1.41% and 1.28% are separate statistics, not individual tax rates. Co-op share loans are outside the illustration.

Each story has a brief reader takeaway. The homepage keeps compact research links; the simulation page holds the detailed account, and September media and definitions remain under expandable sections with their original anchors. `updates/` records dated changes and provides a correction contact; link it from every footer. Preserve original article paths, archived PDFs and the original graphics pack. When publishing substantive corrections, record the old claim, replacement, reason and affected pages; do not present an interpretation limit as an independently validated finding.

## Supplied video introduction

`#paper-introduction` places The Three Illusions of Real Estate beside the homepage paper cards, with native playback controls, playsinline, a poster and preload=none. The 4:47 video was supplied by Pablo on 9 October. The web copy is H.264/AAC with faststart and is compressed from about 58 MiB to 30 MiB, preserving duration. Keep the supplied original intact. The AI-generated overview includes schematic illustrations and broader wording than the papers; its visible note qualifies the cash gap, index-path interpretation and conditional simulation. Do not present its drawn charts as verified research series. A cinematic replacement is being requested from the latest public source PDFs in Pablo's specified notebook.


## Heading alignment

Shared section headings use the full content width, with a centered introduction below. Page mastheads, research actions and metadata follow the same alignment; article text, evidence notes and tables retain their reading alignment. Headings wrap naturally with balanced lines on narrow screens; never force no-wrap or shrink text to fit. The paper video has centered title, introductory copy and caption. The redundant attribution sentence beside it was removed at Pablo’s request; the schematic-chart qualifications remain visible.


## Matched model explorer, 14 October 2026

The Wedge page uses a 15 KB static JSON export of the default-policy runs reused in v6.4. It does not rerun the model in the browser. Rebuild with `python3 tools/export_wedge.py --replication /path/to/execution_certainty_wedge_v6_4/replication` (NumPy required). The exporter checks shared seeds, identical arrivals and oracle denominators, resolved cohorts, paired changes and standard errors against the saved per-seed runs. Model data contain no transaction records or addresses.

Changing the population changes the access measure only; instrument parameters and whole-run value remain fixed. Presets are descriptive proxy mappings, not causal NYC estimates. The all-company preset's realised model share is about 25%, not the empirical 22.84%. The constant charge matches the duty's mean scheduled haircut, not its access gain. Do not mix these runs with separately tuned target-access experiments.

The current tax-story downloads use preprint v3.0 and replication v2.0. The original graphics ZIP remains an archive; the dated `housing-stories-graphics-20261014.zip` is the current Press download. The corresponding correction is recorded at `/updates/#2026-10-14-model-and-tax-story`. Manuscript PDFs and archived replication outputs were preserved.

The Wedge primary link and benchmark figure use the verified 14 October v6.4 release (Zenodo 23362696). The v6.1 PDF and figure remain available at their original paths. The explorer shows default-policy scenarios; it does not mix in the separately tuned access-target settings of v6.4 Tables 4–5.

## Condominium unit-lot correction, 21 October 2026

The deposited 1.1.0 linker limited condominium unit lots to 1001–1999. The official PLUTO range is 1001–6999. The former Bronx public-record-gap interpretation is withdrawn at its original story URL. Until corrected outputs are checked and released, the explorer withholds condo and combined-property link/financing fields, retaining raw counts and price medians. Blank link fields in downloads carry `linkage_status=under_review`. House and co-op fields are unchanged. Original aggregates are archived under `assets/explore/archive/`; original paper PDFs and dated chart archives remain available. The current press pack omits condo linkage graphics. Candidate expanded-range counts are not a document-validated accuracy measure and are not published in this correction.

### Responsive layouts (22 October 2026)

The homepage story row uses `auto-fit`, so removing a card does not leave an empty third column. On desktop, an odd final card in the Stories list spans the row; cards with images use a side-by-side layout there. Shared shells use a 1440px maximum and align the navigation with page content. Article prose keeps its narrower reading width.

On phones, the five navigation links occupy one grid row with 44px touch targets. Research SVGs retain a readable width inside a keyboard-focusable scrolling figure with a visible sideways-scroll hint. Explorer and tax tables retain their labelled mobile layouts. CSS changes must update the stylesheet query revision in every HTML route and mirror changes to `dist/`.

The 22 October check covered all 19 routes at 320, 375, 768, 1024, 1440 and 1920px. It also exercised explorer borough/property/year filters and the tax-threshold selector. Verification evidence is saved outside the public site in `paper_improvements_2026-10-22/website_responsive/`.


### Paper releases, 25 October 2026

Current Zenodo records are House 3.10 (23638520), Tax 3.3 (23638571) and full Deed 1.0.12 (23638576). The manuscript downloads match those records byte for byte. House’s 18 follow-up financing cases remain unresolved. The Deed page and story distinguish fixed-label chart bands from model-dependent classification-rate ranges and the 40 human-reference readings from historical AI agreement. The family-story citywide surname/address counts remain explicitly dated to dataset 1.1.0; no updated count is inferred from improved linkage. Baseline archives and earlier download URLs are retained. Journal files were not replaced.
