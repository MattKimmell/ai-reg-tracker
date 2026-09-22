/* US AI Reg Tracker — static SPA (hash routes) */
(function () {
  "use strict";

  const STATUS_META = {
    in_force: { label: "In force", css: "status-in-force" },
    enacted_pending: { label: "Enacted / pending", css: "status-pending" },
    proposed_hot: { label: "Proposed (hot)", css: "status-hot" },
    quiet: { label: "Quiet", css: "status-quiet" },
    watch: { label: "Watch", css: "status-watch" },
  };

  const RELEVANCE_META = {
    high: { label: "High", css: "rel-high" },
    medium: { label: "Medium", css: "rel-medium" },
    low: { label: "Low", css: "rel-low" },
    none: { label: "None", css: "rel-none" },
  };

  const US_TILE_ROWS = [
    [null, null, null, null, null, null, null, null, null, null, null, "ME"],
    ["AK", null, "WA", "OR", "ID", "MT", "ND", "MN", "WI", "MI", null, "VT", "NH"],
    [null, null, "CA", "NV", "UT", "WY", "SD", "IA", "IL", "IN", "OH", "PA", "NY", "MA"],
    [null, null, "AZ", "CO", "NE", "MO", "KY", "WV", "VA", "MD", "DE", "NJ", "CT", "RI"],
    [null, null, null, "NM", "KS", "AR", "TN", "NC", "SC", null, null, null, null, null],
    [null, null, null, null, "OK", "LA", "MS", "AL", "GA", null, null, null, null, null],
    [null, null, null, null, null, "TX", null, null, "FL", null, null, null, null, null],
    ["HI", null, null, null, null, null, null, null, "DC", null, null, null, null, null],
  ];

  let DATA = null;
  let activityChart = null;
  let searchBound = false;

  function esc(s) {
    if (s == null) return "";
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function statusMeta(label) {
    return STATUS_META[label] || STATUS_META.quiet;
  }

  function relMeta(rel) {
    return RELEVANCE_META[rel] || RELEVANCE_META.none;
  }

  function enrich(j) {
    const m = statusMeta(j.status_label);
    return Object.assign({}, j, {
      status_display: m.label,
      status_css: m.css,
    });
  }

  function parseRoute() {
    const raw = (location.hash || "#/").replace(/^#/, "") || "/";
    const path = raw.split("?")[0];
    const qs = raw.includes("?") ? raw.slice(raw.indexOf("?") + 1) : "";
    const params = new URLSearchParams(qs);
    if (path === "/" || path === "") {
      return { page: "home", filter: params.get("filter") || "all", q: params.get("q") || "" };
    }
    if (path === "/about") return { page: "about" };
    const m = path.match(/^\/j\/([^/]+)\/?$/i);
    if (m) return { page: "jurisdiction", code: decodeURIComponent(m[1]).toUpperCase() };
    return { page: "notfound" };
  }

  function setNav(active) {
    document.getElementById("nav-home").classList.toggle("active", active === "home");
    document.getElementById("nav-about").classList.toggle("active", active === "about");
  }

  function computeStats() {
    const by = {};
    for (const j of DATA.jurisdictions) {
      by[j.status_label] = (by[j.status_label] || 0) + 1;
    }
    let voiceHigh = 0;
    for (const d of DATA.details) {
      for (const o of d.obligations || []) {
        if (o.voice_cs_relevance === "high") voiceHigh += 1;
      }
    }
    return {
      in_force: by.in_force || 0,
      enacted_pending: by.enacted_pending || 0,
      proposed_hot: by.proposed_hot || 0,
      watch: by.watch || 0,
      quiet: by.quiet || 0,
      voice_high: voiceHigh,
    };
  }

  function activitySeries() {
    const counter = {};
    for (const d of DATA.details) {
      for (const h of d.history || []) {
        const m = (h.event_date || "").slice(0, 7);
        if (m.length === 7 && m[4] === "-") counter[m] = (counter[m] || 0) + 1;
      }
      for (const o of d.obligations || []) {
        const m = (o.effective_date || "").slice(0, 7);
        if (m.length === 7 && m[4] === "-") counter[m] = (counter[m] || 0) + 1;
      }
    }
    const keys = Object.keys(counter).sort();
    if (!keys.length) return [];
    const end = keys[keys.length - 1];
    let y = +end.slice(0, 4);
    let mo = +end.slice(5, 7);
    const series = [];
    for (let i = 0; i < 24; i++) {
      const k = y.toString().padStart(4, "0") + "-" + mo.toString().padStart(2, "0");
      series.push({ month: k, count: counter[k] || 0 });
      mo -= 1;
      if (mo === 0) { mo = 12; y -= 1; }
    }
    series.reverse();
    while (series.length && series[0].count === 0) series.shift();
    return series;
  }

  function buildSearchIndex() {
    return DATA.details.map((d) => {
      const j = d.jurisdiction;
      const bits = [j.code, j.name, j.summary || ""];
      for (const o of d.obligations || []) {
        bits.push(o.title || "", o.summary || "", o.voice_cs_why || "");
        if (o.themes) bits.push(...o.themes);
      }
      return {
        code: j.code,
        name: j.name,
        status_label: j.status_label,
        text: bits.join(" ").toLowerCase(),
      };
    });
  }

  function filterJurisdictions(filter) {
    let list = DATA.jurisdictions.slice();
    if (filter === "hot") {
      list = list.filter((j) =>
        j.status_label === "proposed_hot" || j.status_label === "enacted_pending"
      );
    } else if (filter === "in_force") {
      list = list.filter((j) => j.status_label === "in_force");
    } else if (filter === "voice" || filter === "voice_cs") {
      const codes = new Set();
      for (const d of DATA.details) {
        const has = (d.obligations || []).some(
          (o) => o.voice_cs_relevance === "high" || o.voice_cs_relevance === "medium"
        );
        if (has) codes.add(d.jurisdiction.code);
      }
      list = list.filter((j) => codes.has(j.code));
    }
    return list.map(enrich);
  }

  function renderMap(byCode) {
    let html = '<p class="section-label">United States map</p><div class="map-panel" id="us-map">';
    for (const row of US_TILE_ROWS) {
      html += '<div class="map-row">';
      for (const code of row) {
        if (!code) {
          html += '<span class="map-cell empty-cell" aria-hidden="true"></span>';
          continue;
        }
        const j = byCode[code];
        if (!j) {
          html += `<span class="map-cell empty-cell" title="${esc(code)}"></span>`;
          continue;
        }
        const e = enrich(j);
        html += `<a class="map-cell ${e.status_css}" href="#/j/${esc(e.code)}" data-code="${esc(e.code)}" title="${esc(e.name)} — ${esc(e.status_display)}">${esc(e.code)}</a>`;
      }
      html += "</div>";
    }
    html += "</div>";
    return html;
  }

  function renderHome(filter) {
    setNav("home");
    document.title = "US AI Regulation Status · US AI Reg Tracker";
    const stats = computeStats();
    const jurisdictions = filterJurisdictions(filter);
    const federal = jurisdictions.filter((j) => j.kind === "federal");
    const states = jurisdictions.filter((j) => j.kind === "state" || j.kind === "local");
    const byCode = {};
    for (const j of DATA.jurisdictions) byCode[j.code] = j;

    const chips = ["all", "hot", "in_force", "voice"];
    const chipLabels = {
      all: "All",
      hot: "Hot",
      in_force: "In force",
      voice: "Voice/conversation",
    };

    let html = "";
    html += `<p class="meta-line">Last global refresh: <strong>${esc(DATA.last_global_refresh || "—")}</strong>
      · Showing ${jurisdictions.length} jurisdiction${jurisdictions.length !== 1 ? "s" : ""}</p>`;

    html += `<div class="stats-row">
      <div class="stat-card"><div class="stat-num">${stats.in_force}</div><div class="stat-label">In force</div></div>
      <div class="stat-card"><div class="stat-num">${stats.enacted_pending}</div><div class="stat-label">Enacted / pending</div></div>
      <div class="stat-card"><div class="stat-num">${stats.proposed_hot}</div><div class="stat-label">Proposed (hot)</div></div>
      <div class="stat-card"><div class="stat-num">${stats.watch}</div><div class="stat-label">Watch</div></div>
      <div class="stat-card"><div class="stat-num">${stats.quiet}</div><div class="stat-label">Quiet</div></div>
      <div class="stat-card accent"><div class="stat-num">${stats.voice_high}</div><div class="stat-label">Voice/conversation high</div></div>
    </div>`;

    html += `<div class="toolbar">
      <div class="chips">`;
    for (const c of chips) {
      html += `<a class="chip ${filter === c ? "active" : ""}" href="#/?filter=${c}">${chipLabels[c]}</a>`;
    }
    html += `</div>
      <div class="search-wrap">
        <label class="sr-only" for="search-box">Search</label>
        <input type="search" id="search-box" placeholder="Search state, code, obligation, theme…" autocomplete="off">
        <div id="search-results" class="search-results" hidden></div>
      </div>
    </div>`;

    html += `<div class="legend">
      <span class="l-in-force">In force</span>
      <span class="l-pending">Enacted / pending</span>
      <span class="l-hot">Proposed (hot)</span>
      <span class="l-watch">Watch</span>
      <span class="l-quiet">Quiet</span>
    </div>`;

    if (federal.length) {
      html += `<p class="section-label">Federal</p>`;
      for (const j of federal) {
        html += `<a class="federal-card ${j.status_css}" href="#/j/${esc(j.code)}" data-code="${esc(j.code)}" style="display:block; text-decoration:none; color:inherit;">
          <div style="display:flex; flex-wrap:wrap; align-items:center; gap:0.5rem;">
            <h2 style="margin:0;">${esc(j.name)}</h2>
            <span class="pill ${j.status_css}">${esc(j.status_display)}</span>
          </div>
          <p>${esc(j.summary)}</p>
          <p style="font-size:0.8rem; margin-top:0.6rem;">Reviewed ${esc(j.last_reviewed || "—")} →</p>
        </a>`;
      }
    }

    html += renderMap(byCode);

    html += `<div class="chart-panel">
      <p class="section-label">Regulatory activity (history events + obligation effective dates)</p>
      <canvas id="activity-chart" height="100" aria-label="Activity over time chart"></canvas>
    </div>`;

    if (states.length) {
      html += `<p class="section-label">States &amp; DC (list)</p><div class="grid" id="state-grid">`;
      for (const j of states) {
        html += `<a class="state-tile ${j.status_css}" href="#/j/${esc(j.code)}" data-code="${esc(j.code)}" title="${esc(j.name)}">
          <div class="code">${esc(j.code)}</div>
          <div class="name">${esc(j.name)}</div>
          <div class="badge">${esc(j.status_display)}</div>
        </a>`;
      }
      html += `</div>`;
    } else {
      html += `<p class="empty">No jurisdictions match this filter.</p>`;
    }

    document.getElementById("app").innerHTML = html;
    bindSearch();
    drawChart();
  }

  function drawChart() {
    const canvas = document.getElementById("activity-chart");
    if (!canvas) return;
    if (activityChart) {
      activityChart.destroy();
      activityChart = null;
    }
    const data = activitySeries();
    if (!data.length) {
      canvas.parentElement.insertAdjacentHTML("beforeend", '<p class="empty">No dated activity yet.</p>');
      return;
    }
    function make() {
      if (typeof Chart === "undefined") return false;
      activityChart = new Chart(canvas.getContext("2d"), {
        type: "bar",
        data: {
          labels: data.map((d) => d.month),
          datasets: [{
            label: "Events / effective dates",
            data: data.map((d) => d.count),
            backgroundColor: "rgba(91, 159, 212, 0.55)",
            borderColor: "rgba(91, 159, 212, 0.95)",
            borderWidth: 1,
            borderRadius: 3,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: { legend: { display: false } },
          scales: {
            x: {
              ticks: { color: "#8b9bb4", maxRotation: 45, autoSkip: true, maxTicksLimit: 12 },
              grid: { color: "rgba(45,58,79,0.5)" },
            },
            y: {
              beginAtZero: true,
              ticks: { color: "#8b9bb4", precision: 0 },
              grid: { color: "rgba(45,58,79,0.5)" },
            },
          },
        },
      });
      return true;
    }
    if (!make()) {
      let n = 0;
      const t = setInterval(function () {
        n += 1;
        if (make() || n > 40) clearInterval(t);
      }, 50);
    }
  }

  function bindSearch() {
    const input = document.getElementById("search-box");
    const results = document.getElementById("search-results");
    if (!input || !results) return;
    const index = buildSearchIndex();

    function clearHighlights() {
      document.querySelectorAll(".map-cell.hit, .state-tile.hit, .federal-card.hit").forEach((el) => {
        el.classList.remove("hit");
      });
    }
    function highlight(codes) {
      clearHighlights();
      codes.forEach((code) => {
        document.querySelectorAll('[data-code="' + code + '"]').forEach((el) => el.classList.add("hit"));
      });
    }
    function run() {
      const q = (input.value || "").trim().toLowerCase();
      if (!q) {
        results.hidden = true;
        results.innerHTML = "";
        clearHighlights();
        return;
      }
      const matches = index.filter((item) =>
        item.text.indexOf(q) !== -1 ||
        item.code.toLowerCase().indexOf(q) !== -1 ||
        item.name.toLowerCase().indexOf(q) !== -1
      ).slice(0, 12);
      highlight(matches.map((m) => m.code));
      if (!matches.length) {
        results.innerHTML = '<div class="search-empty">No matches</div>';
        results.hidden = false;
        return;
      }
      results.innerHTML = matches.map((m) =>
        `<a class="search-item" href="#/j/${esc(m.code)}"><strong>${esc(m.code)}</strong> ${esc(m.name)} <span class="muted">${esc(m.status_label)}</span></a>`
      ).join("");
      results.hidden = false;
    }
    input.addEventListener("input", run);
    input.addEventListener("keydown", (e) => {
      if (e.key === "Escape") { input.value = ""; run(); input.blur(); }
    });
  }

  function findDetail(code) {
    return DATA.details.find((d) => d.jurisdiction.code === code) || null;
  }

  function renderJurisdiction(code) {
    setNav("home");
    const detail = findDetail(code);
    if (!detail) {
      document.title = "Not found · US AI Reg Tracker";
      document.getElementById("app").innerHTML =
        `<a class="back" href="#/">← All jurisdictions</a>
         <p class="empty">Jurisdiction ${esc(code)} not found.</p>`;
      return;
    }
    const j = enrich(detail.jurisdiction);
    document.title = `${j.name} · US AI Reg Tracker`;

    let html = `<a class="back" href="#/">← All jurisdictions</a>
    <div class="j-header">
      <span class="pill ${j.status_css}">${esc(j.status_display)}</span>
      <span class="pill" style="margin-left:0.35rem;">${esc(j.kind)}</span>
      <h1>${esc(j.name)} <span style="color:var(--muted); font-weight:400; font-size:1rem;">(${esc(j.code)})</span></h1>
      <p class="summary">${esc(j.summary)}</p>
      <p class="meta-line" style="margin-top:0.75rem;">Last reviewed: ${esc(j.last_reviewed || "—")}</p>
    </div>`;

    if (j.notes) {
      html += `<div class="notes"><strong>Notes:</strong> ${esc(j.notes)}</div>`;
    }

    html += `<h3 class="block-title">Obligations</h3>`;
    const obligations = detail.obligations || [];
    if (obligations.length) {
      for (const o of obligations) {
        const rm = relMeta(o.voice_cs_relevance);
        html += `<div class="obl">
          <h4>${esc(o.title)}</h4>
          <div class="meta">
            <span class="pill ${rm.css}">Voice/conversation: ${esc(rm.label)}</span>
            <span>Status: ${esc(o.status)}</span>
            ${o.effective_date ? `<span>Effective: ${esc(o.effective_date)}</span>` : ""}
          </div>
          <p>${esc(o.summary)}</p>`;
        if (o.voice_cs_why) {
          html += `<p class="why"><strong>Why it matters:</strong> ${esc(o.voice_cs_why)}</p>`;
        }
        if (o.themes && o.themes.length) {
          html += `<div class="themes">`;
          for (const t of o.themes) {
            html += `<span class="theme-tag">${esc(t)}</span>`;
          }
          html += `</div>`;
        }
        if (o.sources && o.sources.length) {
          html += `<ul class="sources">`;
          for (const s of o.sources) {
            html += `<li><a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.label)}</a></li>`;
          }
          html += `</ul>`;
        }
        html += `</div>`;
      }
    } else {
      html += `<p class="empty">No specific obligations tracked yet for this jurisdiction.</p>`;
    }

    const jSources = (detail.sources || []).filter((s) => !s.obligation_id);
    if (jSources.length) {
      html += `<h3 class="block-title">Jurisdiction sources</h3><ul class="sources">`;
      for (const s of jSources) {
        html += `<li><a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.label)}</a></li>`;
      }
      html += `</ul>`;
    }

    html += `<h3 class="block-title">History</h3>`;
    const history = detail.history || [];
    if (history.length) {
      html += `<ul class="timeline">`;
      for (const h of history) {
        html += `<li>
          <div class="date">${esc(h.event_date)}</div>
          <div class="title">${esc(h.title)}</div>
          ${h.detail ? `<div class="detail">${esc(h.detail)}</div>` : ""}
          ${h.source_url ? `<div class="detail"><a href="${esc(h.source_url)}" target="_blank" rel="noopener noreferrer">Source</a></div>` : ""}
        </li>`;
      }
      html += `</ul>`;
    } else {
      html += `<p class="empty">No history events yet.</p>`;
    }

    document.getElementById("app").innerHTML = html;
  }

  function renderAbout() {
    setNav("about");
    document.title = "About · US AI Reg Tracker";
    document.getElementById("app").innerHTML = `
      <h2 style="margin-top:0;">About</h2>
      <div class="about-body">
        <p>
          This is an <strong>operational briefing</strong> on US AI regulation that may affect
          voice/conversation AI operators, customer-service bots, and phone AI — including
          disclosure, TCPA synthetic-voice, ADMT, and related themes. It is
          <strong>not legal advice</strong>. Status labels and summaries are curated for product
          and compliance awareness; always confirm against primary sources before decisions.
        </p>
        <p>
          Data is updated periodically. Each jurisdiction page links to primary sources
          (statutes, bill pages, agency materials). Federal coverage appears as its own card;
          states and DC are on the map and list below.
        </p>
        <p style="margin-bottom:0; font-size:0.85rem;">
          Last global refresh: ${esc(DATA.last_global_refresh || "—")}
        </p>
      </div>`;
  }

  function render() {
    if (!DATA) return;
    const route = parseRoute();
    if (route.page === "home") renderHome(route.filter);
    else if (route.page === "about") renderAbout();
    else if (route.page === "jurisdiction") renderJurisdiction(route.code);
    else {
      setNav("home");
      document.getElementById("app").innerHTML =
        `<p class="empty">Page not found. <a href="#/">Go home</a></p>`;
    }
    window.scrollTo(0, 0);
  }

  async function boot() {
    const el = document.getElementById("app");
    try {
      const res = await fetch("data/all.json", { cache: "no-cache" });
      if (!res.ok) throw new Error("HTTP " + res.status);
      DATA = await res.json();
      render();
    } catch (err) {
      el.innerHTML = `<p class="empty">Failed to load data/all.json (${esc(err.message)}).
        Run <code>python scripts/export_static.py</code> then open via a local server or GitHub Pages.</p>`;
    }
  }

  window.addEventListener("hashchange", render);
  boot();
})();
