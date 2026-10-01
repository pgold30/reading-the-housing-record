"""Reproduce Housing Stories' borough-by-price and annual condo coverage checks.

Python standard library only. Keep recorded_mortgage_example.py beside this file.
Usage: python condo_coverage_check.py /path/to/dataset/build --output results
Download dataset v1.0.1: https://zenodo.org/records/23047979
Coverage describes matches, not verified financing or classification accuracy.
"""
import argparse
import collections
from pathlib import Path
from recorded_mortgage_example import eligible_condos, write


def band(price):
    for edge, label in [(100000, '<100k'), (500000, '100k–<500k'),
                        (1000000, '500k–<1m'), (2000000, '1m–<2m'),
                        (6000000, '2m–<6m')]:
        if price < edge:
            return label
    return '>=6m'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('build', type=Path)
    p.add_argument('--output', type=Path, default=Path('results'))
    a = p.parse_args()
    rows, _ = eligible_condos(a.build)
    a.output.mkdir(parents=True, exist_ok=True)
    cells = collections.defaultdict(collections.Counter)
    years = collections.defaultdict(collections.Counter)
    for sale in rows:
        cell = cells[(sale['borough'], band(float(sale['sale_price'])))]
        year = years[(sale['borough'], sale['sale_date'][:4])]
        for count in [cell, year]:
            count['eligible'] += 1
            count['unique'] += sale['deed_match'] == 'unique'
    cell_rows = [dict(borough=b, price_band=k, eligible=n['eligible'],
                     unique=n['unique'], coverage_pct=100*n['unique']/n['eligible'])
                 for (b, k), n in sorted(cells.items())]
    write(a.output/'condo_borough_price_cells.csv', cell_rows)
    gaps = []
    for y in range(2016, 2026):
        m, b = years[('1', str(y))], years[('2', str(y))]
        mr, br = 100*m['unique']/m['eligible'], 100*b['unique']/b['eligible']
        gaps.append(dict(year=y, manhattan_coverage_pct=mr,
                         bronx_coverage_pct=br, difference_pp=mr-br))
    write(a.output/'condo_manhattan_bronx_annual_gap.csv', gaps)
    print('Eligible condo sales:', len(rows))
    print('Saved borough-by-price counts and annual Manhattan–Bronx gaps to', a.output)


if __name__ == '__main__':
    main()
