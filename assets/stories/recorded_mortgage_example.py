"""Annual condo deed-link coverage and recorded-mortgage share. Python stdlib.

Usage: python recorded_mortgage_example.py /path/to/dataset/build --output annual.csv
Reads frozen sales.csv.gz and links.csv.gz; never calls an API or reads names.
The mortgage share is conditional on uniquely linked condos. No-match is not
verified cash, and unlinked sales are never assigned financing=0.
"""
import argparse,csv,gzip
from pathlib import Path

def read(path):
 with gzip.open(path,'rt',newline='') as f:yield from csv.DictReader(f)

def eligible_condos(build):
 sales={};excluded={'all_condos':0,'outside_four_boroughs':0,'nonpositive_price_in_four_boroughs':0,'outside_date_range':0}
 for s in read(build/'sales.csv.gz'):
  if s['property_group']!='condo':continue
  excluded['all_condos']+=1
  if not '2016-01-01'<=s['sale_date']<'2026-01-01':excluded['outside_date_range']+=1;continue
  if s['borough'] not in {'1','2','3','4'}:excluded['outside_four_boroughs']+=1;continue
  if float(s['sale_price'] or 0)<=0:excluded['nonpositive_price_in_four_boroughs']+=1;continue
  if s['sale_id'] in sales:raise ValueError('Duplicate eligible sale_id')
  sales[s['sale_id']]=s
 seen=set()
 for l in read(build/'links.csv.gz'):
  sid=l['sale_id']
  if sid not in sales:continue
  if sid in seen:raise ValueError('Duplicate eligible link key')
  seen.add(sid);status=l['deed_match'];finance=l['financed_base']
  if status not in {'unique','none','ambiguous'}:raise ValueError('Unexpected eligible status')
  if status=='unique' and finance not in {'0','1'}:raise ValueError('Missing financing on unique condo')
  if status!='unique' and finance!='':raise ValueError('Financing present without unique condo deed')
  sales[sid].update(deed_match=status,financed_base=finance)
 if seen!=sales.keys():raise ValueError('Eligible sale missing from links')
 return list(sales.values()),excluded

def annual(rows):
 out=[]
 for year in sorted({s['sale_date'][:4] for s in rows}):
  ss=[s for s in rows if s['sale_date'][:4]==year];n=len(ss);linked=sum(s['deed_match']=='unique' for s in ss);mortgage=sum(s['financed_base']=='1' for s in ss)
  out.append({'year':year,'eligible_condo_sales':n,'unique_deed':linked,'no_deed_match':sum(s['deed_match']=='none' for s in ss),'ambiguous_deed':sum(s['deed_match']=='ambiguous' for s in ss),'mortgage_match_base':mortgage,'no_mortgage_match_base':sum(s['financed_base']=='0' for s in ss),'financing_unmeasured':sum(s['financed_base']=='' for s in ss),'unique_deed_pct':100*linked/n,'mortgage_match_pct_of_linked':100*mortgage/linked if linked else ''})
 return out

def write(path,rows):
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('build',type=Path);p.add_argument('--output',type=Path,default=Path('annual_condo_coverage.csv'));a=p.parse_args();rows,excluded=eligible_condos(a.build);result=annual(rows);write(a.output,result)
 print('Eligible condo sales:',len(rows));print('Exclusions:',excluded);print('Saved:',a.output)
 print('Mortgage shares refer only to uniquely linked sales; missing financing is not cash.')
if __name__=='__main__':main()
