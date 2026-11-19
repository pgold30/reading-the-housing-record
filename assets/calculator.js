// Interactive NYC Buyer Closing-Tax Calculator (MRT + Mansion Tax statutory gross schedules).
(() => {
  const priceInput = document.querySelector('#calc-price');
  const propSelect = document.querySelector('#calc-property');
  const downSelect = document.querySelector('#calc-down-pct');
  const loanInput = document.querySelector('#calc-loan');
  const form = document.querySelector('#calc-form');
  if (!form) return;

  const usd = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
  const pct = (v) => (v * 100).toFixed(2).replace(/\.00$/, '') + '%';

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

  function mrtGross(loan, property) {
    if (property === 'coop' || loan <= 0) return { rate: 0, tax: 0 };
    const rate = loan >= 500000 ? 0.01925 : 0.018;
    return { rate, tax: loan * rate };
  }

  function syncLoanFromDown() {
    const price = Math.max(0, Number(priceInput.value) || 0);
    if (downSelect.value === 'custom') return;
    const downPct = Number(downSelect.value) / 100;
    const loan = Math.max(0, Math.round(price * (1 - downPct)));
    loanInput.value = String(loan);
  }

  function render() {
    const price = Math.max(0, Number(priceInput.value) || 0);
    const property = propSelect.value;
    let loan = Math.max(0, Number(loanInput.value) || 0);
    if (loan > price && price > 0) loan = price;
    const down = Math.max(0, price - loan);

    const mRate = mansionRate(price);
    const mTax = price * mRate;
    const mrt = mrtGross(loan, property);
    const borrowerTotal = mTax + mrt.tax;
    const cashTotal = mTax;

    document.querySelector('#out-mrt').textContent = usd.format(Math.round(mrt.tax));
    document.querySelector('#out-mrt-note').textContent =
      property === 'coop'
        ? 'Co-op share loans are exempt from NYC mortgage recording tax ($0).'
        : loan <= 0
          ? 'No mortgage recorded ($0 mortgage recording tax).'
          : `${pct(mrt.rate)} gross borrower rate on ${usd.format(loan)} loan` +
            (down > 0 ? ` (${((mrt.tax / down) * 100).toFixed(1)}% of ${usd.format(down)} down payment).` : '.');

    document.querySelector('#out-mansion').textContent = usd.format(Math.round(mTax));
    document.querySelector('#out-mansion-note').textContent =
      mRate > 0
        ? `${pct(mRate)} whole-price buyer tax at ${usd.format(price)}.`
        : 'Applies to residential purchases of $1,000,000 or more ($0 below $1M).';

    document.querySelector('#out-borrower-total').textContent = usd.format(Math.round(borrowerTotal));
    document.querySelector('#out-cash-total').textContent = usd.format(Math.round(cashTotal));
    document.querySelector('#out-gap').textContent = usd.format(Math.round(borrowerTotal - cashTotal));

    // Comparison bars
    const maxBar = Math.max(borrowerTotal, cashTotal, 1);
    document.querySelector('#bar-borrower').style.width = `${Math.max(borrowerTotal > 0 ? 4 : 0, (borrowerTotal / maxBar) * 100)}%`;
    document.querySelector('#bar-cash').style.width = `${Math.max(cashTotal > 0 ? 4 : 0, (cashTotal / maxBar) * 100)}%`;
    document.querySelector('#bar-borrower-val').textContent = usd.format(Math.round(borrowerTotal));
    document.querySelector('#bar-cash-val').textContent = usd.format(Math.round(cashTotal));

    // Dynamic cliff alerts
    const alerts = [];
    if (property !== 'coop' && loan >= 500000 && loan <= 535000) {
      const belowTax = 499999 * 0.018;
      const diff = Math.round(mrt.tax - belowTax);
      alerts.push(
        `Mortgage cliff ($500,000): Because crossing $500,000 raises the rate from 1.80% to 1.925% on the entire loan, a ${usd.format(loan)} mortgage adds ${usd.format(diff)} in gross recording tax compared with $499,999 ($625 jump right at $500,000).`
      );
    }
    for (const notch of [1000000, 2000000, 3000000, 5000000, 10000000]) {
      if (price >= notch && price <= notch + 50000) {
        const belowTax = (notch - 1) * mansionRate(notch - 1);
        const jump = Math.round(notch * mansionRate(notch) - belowTax);
        alerts.push(
          `Mansion-tax cliff (${usd.format(notch)}): Crossing ${usd.format(notch)} applies the higher ${pct(mansionRate(notch))} rate to the entire price, adding ${usd.format(jump)} in buyer tax compared with ${usd.format(notch - 1)}.`
        );
        break;
      }
    }
    const alertBox = document.querySelector('#calc-cliff-alert');
    if (alerts.length) {
      alertBox.hidden = false;
      alertBox.innerHTML = '<strong>Threshold cliff alert:</strong> ' + alerts.join(' ');
    } else {
      alertBox.hidden = true;
      alertBox.textContent = '';
    }

    // Highlight matching preset pill
    document.querySelectorAll('[data-calc-preset]').forEach((btn) => {
      try {
        const p = JSON.parse(btn.dataset.calcPreset);
        const active =
          Number(p.price) === price &&
          p.property === property &&
          Number(p.loan) === loan;
        btn.setAttribute('aria-pressed', String(active));
      } catch {}
    });
  }

  priceInput.addEventListener('input', () => { syncLoanFromDown(); render(); });
  downSelect.addEventListener('change', () => { syncLoanFromDown(); render(); });
  propSelect.addEventListener('change', render);
  loanInput.addEventListener('input', () => { downSelect.value = 'custom'; render(); });
  form.addEventListener('submit', (e) => e.preventDefault());

  document.querySelectorAll('[data-calc-preset]').forEach((btn) => {
    btn.addEventListener('click', () => {
      try {
        const p = JSON.parse(btn.dataset.calcPreset);
        priceInput.value = String(p.price);
        propSelect.value = p.property;
        downSelect.value = p.downPct ?? 'custom';
        loanInput.value = String(p.loan);
        render();
      } catch {}
    });
  });

  render();
})();
