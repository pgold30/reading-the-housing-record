"""14 October 2026: humanizer pass over the five stories (prose only; facts unchanged)."""
from pathlib import Path
import shutil
ROOT = Path(__file__).resolve().parent
EDITS = {
 'stories/mortgage-recording-tax/index.html': [
  ("These are gross charges on each recorded loan, before credits, exemptions and consolidation agreements, so they describe the schedule rather than any one buyer’s bill.",
   "These are gross charges on each recorded loan, before credits, exemptions and consolidation agreements. A buyer’s actual bill can be lower."),
  ("<p>A buyer who can pay cash skips the tax. A buyer who needs a loan pays it, and the less someone has saved, the bigger the loan and the bigger the tax.",
   "<p>Paying cash skips the tax. Borrowing triggers it, and the less someone has saved, the bigger the loan and the bigger the tax."),
  ("Those figures hold sales fixed: they show the size of the swap, not a forecast.",
   "Those figures hold sales fixed, so they measure the size of the swap and do not predict how buyers would respond."),
  ("<p>The records show the statutory charge. They cannot show how much of it ends up with buyers, sellers or lenders.</p>",
   "<p>The records show the statutory charge but not how much of it ends up with buyers, sellers or lenders.</p>"),
 ],
 'stories/nyc-million-dollar-tax-line/index.html': [
  ("<p>Not everyone moved. Across the three new lines,", "<p>Across the three new lines,"),
  ("<p>Who stays matters. Where a company sold the home,", "<p>Where a company sold the home,"),
  ("A tax line this sharp charges most the buyers and sellers who do not notice it, or cannot change the price.",
   "The jump falls hardest on buyers and sellers who miss the line or cannot move a price that is already set."),
 ],
 'stories/cash-buyer-discount/index.html': [
  (" That comparison does not tell us what would happen to a particular sale if the buyer changed payment method.", ""),
  ("Excluding this reproducibly identified group changes the estimate substantially; that change does not identify how much family transfers cause the original gap.",
   "Setting this group aside halves the estimate, but that alone does not show how much of the gap family transfers cause."),
  ("That is a useful way to assemble a large dataset, but a nearby mortgage does not automatically establish purchase financing. The borrower, collateral and purpose of the loan need to fit the purchase.",
   "A nearby mortgage counts as purchase financing only when its borrower, collateral and purpose fit the purchase."),
 ],
 'stories/foreclosure-deed-price/index.html': [
  ("These are descriptive patterns, not rules that classify a deed by themselves.",
   "Neither pattern classifies a deed on its own."),
 ],
 'stories/missing-condo-sales/index.html': [
  ("This comparison does show that the pooled borough gap is not simply a comparison of expensive Manhattan homes with cheaper Bronx homes.",
   "So the borough gap is more than a gap between expensive Manhattan homes and cheaper Bronx ones."),
 ],
}
for f, pairs in EDITS.items():
    p = ROOT / f; t = p.read_text()
    for a, b in pairs:
        assert t.count(a) == 1, (f, a[:70], t.count(a)); t = t.replace(a, b)
    p.write_text(t); shutil.copyfile(p, ROOT / 'dist' / f)
print('ok')
