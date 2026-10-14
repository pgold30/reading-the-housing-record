"""14 October 2026: sharper story headlines and decks, fairness sections and
current paper versions.

Every number below was checked against the current releases: The Shape of the
Tax v3.0 (Sections 2.2, 4.4, 4.8, 4.9, 5; Table 4; Supplemental Appendix
Section I, Tables A13-A14), Who Gets the House? v3.7 (abstract, Section 4) and
When a Deed Is Not a Market Sale v1.0.9 (abstract, Section 5, Figure 6 table).
Edits the root files and mirrors them into dist/. Run once from the repo root.
"""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
EDITED = []


def edit(path, pairs, count=None):
    p = ROOT / path
    t = p.read_text()
    for old, new in pairs:
        n = t.count(old)
        assert n >= 1, (path, old[:80])
        if count is not None:
            assert n == count, (path, old[:80], n)
        t = t.replace(old, new)
    p.write_text(t)
    EDITED.append(path)


# ---------------------------------------------------------------- titles
TITLES = {
    "Buying with a mortgage in NYC comes with an extra tax":
        "Same $900,000 condo, $13,860 more in tax for the buyer with a mortgage",
    "At $2 million, one extra dollar adds about $5,000 in tax":
        "One dollar over $2 million costs a New York buyer $5,000 in tax",
    "The cash discount shrinks after screening possible family transfers":
        "Half the cash-buyer discount fades once possible family sales are set aside",
    "A foreclosure deed’s dollar amount may not be a sale price":
        "When a lender takes back a home, the record can look like a sale",
    "The condo data gap is much wider in the Bronx":
        "Public records link fewer than half of Bronx condo sales to a deed",
}
DECKS = {
    "mortgage-recording-tax": (
        "House and condo buyers who borrow face a recording tax that a comparable cash purchase avoids. What does that add, and is the distinction fair?",
        "Buyers who borrow owe a recording tax on the loan that cash buyers never pay. Across four boroughs it comes to about $244 million a year."),
    "nyc-million-dollar-tax-line": (
        "Crossing $2 million adds about $5,000 to the buyer’s tax under the 2019 rules. Sales shifted below that line after the reform. House and condo buyers who take a mortgage face another tax.",
        "Since the 2019 tax change, sales at exactly $1,999,999 went from about one a year to about 21. Most deals that would have closed at $2 million now close just below it, and four in ten still pay the jump."),
    "cash-buyer-discount": (
        "Buyers recorded as paying cash often pay less for the same house. Screening possible transfers between relatives roughly halves that gap.",
        "In New York City records, houses bought for cash sell for about 9% less. Set aside sales between people who share a surname and the gap halves; when a company pays cash, it is too small to tell from zero."),
    "foreclosure-deed-price": (
        "A foreclosure amount may reflect a bid or debt. Treating it as a market price changes a house-price index through the financial crisis.",
        "Foreclosure deeds can carry a lender’s bid or a cancelled debt, and most reach the city’s sales file as if they were prices. In the Bronx, counting them shifts the 2010 house-price index by about a tenth."),
    "missing-condo-sales": (
        "The same public-record match links about four in five eligible Manhattan sales to a deed, but fewer than half in the Bronx. That changes which transactions appear in financing comparisons.",
        "The same matching rules link 79% of Manhattan condo sales to a deed and 45% in the Bronx, even at the same prices. Studies built on the linked sales see much less of the Bronx."),
}
FILES = [str(p.relative_to(ROOT)) for p in sorted((ROOT / 'stories').glob('*/index.html'))] + ['stories/index.html', 'stories/feed.xml', 'index.html']
for f in FILES:
    p = ROOT / f
    t = p.read_text(); o = t
    for a, b in TITLES.items():
        t = t.replace(a, b)
    if t != o:
        p.write_text(t); EDITED.append(f)
for slug, (old, new) in DECKS.items():
    edit(f'stories/{slug}/index.html', [(old, new)])

# Updated dates on the edited stories.
for slug in ('mortgage-recording-tax', 'nyc-million-dollar-tax-line', 'cash-buyer-discount', 'foreclosure-deed-price', 'missing-condo-sales'):
    p = ROOT / f'stories/{slug}/index.html'; t = p.read_text()
    t = t.replace('"dateModified": "2026-10-09"', '"dateModified": "2026-10-14"')
    t = t.replace('<span>Updated 9 October 2026</span>', '<span>Updated 14 October 2026</span>')
    if slug == 'mortgage-recording-tax':
        t = t.replace('<time datetime="2026-10-09">9 October 2026</time><span>4 min read</span>',
                      '<time datetime="2026-10-09">9 October 2026</time><span>Updated 14 October 2026</span><span>5 min read</span>')
    p.write_text(t)

# ---------------------------------------------------------------- mortgage recording tax
edit('stories/mortgage-recording-tax/index.html', [
    ("<p>Consider a $900,000 condominium bought in either of two ways: without a mortgage, or with a $720,000 loan. Under the borrower schedule used in my study, the loan carries a gross mortgage recording charge of $13,860. The purchase without a mortgage carries no purchase-mortgage recording charge.</p>\n<p>That difference comes from how the purchase is financed. It sits alongside taxes on the transfer of the property, even when the sale price is below the $1 million mansion-tax threshold.</p>",
     "<p>Two people buy the same $900,000 condo. One pays cash. The other puts 20% down and borrows $720,000. When that loan is recorded at closing, the second buyer owes $13,860 in mortgage recording tax before any credits, on top of the down payment. The cash buyer owes none of it.</p>\n<p>The difference comes only from how the home is paid for. It applies below the $1 million mansion-tax line too, and it falls due at the moment a borrower has the least cash to spare.</p>"),
    ("Illustration from <em>The Shape of the Tax</em>, v2.8, Section 1.", "Illustration from <em>The Shape of the Tax</em>, v3.0, Supplemental Appendix Section I."),
    ("<p>My study links sales and recorded mortgages in Manhattan, the Bronx, Brooklyn and Queens from 2016 to 2025. Applying the standard borrower schedule to recorded principal gives a gross charge averaging 1.41% of purchase price for houses and 1.28% for condominiums in the financed sample.</p>\n<p>Those are sample averages expressed as a share of price. They are not tax rates to apply to your own purchase. They also are not observed payments: the calculation cannot recover every credit, exemption or consolidation adjustment.</p>",
     "<p>My study links sales and recorded mortgages in Manhattan, the Bronx, Brooklyn and Queens from 2016 to 2025: 172,725 financed house and condo purchases. Applying the borrower schedule to each recorded loan gives a charge averaging 1.41% of the purchase price for houses and 1.28% for condos. Summed over every financed purchase between $300,000 and $6 million, it comes to about $244 million a year.</p>\n<p>These are gross charges on each recorded loan, before credits, exemptions and consolidation agreements, so they describe the schedule rather than any one buyer’s bill.</p>"),
    ("<p>A buyer who can pay without a mortgage avoids this purchase-financing charge. A buyer who needs to borrow faces a statutory charge in addition to the taxes on the transfer. That raises a question for tax policy: should needing a loan change the tax attached to buying an otherwise comparable home?</p>\n<p>The records measure the statutory difference. They cannot tell us how much ultimately falls on buyers through closing costs, sellers through prices, or lenders through loan terms. Nor does the study establish which replacement tax would be best.</p>",
     "<p>A buyer who can pay cash skips the tax. A buyer who needs a loan pays it, and the less someone has saved, the bigger the loan and the bigger the tax. A co-op buyer who borrows pays none of it either, because a co-op loan is secured by shares, not by real property. Should needing a loan raise the tax on buying a home?</p>\n<p>In May 2026, Albany considered a 1% tax on all-cash purchases of $1 million or more; it was left out of the budget passed on 27 May. The recording tax already sets cash and financed buyers apart at every price, and it is the borrower who pays.</p>\n<p>The paper prices one alternative. Raising the same $244 million from every house and condo purchase, whatever the financing, would take a flat 0.88% of the price. Under the schedules the paper tests, about nine in ten financed buyers would pay less, by roughly $5,000 on average, and cash buyers about $11,000 to $13,000 more. Those figures hold sales fixed: they show the size of the swap, not a forecast.</p>\n<p>The records show the statutory charge. They cannot show how much of it ends up with buyers, sellers or lenders.</p>"),
    ("in <a href=\"../../papers/the-shape-of-the-tax/\">The Shape of the Tax</a>, v2.8. The example and borrower rates appear in Section 1; the gross sample charges are reported in Tables 8 and 9. <a href=\"https://zenodo.org/records/23256513\">Paper and analysis archive</a>.",
     "in <a href=\"../../papers/the-shape-of-the-tax/\">The Shape of the Tax</a>, v3.0 (13 October 2026). The borrower rates appear in Section 2.2 and the $244 million total in Section 5; the $900,000 example, the gross charges (Tables A13 and A14) and the replacement schedules are in Supplemental Appendix Section I. <a href=\"https://zenodo.org/records/23333806\">Paper used for this story</a>."),
])
edit('assets/stories/mortgage-recording-comparison-notes.txt', [
    ("Illustration reproduced from The Shape of the Tax v2.7, Section 1:\nhttps://nychousingdata.com/papers/the-shape-of-the-tax/The_Shape_of_the_Tax_preprint_v2.7.pdf\nFixed archive: https://zenodo.org/records/23256513",
     "Illustration from The Shape of the Tax v3.0 (13 October 2026), Supplemental Appendix Section I:\nhttps://doi.org/10.5281/zenodo.23333806"),
])

# ---------------------------------------------------------------- $2 million line
edit('stories/nyc-million-dollar-tax-line/index.html', [
    ("<h2>Reading a comparable near $2 million</h2>",
     "<h2>Who still pays for the extra dollar?</h2>\n<p>Not everyone moved. Across the three new lines, at $2 million, $3 million and $5 million, about six in ten sales that would have closed at the round number now close just below it. The other four in ten still close at exactly the threshold and pay between $5,000 and $37,500 more tax for one extra dollar of price.</p>\n<p>Who stays matters. Where a company sold the home, a group that includes developers whose prices are set in an offering plan before units go on sale, 42% of those deals moved, against 68% where no company sold. Buyers with a mortgage record a price one dollar below the line about twice as often as cash buyers, as would happen if a lender, an appraiser or a closing attorney spots the step. A tax line this sharp charges most the buyers and sellers who do not notice it, or cannot change the price.</p>\n<h2>Reading a comparable near $2 million</h2>"),
    ("<p>The result concerns the shape of a transaction-tax schedule. A charge on the whole price creates a sudden step at the boundary. A charge confined to the portion above a threshold would have a different structure. This study does not estimate how buyers would respond to a replacement schedule.</p>\n<p>It also does not measure the government's lost receipts. Calculations that treat extra sales below a threshold as transactions moved from above it depend on that assumption. Nor do sale records reveal whether buyers, sellers or intermediaries ultimately bear the cost.</p>",
     "<p>For the city, the money at stake is small. The sales that moved avoid about $1.6 million to $2.9 million a year in tax, under 1% of the $296 million a year the 2019 schedule implies. That count treats the extra sales below each line as deals moved from just above it.</p>\n<p>The jumps exist because each rate applies to the whole price. A slice schedule, which charges each rate only on the part of the price above a line, has no one-dollar cliff, and the paper shows two that raise the same $296 million from the same sales. One keeps the progressive shape of today’s steps, and 7% of sales would pay more under it. The United Kingdom made the same switch for its stamp duty in December 2014. The study holds prices fixed for these figures and does not predict how buyers would respond, or who would bear the cost.</p>"),
    ("The figures use version 3.0, which keeps one row per deed and checks the merged sales rows against the registry.",
     "The figures use version 3.0, which keeps one row per deed and checks the merged sales rows against the registry. The share of deals that moved, by seller type, is in Section 4.4 and Table 4; the avoided tax and the slice schedules are in Sections 4.8 and 4.9 and Tables 10 and 11."),
])

# ---------------------------------------------------------------- cash discount
edit('stories/cash-buyer-discount/index.html', [
    ("<p>A house sells twice. The buyer with a mortgage pays more than the buyer recorded as paying cash. How much of that difference is a discount for a more certain closing?</p>",
     "<p>A house sells twice: once to a buyer with a mortgage, once to a buyer who pays cash. In New York City’s records the cash buyer pays about 9% less. In May 2026 Albany weighed a 1% tax on all-cash purchases of $1 million or more. So who gets the cash discount, and how much of it is a reward for a sure closing?</p>"),
    ("<p>The review used AI readings of the instruments followed by an AI cross-check against City records. It is a consistency check with the limitations documented in the paper. It does not verify every cash label or supply an independent accuracy rate for the full sample.</p>\n", ""),
    ("The headline estimates and chart are retained in version 3.6.",
     "The headline estimates and chart are retained in versions 3.6 and 3.7. The document review used AI readings of the instruments followed by an AI cross-check against City records; it is a consistency check with the limitations documented in the paper, and it does not verify every cash label or supply an independent accuracy rate for the full sample."),
    ('<a href="https://zenodo.org/records/23258572">', '<a href="https://zenodo.org/records/23276603">'),
])

# ---------------------------------------------------------------- foreclosure deeds
edit('stories/foreclosure-deed-price/index.html', [
    ("<p>A dollar amount in a property record looks like a sale price. For some foreclosure transfers, it can describe something else: an auction bid, a judgment or debt discharged when a lender takes title.</p>",
     "<p>A lender takes back a house at a foreclosure auction. The deed records an amount, perhaps the lender’s bid or the debt it cancels, often down to the cent. That figure can land in the public sales file and look like any other sale price.</p>"),
    ("Neither is a known true measure of every home's market value.</p>",
     "Neither is a known true measure of every home's market value.</p>\n<p>The effect is concentrated where lenders took back the most homes. For Bronx houses, where 11% of repeat-sale pairs touch a flagged deed, the index built with them sits 10.9 log points above the index without them in the third quarter of 2010 (95% interval 6.6 to 14.7). Anyone reading Bronx prices from the public file, from a buyer checking comparables to a reporter charting the recovery, may be reading some of these amounts.</p>"),
    ("The current paper includes the hedonic comparison and clarifies the interpretation of the index differences.",
     "The current paper includes the hedonic comparison and clarifies the interpretation of the index differences. The Bronx figure is from version 1.0.9, Section 5 and Figure 6."),
])

# ---------------------------------------------------------------- condo coverage
edit('stories/missing-condo-sales/index.html', [
    ("<p>To compare cash and mortgage purchases, start with a list of condo sales, find their deeds and look for mortgages. The difficulty is that the deed match reaches very different shares of the market across New York City.</p>",
     "<p>To see who buys condos with cash, you start with a list of sales, find each deed and look for a mortgage. In Manhattan that works for about four sales in five. In the Bronx it works for fewer than half, so any study built on the linked records sees much less of the Bronx.</p>"),
])

# ---------------------------------------------------------------- index cards, feed, homepage
CARDS = [
    ("House and condo buyers who borrow face a recording tax that a comparable cash purchase avoids. What does that add, and is the distinction fair? Co-op share loans fall outside this illustration.",
     "Buyers who borrow owe a recording tax on the loan that a cash buyer never pays: $13,860 on a $720,000 mortgage. Should needing a loan raise the tax on buying a home? The figure is the gross charge before credits and exemptions."),
    ("Since 2019 a buyer at $2 million owes about $5,000 more in tax than a buyer at $1,999,999. Did that one dollar change where deals close? The records show recorded prices, not how each deal was negotiated.",
     "Since 2019 a buyer at $2 million owes about $5,000 more in tax than a buyer at $1,999,999, and four in ten deals at the round number still pay it. Who stays on the line? The records show recorded prices, not how each deal was negotiated."),
    ("Buyers recorded as paying cash often pay less for the same house. How much of that gap is a real discount, and how much is transfers between relatives? A shared surname is a rough screen, not proof of a family sale.",
     "Houses bought for cash sell for about 9% less than the same houses bought with a mortgage. How much of that is a reward for a sure closing? Setting aside sales between people who share a surname halves it; a shared surname is a rough screen, not proof of a family sale."),
    ("Some foreclosure deeds record a bid or a discharged debt where a sale price would be. What happens to a price index when those amounts count as sales? A few transfers cannot be classified from the public record alone.",
     "Some foreclosure deeds record a bid or a cancelled debt where a sale price would be, and most reach the city’s sales file. How far does that move a price index? In the Bronx, 10.9 log points in 2010; some transfers cannot be classified from the public record alone."),
    ("The same matching rules link 78.9% of eligible Manhattan condo sales to a deed and 44.7% in the Bronx. How does that change comparisons between boroughs? The rates describe the record linkage, not the condo market itself.",
     "The same matching rules link 78.9% of eligible Manhattan condo sales to a deed and 44.7% in the Bronx, even within the same price range. How does that change comparisons between boroughs? The rates describe the record linkage, not the condo market itself."),
]
edit('stories/index.html', CARDS)
edit('stories/feed.xml', [
    ("<summary>House and condo buyers who borrow face a recording tax that a comparable cash purchase avoids. What does that add, and is the distinction fair?</summary>",
     "<summary>" + DECKS['mortgage-recording-tax'][1] + "</summary>"),
    ("<summary>New York City sales shifted below $2 million after a new tax step arrived in 2019. The records show how a line in the tax code changed the prices people recorded.</summary>",
     "<summary>" + DECKS['nyc-million-dollar-tax-line'][1] + "</summary>"),
    ("<summary>A comparison of repeat house sales finds a sizeable cash-mortgage gap. Removing possible transfers between relatives roughly halves it.</summary>",
     "<summary>" + DECKS['cash-buyer-discount'][1] + "</summary>"),
    ("<summary>When lenders take title, legal rules can shape the amount in the record. Including those transfers changes a constructed house-price index through the financial crisis.</summary>",
     "<summary>" + DECKS['foreclosure-deed-price'][1] + "</summary>"),
    ("<summary>The same public-record match links about four in five eligible Manhattan sales to a deed, but fewer than half in the Bronx. That changes which transactions appear in financing comparisons.</summary>",
     "<summary>" + DECKS['missing-condo-sales'][1] + "</summary>"),
])
p = ROOT / 'stories/feed.xml'; t = p.read_text()
t = t.replace('<updated>2026-10-09T12:00:00+02:00</updated>', '<updated>2026-10-14T12:00:00+02:00</updated>'); p.write_text(t)
edit('index.html', [
    ("<p>House and condo buyers who borrow face a recording tax that a comparable cash purchase avoids. A $720,000 loan illustrates the difference, before credits, exemptions and consolidation adjustments.</p>",
     "<p>Buyers who borrow owe a recording tax on the loan that cash buyers never pay: $13,860 on a $720,000 mortgage, about $244 million a year across four boroughs, before credits, exemptions and consolidation adjustments.</p>"),
])

# ---------------------------------------------------------------- mirror into dist/
for f in sorted(set(EDITED)):
    src, dst = ROOT / f, ROOT / 'dist' / f
    assert dst.exists(), dst
    shutil.copyfile(src, dst)
print('edited and mirrored:', sorted(set(EDITED)))
