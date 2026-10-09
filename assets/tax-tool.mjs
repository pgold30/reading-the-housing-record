// Historical full-residential buyer tax only. TSB-M-19(1)R, June 2019.
export function buyerTaxCents(price,after){
  if(!Number.isInteger(price)||price<0||price>=5000000)throw new RangeError('Illustration covers prices below $5 million');
  const basisPoints=price<1000000?0:after&&price>=3000000?150:after&&price>=2000000?125:100;
  return Math.round(price*basisPoints/100);
}
export function thresholdRows(threshold){
  if(![1000000,2000000,3000000].includes(threshold))throw new RangeError('Unsupported threshold');
  return [false,true].map(after=>({period:after?'2019 rules':'Before 2019 reform',below:buyerTaxCents(threshold-1,after),at:buyerTaxCents(threshold,after),jump:buyerTaxCents(threshold,after)-buyerTaxCents(threshold-1,after)}));
}
if(typeof document!=='undefined'){
  const input=document.querySelector('#tax-threshold');const money=c=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD'}).format(c/100);
  function render(){const t=Number(input.value),rows=thresholdRows(t);const tbody=document.querySelector('#tax-rows');tbody.replaceChildren();for(const r of rows){const tr=document.createElement('tr');for(const v of [r.period,money(r.below),money(r.at),money(r.jump)]){const td=document.createElement('td');td.textContent=v;tr.append(td);}tbody.append(tr);}document.querySelector('#tax-below').textContent=money((t-1)*100);document.querySelector('#tax-at').textContent=money(t*100);document.querySelector('#tax-summary').textContent='Under the 2019 rules, the last $1 adds '+money(rows[1].jump)+' in buyer tax at this line.';const chart=document.querySelector('#tax-chart');chart.replaceChildren();chart.setAttribute('aria-label','Buyer tax increase when the price rises by $1 to '+money(t*100));rows.forEach(r=>{const group=document.createElement('div');const label=document.createElement('div');label.className='tax-bar-label';const period=document.createElement('span');period.textContent=r.period;const amount=document.createElement('strong');amount.textContent=money(r.jump);label.append(period,amount);const track=document.createElement('div');track.className='tax-bar-track';const fill=document.createElement('span');fill.style.width=Math.max(.5,100*r.jump/Math.max(...rows.map(r=>r.jump),1))+'%';track.append(fill);group.append(label,track);chart.append(group);});}
  input.addEventListener('change',render);document.querySelector('#tax-download').addEventListener('click',()=>{const t=Number(input.value);const text='threshold_usd,period,price_below_usd,tax_below_usd,price_at_usd,tax_at_usd,tax_jump_usd\r\n'+thresholdRows(t).map(r=>[t,r.period,t-1,(r.below/100).toFixed(2),t,(r.at/100).toFixed(2),(r.jump/100).toFixed(2)].join(',')).join('\r\n');const url=URL.createObjectURL(new Blob([text],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='nyc-2019-tax-threshold-'+t+'.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});render();
}
