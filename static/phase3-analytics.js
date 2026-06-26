const qs = (selector) => document.querySelector(selector);

const metrics = [
  { id: "oer_percent", title: "OER", unit: "%" },
  { id: "press_current_a", title: "Press Current", unit: "A" },
  { id: "tank_level_percent", title: "CPO Tank Level", unit: "%" },
];

function formatValue(value) {
  if (typeof value !== "number") {
    return value;
  }
  return Number.isInteger(value) ? value.toString() : value.toFixed(1);
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
  const response = await fetch(`/api/analytics/trends?metric=${metric.id}&minutes=60`);
  const trend = await response.json();
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

async function refreshDashboard() {
  const [summaryResponse, eventsResponse] = await Promise.all([
    fetch("/api/analytics/summary"),
    fetch("/api/analytics/events?limit=12"),
  ]);
  const summary = await summaryResponse.json();
  const events = await eventsResponse.json();

  qs("#storage-status").textContent = `${summary.storage.engine} historian - ${summary.storage.sample_count} samples`;
  qs("#generated-at").textContent = new Date(summary.generated_at).toLocaleTimeString();
  renderCards(summary.management_cards);
  renderStations(summary.station_states);
  renderPress(summary.screw_press);
  renderArchitecture(summary.architecture_layers);
  renderEvents(events.events);
  await Promise.all(metrics.map(renderTrend));
}

async function resetDashboard() {
  const button = qs("#reset-analytics");
  button.disabled = true;
  button.textContent = "RESETTING";
  await fetch("/api/analytics/reset", { method: "POST" });
  await refreshDashboard();
  button.textContent = "RESET DEMO DATA";
  button.disabled = false;
}

qs("#reset-analytics").addEventListener("click", resetDashboard);
refreshDashboard();
setInterval(refreshDashboard, 5000);
