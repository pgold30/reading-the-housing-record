# Reading the Housing Record

Research website for Pablo Loschi's work on New York City housing records:

- *Who Gets the House? Related-Party Transfers and the Cash–Mortgage Price Gap in New York City* — [10.5281/zenodo.22421850](https://doi.org/10.5281/zenodo.22421850)
- *When a Deed Is Not a Market Sale: Foreclosure Transfers, Statutory Consideration, and Repeat-Sales House-Price Measurement* — [10.5281/zenodo.22925383](https://doi.org/10.5281/zenodo.22925383)
- *The Shape of the Tax: Transaction Shifting at New York City's 2019 Transfer-Tax Notches and the Mortgage Recording Tax* — [10.5281/zenodo.22925301](https://doi.org/10.5281/zenodo.22925301)
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

The primary navigation is Explore data, Stories, Research, For journalists and About. Paper sidebars link to the matching general-reader story and shared dataset page, avoiding repeated Zenodo links. LinkedIn, Medium and the generic Zenodo-profile link are omitted from the About links at Pablo's request.

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
