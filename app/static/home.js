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
      document.querySelectorAll(".map-cell.hit, .state-tile.hit, .federal-card.hit").forEach(function (el) {
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

  function boot() {
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
