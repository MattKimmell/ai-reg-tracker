/* Ellavox AI Reg Tracker — static SPA (hash routes) */
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

  let DATA = null;

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
      return { page: "home", filter: params.get("filter") || "all" };
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

  function filterJurisdictions(filter) {
    let list = DATA.jurisdictions.slice();
    if (filter === "hot") {
      list = list.filter((j) =>
        j.status_label === "proposed_hot" || j.status_label === "enacted_pending"
      );
    } else if (filter === "in_force") {
      list = list.filter((j) => j.status_label === "in_force");
    } else if (filter === "ellavox") {
      const codes = new Set();
      for (const d of DATA.details) {
        const has = (d.obligations || []).some(
          (o) => o.ellavox_relevance === "high" || o.ellavox_relevance === "medium"
        );
        if (has) codes.add(d.jurisdiction.code);
      }
      list = list.filter((j) => codes.has(j.code));
    }
    return list.map(enrich);
  }

  function renderHome(filter) {
    setNav("home");
    document.title = "US AI Regulation Status · Ellavox";
    const jurisdictions = filterJurisdictions(filter);
    const federal = jurisdictions.filter((j) => j.kind === "federal");
    const states = jurisdictions.filter((j) => j.kind === "state" || j.kind === "local");
    const chips = ["all", "hot", "in_force", "ellavox"];
    const chipLabels = {
      all: "All",
      hot: "Hot",
      in_force: "In force",
      ellavox: "Ellavox-relevant",
    };

    let html = "";
    html += `<p class="meta-line">Last global refresh: <strong>${esc(DATA.last_global_refresh || "—")}</strong>
      · Showing ${jurisdictions.length} jurisdiction${jurisdictions.length !== 1 ? "s" : ""}</p>`;
    html += `<div class="chips">`;
    for (const c of chips) {
      html += `<a class="chip ${filter === c ? "active" : ""}" href="#/?filter=${c}">${chipLabels[c]}</a>`;
    }
    html += `</div>`;
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
        html += `<a class="federal-card ${j.status_css}" href="#/j/${esc(j.code)}" style="display:block; text-decoration:none; color:inherit;">
          <div style="display:flex; flex-wrap:wrap; align-items:center; gap:0.5rem;">
            <h2 style="margin:0;">${esc(j.name)}</h2>
            <span class="pill ${j.status_css}">${esc(j.status_display)}</span>
          </div>
          <p>${esc(j.summary)}</p>
          <p style="font-size:0.8rem; margin-top:0.6rem;">Reviewed ${esc(j.last_reviewed || "—")} →</p>
        </a>`;
      }
    }

    if (states.length) {
      html += `<p class="section-label">States &amp; DC</p><div class="grid">`;
      for (const j of states) {
        html += `<a class="state-tile ${j.status_css}" href="#/j/${esc(j.code)}" title="${esc(j.name)}">
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
  }

  function findDetail(code) {
    return DATA.details.find((d) => d.jurisdiction.code === code) || null;
  }

  function renderJurisdiction(code) {
    setNav("home");
    const detail = findDetail(code);
    if (!detail) {
      document.title = "Not found · Ellavox AI Reg Tracker";
      document.getElementById("app").innerHTML =
        `<a class="back" href="#/">← All jurisdictions</a>
         <p class="empty">Jurisdiction ${esc(code)} not found.</p>`;
      return;
    }
    const j = enrich(detail.jurisdiction);
    document.title = `${j.name} · Ellavox AI Reg Tracker`;

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
        const rm = relMeta(o.ellavox_relevance);
        html += `<div class="obl">
          <h4>${esc(o.title)}</h4>
          <div class="meta">
            <span class="pill ${rm.css}">Ellavox: ${esc(rm.label)}</span>
            <span>Status: ${esc(o.status)}</span>
            ${o.effective_date ? `<span>Effective: ${esc(o.effective_date)}</span>` : ""}
          </div>
          <p>${esc(o.summary)}</p>`;
        if (o.ellavox_why) {
          html += `<p class="why"><strong>Why it matters:</strong> ${esc(o.ellavox_why)}</p>`;
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
    document.title = "About · Ellavox AI Reg Tracker";
    document.getElementById("app").innerHTML = `
      <h2 style="margin-top:0;">About</h2>
      <div class="about-body">
        <p>
          This is an <strong>operational briefing</strong> for Ellavox teams tracking US AI regulation
          that may affect voice AI workers, customer-service bots, and property-management verticals.
          It is <strong>not legal advice</strong>. Status labels and summaries are curated for product
          and GTM awareness; always confirm against primary sources before compliance decisions.
          Data is refreshed by a monthly Grok Bot routine and exported to this static site for GitHub Pages.
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
