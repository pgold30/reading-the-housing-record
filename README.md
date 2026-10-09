# Reading the Housing Record

Research website for Pablo Loschi's work on New York City housing records:

- *Who Gets the House? Related-Party Transfers and the Cash–Mortgage Price Gap in New York City* — [10.5281/zenodo.22421850](https://doi.org/10.5281/zenodo.22421850)
- *When a Deed Is Not a Market Sale: Foreclosure Transfers, Statutory Consideration, and Repeat-Sales House-Price Measurement* — [10.5281/zenodo.22925383](https://doi.org/10.5281/zenodo.22925383)
- *The Shape of the Tax: Transaction Shifting at New York City's 2019 Transfer-Tax Notches and the Mortgage Recording Tax* — [10.5281/zenodo.22925301](https://doi.org/10.5281/zenodo.22925301)
- *The Execution-Certainty Wedge* — model and replication links on its paper page.

Live site: https://nychousingdata.com/

Static HTML and CSS, no build step. Numbers on the site come from the linked public paper releases. Release identifiers remain in citation metadata and download filenames; page summaries omit revision logs.

## Housing Stories

The `stories/` section explains the research for general readers. Its initial order is an editorial estimate of reader appeal: tax thresholds, cash buyers, foreclosure deeds, condominium linkage. It is not a measured popularity ranking. Four articles link to their sources and offer eight downloadable graphics, CSV files and an Atom feed. Original new article text and graphics are CC BY 4.0; underlying releases keep their own terms.

The condominium article adds a descriptive borough-by-price comparison and annual coverage check on frozen dataset v1.0.1. Its runnable Python files are included in the graphics bundle. Coverage, agreement with earlier code and verified accuracy are separate concepts. Missing deed or mortgage links cannot establish cash financing.

Journal submission names and references were supplied by Pablo on 1 October 2026. They describe submissions, not accepted publications; citation metadata continues to identify the Zenodo preprints.

## Deployment

Paper and dataset findings use full-width rows so that their qualifications remain readable. Paper pages put the PDF and replication links below the title. The shared layout has been checked at 390, 768, 1024 and 1440 pixels; tables and citations scroll within their own containers. Keep long findings out of narrow statistic cards.

GitHub Pages serves `main` at the repository root. `dist/` mirrors the public files for the existing secondary hosting setup. Keep both copies in sync when editing. The website has no added tracking or contact form. Email links use Pablo's public address; preparing pitches does not send messages.

## Paper page conventions

Each paper page presents a short finding, one PDF action, one replication action and section navigation. Replication links identify the fixed public release behind the displayed findings. Citation metadata retains the paper DOI. Keep substantive interpretation limits in a short scope note; document audit detail and revision history belong in the linked manuscript/archive. Do not describe audit agreement as independently verified accuracy. New review scenarios remain off the public site until incorporated into a public paper release.

The primary navigation is Overview, Stories, Papers, Data and About. Paper sidebars link to the matching general-reader story and shared dataset page, avoiding repeated Zenodo links. LinkedIn, Medium and the generic Zenodo-profile link are omitted from the About links at Pablo's request.

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
