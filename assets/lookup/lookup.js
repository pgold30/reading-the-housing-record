// Zero-VM Static Lookup for NYC Neighborhoods (2020 NTAs), ZIP codes, and Major Condo Buildings.
const BASE = '../assets/lookup/';
const DEFAULT_ID = 'zip-10013';

const numFmt = new Intl.NumberFormat('en-US');
const usdFmt = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
const pctText = (v) => (v === null || v === undefined ? 'Outside ACRIS / <10 flagged' : `${v.toFixed(1)}%`);

const MANSION_TIERS = [
  { min: 25000000, rate: 0.039 },
  { min: 20000000, rate: 0.0375 },
  { min: 15000000, rate: 0.035 },
  { min: 10000000, rate: 0.0325 },
  { min: 5000000, rate: 0.0225 },
  { min: 3000000, rate: 0.015 },
  { min: 2000000, rate: 0.0125 },
  { min: 1000000, rate: 0.01 },
  { min: 0, rate: 0 },
];

function mansionRate(price) {
  for (const t of MANSION_TIERS) {
    if (price >= t.min) return t.rate;
  }
  return 0;
}

function dominantPropertyType(mix) {
  const entries = [
    ['house', mix.house || 0],
    ['condo', mix.condo || 0],
    ['coop', mix.coop || 0],
  ].sort((a, b) => b[1] - a[1]);
  return entries[0][0];
}

function illustrativeClosingTax(price, mix) {
  const dom = dominantPropertyType(mix);
  const mRate = mansionRate(price);
  const mTax = price * mRate;
  if (dom === 'coop') {
    return { total: mTax, mTax, mRate, mrt: 0, mrtRate: 0, dom };
  }
  const loan = price * 0.8;
  const mrtRate = loan >= 500000 ? 0.01925 : 0.018;
  const mrt = loan * mrtRate;
  return { total: mTax + mrt, mTax, mRate, mrt, mrtRate, dom };
}

function shardForId(id) {
  if (id.startsWith('zip-')) return 'zip';
  if (id.startsWith('nta-')) return 'nta';
  if (id.startsWith('bin-')) {
    const bin = id.slice(4);
    return 'b' + bin.charAt(bin.length - 1);
  }
  return null;
}

function kindLabel(kind) {
  if (kind === 'zip') return 'NYC ZIP Code';
  if (kind === 'nta') return 'NYC Neighborhood (2020 NTA)';
  if (kind === 'building') return 'NYC Condo Building';
  return 'NYC Record Group';
}

function propLabel(key) {
  if (key === 'house') return '1–3 family houses';
  if (key === 'condo') return 'Condominiums';
  if (key === 'coop') return 'Co-operative apartments';
  return key;
}

function normQuery(q) {
  return q.toLowerCase().replace(/[^a-z0-9\s\-]/g, ' ').replace(/\s+/g, ' ').trim();
}

const shardCache = new Map();
let indexItems = [];
let benchmarks = null;
let currentRecord = null;
let activeKind = 'all';
let activeHighlight = -1;
let currentMatches = [];

const queryInput = document.querySelector('#lookup-query');
const resultsList = document.querySelector('#lookup-results');
const statusEl = document.querySelector('#lookup-status');
const cardEl = document.querySelector('#lookup-card');

async function fetchJson(relPath) {
  const res = await fetch(BASE + relPath);
  if (!res.ok) throw new Error(`HTTP ${res.status} loading ${relPath}`);
  return res.json();
}

async function loadEntity(id) {
  const shardName = shardForId(id);
  if (!shardName) return null;
  if (!shardCache.has(shardName)) {
    shardCache.set(shardName, await fetchJson(`shards/${shardName}.json`));
  }
  return shardCache.get(shardName)[id] || null;
}

function rankSearch(rawQuery) {
  const q = normQuery(rawQuery);
  const tokens = q ? q.split(' ') : [];
  const filtered = activeKind === 'all' ? indexItems : indexItems.filter((it) => it[0] === activeKind);

  if (!tokens.length) {
    return filtered.slice(0, 12);
  }

  const scored = [];
  for (const item of filtered) {
    // item: [kindShort, id, displayName, subtitle, searchBlob, nSales]
    const hay = item[4];
    let ok = true;
    for (const tok of tokens) {
      if (!hay.includes(tok)) {
        ok = false;
        break;
      }
    }
    if (!ok) continue;

    const labelLow = item[2].toLowerCase();
    let score = 0;
    if (item[1].endsWith('-' + q) || labelLow === q || labelLow === `zip ${q}`) score += 10000;
    else if (labelLow.startsWith(q) || labelLow.startsWith(`zip ${q}`)) score += 4000;
    else if (hay.startsWith(q)) score += 2000;
    else if (labelLow.includes(q)) score += 1000;
    score += Math.min(item[5], 5000) / 10;
    scored.push([score, item]);
  }
  scored.sort((a, b) => b[0] - a[0] || b[1][5] - a[1][5]);
  return scored.slice(0, 12).map((s) => s[1]);
}

function hideResults() {
  resultsList.hidden = true;
  resultsList.replaceChildren();
  queryInput.setAttribute('aria-expanded', 'false');
  activeHighlight = -1;
}

function showResults(matches) {
  currentMatches = matches;
  activeHighlight = matches.length ? 0 : -1;
  resultsList.replaceChildren();

  if (!matches.length) {
    const emptyLi = document.createElement('li');
    emptyLi.className = 'lookup-result-empty';
    emptyLi.textContent = 'No matching ZIP, neighborhood, or condo building (25+ condo sales required for buildings).';
    resultsList.append(emptyLi);
    resultsList.hidden = false;
    queryInput.setAttribute('aria-expanded', 'true');
    return;
  }

  matches.forEach((item, idx) => {
    const li = document.createElement('li');
    li.id = `lookup-opt-${idx}`;
    li.role = 'option';
    li.className = 'lookup-result-item' + (idx === 0 ? ' is-active' : '');
    li.setAttribute('aria-selected', String(idx === 0));

    const top = document.createElement('div');
    top.className = 'lookup-result-top';
    const titleSpan = document.createElement('strong');
    titleSpan.textContent = item[2];
    const badgeSpan = document.createElement('span');
    badgeSpan.className = 'lookup-result-kind';
    badgeSpan.textContent =
      (item[0] === 'z' ? 'ZIP' : item[0] === 'n' ? 'Neighborhood' : 'Condo bldg') +
      ` · ${numFmt.format(item[5])} sales`;
    top.append(titleSpan, badgeSpan);

    const sub = document.createElement('div');
    sub.className = 'lookup-result-sub';
    sub.textContent = item[3];

    li.append(top, sub);
    li.addEventListener('mousedown', (e) => {
      e.preventDefault();
      selectEntity(item[1], true);
    });
    resultsList.append(li);
  });

  resultsList.hidden = false;
  queryInput.setAttribute('aria-expanded', 'true');
}

function syncHighlight() {
  const children = resultsList.querySelectorAll('[role="option"]');
  children.forEach((el, idx) => {
    const on = idx === activeHighlight;
    el.classList.toggle('is-active', on);
    el.setAttribute('aria-selected', String(on));
    if (on) el.scrollIntoView({ block: 'nearest' });
  });
}

function renderCard(rec) {
  currentRecord = rec;
  const boroBench = benchmarks.boroughs[String(rec.borough)] || benchmarks.nyc;
  const nycBench = benchmarks.nyc;

  const u = new URL(location.href);
  u.searchParams.set('id', rec.id);
  history.replaceState(null, '', u.pathname + '?' + u.searchParams.toString());

  document.querySelector('#card-badge').textContent = kindLabel(rec.kind);
  document.querySelector('#card-title').textContent = rec.name;
  const extraBuilt = rec.year_built ? ` · Built ~${rec.year_built}` : '';
  const extraAliases = rec.aliases && rec.aliases.length ? ` · Also filed as ${rec.aliases.slice(0, 2).join(' / ')}` : '';
  document.querySelector('#card-subtitle').textContent = rec.subtitle + extraBuilt + extraAliases;

  // Tile 1: Sales count & mix
  document.querySelector('#m-sales').textContent = numFmt.format(rec.n_sales);
  const mixParts = [];
  if (rec.mix.house) mixParts.push(`${numFmt.format(rec.mix.house)} houses`);
  if (rec.mix.condo) mixParts.push(`${numFmt.format(rec.mix.condo)} condos`);
  if (rec.mix.coop) mixParts.push(`${numFmt.format(rec.mix.coop)} co-ops`);
  document.querySelector('#m-sales-note').textContent =
    (mixParts.length ? mixParts.join(' · ') : 'Residential records >= $10k') + '.';

  // Tile 2: Median price & delta vs borough
  document.querySelector('#m-price').textContent = usdFmt.format(rec.median_price);
  const priceDiffPct = boroBench.median_price
    ? ((rec.median_price - boroBench.median_price) / boroBench.median_price) * 100
    : 0;
  const diffSign = priceDiffPct >= 0 ? '+' : '';
  document.querySelector('#m-price-note').textContent =
    `IQR ${usdFmt.format(rec.p25_price)}–${usdFmt.format(rec.p75_price)} · ${diffSign}${priceDiffPct.toFixed(0)}% vs. ${boroBench.name || 'NYC'} median (${usdFmt.format(boroBench.median_price)}).`;

  // Tile 3: Unmatched mortgage ("cash") share (NEVER fake co-op or Staten Island as cash)
  const cashEl = document.querySelector('#m-cash');
  const cashNoteEl = document.querySelector('#m-cash-note');
  if (rec.unmatched_pct === null) {
    cashEl.textContent = rec.borough === 5 ? 'Outside ACRIS' : 'Insufficient data';
    cashNoteEl.textContent =
      rec.borough === 5
        ? 'Staten Island deeds are filed with the Richmond County Clerk outside ACRIS.'
        : `${numFmt.format(rec.flagged_n)} ACRIS-flagged deeds (need >= 10 flagged house/condo sales; co-ops excluded).`;
  } else {
    cashEl.textContent = `${rec.unmatched_pct.toFixed(1)}%`;
    let benchCmp = '';
    if (boroBench.unmatched_pct !== null) {
      const pts = rec.unmatched_pct - boroBench.unmatched_pct;
      benchCmp = ` (${pts >= 0 ? '+' : ''}${pts.toFixed(1)} pts vs. ${boroBench.name} ${boroBench.unmatched_pct.toFixed(1)}%)`;
    } else if (nycBench.unmatched_pct !== null) {
      const pts = rec.unmatched_pct - nycBench.unmatched_pct;
      benchCmp = ` (${pts >= 0 ? '+' : ''}${pts.toFixed(1)} pts vs. NYC ACRIS ${nycBench.unmatched_pct.toFixed(1)}%)`;
    }
    cashNoteEl.textContent = `${numFmt.format(rec.unmatched_n)} unmatched / ${numFmt.format(rec.flagged_n)} ACRIS-flagged house & condo sales${benchCmp}.`;
  }

  // Tile 4: Illustrative statutory buyer closing taxes at median
  const taxEst = illustrativeClosingTax(rec.median_price, rec.mix);
  document.querySelector('#m-tax').textContent = usdFmt.format(Math.round(taxEst.total));
  if (taxEst.dom === 'coop') {
    document.querySelector('#m-tax-note').textContent =
      `Majority co-op: $0 NYC mortgage tax; mansion tax ${(taxEst.mRate * 100).toFixed(2).replace(/\.00$/, '')}% (${usdFmt.format(Math.round(taxEst.mTax))}) at median.`;
  } else {
    document.querySelector('#m-tax-note').textContent =
      `At median (${propLabel(taxEst.dom)}): ${usdFmt.format(Math.round(taxEst.mrt))} MRT on 80% loan + ${usdFmt.format(Math.round(taxEst.mTax))} mansion tax.`;
  }

  // Calculator deep link
  const calcBtn = document.querySelector('#open-calculator');
  calcBtn.href = `../calculator/?price=${encodeURIComponent(rec.median_price)}&property=${encodeURIComponent(taxEst.dom)}&down=20`;

  // Property mix table
  const tbodyType = document.querySelector('#type-rows');
  tbodyType.replaceChildren();
  for (const key of ['house', 'condo', 'coop']) {
    const seg = rec.by_type && rec.by_type[key];
    if (!seg) continue;
    const tr = document.createElement('tr');
    const cells = [
      propLabel(key),
      numFmt.format(seg.n),
      usdFmt.format(seg.med),
      key === 'coop' ? 'n/a (UCC-1)' : numFmt.format(seg.fn),
      key === 'coop' ? 'Outside ACRIS' : pctText(seg.cp),
    ];
    cells.forEach((val) => {
      const td = document.createElement('td');
      td.textContent = val;
      tr.append(td);
    });
    tbodyType.append(tr);
  }

  // LTV & CEMA line
  const ltvParts = [];
  if (rec.valid_ltv_n >= 10 && rec.median_ltv !== null) {
    ltvParts.push(
      `Among ${numFmt.format(rec.valid_ltv_n)} matched loans in (5%, 105%] LTV: median LTV is ${rec.median_ltv.toFixed(1)}%, and ${rec.high_ltv_pct.toFixed(1)}% exceed 95% LTV.`
    );
  }
  if (rec.cema_n > 0) {
    ltvParts.push(`${numFmt.format(rec.cema_n)} matched mortgages flagged with CEMA assignments in ACRIS.`);
  }
  if (!ltvParts.length) {
    ltvParts.push('LTV and high-LTV (>95%) summary suppressed when fewer than 10 valid matched real-property loans appear.');
  }
  document.querySelector('#ltv-summary').textContent = ltvParts.join(' ');

  // Mansion-tax bars
  document.querySelector('#n-1m-val').textContent = `${rec.share_1m_plus.toFixed(1)}% (${numFmt.format(rec.n_1m_plus)})`;
  document.querySelector('#bar-1m').style.width = `${Math.max(rec.share_1m_plus > 0 ? 2 : 0, rec.share_1m_plus)}%`;
  document.querySelector('#n-2m-val').textContent = `${rec.share_2m_plus.toFixed(1)}%`;
  document.querySelector('#bar-2m').style.width = `${Math.max(rec.share_2m_plus > 0 ? 2 : 0, rec.share_2m_plus)}%`;
  document.querySelector('#n-3m-val').textContent = `${rec.share_3m_plus.toFixed(1)}%`;
  document.querySelector('#bar-3m').style.width = `${Math.max(rec.share_3m_plus > 0 ? 2 : 0, rec.share_3m_plus)}%`;
  document.querySelector('#notch-benchmark-note').textContent =
    `NYC overall (>= $10k sales): ${nycBench.share_1m_plus.toFixed(1)}% at or above $1M, ${nycBench.share_2m_plus.toFixed(1)}% at or above $2M, ${nycBench.share_3m_plus.toFixed(1)}% at or above $3M.`;

  // Dynamic scientific scope box
  const scopeBox = document.querySelector('#dynamic-scope');
  scopeBox.replaceChildren();
  const caveats = [];
  if (rec.borough === 5) {
    caveats.push(
      'Staten Island is outside ACRIS: deeds and mortgages are filed with the Richmond County Clerk, so no mortgage-match or cash share is shown here.'
    );
  } else {
    caveats.push(
      '"No-mortgage-match" counts linked ACRIS house and condo deeds with no matched purchase-window mortgage (`financed_base = 0`). It includes unrecorded financing, related-party transfers, and missed links; it does not prove all-cash payment.'
    );
  }
  if ((rec.mix.coop || 0) > 0) {
    caveats.push(
      `This selection includes ${numFmt.format(rec.mix.coop)} co-operative sales. Co-op loans use personal-property UCC-1 filings and are excluded from the real-property mortgage share above (not counted as cash).`
    );
  }
  caveats.push(
    'Counts drop $0 and nominal transfers below $10,000, include non-market transfers above $10,000, and compute illustrative closing taxes using statutory gross schedules (before CEMA reductions, credits, or seller RPTT).'
  );
  caveats.forEach((line) => {
    const p = document.createElement('p');
    p.textContent = line;
    scopeBox.append(p);
  });

  // Annual history table
  const tbodyYr = document.querySelector('#annual-rows');
  tbodyYr.replaceChildren();
  const yrLabels = ['Year', 'Sales (>= $10k)', 'Median price', 'ACRIS flagged', 'Unmatched ("cash")'];
  for (const row of rec.years) {
    const [yr, n, med, fn, cp] = row;
    const tr = document.createElement('tr');
    const vals = [
      String(yr),
      numFmt.format(n),
      med === null ? '—' : usdFmt.format(med),
      numFmt.format(fn),
      fn === 0 ? 'Outside ACRIS' : cp === null ? `<10 flagged (n=${fn})` : `${cp.toFixed(1)}%`,
    ];
    vals.forEach((v, idx) => {
      const td = document.createElement('td');
      td.dataset.label = yrLabels[idx];
      td.textContent = v;
      tr.append(td);
    });
    tbodyYr.append(tr);
  }

  // Preset pill highlight
  document.querySelectorAll('[data-lookup-id]').forEach((btn) => {
    btn.setAttribute('aria-pressed', String(btn.dataset.lookupId === rec.id));
  });

  cardEl.hidden = false;
}

async function selectEntity(id, fromUser = false) {
  statusEl.textContent = 'Loading summary card…';
  try {
    const rec = await loadEntity(id);
    if (!rec) {
      statusEl.textContent = `No entry found for "${id}". Showing ZIP 10013 instead.`;
      const fallback = await loadEntity(DEFAULT_ID);
      if (fallback) renderCard(fallback);
      return;
    }
    renderCard(rec);
    if (fromUser) queryInput.value = rec.name;
    hideResults();
    statusEl.textContent = `Showing ${rec.name} (${numFmt.format(rec.n_sales)} sales >= $10,000 in 2016–2025).`;
  } catch (err) {
    statusEl.textContent = `Could not load "${id}": ${err.message}`;
  }
}

function buildCitationText(rec) {
  const url = `https://nychousingdata.com/lookup/?id=${rec.id}`;
  const cashPart =
    rec.unmatched_pct !== null
      ? `no-mortgage-match ("cash") share ${rec.unmatched_pct.toFixed(1)}% across ${numFmt.format(rec.flagged_n)} ACRIS-flagged deeds`
      : 'outside ACRIS financing linkage';
  return `NYC Housing Data (Pablo Loschi, dataset v1.2.0 / Zenodo doi:10.5281/zenodo.24274709): ${rec.name} (${rec.subtitle}), 2016–2025 residential sales >= $10,000: n = ${numFmt.format(rec.n_sales)}, median ${usdFmt.format(rec.median_price)}, ${cashPart}, ${rec.share_2m_plus.toFixed(1)}% >= $2M. ${url}`;
}

function downloadAnnualCsv(rec) {
  const cols = [
    'entity_id',
    'entity_name',
    'kind',
    'borough',
    'year',
    'sales_10k_plus',
    'median_price_usd',
    'acris_flagged_sales',
    'unmatched_mortgage_pct',
    'data_version',
    'source_url',
  ];
  const srcUrl = `https://nychousingdata.com/lookup/?id=${rec.id}`;
  const lines = [cols.join(',')];
  for (const [yr, n, med, fn, cp] of rec.years) {
    const vals = [
      rec.id,
      `"${String(rec.name).replace(/"/g, '""')}"`,
      rec.kind,
      `"${String(rec.borough_name || '').replace(/"/g, '""')}"`,
      yr,
      n,
      med ?? '',
      fn,
      cp ?? '',
      benchmarks.meta.data_version,
      srcUrl,
    ];
    lines.push(vals.join(','));
  }
  const blob = new Blob([lines.join('\r\n') + '\r\n'], { type: 'text/csv;charset=utf-8' });
  const a = document.createElement('a');
  const url = URL.createObjectURL(blob);
  a.href = url;
  a.download = `nychousingdata-${rec.id}-annual.csv`;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

// Wire events
let debounceTimer = null;
queryInput.addEventListener('input', () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    showResults(rankSearch(queryInput.value));
  }, 60);
});

queryInput.addEventListener('focus', () => {
  if (indexItems.length && (queryInput.value.trim().length > 0 || !resultsList.hidden)) {
    showResults(rankSearch(queryInput.value));
  }
});

queryInput.addEventListener('keydown', (e) => {
  if (resultsList.hidden && (e.key === 'ArrowDown' || e.key === 'ArrowUp')) {
    showResults(rankSearch(queryInput.value));
    return;
  }
  if (e.key === 'Escape') {
    hideResults();
    return;
  }
  if (!currentMatches.length || resultsList.hidden) return;
  if (e.key === 'ArrowDown') {
    e.preventDefault();
    activeHighlight = (activeHighlight + 1) % currentMatches.length;
    syncHighlight();
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    activeHighlight = (activeHighlight - 1 + currentMatches.length) % currentMatches.length;
    syncHighlight();
  } else if (e.key === 'Enter') {
    e.preventDefault();
    const chosen = currentMatches[Math.max(0, activeHighlight)];
    if (chosen) selectEntity(chosen[1], true);
  }
});

document.addEventListener('click', (e) => {
  if (!e.target.closest('.lookup-combobox')) hideResults();
});

document.querySelectorAll('[data-kind]').forEach((btn) => {
  btn.addEventListener('click', () => {
    activeKind = btn.dataset.kind;
    document.querySelectorAll('[data-kind]').forEach((b) => b.setAttribute('aria-pressed', String(b === btn)));
    showResults(rankSearch(queryInput.value));
  });
});

document.querySelectorAll('[data-lookup-id]').forEach((btn) => {
  btn.addEventListener('click', () => selectEntity(btn.dataset.lookupId, false));
});

document.querySelector('#copy-citation').addEventListener('click', async () => {
  if (!currentRecord) return;
  const text = buildCitationText(currentRecord);
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text);
    } else {
      const ta = document.createElement('textarea');
      ta.value = text;
      document.body.append(ta);
      ta.select();
      document.execCommand('copy');
      ta.remove();
    }
    statusEl.textContent = 'Citation & direct link copied to clipboard.';
  } catch {
    statusEl.textContent = 'Copy blocked by browser; copy the URL from your address bar.';
  }
});

document.querySelector('#download-csv').addEventListener('click', () => {
  if (currentRecord) downloadAnnualCsv(currentRecord);
});

window.addEventListener('popstate', () => {
  const id = new URLSearchParams(location.search).get('id') || DEFAULT_ID;
  selectEntity(id, false);
});

// Boot
async function boot() {
  try {
    const [idxData, benchData] = await Promise.all([fetchJson('index.json'), fetchJson('benchmarks.json')]);
    indexItems = idxData.items || [];
    benchmarks = benchData;
    const initialId = new URLSearchParams(location.search).get('id') || DEFAULT_ID;
    await selectEntity(initialId, false);
  } catch (err) {
    statusEl.textContent = `Could not initialize lookup: ${err.message}`;
  }
}

boot();
