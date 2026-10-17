"""Figures and tables for the condominium coverage story, dataset release 1.1.0.

Usage: python condo_story_v110.py /path/to/build --output .
The build folder holds sales.csv.gz (unchanged since 1.0) and the 1.1.0 links.csv.gz.
Keep recorded_mortgage_example.py beside this file. Coverage describes deed links;
it is not verified financing or classification accuracy.
"""
import argparse
import collections
import statistics
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['text.parse_math'] = False

from recorded_mortgage_example import annual, eligible_condos, write

BOROUGHS = {'1': 'Manhattan', '2': 'Bronx', '3': 'Brooklyn', '4': 'Queens'}
BANDS = [(100000, '<100k'), (500000, '100k–<500k'), (1000000, '500k–<1m'),
         (2000000, '1m–<2m'), (6000000, '2m–<6m')]
BAND_LABELS = {'<100k': 'Under $100k', '100k–<500k': '$100k to <$500k', '500k–<1m': '$500k to <$1m',
               '1m–<2m': '$1m to <$2m', '2m–<6m': '$2m to <$6m', '>=6m': '$6m or more'}
INK, MUTED, BLUE, GREY, ORANGE = '#142a3a', '#536774', '#145f83', '#cdd8dc', '#b35d29'
SOURCE = 'Source: linked dataset v1.1.0 (doi:10.5281/zenodo.23414979), run 17 Oct 2026.'


def band(price):
    for edge, label in BANDS:
        if price < edge:
            return label
    return '>=6m'


def frame(title, subtitle, notes):
    fig = plt.figure(figsize=(12, 7), dpi=170)
    fig.patch.set_facecolor('white')
    fig.text(0.055, 0.955, 'READING THE HOUSING RECORD', fontsize=11, fontweight='bold', color=BLUE, va='top')
    fig.text(0.055, 0.915, title, fontsize=24, fontweight='bold', color=INK, va='top')
    fig.text(0.055, 0.835, subtitle, fontsize=12.5, color=MUTED, va='top')
    for i, line in enumerate(notes):
        fig.text(0.055, 0.125 - 0.026 * i, line, fontsize=9.5, color=MUTED, va='top')
    fig.text(0.055, 0.045, 'Pablo Loschi | nychousingdata.com | CC BY 4.0', fontsize=9.5, color=MUTED, va='top')
    ax = fig.add_axes([0.25, 0.22, 0.67, 0.52])
    for side in ('top', 'right', 'left'):
        ax.spines[side].set_visible(False)
    ax.spines['bottom'].set_color('#c3ced4')
    ax.tick_params(colors=MUTED, labelsize=12)
    ax.set_xlim(0, 100)
    return fig, ax


def save(fig, out, name):
    fig.savefig(out / f'{name}.svg', facecolor='white')
    fig.savefig(out / f'{name}.png', facecolor='white')
    plt.close(fig)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('build', type=Path)
    p.add_argument('--output', type=Path, default=Path('.'))
    a = p.parse_args()
    out = a.output
    rows, _ = eligible_condos(a.build)
    assert len(rows) == 126251

    # Coverage by borough and price band.
    by_group = []
    for dim, key in [('borough', lambda r: r['borough']), ('price_band', lambda r: band(float(r['sale_price'])))]:
        cells = collections.defaultdict(collections.Counter)
        for r in rows:
            cells[key(r)][r['deed_match']] += 1
        for g, c in cells.items():
            n = sum(c.values())
            by_group.append(dict(dimension=dim, group=g, eligible=n, linked=c['unique'], none=c['none'],
                                 ambiguous=c['ambiguous'], linked_pct=100 * c['unique'] / n,
                                 none_pct=100 * c['none'] / n, ambiguous_pct=100 * c['ambiguous'] / n))
    order = ['1', '2', '3', '4'] + [b for _, b in BANDS] + ['>=6m']
    by_group.sort(key=lambda d: (d['dimension'] != 'borough', order.index(d['group'])))
    write(out / 'condo_coverage_by_group.csv', by_group)

    same = []
    for b in '1234':
        rr = [r for r in rows if r['borough'] == b and band(float(r['sale_price'])) == '100k–<500k']
        u = sum(r['deed_match'] == 'unique' for r in rr)
        same.append(dict(borough=b, price_band='100k–<500k', eligible=len(rr), linked=u, coverage_pct=100 * u / len(rr)))
    write(out / 'condo-same-price-band.csv', same)

    gaps = []
    for y in range(2016, 2026):
        rate = {}
        for b in '12':
            rr = [r for r in rows if r['borough'] == b and r['sale_date'][:4] == str(y)]
            rate[b] = 100 * sum(r['deed_match'] == 'unique' for r in rr) / len(rr)
        gaps.append(dict(year=y, manhattan_coverage_pct=rate['1'], bronx_coverage_pct=rate['2'],
                         difference_pp=rate['1'] - rate['2']))
    write(out / 'condo_manhattan_bronx_annual_gap.csv', gaps)
    write(out / 'annual_condo_coverage.csv', annual(rows))

    summary = []
    groups = {'all_eligible': rows, 'linked': [r for r in rows if r['deed_match'] == 'unique'],
              'unlinked': [r for r in rows if r['deed_match'] != 'unique'],
              'none': [r for r in rows if r['deed_match'] == 'none'],
              'ambiguous': [r for r in rows if r['deed_match'] == 'ambiguous']}
    for g, rr in groups.items():
        prices = [float(r['sale_price']) for r in rr]
        summary.append(dict(group=g, n=len(rr), median_price=statistics.median(prices),
                            manhattan_pct=100 * sum(r['borough'] == '1' for r in rr) / len(rr),
                            bronx_pct=100 * sum(r['borough'] == '2' for r in rr) / len(rr)))
    write(out / 'condo_group_summary.csv', summary)

    # Figure 1: match outcomes by borough.
    bor = [d for d in by_group if d['dimension'] == 'borough']
    fig, ax = frame('The same match rule covers different markets',
                    'About 96% of eligible Brooklyn condo sales and 88% in Manhattan link to a deed; about 52% in the Bronx.',
                    ['Positive-price condominium sales in the four ACRIS boroughs, 2016-2025.', SOURCE])
    ys = list(range(len(bor)))[::-1]
    for y, d in zip(ys, bor):
        ax.barh(y, d['linked_pct'], color=BLUE, height=0.55)
        ax.barh(y, d['none_pct'], left=d['linked_pct'], color=GREY, height=0.55)
        ax.barh(y, d['ambiguous_pct'], left=d['linked_pct'] + d['none_pct'], color=ORANGE, height=0.55)
        ax.text(d['linked_pct'] / 2, y, f"{d['linked_pct']:.1f}%", color='white', fontsize=13, fontweight='bold', ha='center', va='center')
    ax.set_yticks(ys, [f"{BOROUGHS[d['group']]}\n{d['eligible']:,} eligible sales" for d in bor], fontsize=13, color=INK)
    ax.set_xlabel('Share of eligible condominium sales (%)', fontsize=12.5, color=INK)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in (BLUE, GREY, ORANGE)]
    fig.legend(handles, ['Linked to a deed', 'No qualifying deed', 'Several qualifying units'], loc='upper center',
               bbox_to_anchor=(0.6, 0.79), ncol=3, frameon=False, fontsize=11)
    save(fig, out, 'condo-coverage')

    # Figure 2: coverage by price band.
    pb = [d for d in by_group if d['dimension'] == 'price_band']
    fig, ax = frame('Coverage by recorded price',
                    'Share of eligible condo sales linked to a deed, by recorded price.',
                    ['Positive-price condominium sales in the four ACRIS boroughs, 2016-2025. Coverage, not verified accuracy.', SOURCE])
    ys = list(range(len(pb)))[::-1]
    for y, d in zip(ys, pb):
        ax.barh(y, d['linked_pct'], color=BLUE, height=0.55)
        ax.text(d['linked_pct'] + 1, y, f"{d['linked_pct']:.1f}%", color=INK, fontsize=12.5, fontweight='bold', va='center')
    ax.set_yticks(ys, [f"{BAND_LABELS[d['group']]}\n{d['eligible']:,} eligible sales" for d in pb], fontsize=12, color=INK)
    ax.set_xlabel('Share linked to a deed (%)', fontsize=12.5, color=INK)
    save(fig, out, 'condo-price-coverage')

    # Figure 3: the same price band in each borough.
    fig, ax = frame('A coverage gap within the same price band',
                    'Condo sales from $100,000 to under $500,000, using the same matching rule.',
                    ['Manhattan, Bronx, Brooklyn and Queens; 2016-2025. Denominators shown beside each borough.',
                     SOURCE + ' This does not explain why links are missing.'])
    ys = list(range(len(same)))[::-1]
    for y, d in zip(ys, same):
        ax.barh(y, d['coverage_pct'], color=BLUE, height=0.55)
        ax.text(d['coverage_pct'] + 1, y, f"{d['coverage_pct']:.1f}%", color=INK, fontsize=13, fontweight='bold', va='center')
    ax.set_yticks(ys, [f"{BOROUGHS[d['borough']]}\n{d['eligible']:,} eligible sales" for d in same], fontsize=13, color=INK)
    ax.set_xlabel('Share linked to a deed (%)', fontsize=12.5, color=INK)
    save(fig, out, 'condo-same-price-band')
    print('Eligible condo sales:', len(rows), '; linked:', len(groups['linked']))


if __name__ == '__main__':
    main()
