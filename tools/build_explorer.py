"""Build public aggregate data from the frozen linked-sales release. Stdlib only.

python tools/build_explorer.py /path/to/nyc_linked_dataset/build --archive /path/to/nyc_linked_dataset_v1.0.zip
No names, addresses, parcel IDs or individual records enter the output.
"""
import argparse
import csv
import gzip
import hashlib
import itertools
import json
import statistics
import zipfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANDS = [('under100k', 'Under $100,000'), ('100k500k', '$100,000 to under $500,000'),
         ('500k1m', '$500,000 to under $1 million'), ('1m2m', '$1 million to under $2 million'),
         ('2m6m', '$2 million to under $6 million'), ('6mplus', '$6 million or more')]
COUNTS = ['n', 'eligible', 'unique', 'none', 'ambiguous', 'measured', 'mortgage']

def band(price):
    for upper, key in [(100000, 'under100k'), (500000, '100k500k'), (1000000, '500k1m'),
                       (2000000, '1m2m'), (6000000, '2m6m')]:
        if price < upper:
            return key
    return '6mplus'

def read(path):
    with gzip.open(path, 'rt', newline='') as f:
        yield from csv.DictReader(f)

def build(source, archive=None):
    hashes = {n: hashlib.sha256((source/n).read_bytes()).hexdigest()
              for n in ['sales.csv.gz', 'links.csv.gz']}
    if archive:
        with zipfile.ZipFile(archive) as z:
            for name, digest in hashes.items():
                candidates = [n for n in z.namelist() if n.endswith('/build/'+name) or n == 'build/'+name]
                assert len(candidates) == 1, name
                assert hashlib.sha256(z.read(candidates[0])).hexdigest() == digest, name
    leaves = defaultdict(lambda: {'prices': [], **dict.fromkeys(COUNTS, 0)})
    source_rows = excluded = 0
    for s, l in itertools.zip_longest(read(source/'sales.csv.gz'), read(source/'links.csv.gz')):
        assert s and l and s['sale_id'] == l['sale_id'], 'Input keys/order differ'
        source_rows += 1
        price = float(s['sale_price'] or 0)
        assert price >= 0 and s['property_group'] in {'house', 'condo', 'coop'}
        year = s['sale_date'][:4]
        assert '2016' <= year <= '2025'
        if price <= 0:
            excluded += 1
            continue
        key = (s['borough'], year, s['property_group'], band(price))
        d = leaves[key]
        d['prices'].append(price)
        d['n'] += 1
        eligible = s['borough'] in {'1', '2', '3', '4'} and s['property_group'] in {'house', 'condo'}
        if eligible:
            assert l['deed_match'] in {'unique', 'none', 'ambiguous'}
            d['eligible'] += 1
            d[l['deed_match']] += 1
        else:
            assert l['deed_match'] == '' and l['financed_base'] == ''
        if l['financed_base'] in {'0', '1'}:
            d['measured'] += 1
            d['mortgage'] += int(l['financed_base'])
        if s['property_group'] == 'condo' and l['deed_match'] != 'unique':
            assert l['financed_base'] == '', 'Unlinked condo has measured financing'
    groups = defaultdict(lambda: {'prices': [], **dict.fromkeys(COUNTS, 0)})
    for dims, leaf in leaves.items():
        for key in itertools.product(*[(value, 'all') for value in dims]):
            d = groups[key]
            d['prices'].extend(leaf['prices'])
            for name in COUNTS:
                d[name] += leaf[name]
    rows = []
    for dims, d in sorted(groups.items()):
        row = dict(zip(['borough', 'year', 'property', 'band'], dims))
        row.update({n: d[n] for n in COUNTS})
        row['median'] = statistics.median(d['prices'])
        assert d['unique'] + d['none'] + d['ambiguous'] == d['eligible']
        assert 0 <= d['mortgage'] <= d['measured'] <= d['n']
        rows.append(row)
    totals = next(r for r in rows if all(r[d] == 'all' for d in ['borough', 'year', 'property', 'band']))
    assert source_rows == 729047 and totals['n'] + excluded == source_rows
    condos = next(r for r in rows if r['borough'] == r['year'] == r['band'] == 'all' and r['property'] == 'condo')
    houses = next(r for r in rows if r['borough'] == r['year'] == r['band'] == 'all' and r['property'] == 'house')
    assert condos['unique'] == 93386 and condos['none'] == 22030 and condos['ambiguous'] == 10835
    assert houses['unique'] == 183912 and houses['none'] == 5367
    return {'meta': {'dataset': 'NYC residential sales linked to ACRIS deeds and mortgages',
                     'documentation_version': '1.0.2', 'data_version': '1.0',
                     'source_url': 'https://zenodo.org/records/23257216',
                     'retrieved': '2026-09-26', 'years': list(range(2016, 2026)),
                     'source_rows': source_rows, 'excluded_nonpositive': excluded,
                     'source_sha256': hashes, 'archive_verified': bool(archive),
                     'price_bands': [{'id': k, 'label': v} for k, v in BANDS]}, 'rows': rows}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path)
    p.add_argument('--archive', type=Path)
    a = p.parse_args()
    result = build(a.source, a.archive)
    out = ROOT/'assets/explore'
    out.mkdir(parents=True, exist_ok=True)
    (out/'aggregates.json').write_text(json.dumps(result, separators=(',', ':'))+'\n')
    names = list(result['rows'][0])
    with (out/'aggregates.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=names)
        w.writeheader()
        w.writerows(result['rows'])
    print(json.dumps({'cells': len(result['rows']), 'meta': result['meta']}, indent=2))

if __name__ == '__main__':
    main()
