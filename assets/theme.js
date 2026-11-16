// Manual Bat-Signal dark/light theme toggle, respecting OS preference unless chosen explicitly.
(() => {
  const KEY = 'nyhd-theme';
  const root = document.documentElement;
  const mql = window.matchMedia('(prefers-color-scheme: dark)');

  function effectiveTheme() {
    const t = root.dataset.theme;
    if (t === 'dark' || t === 'light') return t;
    return mql.matches ? 'dark' : 'light';
  }

  function syncButtons() {
    const dark = effectiveTheme() === 'dark';
    document.querySelectorAll('[data-theme-toggle]').forEach((btn) => {
      btn.setAttribute('aria-pressed', String(dark));
      btn.setAttribute('aria-label', dark ? 'Switch back to daylight mode' : 'Summon night mode (Gotham signal)');
      btn.title = dark ? 'Lights on — daylight mode' : 'Summon night mode (Gotham signal)';
    });
  }

  function handleClick(btn) {
    const next = effectiveTheme() === 'dark' ? 'light' : 'dark';
    root.dataset.theme = next;
    try {
      localStorage.setItem(KEY, next);
    } catch {}
    syncButtons();
    if (next === 'dark') {
      btn.classList.remove('is-beaming');
      void btn.offsetWidth;
      btn.classList.add('is-beaming');
    }
  }

  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-theme-toggle]');
    if (btn) handleClick(btn);
  });

  if (typeof mql.addEventListener === 'function') {
    mql.addEventListener('change', syncButtons);
  }
  syncButtons();
})();
