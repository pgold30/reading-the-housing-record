(function () {
  "use strict";

  const params = new URLSearchParams(window.location.search);
  const apiBase = (
    window.PIED_A_TERRE_API_BASE ||
    ""
  ).replace(/\/+$/, "");

  const recoveryForm = document.getElementById("reportRecoveryForm");
  if (recoveryForm) {
    const output = document.getElementById("reportRecoveryStatus");
    recoveryForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const button = recoveryForm.querySelector("button");
      const data = new FormData(recoveryForm);
      button.disabled = true;
      output.textContent = "Checking…";
      try {
        const result = await fetch("https://api.nychousingdata.com/v1/report/recover", {
          method: "POST",
          cache: "no-store",
          credentials: "omit",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: data.get("email"), bbl: data.get("bbl") }),
        });
        if (result.ok) {
          const payload = await result.json().catch(() => ({}));
          output.textContent = "";
          if (payload && typeof payload.download_url === "string" &&
              payload.download_url.startsWith("https://api.nychousingdata.com/v1/report/")) {
            const note = document.createElement("p");
            note.textContent = payload.message || "Your report is ready.";
            const link = document.createElement("a");
            link.href = payload.download_url;
            link.className = "btn btn-primary";
            link.rel = "noopener";
            link.textContent = "Download your report (PDF)";
            output.append(note, link);
          } else {
            output.textContent = (payload && payload.message) ||
              "If a paid report matches, you will get a download link.";
          }
          recoveryForm.reset();
        } else if (result.status === 429) {
          output.textContent = "Too many attempts. Please try again in an hour.";
        } else {
          output.textContent = "Report recovery is unavailable right now. Please try again later.";
        }
      } catch (_error) {
        output.textContent = "Could not reach the report service. Please try again.";
      } finally {
        button.disabled = false;
      }
    });
    return;
  }

  const els = {
    themeToggle: document.getElementById("themeToggle"),
    searchInput: document.getElementById("parcelSearch"),
    clearBtn: document.getElementById("clearSearchBtn"),
    acList: document.getElementById("autocompleteList"),
    statusBadge: document.getElementById("statusBadge"),
    citywideMeta: document.getElementById("citywideMeta"),
    examplePills: document.getElementById("examplePills"),
    errorBanner: document.getElementById("errorBanner"),
    paymentBanner: document.getElementById("paymentBanner"),
    paymentBannerText: document.getElementById("paymentBannerText"),
    paymentRecovery: document.getElementById("paymentRecovery"),
    paymentDownloadBtn: document.getElementById("paymentDownloadBtn"),
    citywidePanel: document.getElementById("citywidePanel"),
    citywideStatsGrid: document.getElementById("citywideStatsGrid"),
    resultSection: document.getElementById("resultSection"),
    parcelBadges: document.getElementById("parcelBadges"),
    parcelAddressTitle: document.getElementById("parcelAddressTitle"),
    parcelSubline: document.getElementById("parcelSubline"),
    verdictCallout: document.getElementById("verdictCallout"),
    copyCitationBtn: document.getElementById("copyCitationBtn"),
    reportPreviewBtn: document.getElementById("reportPreviewBtn"),
    reportCheckoutBtn: document.getElementById("reportCheckoutBtn"),
    partnerInquiryBtn: document.getElementById("partnerInquiryBtn"),
    primaryKpiGrid: document.getElementById("primaryKpiGrid"),
    cliffDetails: document.getElementById("cliffDetails"),
    assessmentDetails: document.getElementById("assessmentDetails"),
    coopCalculatorCard: document.getElementById("coopCalculatorCard"),
    coopForm: document.getElementById("coopForm"),
    unitSharesInput: document.getElementById("unitSharesInput"),
    totalSharesInput: document.getElementById("totalSharesInput"),
    sharePctInput: document.getElementById("sharePctInput"),
    coopEstimateOutput: document.getElementById("coopEstimateOutput"),
    loadBlockUnitsBtn: document.getElementById("loadBlockUnitsBtn"),
    buildingContextSummary: document.getElementById("buildingContextSummary"),
    blockUnitsTableWrap: document.getElementById("blockUnitsTableWrap"),
    acrisSalesWrap: document.getElementById("acrisSalesWrap"),
    disclaimersList: document.getElementById("disclaimersList"),
  };

  let checkoutPending = false;
  let currentParcel = null;
  let acMatches = [];
  let activeAcIndex = -1;
  let debounceTimer = null;
  let partnerCfg = { enabled: false, url: "", label: "" };
  let reportCfg = {
    recoveryEnabled: false,
    enabled: false,
    dynamic: false,
    previewEnabled: true,
    priceUsd: 39,
    url: "",
    label: "",
  };
  let apiFlags = {
    evidenceGated: true,
    bulkRequiresKey: true,
  };

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function fmtUsd(value) {
    if (value === null || value === undefined || Number.isNaN(Number(value))) {
      return "N/A";
    }
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 0,
    }).format(Number(value));
  }

  function fmtPct(value, digits) {
    if (value === null || value === undefined || Number.isNaN(Number(value))) {
      return "N/A";
    }
    return `${Number(value).toFixed(digits ?? 2)}%`;
  }

  function fmtNum(value) {
    if (value === null || value === undefined || Number.isNaN(Number(value))) {
      return "N/A";
    }
    return new Intl.NumberFormat("en-US").format(Number(value));
  }

  function initTheme() {
    if (!els.themeToggle) {
      return;
    }
    const KEY = "nyhd-theme";
    const saved = localStorage.getItem(KEY) || localStorage.getItem("nch_theme");
    const prefersDark =
      window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    const theme = saved === "dark" || saved === "light" ? saved : prefersDark ? "dark" : "light";
    if (saved === "dark" || saved === "light") {
      document.documentElement.setAttribute("data-theme", theme);
    }
    function syncBtn(isDark) {
      els.themeToggle.setAttribute("aria-pressed", String(isDark));
      els.themeToggle.setAttribute(
        "aria-label",
        isDark ? "Switch back to daylight mode" : "Summon night mode (Gotham signal)"
      );
      els.themeToggle.title = isDark ? "Lights on — daylight mode" : "Summon night mode (Gotham signal)";
    }
    syncBtn(theme === "dark");
    els.themeToggle.addEventListener("click", function () {
      const current = document.documentElement.getAttribute("data-theme") || theme;
      const next = current === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      try {
        localStorage.setItem(KEY, next);
      } catch (_err) {}
      syncBtn(next === "dark");
      if (next === "dark") {
        els.themeToggle.classList.remove("is-beaming");
        void els.themeToggle.offsetWidth;
        els.themeToggle.classList.add("is-beaming");
      }
    });
  }

  async function apiRequest(path, options) {
    const opts = options || {};
    const headers = Object.assign({ Accept: "application/json" }, opts.headers || {});
    const res = await fetch(`${apiBase}${path}`, Object.assign({}, opts, { headers }));
    const text = await res.text();
    let data = {};
    try {
      data = text ? JSON.parse(text) : {};
    } catch (_err) {
      data = { detail: text };
    }
    if (!res.ok) {
      throw new Error(data.detail || `HTTP ${res.status}`);
    }
    return data;
  }

  function apiGet(path) {
    return apiRequest(path);
  }

  function apiPost(path, body) {
    return apiRequest(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  }

  function showError(message) {
    els.errorBanner.textContent = message;
    els.errorBanner.hidden = false;
  }

  function clearError() {
    els.errorBanner.hidden = true;
    els.errorBanner.textContent = "";
  }

  async function initHealthAndSummary() {
    try {
      const health = await apiGet("/health");
      if (health.db_ready) {
        els.statusBadge.textContent = `Live · ${fmtNum(health.parcel_count)} parcels (${health.dataset_version})`;
        els.statusBadge.className = "status-pill ok";
      } else {
        els.statusBadge.textContent = "Index empty — run scripts/build_db.py";
        els.statusBadge.className = "status-pill err";
      }
      partnerCfg = {
        enabled: Boolean(health.partner_inquiry_enabled && health.partner_inquiry_url),
        url: health.partner_inquiry_url || "",
        label: health.partner_inquiry_label || "Request report information",
      };
      reportCfg = {
        enabled: Boolean(health.report_checkout_enabled && health.report_checkout_url),
        recoveryEnabled: Boolean(health.report_recovery_enabled),
        dynamic: Boolean(health.report_dynamic_checkout_enabled),
        previewEnabled: health.report_preview_enabled !== false,
        priceUsd: health.report_price_usd || 39,
        url: health.report_checkout_url || "",
        label: health.report_button_label || "Download Public-Record Assessment Report ($79)",
      };
      apiFlags = {
        evidenceGated: health.evidence_gating_enabled !== false,
        bulkRequiresKey: health.bulk_requires_api_key !== false,
      };
      if (health.parcel_count >= 1000 && els.examplePills) {
        const curated = [
          { bbl: "1011714520", label: "1 WEST END AVE, Apt 20A (Condo)" },
          { bbl: "1011230029", label: "101-105 CENTRAL PARK WEST (Co-op)" },
          { bbl: "1012460142", label: "324 WEST 85 STREET (Townhouse)" },
        ];
        els.examplePills.innerHTML = curated
          .map(function (c) {
            return `<button class="preset-pill" type="button" data-bbl="${escapeHtml(c.bbl)}">${escapeHtml(c.label)}</button>`;
          })
          .join("");
        els.examplePills.querySelectorAll(".preset-pill").forEach(function (btn) {
          btn.addEventListener("click", function () {
            loadParcel(btn.getAttribute("data-bbl"));
          });
        });
      }
    } catch (err) {
      els.statusBadge.textContent = "API offline or unreachable";
      els.statusBadge.className = "status-pill err";
      showError(`Could not reach API /health endpoint: ${err.message}`);
      return;
    }

    try {
      const summary = await apiGet("/v1/stats/cliff-summary");
      const city = summary.citywide || {};
      if (city.parcel_count > 0) {
        els.citywideMeta.textContent = `Roll ${summary.meta.dof_roll_year || "2027"} Period ${summary.meta.dof_roll_period || "3"} · ${fmtNum(city.above_threshold_count)} parcels above threshold`;
        els.citywideStatsGrid.innerHTML = `
          <div class="kpi-box">
            <div class="kpi-label">Indexed Parcels</div>
            <div class="kpi-value">${fmtNum(city.parcel_count)}</div>
            <div class="kpi-note">${fmtNum(city.in_scope_count)} covered condo/co-op/Class 1</div>
          </div>
          <div class="kpi-box">
            <div class="kpi-label">Above Threshold</div>
            <div class="kpi-value">${fmtNum(city.above_threshold_count)}</div>
            <div class="kpi-note">Illustrative universe if non-primary</div>
          </div>
          <div class="kpi-box">
            <div class="kpi-label">Near bracket boundary</div>
            <div class="kpi-value">${fmtNum(city.near_boundary_count)}</div>
            <div class="kpi-note">Within 15% of the current lower boundary</div>
          </div>
          <div class="kpi-box">
            <div class="kpi-label">With Linked Protest</div>
            <div class="kpi-value">${fmtNum(city.protested_above_threshold_count)}</div>
            <div class="kpi-note">Above threshold carrying DOF protest code</div>
          </div>
        `;
        els.citywidePanel.hidden = false;
      }
    } catch (_err) {
      // Optional summary card silently skipped if index not built yet
    }

    if (!els.examplePills.children.length) {
      try {
        const sampleQueries = ["WEST", "BEAVER", "BEACH"];
        const pillButtons = [];
        for (const q of sampleQueries) {
          const res = await apiGet(`/v1/autocomplete?q=${encodeURIComponent(q)}&limit=1`);
          if (res.results && res.results.length > 0) {
            const item = res.results[0];
            pillButtons.push(
              `<button class="preset-pill" type="button" data-bbl="${escapeHtml(item.bbl)}">${escapeHtml(item.full_address)} (${escapeHtml(item.bldg_class || "NYC")})</button>`
            );
          }
        }
        els.examplePills.innerHTML = pillButtons.join("");
        els.examplePills.querySelectorAll(".preset-pill").forEach(function (btn) {
          btn.addEventListener("click", function () {
            loadParcel(btn.getAttribute("data-bbl"));
          });
        });
      } catch (_err) {
        // No sample pills needed if empty DB
      }
    }
  }

  function renderAutocomplete(items) {
    acMatches = items;
    activeAcIndex = -1;
    if (!items.length) {
      els.acList.hidden = true;
      els.acList.innerHTML = "";
      els.searchInput.setAttribute("aria-expanded", "false");
      return;
    }

    els.acList.innerHTML = items
      .map(function (item, idx) {
        return `
          <li class="autocomplete-item" role="option" data-index="${idx}" aria-selected="false">
            <div>
              <div class="ac-main">${escapeHtml(item.full_address)}</div>
              <div class="ac-sub">${escapeHtml(item.borough_name)} · BBL ${escapeHtml(item.bbl)} · Class ${escapeHtml(item.bldg_class || "?")}</div>
            </div>
            <div class="ac-right">
              <div><strong>${fmtUsd(item.finmkttot)}</strong></div>
              <div class="ac-sub">${fmtPct(item.statutory_rate_pct)}</div>
            </div>
          </li>
        `;
      })
      .join("");

    els.acList.querySelectorAll(".autocomplete-item").forEach(function (row) {
      row.addEventListener("mousedown", function (evt) {
        evt.preventDefault();
        const idx = Number(row.getAttribute("data-index"));
        if (acMatches[idx]) {
          selectMatch(acMatches[idx]);
        }
      });
    });

    els.acList.hidden = false;
    els.searchInput.setAttribute("aria-expanded", "true");
  }

  function selectMatch(item) {
    els.acList.hidden = true;
    els.searchInput.setAttribute("aria-expanded", "false");
    els.searchInput.value = item.full_address;
    els.clearBtn.hidden = false;
    loadParcel(item.bbl);
  }

  function updateAcHighlight() {
    const rows = els.acList.querySelectorAll(".autocomplete-item");
    rows.forEach(function (row, idx) {
      row.setAttribute("aria-selected", idx === activeAcIndex ? "true" : "false");
      if (idx === activeAcIndex) {
        row.scrollIntoView({ block: "nearest" });
      }
    });
  }

  async function runAutocomplete(query) {
    const trimmed = query.trim();
    if (trimmed.length < 2) {
      renderAutocomplete([]);
      return;
    }
    try {
      const data = await apiGet(`/v1/autocomplete?q=${encodeURIComponent(trimmed)}&limit=10`);
      renderAutocomplete(data.results || []);
    } catch (_err) {
      renderAutocomplete([]);
    }
  }

  function renderParcel(data) {
    currentParcel = data;
    clearError();
    els.resultSection.hidden = false;

    const p = data.parcel;
    const scope = data.scope;
    const assess = data.assessment;
    const exp = data.exposure;
    const badges = [
      `<span class="badge badge-blue">BBL ${escapeHtml(p.bbl)}</span>`,
      `<span class="badge badge-blue">${escapeHtml(p.borough_name)}</span>`,
      `<span class="badge badge-blue">Class ${escapeHtml(p.bldg_class || "N/A")} (Tax Class ${escapeHtml(p.curtaxclass || "?")})</span>`,
    ];
    if (!exp.in_scope) {
      badges.push(`<span class="badge badge-green">Outside Pied-a-Terre Residential Schedule</span>`);
    } else if (scope.is_coop_building) {
      badges.push('<span class="badge badge-blue">Unit share estimate</span>');
    } else if (exp.above_entry_threshold) {
      badges.push(`<span class="badge badge-red">Above Entry Threshold (${fmtPct(exp.statutory_rate_pct)})</span>`);
    } else {
      badges.push(`<span class="badge badge-green">Below Entry Threshold (0%)</span>`);
    }
    if (assess.has_protest_code) {
      badges.push(`<span class="badge badge-blue">DOF Protest Code ${escapeHtml(assess.protest_1)}</span>`);
    }

    els.parcelBadges.innerHTML = badges.join("");
    els.parcelAddressTitle.textContent = p.full_address;
    els.parcelSubline.textContent = `Block ${p.block} · Lot ${p.lot} · ZIP ${p.zip_code || "N/A"}`;

    const displayExposure = scope.is_coop_building && data.coop_default_estimate
      ? data.coop_default_estimate.exposure
      : exp;
    const reportApplies = Boolean(
      displayExposure.above_entry_threshold || (scope.is_coop_building && exp.above_entry_threshold)
    );

    if (els.verdictCallout) {
      els.verdictCallout.className = "verdict-box";
      const message = !scope.in_scope
        ? escapeHtml(scope.scope_reason)
        : scope.is_coop_building
          ? "The roll records a building value. Any displayed unit amount assumes equal shares."
          : displayExposure.above_entry_threshold
            ? "At or above the threshold, the Phase 1 rate applies to the whole value."
            : "The recorded value is below the entry threshold.";
      const warning = exp.unusual_value_flag ? ` <strong>${escapeHtml(exp.unusual_value_note)}.</strong>` : "";
      const boundary = !scope.is_coop_building && exp.cliff
        ? ` DOF value is ${fmtUsd(exp.cliff.distance_above_threshold_dollars)} (${fmtPct(exp.cliff.distance_above_threshold_pct, 1)}) above the ${fmtUsd(exp.entry_threshold)} threshold.`
        : "";
      els.verdictCallout.innerHTML = `<p>${message}${boundary}${warning}</p><p>Public-record data, not legal, tax or appraisal advice. This report does not suggest any value to claim or whether to appeal.</p>`;
      els.verdictCallout.hidden = false;
    }

    if (reportApplies && reportCfg.previewEnabled) {
      els.reportPreviewBtn.href = `${apiBase}/v1/report/sample.pdf`;
      els.reportPreviewBtn.textContent = "View Sample PDF (Example Unit)";
      els.reportPreviewBtn.hidden = false;
    } else {
      els.reportPreviewBtn.hidden = true;
    }

    if (reportApplies && reportCfg.dynamic) {
      els.reportCheckoutBtn.href = "#";
      els.reportCheckoutBtn.removeAttribute("target");
      els.reportCheckoutBtn.removeAttribute("rel");
      els.reportCheckoutBtn.textContent = reportCfg.label;
      els.reportCheckoutBtn.hidden = false;
    } else if (reportApplies && reportCfg.enabled) {
      const sep = reportCfg.url.includes("?") ? "&" : "?";
      els.reportCheckoutBtn.href = `${reportCfg.url}${sep}client_reference_id=${encodeURIComponent(p.bbl)}&bbl=${encodeURIComponent(p.bbl)}`;
      els.reportCheckoutBtn.setAttribute("target", "_blank");
      els.reportCheckoutBtn.setAttribute("rel", "noopener");
      els.reportCheckoutBtn.textContent = reportCfg.label;
      els.reportCheckoutBtn.hidden = false;
    } else {
      els.reportCheckoutBtn.hidden = true;
    }

    if (partnerCfg.enabled) {
      els.partnerInquiryBtn.href = `${partnerCfg.url}${partnerCfg.url.includes("?") ? "&" : "?"}bbl=${encodeURIComponent(p.bbl)}`;
      els.partnerInquiryBtn.textContent = partnerCfg.label;
      els.partnerInquiryBtn.hidden = false;
    } else {
      els.partnerInquiryBtn.hidden = true;
    }

    const surchargeNote = scope.is_coop_building
      ? `Illustrative equal-split unit (${fmtNum(p.coop_apts || p.units || 1)} units) if non-primary`
      : `If covered and non-primary (${exp.band_label})`;

    els.primaryKpiGrid.innerHTML = `
      <div class="kpi-box">
        <div class="kpi-label">DOF Final Market Value</div>
        <div class="kpi-value">${fmtUsd(assess.finmkttot)}</div>
        <div class="kpi-note">YoY vs prior roll: ${assess.yoy_mkt_change_pct !== null ? fmtPct(assess.yoy_mkt_change_pct) : "N/A"}</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-label">Phase 1 Statutory Rate</div>
        <div class="kpi-value">${fmtPct(displayExposure.statutory_rate_pct)}</div>
        <div class="kpi-note">${escapeHtml(displayExposure.band_label)}</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-label">Illustrative Annual Surcharge</div>
        <div class="kpi-value">${fmtUsd(displayExposure.annual_surcharge_if_non_primary)}</div>
        <div class="kpi-note">${escapeHtml(surchargeNote)}</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-label">Phase 1 Two-Year Total</div>
        <div class="kpi-value">${fmtUsd(displayExposure.phase1_two_year_total)}</div>
        <div class="kpi-note">TC107 deadline: ${escapeHtml(scope.tc107_deadline_label)}</div>
      </div>
    `;

    renderCliffPanel(scope, displayExposure);
    renderAssessmentPanel(p, assess, scope);
    renderCoopPanel(p, scope, data.coop_default_estimate);
    renderBuildingContext(p, data.building_context, Boolean(data.evidence_gated));
    renderAcrisSales(data.acris_sales);
    renderDisclaimers(data.disclaimers);

    const nextUrl = new URL(window.location.href);
    nextUrl.searchParams.set("bbl", p.bbl);
    nextUrl.searchParams.delete("session_id");
    nextUrl.searchParams.delete("checkout");
    window.history.replaceState({}, "", nextUrl.toString());
  }

  function renderCliffPanel(scope, exp) {
    if (!exp.in_scope) {
      els.cliffDetails.innerHTML = `<div class="callout-box callout-info">${escapeHtml(scope.scope_reason)}</div>`;
      return;
    }
    const cliff = exp.cliff;
    const next = exp.next_threshold_above;
    const rows = [
      `<tr><th>Schedule Type</th><td>${escapeHtml(exp.schedule_type)}</td></tr>`,
      `<tr><th>Entry Threshold</th><td>${fmtUsd(exp.entry_threshold)}</td></tr>`,
      `<tr><th>Statutory Bracket</th><td>${escapeHtml(exp.band_label)}</td></tr>`,
    ];
    if (cliff) {
      rows.push(
        `<tr><th>Above Entry Threshold By</th><td>${fmtUsd(cliff.distance_above_threshold_dollars)} (${fmtPct(cliff.distance_above_threshold_pct, 1)})</td></tr>`,
        `<tr><th>Next Lower Bracket Boundary</th><td>${fmtUsd(cliff.next_lower_bracket_boundary)}</td></tr>`,
        `<tr><th>Distance to Next Lower Bracket</th><td>${fmtUsd(cliff.distance_to_next_lower_bracket_dollars)}</td></tr>`
      );
    }
    if (next) {
      rows.push(
        `<tr><th>Headroom Before ${fmtPct(next.next_rate_pct)} Band</th><td>${fmtUsd(next.headroom_dollars)} (${fmtPct(next.headroom_pct)})</td></tr>`
      );
    }

    const callout = scope.is_coop_building
      ? '<div class="callout-box callout-info">The bracket shown uses an equal-share unit estimate. Enter actual unit shares below if available.</div>'
      : "";
    const unusual = exp.unusual_value_flag
      ? `<div class="callout-box callout-warn">${escapeHtml(exp.unusual_value_note || "unusual value; check the parcel class")}</div>`
      : "";
    els.cliffDetails.innerHTML = `<table class="kv-table">${rows.join("")}</table>${callout}${unusual}`;
  }

  function renderAssessmentPanel(p, assess, scope) {
    const unitRow = scope.is_coop_building
      ? `<tr><th>Units / Co-op Apts</th><td>${p.units ?? "N/A"} / ${p.coop_apts ?? "N/A"}</td></tr>`
      : `<tr><th>Residential Units</th><td>${p.units ?? "N/A"}</td></tr>`;
    const protestVal = assess.protest_details_gated
      ? `Yes — code &amp; attorney group in $${reportCfg.priceUsd} PDF`
      : `${escapeHtml(assess.protest_1 || "None")} / ${escapeHtml(assess.attorney_group1 || "None")}`;
    els.assessmentDetails.innerHTML = `
      <table class="kv-table">
        <tr><th>Roll Year / Period</th><td>${escapeHtml(p.year)} / Period ${escapeHtml(p.period)} (Final)</td></tr>
        <tr><th>Prior Year Market Value</th><td>${fmtUsd(assess.pymkttot)}</td></tr>
        <tr><th>Final Actual Assessed Total</th><td>${fmtUsd(assess.finacttot)}</td></tr>
        <tr><th>Final Taxable Total</th><td>${fmtUsd(assess.fintxbtot)}</td></tr>
        <tr><th>Assessed / Market Ratio</th><td>${assess.assessed_to_market_ratio !== null ? fmtPct(assess.assessed_to_market_ratio * 100, 2) : "N/A"}</td></tr>
        <tr><th>Year Built / Gross SqFt</th><td>${p.yrbuilt || "N/A"} / ${p.gross_sqft ? fmtNum(p.gross_sqft) : "N/A"} sqft</td></tr>
        ${unitRow}
        <tr><th>DOF Protest / Atty Group</th><td>${protestVal}</td></tr>
        <tr><th>TC107 Filing Window</th><td>${escapeHtml(scope.tc107_deadline_label)}</td></tr>
      </table>
    `;
  }

  function renderCoopPanel(p, scope, defaultEstimate) {
    if (!scope.is_coop_building) {
      els.coopCalculatorCard.hidden = true;
      els.coopEstimateOutput.innerHTML = "";
      return;
    }
    els.coopCalculatorCard.hidden = false;
    els.unitSharesInput.value = "";
    els.totalSharesInput.value = "";
    els.sharePctInput.value = "";
    if (defaultEstimate) {
      renderCoopEstimateOutput(defaultEstimate);
    }
  }

  function renderCoopEstimateOutput(estimate) {
    const exp = estimate.exposure;
    const cliff = exp.cliff;
    els.coopEstimateOutput.innerHTML = `
      <div class="stats-grid">
        <div class="kpi-box">
          <div class="kpi-label">Allocated Unit Value</div>
          <div class="kpi-value">${fmtUsd(estimate.estimated_unit_market_value)}</div>
          <div class="kpi-note">${fmtPct(estimate.ownership_pct, 3)} of ${fmtUsd(estimate.building_market_value)} (${escapeHtml(estimate.allocation_method)})</div>
        </div>
        <div class="kpi-box">
          <div class="kpi-label">Allocated Rate</div>
          <div class="kpi-value">${fmtPct(exp.statutory_rate_pct)}</div>
          <div class="kpi-note">${escapeHtml(exp.band_label)}</div>
        </div>
        <div class="kpi-box">
          <div class="kpi-label">Illustrative Unit Tax / Yr</div>
          <div class="kpi-value">${fmtUsd(exp.annual_surcharge_if_non_primary)}</div>
          <div class="kpi-note">${cliff ? `${fmtUsd(cliff.distance_above_threshold_dollars)} above the entry threshold` : "Below $1M entry threshold"}</div>
        </div>
      </div>
    `;
  }

  function renderBuildingContext(p, ctx, evidenceGated) {
    els.blockUnitsTableWrap.hidden = true;
    els.blockUnitsTableWrap.innerHTML = "";
    const hideBulk = Boolean(evidenceGated || apiFlags.bulkRequiresKey);
    els.loadBlockUnitsBtn.hidden = hideBulk;

    let extraHtml = "";
    if (evidenceGated) {
      extraHtml = `
        <div class="locked-box">
          <div><strong>Unit-by-unit peer table included in the $${reportCfg.priceUsd} assessment report:</strong> Unlock up to 12 comparable building units (unit numbers, DOF market values, statutory rates and threshold distances for RPTL § 581 review).</div>
          <button type="button" class="btn-primary btn-sm js-unlock-pdf">Unlock Full Unit PDF ($${reportCfg.priceUsd})</button>
        </div>
      `;
    } else if (apiFlags.bulkRequiresKey) {
      extraHtml = `<p class="muted-line" style="margin-top:10px">Block-level unit exports are available for full-building audits or via B2B API key (<a href="#for-firms">see below</a>).</p>`;
    }

    els.buildingContextSummary.innerHTML = `
      <table class="kv-table">
        <tr><th>Grouping Key</th><td><code>${escapeHtml(ctx.grouping)}</code></td></tr>
        <tr><th>Total Parcels in Group</th><td>${fmtNum(ctx.parcel_count)}</td></tr>
        <tr><th>Above Threshold Parcels</th><td>${fmtNum(ctx.above_threshold_parcels ?? ctx.above_threshold_count)}</td></tr>
        <tr><th>Parcels near a bracket boundary</th><td>${fmtNum(ctx.near_boundary_parcels)}</td></tr>
        <tr><th>Aggregate Illustrative Annual Surcharge</th><td>${fmtUsd(ctx.total_illustrative_annual_surcharge)}</td></tr>
      </table>
      ${extraHtml}
    `;
  }

  function renderAcrisSales(acris) {
    if (acris && acris.gated) {
      const ratioNote = acris.finmkttot_to_last_sale_ratio
        ? `<p class="muted-line">Latest DOF Market Value / Last Sale Ratio: <strong>${Number(acris.finmkttot_to_last_sale_ratio).toFixed(2)}x</strong> (${fmtNum(acris.sale_count)} indexed parcel sale${acris.sale_count === 1 ? "" : "s"})</p>`
        : `<p class="muted-line">${fmtNum(acris.sale_count || 0)} direct parcel sale(s) plus building/ZIP comparable sales indexed in this roll.</p>`;
      els.acrisSalesWrap.innerHTML = `
        ${ratioNote}
        <div class="locked-box">
          <div><strong>Itemized ACRIS sales &amp; peer comps included in the $${reportCfg.priceUsd} assessment report:</strong> Unlock deed dates, recorded prices, mortgage/CEMA flags, ACRIS document IDs, up to 8 building/ZIP comps, and the July 2028 Phase-2 preview.</div>
          <button type="button" class="btn-primary btn-sm js-unlock-pdf">Unlock Full Unit PDF ($${reportCfg.priceUsd})</button>
        </div>
      `;
      return;
    }
    if (!acris || !acris.recent_sales || acris.recent_sales.length === 0) {
      els.acrisSalesWrap.innerHTML = `
        <p class="muted-line">
          No ACRIS residential sales linked to BBL ${escapeHtml(currentParcel.parcel.bbl)} in this index
          (optional <code>sales.csv.gz</code> + <code>links.csv.gz</code> linkage applies when loaded at build time).
        </p>
      `;
      return;
    }
    const ratioNote = acris.finmkttot_to_last_sale_ratio
      ? `<p class="muted-line">Latest DOF Market Value / Last Sale Ratio: <strong>${Number(acris.finmkttot_to_last_sale_ratio).toFixed(2)}x</strong></p>`
      : "";
    const rows = acris.recent_sales
      .map(function (sale) {
        const financing =
          sale.financed === null
            ? "Unlinked"
            : sale.financed
            ? `${sale.cema ? "CEMA Mortgage" : "Mortgage"} (${fmtUsd(sale.mortgage_amount)})`
            : "Cash / No Mtge";
        return `
          <tr>
            <td>${escapeHtml(sale.sale_date || "N/A")}</td>
            <td><strong>${fmtUsd(sale.sale_price)}</strong></td>
            <td>${escapeHtml(financing)}</td>
            <td><code>${escapeHtml(sale.deed_document_id || "-")}</code></td>
          </tr>
        `;
      })
      .join("");
    els.acrisSalesWrap.innerHTML = `
      ${ratioNote}
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr><th>Sale Date</th><th>Sale Price</th><th>Financing</th><th>ACRIS Deed</th></tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    `;
  }

  function renderDisclaimers(disclaimers) {
    const items = Object.values(disclaimers || {});
    els.disclaimersList.innerHTML = items
      .map(function (line) {
        return `<li>${escapeHtml(line)}</li>`;
      })
      .join("");
  }

  async function loadParcel(bbl) {
    try {
      clearError();
      const data = await apiGet(`/v1/parcel/${encodeURIComponent(bbl)}`);
      renderParcel(data);
    } catch (err) {
      showError(`Parcel lookup failed for ${bbl}: ${err.message}`);
    }
  }

  els.searchInput.addEventListener("input", function () {
    els.clearBtn.hidden = !els.searchInput.value.trim();
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(function () {
      runAutocomplete(els.searchInput.value);
    }, 140);
  });

  els.searchInput.addEventListener("keydown", function (evt) {
    if (els.acList.hidden || !acMatches.length) {
      if (evt.key === "Enter" && els.searchInput.value.trim()) {
        evt.preventDefault();
        runAutocomplete(els.searchInput.value);
      }
      return;
    }
    if (evt.key === "ArrowDown") {
      evt.preventDefault();
      activeAcIndex = (activeAcIndex + 1) % acMatches.length;
      updateAcHighlight();
    } else if (evt.key === "ArrowUp") {
      evt.preventDefault();
      activeAcIndex = (activeAcIndex - 1 + acMatches.length) % acMatches.length;
      updateAcHighlight();
    } else if (evt.key === "Enter") {
      evt.preventDefault();
      const chosen = acMatches[activeAcIndex >= 0 ? activeAcIndex : 0];
      if (chosen) {
        selectMatch(chosen);
      }
    } else if (evt.key === "Escape") {
      els.acList.hidden = true;
    }
  });

  els.clearBtn.addEventListener("click", function () {
    els.searchInput.value = "";
    els.clearBtn.hidden = true;
    renderAutocomplete([]);
    els.searchInput.focus();
  });

  document.addEventListener("click", function (evt) {
    if (!evt.target.closest(".search-shell")) {
      els.acList.hidden = true;
    }
  });

  els.coopForm.addEventListener("submit", async function (evt) {
    evt.preventDefault();
    if (!currentParcel) {
      return;
    }
    const qs = new URLSearchParams({ bbl: currentParcel.parcel.bbl });
    const pct = els.sharePctInput.value.trim();
    const uShares = els.unitSharesInput.value.trim();
    const tShares = els.totalSharesInput.value.trim();

    if (pct) {
      qs.set("share_pct", pct);
    } else if (uShares && tShares) {
      qs.set("unit_shares", uShares);
      qs.set("total_shares", tShares);
    }

    try {
      clearError();
      const data = await apiGet(`/v1/coop-estimate?${qs.toString()}`);
      renderCoopEstimateOutput(data.estimate);
    } catch (err) {
      showError(`Co-op calculation error: ${err.message}`);
    }
  });

  els.loadBlockUnitsBtn.addEventListener("click", async function () {
    if (!currentParcel) {
      return;
    }
    const p = currentParcel.parcel;
    try {
      clearError();
      const res = await apiGet(
        `/v1/building-units/${encodeURIComponent(p.boro)}/${encodeURIComponent(p.block)}?limit=25`
      );
      const rows = (res.units || [])
        .map(function (u) {
          return `
            <tr>
              <td><button class="unit-link" type="button" data-bbl="${escapeHtml(u.bbl)}">${escapeHtml(u.full_address)}</button></td>
              <td>${escapeHtml(u.bldg_class || "-")}</td>
              <td>${fmtUsd(u.finmkttot)}</td>
              <td>${fmtPct(u.statutory_rate_pct)}</td>
              <td>${u.near_boundary ? "Yes" : "No"}</td>
            </tr>
          `;
        })
        .join("");

      els.blockUnitsTableWrap.innerHTML = `
        <table class="data-table">
          <thead>
            <tr><th>Parcel / Unit</th><th>Class</th><th>DOF Market Val</th><th>Rate</th><th>Near bracket boundary</th></tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      `;
      els.blockUnitsTableWrap.hidden = false;
      els.blockUnitsTableWrap.querySelectorAll(".unit-link").forEach(function (btn) {
        btn.addEventListener("click", function () {
          loadParcel(btn.getAttribute("data-bbl"));
        });
      });
    } catch (err) {
      showError(`Could not load block units: ${err.message}`);
    }
  });

  els.copyCitationBtn.addEventListener("click", async function () {
    if (!currentParcel) {
      return;
    }
    const p = currentParcel.parcel;
    const exp = currentParcel.exposure;
    const text = [
      `${p.full_address} (${p.borough_name}, BBL ${p.bbl})`,
      `NYC DOF ${p.year} Final Roll market value: ${fmtUsd(currentParcel.assessment.finmkttot)} (${exp.band_label})`,
      `Source: ${currentParcel.citation.source_label} — ${window.location.href}`,
    ].join(" | ");
    try {
      await navigator.clipboard.writeText(text);
      els.copyCitationBtn.textContent = "Copied!";
      setTimeout(function () {
        els.copyCitationBtn.textContent = "Copy Citation & Link";
      }, 1800);
    } catch (_err) {
      showError(`Citation text ready: ${text}`);
    }
  });

  els.resultSection.addEventListener("click", function (evt) {
    if (evt.target.closest(".js-unlock-pdf") && els.reportCheckoutBtn && !els.reportCheckoutBtn.hidden) {
      els.reportCheckoutBtn.click();
    }
  });

  els.reportCheckoutBtn.addEventListener("click", async function (evt) {
    if (!currentParcel || !reportCfg.dynamic) {
      return;
    }
    evt.preventDefault();
    if (checkoutPending) return;
    checkoutPending = true;
    const origLabel = els.reportCheckoutBtn.textContent;
    els.reportCheckoutBtn.textContent = "Opening Stripe Checkout...";
    els.reportCheckoutBtn.setAttribute("aria-disabled", "true");
    try {
      clearError();
      const returnUrl = window.location.origin + window.location.pathname;
      const data = await apiPost("/v1/checkout/report", {
        bbl: currentParcel.parcel.bbl,
        return_url: returnUrl,
      });
      if (data && data.checkout_url) {
        window.location.href = data.checkout_url;
        return;
      }
      throw new Error("Missing checkout_url from server.");
    } catch (err) {
      showError(`Could not start PDF checkout: ${err.message}`);
      els.reportCheckoutBtn.textContent = origLabel;
      els.reportCheckoutBtn.removeAttribute("aria-disabled");
    } finally {
      checkoutPending = false;
    }
  });

  async function verifyStripeSession(sessionId) {
    try {
      const res = await apiGet(
        `/v1/report/verify-session?session_id=${encodeURIComponent(sessionId)}`
      );
      if (res && res.paid && res.bbl) {
        await loadParcel(res.bbl);
        els.paymentBannerText.textContent = `Payment verified for BBL ${res.bbl}. Your Public-Record Assessment Report is ready.`;
        els.paymentDownloadBtn.href = `${apiBase}${res.download_url}`;
        els.paymentRecovery.hidden = !reportCfg.recoveryEnabled;
        els.paymentBanner.hidden = false;
      } else {
        showError("Stripe checkout session is not marked as paid yet. If you need another link, use the recovery page when email recovery is available.");
      }
    } catch (err) {
      showError(`Could not verify Stripe session: ${err.message}`);
    }
  }

  if (params.has("session_id")) {
    const cleanUrl = new URL(window.location.href);
    cleanUrl.searchParams.delete("session_id");
    window.history.replaceState({}, "", cleanUrl);
  }

  initTheme();
  initHealthAndSummary().then(function () {
    const checkoutSessionId = params.get("session_id");
    const initialBbl = params.get("bbl");
    if (checkoutSessionId) {
      verifyStripeSession(checkoutSessionId);
    } else if (initialBbl) {
      loadParcel(initialBbl);
    }
  });
})();
