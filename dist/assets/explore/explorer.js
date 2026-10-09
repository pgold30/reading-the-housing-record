const form = document.querySelector('#explore-filters');
const dims = ['borough','year','property','band'];
const defaults = {borough:'all',year:'all',property:'house',band:'all'};
const number = new Intl.NumberFormat('en-US');
const dollars = new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0});
const percent = (a,b) => b ? (100*a/b).toFixed(1)+'%' : 'Not available';
const empty = {n:0,eligible:0,unique:0,none:0,ambiguous:0,measured:0,mortgage:0,median:null};
let dataset, lookup, selection, series;
const charts = [['n','Recorded transactions','Recorded transactions'],['median','Median recorded price','US dollars'],['coverage','Unique deed coverage','Percent of eligible records']];
const key = r => dims.map(d=>r[d]).join('|');
function value(row,metric){return metric==='coverage' ? (row.eligible ? 100*row.unique/row.eligible : null) : row[metric];}
function format(v,metric){return v===null ? 'Not available' : metric==='median' ? dollars.format(v) : metric==='coverage' ? v.toFixed(1)+'%' : number.format(v);}
function node(tag,attrs={},text){const n=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);if(text!==undefined)n.textContent=text;return n;}
function draw(metric,title,unit){
  const svg=node('svg',{viewBox:'0 0 900 330',role:'img','aria-label':title+' by year for '+document.querySelector('#selection-label').textContent,xmlns:'http://www.w3.org/2000/svg'});
  svg.append(node('rect',{width:900,height:330,fill:'#fff'}));
  svg.append(node('title',{},title+' — '+document.querySelector('#selection-label').textContent));
  svg.append(node('text',{x:90,y:25,fill:'#4c6170','font-size':14,'font-family':'sans-serif'},unit));
  const vals=series.map(r=>value(r,metric));
  const max=metric==='coverage'?100:Math.max(...vals.filter(v=>v!==null),1)*1.12;
  const x=i=>100+(i+.5)*760/series.length;
  const y=v=>265-220*v/max;
  for(let i=0;i<=4;i++){const v=max*i/4;svg.append(node('line',{x1:90,x2:870,y1:y(v),y2:y(v),stroke:'#d9e2e5'}));svg.append(node('text',{x:80,y:y(v)+5,'text-anchor':'end',fill:'#4c6170','font-size':13,'font-family':'sans-serif'},metric==='median'?'$'+number.format(Math.round(v)):metric==='coverage'?v+'%':number.format(Math.round(v))));}
  vals.forEach((v,i)=>{if(v!==null){const bar=node('rect',{x:x(i)-Math.min(25,260/series.length),y:y(v),width:Math.min(50,520/series.length),height:265-y(v),fill:metric==='median'?'#a75a32':'#145f83'});bar.append(node('title',{},series[i].year+': '+format(v,metric)));svg.append(bar);}else svg.append(node('text',{x:x(i),y:250,'text-anchor':'middle',fill:'#4c6170','font-size':13},'n/a'));svg.append(node('text',{x:x(i),y:288,'text-anchor':'middle',fill:'#142a3a','font-size':14,'font-family':'sans-serif'},series[i].year));});
  svg.append(node('text',{x:90,y:309,fill:'#4c6170','font-size':11,'font-family':'sans-serif'},document.querySelector('#selection-label').textContent));
  svg.append(node('text',{x:90,y:327,fill:'#4c6170','font-size':11,'font-family':'sans-serif'},'NYC Housing Data · DOF / ACRIS · frozen extract 26 Sep 2026 · recorded prices, not a price index'));
  document.querySelector('#chart-'+metric).replaceChildren(svg);
}
function download(text,type,name){const u=URL.createObjectURL(new Blob([text],{type}));const a=document.createElement('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);}
function csv(metric){const cols=['year','recorded_transactions','median_recorded_price_usd','eligible_for_deed_link','unique_deed_links','unmatched_deed_links','ambiguous_deed_links','mortgage_measurement_records','mortgage_matches','unique_deed_coverage_pct','mortgage_match_pct','borough_filter','property_filter','price_band_filter','data_version','source_snapshot'];const rows=series.map(r=>[r.year,r.n,r.median??'',r.eligible,r.unique,r.none,r.ambiguous,r.measured,r.mortgage,r.eligible?(100*r.unique/r.eligible).toFixed(4):'',r.measured?(100*r.mortgage/r.measured).toFixed(4):'',selection.borough,selection.property,selection.band,dataset.meta.data_version,dataset.meta.retrieved]);download([cols,...rows].map(r=>r.join(',')).join('\r\n')+'\r\n','text/csv;charset=utf-8','nyc-housing-'+metric+'.csv');}
function render(){
  selection=Object.fromEntries(dims.map(d=>[d,form.elements[d].value]));
  const q=new URLSearchParams();for(const d of dims)if(selection[d]!==defaults[d])q.set(d,selection[d]);history.replaceState(null,'',location.pathname+(q.size?'?'+q:''));
  const labels=dims.map(d=>form.elements[d].selectedOptions[0].textContent);document.querySelector('#selection-label').textContent=labels.join(' · ');
  const r=lookup.get(key(selection))||empty;
  document.querySelector('#metric-count').textContent=number.format(r.n);
  document.querySelector('#metric-price').textContent=r.median===null?'Not available':dollars.format(r.median);
  document.querySelector('#metric-coverage').textContent=percent(r.unique,r.eligible);
  document.querySelector('#metric-mortgage').textContent=percent(r.mortgage,r.measured);
  document.querySelector('#coverage-denominator').textContent=number.format(r.unique)+' unique links / '+number.format(r.eligible)+' eligible records';
  document.querySelector('#mortgage-denominator').textContent=number.format(r.mortgage)+' matches / '+number.format(r.measured)+' records with a financing flag';
  document.querySelector('#record-count-note').textContent=r.n===0?'No positive-price records in this selection.':r.n<20?'Small selection: fewer than 20 recorded transactions. Treat the median cautiously.':'Counts include nominal, related and other transfers; no market-sale screen is applied.';
  const years=selection.year==='all'?dataset.meta.years.map(String):[selection.year];
  series=years.map(year=>({...empty,...selection,year,...lookup.get(key({...selection,year}))}));
  const tbody=document.querySelector('#data-rows');tbody.replaceChildren();for(const row of series){const tr=document.createElement('tr');for(const v of [row.year,number.format(row.n),format(row.median,'median'),percent(row.unique,row.eligible),number.format(row.eligible),percent(row.mortgage,row.measured),number.format(row.measured)]){const td=document.createElement('td');td.textContent=v;tr.append(td);}tbody.append(tr);}
  charts.forEach(c=>draw(...c));document.querySelector('#explore-status').textContent='Showing '+number.format(r.n)+' recorded transactions. The table and downloads reflect these filters.';
}
try{
  const response=await fetch('../assets/explore/aggregates.json');if(!response.ok)throw Error('Data unavailable');dataset=await response.json();if(!Array.isArray(dataset.rows)||!dataset.meta?.years)throw Error('Invalid data');lookup=new Map(dataset.rows.map(r=>[key(r),r]));
  const q=new URLSearchParams(location.search);for(const d of dims){const allowed=[...form.elements[d].options].map(o=>o.value);form.elements[d].value=allowed.includes(q.get(d))?q.get(d):defaults[d];}
  form.addEventListener('change',render);form.addEventListener('submit',e=>e.preventDefault());document.querySelector('#reset-filters').addEventListener('click',()=>{for(const d of dims)form.elements[d].value=defaults[d];render();});document.querySelector('#share-view').addEventListener('click',async()=>{try{await navigator.clipboard.writeText(location.href);document.querySelector('#explore-status').textContent='Link copied. It opens this selection.';}catch{document.querySelector('#explore-status').textContent='Copy the address in your browser to share this selection.';}});
  document.querySelectorAll('[data-csv]').forEach(b=>b.addEventListener('click',()=>csv(b.dataset.csv)));document.querySelectorAll('[data-svg]').forEach(b=>b.addEventListener('click',()=>download(new XMLSerializer().serializeToString(document.querySelector('#chart-'+b.dataset.svg+' svg')),'image/svg+xml','nyc-housing-'+b.dataset.svg+'.svg')));render();
}catch(e){document.querySelector('#explore-status').textContent='The interactive data could not load. Download the aggregate CSV below or try again.';document.querySelector('#explore-status').className='tool-error';form.querySelectorAll('select').forEach(s=>s.disabled=true);document.querySelectorAll('#reset-filters,#share-view,[data-csv],[data-svg]').forEach(b=>b.disabled=true);}
