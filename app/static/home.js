/* Home page: search + activity chart (Chart.js CDN) */
(function () {
  "use strict";

  function initChart() {
    var canvas = document.getElementById("activity-chart");
    if (!canvas || typeof Chart === "undefined") return;
    var data = window.TRACKER_ACTIVITY || [];
    if (!data.length) {
      canvas.parentElement.insertAdjacentHTML(
        "beforeend",
        '<p class="empty">No dated activity yet.</p>'
      );
      return;
    }
    new Chart(canvas.getContext("2d"), {
      type: "bar",
      data: {
        labels: data.map(function (d) { return d.month; }),
        datasets: [{
          label: "Events / effective dates",
          data: data.map(function (d) { return d.count; }),
          backgroundColor: "rgba(91, 159, 212, 0.55)",
          borderColor: "rgba(91, 159, 212, 0.95)",
          borderWidth: 1,
          borderRadius: 3,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: { display: false },
          title: { display: false },
        },
        scales: {
          x: {
            ticks: { color: "#8b9bb4", maxRotation: 45, minRotation: 0, autoSkip: true, maxTicksLimit: 12 },
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
  }

  function initSearch() {
    var input = document.getElementById("search-box");
    var results = document.getElementById("search-results");
    var index = window.TRACKER_SEARCH || [];
    if (!input || !results) return;

    function clearHighlights() {
      document.querySelectorAll(".us-map .state.hit, .state-tile.hit, .federal-card.hit").forEach(function (el) {
        el.classList.remove("hit");
      });
    }

    function highlight(codes) {
      clearHighlights();
      codes.forEach(function (code) {
        document.querySelectorAll('[data-code="' + code + '"]').forEach(function (el) {
          el.classList.add("hit");
        });
      });
    }

    function run() {
      var q = (input.value || "").trim().toLowerCase();
      if (!q) {
        results.hidden = true;
        results.innerHTML = "";
        clearHighlights();
        return;
      }
      var matches = index.filter(function (item) {
        return item.text.indexOf(q) !== -1 ||
          item.code.toLowerCase().indexOf(q) !== -1 ||
          item.name.toLowerCase().indexOf(q) !== -1;
      }).slice(0, 12);

      highlight(matches.map(function (m) { return m.code; }));

      if (!matches.length) {
        results.innerHTML = '<div class="search-empty">No matches</div>';
        results.hidden = false;
        return;
      }
      results.innerHTML = matches.map(function (m) {
        var href = "/j/" + encodeURIComponent(m.code);
        return '<a class="search-item" href="' + href + '"><strong>' +
          m.code + '</strong> ' + m.name +
          ' <span class="muted">' + m.status_label + '</span></a>';
      }).join("");
      results.hidden = false;
    }

    input.addEventListener("input", run);
    input.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        input.value = "";
        run();
        input.blur();
      }
    });
    document.addEventListener("click", function (e) {
      if (!results.contains(e.target) && e.target !== input) {
        results.hidden = true;
      }
    });
  }



  var LABEL_NUDGE = {
    RI: [14, 2], DE: [14, 2], CT: [2, 3], NJ: [12, 2], MD: [14, 8],
    DC: [16, 10], MA: [8, 0], NH: [10, -2], VT: [-2, 2],
    FL: [10, 12], LA: [-2, 10], MI: [10, 18], AK: [18, -8], HI: [0, 2],
    ID: [0, 8], NV: [2, 6], CA: [-4, 8], WV: [2, 4]
  };

  function addStateLabels(svg) {
    var NS = "http://www.w3.org/2000/svg";
    var layer = document.createElementNS(NS, "g");
    layer.setAttribute("class", "state-labels");
    layer.setAttribute("pointer-events", "none");
    var nodes = svg.querySelectorAll(":scope > [data-code]");
    nodes.forEach(function (el) {
      var code = (el.getAttribute("data-code") || "").toUpperCase();
      if (!code) return;
      var box;
      try { box = el.getBBox(); } catch (err) { return; }
      if (!box.width && !box.height) return;
      var x = box.x + box.width / 2;
      var y = box.y + box.height / 2;
      var n = LABEL_NUDGE[code];
      if (n) { x += n[0]; y += n[1]; }
      var text = document.createElementNS(NS, "text");
      text.setAttribute("x", String(x));
      text.setAttribute("y", String(y));
      text.setAttribute("class", "state-abbr");
      text.setAttribute("text-anchor", "middle");
      text.setAttribute("dominant-baseline", "middle");
      text.textContent = code;
      layer.appendChild(text);
    });
    svg.appendChild(layer);
  }

  function mountUsMap() {
    var panel = document.getElementById("us-map");
    var byCode = window.TRACKER_MAP || {};
    if (!panel) return;

    function apply(svgRoot) {
      svgRoot.classList.add("us-map");
      svgRoot.removeAttribute("width");
      svgRoot.removeAttribute("height");
      var nodes = svgRoot.querySelectorAll(":scope > [data-code]");
      nodes.forEach(function (el) {
        var code = (el.getAttribute("data-code") || "").toUpperCase();
        var meta = byCode[code];
        if (!meta) return;
        if (meta.status_css) el.classList.add(meta.status_css);
        el.setAttribute("data-code", code);
        var tip = (meta.name || code) + " — " + (meta.status_display || "");
        el.setAttribute("title", tip);
        el.setAttribute("aria-label", tip);
        el.setAttribute("tabindex", "0");
        el.setAttribute("role", "link");
        var go = function () {
          window.location.href = "/j/" + encodeURIComponent(code);
        };
        el.addEventListener("click", function (ev) {
          ev.preventDefault();
          go();
        });
        el.addEventListener("keydown", function (ev) {
          if (ev.key === "Enter" || ev.key === " ") {
            ev.preventDefault();
            go();
          }
        });
      });
      addStateLabels(svgRoot);
    }

    fetch("/static/us-states.svg", { cache: "force-cache" })
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.text();
      })
      .then(function (svgText) {
        panel.innerHTML = svgText;
        var svg = panel.querySelector("svg");
        if (!svg) throw new Error("SVG missing");
        apply(svg);
      })
      .catch(function (err) {
        panel.innerHTML = '<p class="map-loading">Map failed to load (' +
          String(err.message || err) + ').</p>';
      });
  }

  function boot() {
    mountUsMap();
    initSearch();
    if (typeof Chart !== "undefined") initChart();
    else {
      // Chart.js defer — wait briefly
      var n = 0;
      var t = setInterval(function () {
        n += 1;
        if (typeof Chart !== "undefined") {
          clearInterval(t);
          initChart();
        } else if (n > 40) clearInterval(t);
      }, 50);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
