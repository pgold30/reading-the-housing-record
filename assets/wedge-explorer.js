const panel = document.querySelector('#simulation-explorer');
const status = panel.querySelector('[data-status]');
const scenarioSelect = panel.querySelector('#wedge-scenario');
const populationSelect = panel.querySelector('#wedge-population');
const benchmarkSelect = panel.querySelector('#wedge-benchmark');
const chart = panel.querySelector('[data-chart]');
const table = panel.querySelector('tbody');
let dataset;

function el(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}
function format(n, signed = false) {
  const value = Math.abs(n) < 0.005 && n !== 0 ? n.toPrecision(2) : n.toFixed(2);
  return (signed && n > 0 ? '+' : '') + value;
}
function selected() {
  return dataset.scenarios.find(s => s.id === scenarioSelect.value);
}
function render() {
  const scenario = selected();
  const cohort = populationSelect.value === 'cohort';
  const oracle = benchmarkSelect.value === 'oracle';
  const accessKey = cohort ? 'cohort_access_pp' : 'full_access_pp';
  const accessSE = cohort ? 'cohort_access_se' : 'full_access_se';
  const efficiencyKey = oracle ? 'oracle_pp' : 'moving_pp';
  const efficiencySE = oracle ? 'oracle_se' : 'moving_se';
  const rows = Object.entries(scenario.policies);
  const maximum = Math.max(0.01, ...rows.map(([, r]) => Math.abs(r[efficiencyKey])));
  panel.querySelector('[data-context]').textContent =
    `Offer discount ${scenario.discount_pct.toFixed(2)}%; institutional purchases in the model ${scenario.institutional_share_pct.toFixed(1)}%. Before an instrument, ${format(cohort ? scenario.cohort_unserved_pct : scenario.full_unserved_pct)}% of owner-occupiers are counted as leaving without buying under this population measure.`;
  panel.querySelector('[data-population-note]').textContent = cohort
    ? 'Completed cohort: buyers entering in periods 36–83, all followed to purchase or exit by period 119.'
    : 'Full run: unserved exits divided by all owner-occupier arrivals. Buyers still waiting at the end remain in the denominator.';
  panel.querySelector('[data-benchmark-note]').textContent = oracle
    ? 'Fixed oracle: the highest valuations among all arriving bidder instances, holding supply and arrivals fixed across instruments. It is an illustrative allocation benchmark.'
    : 'Moving benchmark: the best valuation in the current bidder pool at each listing. The instrument changes that pool, so this denominator changes too.';
  panel.querySelector('[data-charge-note]').textContent =
    `The constant charge uses a ${scenario.constant_charge_pct.toFixed(2)}% scheduled haircut. It matches the duty’s mean district-period schedule; it is not tuned to equal access.`;
  chart.replaceChildren();
  table.replaceChildren();
  for (const [id, row] of rows) {
    const policy = dataset.policies[id];
    const item = el('div', undefined, 'wedge-bar-row');
    item.append(el('span', policy, 'wedge-policy'));
    const track = el('div', undefined, 'wedge-bar-track');
    track.setAttribute('aria-hidden', 'true');
    const bar = el('span', undefined, row[efficiencyKey] < 0 ? 'wedge-bar negative' : 'wedge-bar positive');
    bar.style.width = `${Math.abs(row[efficiencyKey]) / maximum * 48}%`;
    if (row[efficiencyKey] < 0) bar.style.right = '50%';
    else bar.style.left = '50%';
    track.append(bar);
    item.append(track, el('span', `${format(row[efficiencyKey], true)} pp`, 'wedge-bar-value'));
    chart.append(item);
    const tr = el('tr');
    const th = el('th', policy); th.scope = 'row'; tr.append(th);
    for (const [key, se, suffix] of [[accessKey, accessSE, ' pp'], [efficiencyKey, efficiencySE, ' pp'], ['value_change_pct', 'value_change_se', '%']]) {
      const td = el('td');
      td.append(el('span', format(row[key], true) + suffix), el('small', `SE ${format(row[se])}`));
      tr.append(td);
    }
    table.append(tr);
  }
  panel.querySelector('[data-chart-title]').textContent = `Efficiency change: ${oracle ? 'fixed oracle' : 'moving benchmark'}`;
  panel.querySelector('[data-access-heading]').textContent = `Reduction in unserved share (${cohort ? 'cohort' : 'full run'})`;
  panel.querySelector('[data-efficiency-heading]').textContent = `Efficiency change (${oracle ? 'fixed oracle' : 'moving'})`;
  status.textContent = `${scenario.label}. ${cohort ? 'Completed cohort' : 'Full run'} access; ${oracle ? 'fixed oracle' : 'moving'} efficiency. Five instruments displayed.`;
}
function download() {
  const s = selected();
  const header = ['scenario', 'policy', 'population', 'benchmark', 'access_reduction_pp', 'access_se', 'efficiency_change_pp', 'efficiency_se', 'realised_value_change_pct', 'value_se', 'offer_discount_pct', 'baseline_institutional_share_pct', 'constant_scheduled_haircut_pct', 'seed_count', 'source_record'];
  const cohort = populationSelect.value === 'cohort', oracle = benchmarkSelect.value === 'oracle';
  const rows = Object.entries(s.policies).map(([id, r]) => [s.id, id, populationSelect.value, benchmarkSelect.value,
    r[cohort ? 'cohort_access_pp' : 'full_access_pp'], r[cohort ? 'cohort_access_se' : 'full_access_se'],
    r[oracle ? 'oracle_pp' : 'moving_pp'], r[oracle ? 'oracle_se' : 'moving_se'], r.value_change_pct, r.value_change_se,
    s.discount_pct, s.institutional_share_pct, s.constant_charge_pct, dataset.seeds.length, dataset.source_record]);
  const csv = [header, ...rows].map(row => row.map(v => '"' + String(v).replaceAll('"', '""') + '"').join(',')).join('\r\n') + '\r\n';
  const url = URL.createObjectURL(new Blob([csv], {type: 'text/csv;charset=utf-8'}));
  const a = el('a'); a.href = url; a.download = `wedge-${s.id}-${populationSelect.value}-${benchmarkSelect.value}.csv`;
  a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
}
try {
  const response = await fetch('../../assets/data/wedge-explorer.json');
  if (!response.ok) throw new Error('Simulation data unavailable');
  dataset = await response.json();
  if (dataset.scenarios.length !== 5 || dataset.seeds.length !== 12) throw new Error('Unexpected archive');
  for (const scenario of dataset.scenarios) {
    const option = el('option', scenario.label); option.value = scenario.id; scenarioSelect.append(option);
  }
  scenarioSelect.value = 'nyc_company_cash';
  for (const control of [scenarioSelect, populationSelect, benchmarkSelect]) {
    control.disabled = false; control.addEventListener('change', render);
  }
  const button = panel.querySelector('[data-download]'); button.disabled = false; button.addEventListener('click', download);
  panel.querySelector('[data-output]').hidden = false;
  render();
} catch (error) {
  status.textContent = 'The interactive results could not load. Use the complete CSV or replication files linked below.';
}
