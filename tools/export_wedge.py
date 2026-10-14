"""Export matched archived v6.1 results; never run or alter the simulation."""
import csv
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--replication', type=Path, default=ROOT / 'execution_certainty_wedge_v6_1/replication')
SRC = parser.parse_args().replication
DEST = Path(__file__).resolve().parents[1] / 'assets/data'
LABELS = {
    'paper_baseline': 'Paper baseline: illustrative high competition',
    'nyc_company_cash': 'NYC company-cash proxy',
    'nyc_upper_discount': 'Upper company-cash discount',
    'nyc_all_companies': 'All company buyers proxy',
    'naive_headline': 'Headline gap used as an offer discount',
}
POLICIES = {
    'static_cap': 'Per-entity cap', 'wfq': 'Fair-share quota',
    'contention_duty': 'Contention duty', 'constant_charge': 'Constant charge',
    'combined': 'Quota and duty combined',
}

def main():
    a = json.loads((SRC / 'nyc_anchored.json').read_text())
    c = json.loads((SRC / 'nyc_cohort_check.json').read_text())
    assert a['seeds'] == c['seeds'] and len(a['seeds']) == 12
    result = {'version': 'Archived Wedge v6.1', 'seeds': a['seeds'],
              'cohort': c['cohort'], 'source_record': 'https://zenodo.org/records/23042897',
              'sources': {f: hashlib.sha256((SRC / f).read_bytes()).hexdigest()
                          for f in ['nyc_anchored.json', 'nyc_cohort_check.json']},
              'policies': POLICIES, 'scenarios': []}
    flat = []
    for name, label in LABELS.items():
        original, cohort = a['scenarios'][name], c['scenarios'][name]
        assert cohort['original_summary_exact']
        base = cohort['runs']['unconstrained']
        assert len(base) == 12
        item = {'id': name, 'label': label, 'discount_pct': 100 * original['w'],
                'institutional_share_pct': 100 * original['regimes']['unconstrained']['inst_share'],
                'capacity': original['inst_capacity'], 'constant_charge_pct': 100 * original['constant_charge_h'],
                'full_unserved_pct': 100 * original['regimes']['unconstrained']['starvation_rate'],
                'cohort_unserved_pct': cohort['regimes']['unconstrained']['cohort_unserved_pct'], 'policies': {}}
        for regime, policy in POLICIES.items():
            s = cohort['regimes'][regime]
            runs = cohort['runs'][regime]
            assert len(runs) == 12
            for k, v in original['regimes'][regime].items():
                assert np.isclose(v, s[k], rtol=0, atol=1e-10), (name, regime, k)
            for row, b in zip(runs, base):
                assert row['cohort_remaining'] == 0
                assert row['cohort_entered'] == row['cohort_served'] + row['cohort_unserved']
                assert row['input_values_sha256'] == b['input_values_sha256']
                assert row['oracle_denominator'] == b['oracle_denominator']
                assert row['fresh_units'] == b['fresh_units']
            d = 100 * np.array([r['contemporaneous_eff'] - b['contemporaneous_eff'] for r, b in zip(runs, base)])
            for field, summary, se in [('starvation_rate', 'starvation_change_pp', 'starvation_change_se'),
                                       ('cohort_unserved_rate', 'cohort_change_pp', 'cohort_change_se'),
                                       ('oracle_eff', 'oracle_change_pp', 'oracle_change_se')]:
                changes = 100 * np.array([r[field] - b[field] for r, b in zip(runs, base)])
                assert np.isclose(s[summary], changes.mean(), rtol=0, atol=1e-10)
                assert np.isclose(s[se], changes.std(ddof=1)/np.sqrt(12), rtol=0, atol=1e-10)
            out = {'full_access_pp': -s['starvation_change_pp'], 'full_access_se': s['starvation_change_se'],
                   'cohort_access_pp': -s['cohort_change_pp'], 'cohort_access_se': s['cohort_change_se'],
                   'value_change_pct': s['value_index'] - 100, 'value_change_se': s['value_change_se'],
                   'oracle_pp': s['oracle_change_pp'], 'oracle_se': s['oracle_change_se'],
                   'moving_pp': s['contemp_change_pp'], 'moving_se': float(d.std(ddof=1) / np.sqrt(12))}
            assert np.isclose(out['moving_pp'], d.mean(), rtol=0, atol=1e-10)
            assert all(np.isfinite(v) for v in out.values())
            item['policies'][regime] = out
            flat.append({'scenario': name, 'policy': regime, 'offer_discount_pct': item['discount_pct'],
                         'baseline_institutional_share_pct': item['institutional_share_pct'],
                         'constant_scheduled_haircut_pct': item['constant_charge_pct'], 'seeds': 12, **out})
        result['scenarios'].append(item)
    DEST.mkdir(exist_ok=True)
    (DEST / 'wedge-explorer.json').write_text(json.dumps(result, indent=2) + '\n')
    with (DEST / 'wedge-explorer.csv').open('w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(flat[0]), lineterminator="\n"); w.writeheader(); w.writerows(flat)
    print(f'Exported and checked {len(flat)} matched scenario/policy rows across 12 seeds.')

if __name__ == '__main__':
    main()
