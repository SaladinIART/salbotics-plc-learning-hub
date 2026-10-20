const qs = (selector) => document.querySelector(selector);

const metrics = [
  { id: "oer_percent", title: "OER", unit: "%" },
  { id: "press_current_a", title: "Press Current", unit: "A" },
  { id: "tank_level_percent", title: "CPO Tank Level", unit: "%" },
];

const fallbackArchitectureLayers = [
  {
    layer: "OT",
    meaning: "PLC, VFD, HMI, SCADA, sensors, actuators, and local machine control.",
    dashboard_value: "Shows what the plant is doing now.",
  },
  {
    layer: "IT",
    meaning: "Server, database, backup, browser access, and user accounts.",
    dashboard_value: "Keeps data available after the machine event has passed.",
  },
  {
    layer: "MES",
    meaning: "Shift, batch, production order, downtime reason, and performance tracking.",
    dashboard_value: "Turns plant data into production context.",
  },
  {
    layer: "ERP",
    meaning: "Inventory, costing, purchasing, sales, and management reporting.",
    dashboard_value: "Connects production reality to business decisions.",
  },
];

function formatValue(value) {
  if (typeof value !== "number") {
    return value;
  }
  return Number.isInteger(value) ? value.toString() : value.toFixed(1);
}

async function loadJson(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`${url} returned HTTP ${response.status}`);
  }
  return response.json();
}

function renderCards(cards) {
  qs("#management-cards").innerHTML = cards
    .map(
      (card) => `
        <article class="analytics-kpi-card ${card.status}">
          <span>${card.label}</span>
          <strong>${formatValue(card.value)}</strong>
          <b>${card.unit}</b>
          <p>${card.explanation}</p>
        </article>
      `,
    )
    .join("");
}

function renderStations(stations) {
  qs("#station-states").innerHTML = stations
    .map(
      (station) => `
        <div class="station-state-row">
          <strong>${station.name}</strong>
          <span>${station.state}</span>
          <p>${station.business_meaning}</p>
        </div>
      `,
    )
    .join("");
}

function renderPress(press) {
  qs("#press-deep-dive").innerHTML = `
    <div><span>Motor current</span><strong>${formatValue(press.motor_current_a)} A</strong></div>
    <div><span>Load</span><strong>${formatValue(press.load_percent)}%</strong></div>
    <div><span>Vibration</span><strong>${formatValue(press.vibration_mm_s)} mm/s</strong></div>
    <div><span>Output flow</span><strong>${formatValue(press.output_flow_tph)} t/h</strong></div>
    <p>${press.maintenance_hint}</p>
  `;
}

function renderArchitecture(layers) {
  qs("#architecture-table").innerHTML = layers
    .map(
      (layer) => `
        <tr>
          <th>${layer.layer}</th>
          <td>${layer.meaning}</td>
          <td>${layer.dashboard_value}</td>
        </tr>
      `,
    )
    .join("");
}

function renderEvents(events) {
  if (!events.length) {
    qs("#event-table").innerHTML = `
      <tr>
        <td colspan="5">No historian events yet. The collector will add events as simulated plant time advances.</td>
      </tr>
    `;
    return;
  }

  qs("#event-table").innerHTML = events
    .map(
      (event) => `
        <tr>
          <td>${new Date(event.timestamp).toLocaleTimeString()}</td>
          <td>${event.severity}</td>
          <td>${event.source}</td>
          <td>${event.message}</td>
          <td>${event.detail}</td>
        </tr>
      `,
    )
    .join("");
}

function pointsToPolyline(points, width, height) {
  if (points.length === 0) {
    return "";
  }
  const values = points.map((point) => point.value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  return points
    .map((point, index) => {
      const x = points.length === 1 ? width : (index / (points.length - 1)) * width;
      const y = height - ((point.value - min) / range) * height;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
}

async function renderTrend(metric) {
  const trend = await loadJson(`/api/analytics/trends?metric=${metric.id}&minutes=60`);
  const latest = trend.points.at(-1)?.value ?? 0;
  const polyline = pointsToPolyline(trend.points, 300, 96);
  qs(`#trend-${metric.id}`).innerHTML = `
    <div class="trend-head">
      <span>${metric.title}</span>
      <strong>${formatValue(latest)} ${trend.unit || metric.unit}</strong>
    </div>
    <svg viewBox="0 0 300 110" role="img" aria-label="${metric.title} trend">
      <line x1="0" y1="96" x2="300" y2="96"></line>
      <polyline points="${polyline}"></polyline>
    </svg>
  `;
}

function renderTrendFallback(metric) {
  qs(`#trend-${metric.id}`).innerHTML = `
    <div class="trend-head">
      <span>${metric.title}</span>
      <strong>NO DATA</strong>
    </div>
    <div class="trend-placeholder">
      Restart the local FastAPI server so the Phase 3 analytics endpoints can feed this chart.
    </div>
  `;
}

function renderApiError(error) {
  const detail = error instanceof Error ? error.message : "Unknown analytics API error";
  console.error("Phase 3 analytics failed to load:", error);

  qs("#storage-status").textContent = "ANALYTICS API UNAVAILABLE";
  qs("#generated-at").textContent = "restart server";
  qs("#management-cards").innerHTML = `
    <article class="analytics-kpi-card alarm analytics-wide-card">
      <span>Dashboard data not loaded</span>
      <strong>NO DATA</strong>
      <b>API OFFLINE</b>
      <p>
        The page loaded, but the running server did not answer the Phase 3 API.
        Close the old launcher/server and start it again so /api/analytics/* routes are active.
      </p>
      <p class="analytics-error-detail">${detail}</p>
    </article>
  `;
  metrics.forEach(renderTrendFallback);
  qs("#event-table").innerHTML = `
    <tr class="event-error-row">
      <td>--</td>
      <td>ERROR</td>
      <td>Phase 3 API</td>
      <td>No analytics data returned</td>
      <td>${detail}</td>
    </tr>
  `;
  qs("#station-states").innerHTML = `
    <div class="station-state-row">
      <strong>No live station data</strong>
      <span>API OFFLINE</span>
      <p>Restart the local app to load simulated oil-palm station states.</p>
    </div>
  `;
  qs("#press-deep-dive").innerHTML = `
    <p class="analytics-error-detail">
      Screw press values come from the local SQLite historian API. They will appear after the current server is restarted.
    </p>
  `;
  renderArchitecture(fallbackArchitectureLayers);
}

async function refreshDashboard() {
  try {
    const [summary, events] = await Promise.all([
      loadJson("/api/analytics/summary"),
      loadJson("/api/analytics/events?limit=12"),
    ]);

    qs("#storage-status").textContent = `${summary.storage.engine} historian - ${summary.storage.sample_count} samples`;
    qs("#generated-at").textContent = new Date(summary.generated_at).toLocaleTimeString();
    renderCards(summary.management_cards);
    renderStations(summary.station_states);
    renderPress(summary.screw_press);
    renderArchitecture(summary.architecture_layers);
    renderEvents(events.events);
    await Promise.all(metrics.map(renderTrend));
  } catch (error) {
    renderApiError(error);
  }
}

async function resetDashboard() {
  const button = qs("#reset-analytics");
  button.disabled = true;
  button.textContent = "RESETTING";
  try {
    await loadJson("/api/analytics/reset", { method: "POST" });
    await refreshDashboard();
  } catch (error) {
    renderApiError(error);
  } finally {
    button.textContent = "RESET DEMO DATA";
    button.disabled = false;
  }
}


// The public website has no trainer server behind it. There, show a calm
// preview message instead of polling an API that does not exist.
function onTrainerPage() {
  const path = location.pathname;
  return /^\/static\//.test(path) || !/(\.html|\/)$/.test(path);
}

const PREVIEW_NOTE = "Live numbers appear when you run the free Windows trainer. This website shows the layout only.";

function renderWebsitePreview() {
  qs("#storage-status").textContent = "Preview: runs in the trainer";
  qs("#generated-at").textContent = "not running here";
  qs("#reset-analytics").hidden = true;
  qs("#management-cards").innerHTML = `
    <article class="analytics-kpi-card analytics-wide-card">
      <span>Dashboard preview</span>
      <strong>Live in the trainer</strong>
      <p>${PREVIEW_NOTE}</p>
    </article>
  `;
  metrics.forEach((metric) => {
    const panel = qs(`#trend-${metric.id}`);
    if (!panel) return;
    panel.innerHTML = `
      <div class="trend-head"><span>${metric.title}</span><strong>Preview</strong></div>
      <div class="trend-placeholder">This chart fills in when the trainer is running.</div>
    `;
  });
  qs("#event-table").innerHTML = `
    <tr><td>--</td><td>INFO</td><td>Website preview</td><td>Events appear in the trainer</td><td>${PREVIEW_NOTE}</td></tr>
  `;
  qs("#station-states").innerHTML = `
    <div class="station-state-row"><strong>Station states</strong><span>PREVIEW</span><p>Shown live in the trainer.</p></div>
  `;
  qs("#press-deep-dive").innerHTML = `<p>Screw press values are shown live in the trainer.</p>`;
  renderArchitecture(fallbackArchitectureLayers);
}

qs("#reset-analytics").addEventListener("click", resetDashboard);
if (onTrainerPage()) {
  refreshDashboard();
  setInterval(refreshDashboard, 5000);
} else {
  renderWebsitePreview();
}
