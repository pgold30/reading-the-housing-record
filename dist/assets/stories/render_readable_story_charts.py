"""Readable desktop/phone charts from saved story CSVs; no data queries or estimates.

The CSVs are the existing published series and illustrations. Captions on the
story pages retain their source releases, samples and inference qualifications.
"""
from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
P=Path(__file__).resolve().parent
BLUE='#145f83'; ORANGE='#b75b2c'; LIGHT='#a9c3d1'; INK='#536774'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':14,'text.parse_math':False,'svg.fonttype':'none'})
def rows(n):
 with (P/(n+'.csv')).open() as f:return list(csv.DictReader(f))
def style(ax):
 for side in ['top','right']:ax.spines[side].set_visible(False)
 for side in ['left','bottom']:ax.spines[side].set_color(INK)
 ax.tick_params(colors=INK);ax.grid(axis='y',color='#d9e1e6',alpha=.7);ax.set_axisbelow(True)
def save(fig,n,mobile):
 fig.tight_layout(pad=1)
 suffix='-mobile' if mobile else ''
 p=P/(n+suffix+'.svg');fig.savefig(p,metadata={'Date':None});p.write_text('\n'.join(x.rstrip() for x in p.read_text().replace("font-family: 'DejaVu Sans'","font-family: Arial, sans-serif").splitlines())+'\n')
 if not mobile:fig.savefig(P/(n+'.png'),dpi=150)
 plt.close(fig)
def dollars(x,_):return f'${x:,.0f}'
def dates(ax,r,mobile):
 years=[int(x['quarter'][:4])+(int(x['quarter'][-1])-1)/4 for x in r]
 ax.set_xlim(years[0],years[-1]);ax.set_xticks([2005,2015,2025] if mobile else [2005,2010,2015,2020,2025]);return years
for mobile in [False,True]:
 plt.rcParams['font.size']=11 if mobile else 15
 size=(4.4,4.4) if mobile else (10,5.6)
 n='cash-discount';r=rows(n);fig,ax=plt.subplots(figsize=((4.4,5.2) if mobile else (10,4.8)))
 labels=['All house pairs','Shared-surname\ndeeds excluded','Company cash buyers'] if mobile else ['All house pairs','Shared-surname deeds excluded','Company cash buyers']
 for i,x in enumerate(r):
  v,lo,hi=[float(x[k]) for k in ['estimate','low','high']];ax.errorbar(v,i,xerr=[[v-lo],[hi-v]],fmt='o',color=BLUE,capsize=5,markersize=8,linewidth=2.5);ax.text(hi+.25,i,f'{v:.2f}',va='center',fontsize=11 if mobile else 15)
 ax.set_yticks(range(3),labels);ax.invert_yaxis();ax.set_ylim(2.6,-.6);ax.axvline(0,color=INK,lw=1);ax.set_xlim(-3,14);ax.set_xlabel('Financed minus cash (log points)');style(ax);ax.grid(axis='y',visible=False);ax.grid(axis='x',color='#d9e1e6');save(fig,n,mobile)
 n='mortgage-recording-comparison';r=rows(n);fig,ax=plt.subplots(figsize=size)
 ax.set_title(f"Same ${float(r[0]['price_usd']):,.0f} condo",fontsize=14 if mobile else 18,pad=16)
 vals=[float(x['gross_borrower_charge_usd']) for x in r];ax.bar([0,1],vals,color=[LIGHT,BLUE],width=.6)
 for i,v in enumerate(vals):ax.text(i,v+700,f'${v:,.0f}',ha='center',weight='bold',fontsize=18 if mobile else 24)
 ax.set_xticks([0,1],['No purchase\nmortgage','$720,000\nmortgage']);ax.set_ylabel('Gross borrower charge');ax.set_ylim(0,18000);ax.yaxis.set_major_formatter(FuncFormatter(dollars));style(ax);save(fig,n,mobile)
 n='tax-dollar-step';r=rows(n);fig,ax=plt.subplots(figsize=size);vals=[float(x['buyer_tax']) for x in r]
 ax.bar([0,1],vals,color=[LIGHT,BLUE],width=.6)
 for i,v in enumerate(vals):ax.text(i,v+700,f'${v:,.2f}',ha='center',weight='bold',fontsize=13 if mobile else 22)
 ax.set_xticks([0,1],['$1,999,999\npurchase','$2,000,000\npurchase']);ax.set_ylabel('Buyer mansion + supplemental tax');ax.set_ylim(0,30000);ax.yaxis.set_major_formatter(FuncFormatter(lambda x,_:f'${x/1000:g}k'));style(ax);save(fig,n,mobile)
 n='tax-round-prices';r=rows(n);fig,ax=plt.subplots(figsize=((4.4,6) if mobile else (10,5.4)))
 for i,x in enumerate(r):
  for j,(k,c) in enumerate([('before',LIGHT),('after',BLUE)]):
   v=float(x[k]);y=i+(j-.5)*.34;ax.barh(y,v,height=.3,color=c,label=('Jan 2016–Mar 2019' if j==0 else 'Jan 2020–Dec 2025') if i==0 else None);ax.text(v+.13,y,f'{v:.1f}',va='center',fontsize=10 if mobile else 13)
 ax.set_yticks(range(len(r)),[x['price'].replace(' million','M') for x in r]);ax.invert_yaxis();ax.set_xlim(0,12);ax.set_xlabel('Exact-price sales /\nsurrounding price density' if mobile else 'Exact-price sales / surrounding price density');ax.legend(loc='lower center',bbox_to_anchor=(.5,1.01),ncol=1 if mobile else 2,fontsize=9 if mobile else 12,frameon=False);style(ax);ax.grid(axis='y',visible=False);ax.grid(axis='x',color='#d9e1e6');save(fig,n,mobile)
 n='deed-index-paths';r=rows(n);fig,ax=plt.subplots(figsize=size);xs=dates(ax,r,mobile)
 for k,label,c in [('raw_index','Including flagged transfers',BLUE),('screened_index','Excluding flagged transfers',ORANGE)]:ax.plot(xs,[float(x[k]) for x in r],label=label,color=c,lw=2.3)
 ax.set_ylabel('Index (2003 Q1 = 100)');ax.set_xlabel('Sale quarter');ax.legend(loc='upper left',fontsize=8.5 if mobile else 12,frameon=False);style(ax);save(fig,n,mobile)
 n='deed-path-uncertainty';allrows=rows(n);r=[x for x in allrows if x['definition']=='D0'];other=[x for x in allrows if x['definition']=='D4'];assert [x['quarter'] for x in r]==[x['quarter'] for x in other]
 fig,ax=plt.subplots(figsize=size);xs=dates(ax,r,mobile)
 ax.fill_between(xs,[float(x['joint_low']) for x in r],[float(x['joint_high']) for x in r],color=BLUE,alpha=.15,label='95% joint band')
 ax.plot(xs,[float(x['difference']) for x in r],color=BLUE,label='Published definition',lw=2.2);ax.plot(xs,[float(x['difference']) for x in other],color=ORANGE,label='Narrowest definition',lw=2.2);ax.axhline(0,color=INK,lw=.8)
 ax.set_ylabel('Raw minus screened (log points)');ax.set_xlabel('Sale quarter');ax.legend(loc='upper right',fontsize=8.5 if mobile else 12,frameon=False);style(ax);save(fig,n,mobile)
 n='second-home-surcharge';r=rows(n);fig,ax=plt.subplots(figsize=size)
 ax.plot([0,999999],[0,0],color=BLUE,lw=3);ax.plot([float(x['dof_value_dollars']) for x in r if float(x['dof_value_dollars'])>=1000000],[float(x['annual_surcharge_dollars']) for x in r if float(x['dof_value_dollars'])>=1000000],color=BLUE,lw=3)
 ax.plot([1000000,1000000],[0,40000],color=INK,ls='--');ax.scatter([1000000],[40000],color=BLUE,zorder=3);ax.annotate('$40,000 at $1M',xy=(1000000,40000),xytext=(200000,65000),arrowprops={'arrowstyle':'-','color':INK},fontsize=11 if mobile else 15)
 ax.set_xlim(0,3000000);ax.set_ylim(-4000,135000);ax.set_xticks([0,1000000,2000000,3000000]);ax.xaxis.set_major_formatter(FuncFormatter(lambda x,_:f'${x/1e6:g}M'));ax.set_yticks([0,40000,80000,120000]);ax.yaxis.set_major_formatter(FuncFormatter(lambda x,_:f'${x/1000:g}k'));ax.set_xlabel('City value');ax.set_ylabel('Annual surcharge');style(ax);save(fig,n,mobile)
print('Rendered seven charts in desktop and phone layouts; all CSVs read only.')
