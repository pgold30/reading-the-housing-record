"""Render qualified display labels from the existing, unchanged saved count CSVs.

No data query or empirical recalculation. The original CSV headers are retained
for download compatibility; their categories describe threshold screens, not
observed tax liability or a 2028 forecast.
"""
from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
P=Path(__file__).resolve().parent
BLUE,MID,LIGHT,INK,GRID,TEXT='#145f83','#5e93ad','#a9c3d1','#536774','#d9e1e6','#1d2b33'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':15,'text.parse_math':False})
def style(ax):
 for side in ['top','right']:ax.spines[side].set_visible(False)
 for side in ['left','bottom']:ax.spines[side].set_color(INK)
 ax.tick_params(colors=INK);ax.grid(axis='y',color=GRID,lw=.8);ax.set_axisbelow(True)
def save(fig,name):
 fig.savefig(P/(name+'.svg'),metadata={'Date':None})
 svg=P/(name+'.svg');svg.write_text('\n'.join(x.rstrip() for x in svg.read_text().splitlines())+'\n')
 fig.savefig(P/(name+'.png'),dpi=150)
 # Phone layouts keep labels readable instead of shrinking a desktop canvas.
 fig.set_size_inches(4.4,7.8 if len(fig.axes)>1 else 3.9)
 for i,ax in enumerate(fig.axes):
  ax.tick_params(labelsize=11)
  ax.xaxis.label.set_fontsize(11);ax.yaxis.label.set_fontsize(11)
  ax.title.set_fontsize(13)
  for label in ax.texts:label.set_fontsize(11)
  if len(fig.axes)>1:
   ax.set_position([.18,.58 if i==0 else .09,.78,.34]);ax.set_ylabel('')
  elif name=='second-home-condo-counts':
   ax.set_xticks([700000,1000000,1300000]);ax.set_xlabel('City value ($25,000 bands)')
  else:
   ax.set_xticks([0,2,4,6]);ax.set_xticklabels(['$800k','$900k','$1M','$1.1M']);ax.set_xlabel('City value ($50,000 bands)');ax.set_ylabel('Sale price')
 if len(fig.axes)==1:fig.tight_layout(pad=.8)
 fig.savefig(P/(name+'-mobile.svg'),metadata={'Date':None})
 mobile=P/(name+'-mobile.svg');mobile.write_text('\n'.join(x.rstrip() for x in mobile.read_text().splitlines())+'\n')
 plt.close(fig)
with (P/'second-home-condo-counts.csv').open() as f:rows=list(csv.DictReader(f))
lo=[int(x['dof_value_from']) for x in rows];counts=[int(x['condo_units']) for x in rows]
fig,ax=plt.subplots(figsize=(9,5.2),dpi=100)
for x,n in zip(lo,counts):ax.bar(x+12500,n,width=22000,color=BLUE if x>=1000000 else LIGHT)
ax.axvline(1000000,color=INK,lw=1.2,ls=(0,(3,3)));top=max(counts)*1.18;ax.set_ylim(0,top)
ax.set_xlim(700000,1300000);ax.xaxis.set_major_formatter(FuncFormatter(lambda x,_:f'${x/1e6:g}M' if x>=1e6 else f'${x/1e3:.0f}k'))
ax.yaxis.set_major_formatter(FuncFormatter(lambda y,_:f'{y:,.0f}'))
ax.set_xlabel('City value, 2026–27 ($25,000 bands)',color=INK,fontsize=14,labelpad=8)
ax.set_ylabel('Condo units',color=INK,fontsize=14,labelpad=8);style(ax)
fig.tight_layout();save(fig,'second-home-condo-counts')
with (P/'second-home-2028.csv').open() as f:rows=list(csv.DictReader(f))
fig,axes=plt.subplots(1,2,figsize=(9,5.2),dpi=100,gridspec_kw={'wspace':.35})
for ax,row in zip(axes,rows):
 both,city,price=[int(row[k]) for k in ['stay_in','drop_out','come_in']]
 n1,n2=both+city,both+price;ax.bar(0,both,width=.72,color=BLUE);ax.bar(0,city,width=.72,bottom=both,color=LIGHT)
 ax.bar(1,both,width=.72,color=BLUE);ax.bar(1,price,width=.72,bottom=both,color=MID)
 ymax=max(n1,n2)*1.18;ax.set_ylim(0,ymax)
 for x,n in [(0,n1),(1,n2)]:ax.text(x,n+ymax*.015,f'{n:,}',ha='center',va='bottom',color=TEXT,fontsize=14,fontweight='bold')
 ax.text(0,both+city/2,f'{city:,}\nvalue only',ha='center',va='center',color=TEXT,fontsize=14)
 ax.text(1,both+price/2,f'{price:,}\nprice only',ha='center',va='center',color='white',fontsize=14)
 for x in [0,1]:ax.text(x,both/2,f'{both:,}\nboth',ha='center',va='center',color='white',fontsize=14)
 ax.set_xticks([0,1]);ax.set_xticklabels(['City value:\n$1M+','Sale price:\n$5M+'],fontsize=14);ax.set_xlim(-.6,1.6)
 ax.yaxis.set_major_formatter(FuncFormatter(lambda y,_:f'{y:,.0f}'));style(ax);ax.set_title(row['borough'],loc='left',color=TEXT,fontsize=14)
axes[0].set_ylabel('Condo units',color=INK,fontsize=14,labelpad=8)
fig.subplots_adjust(left=.13,right=.98,top=.93,bottom=.18,wspace=.4);save(fig,'second-home-2028')
print('Rendered two charts from unchanged saved CSVs.')
with (P/'second-home-price-vs-value.csv').open() as f:rows=list(csv.DictReader(f))
fig,ax=plt.subplots(figsize=(9,5.2),dpi=100)
for i,r in enumerate(rows):
 color=BLUE if int(r['dof_value_from'])>=1000000 else LIGHT
 ax.plot([i,i],[float(r['price_p25']),float(r['price_p75'])],color=color,lw=7,solid_capstyle='butt',alpha=.35)
 ax.scatter([i],[float(r['price_median'])],s=80,color=color,zorder=3)
ax.axvline(3.5,color=INK,lw=1.2,ls=(0,(3,3)))
vals=[int(r['dof_value_from']) for r in rows];ax.set_xticks(list(range(len(rows))))
ax.set_xticklabels([(f'${v/1e6:g}M' if v%100000==0 else f'${v/1e6:.2f}M') if v>=1000000 else f'${v/1e3:.0f}k' for v in vals],fontsize=14)
ax.set_ylim(0,7500000);ax.yaxis.set_major_formatter(FuncFormatter(lambda y,_:f'${y/1e6:.0f}M' if y else '$0'))
ax.set_xlabel('City value, 2026–27 ($50,000 bands, starting at)',color=INK,fontsize=14,labelpad=8)
ax.set_ylabel('Sale price, 2023 to 2025',color=INK,fontsize=14,labelpad=8);style(ax)
fig.tight_layout();save(fig,'second-home-price-vs-value')
print('Rendered sale-price chart from unchanged saved CSV.')
