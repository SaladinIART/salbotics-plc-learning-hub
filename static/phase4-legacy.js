const legacyQs = (selector) => document.querySelector(selector);

function legacyFormat(value) {
  if (typeof value === "number") {
    return Number.isInteger(value) ? value.toString() : value.toFixed(1);
  }
  if (typeof value === "boolean") {
    return value ? "TRUE" : "FALSE";
  }
  return value;
}

let legacyJson = async function (url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`${url} returned HTTP ${response.status}`);
  }
  return response.json();
};

function renderLegacyCards(cards) {
  legacyQs("#legacy-cards").innerHTML = cards
    .map(
      (card) => `
        <article class="analytics-kpi-card ${card.status}">
          <span>${card.label}</span>
          <strong>${legacyFormat(card.value)}</strong>
          <b>${card.unit}</b>
          <p>${card.explanation}</p>
        </article>
      `,
    )
    .join("");
}

function renderLegacyStation(summary) {
  const station = summary.legacy_station;
  const comms = summary.communication;
  legacyQs("#legacy-station").innerHTML = `
    <div><span>Station</span><strong>${station.name}</strong></div>
    <div><span>Legacy HMI</span><strong>${station.legacy_hmi}</strong></div>
    <div><span>Adapter</span><strong>${station.adapter}</strong></div>
    <div><span>Control</span><strong>${station.control_authority}</strong></div>
    <div><span>Transport</span><strong>${comms.transport} ${comms.host}:${comms.port}</strong></div>
    <div><span>Library</span><strong>${comms.modbus_library}</strong></div>
    <div><span>Status</span><strong>${comms.read_status} / ${comms.health}</strong></div>
  `;
}

function renderLegacyWorkflow(workflow) {
  legacyQs("#legacy-workflow").innerHTML = workflow
    .map(
      (item, index) => `
        <article class="legacy-workflow-card">
          <b>${index + 1}</b>
          <h3>${item.step}</h3>
          <p>${item.meaning}</p>
        </article>
      `,
    )
    .join("");
}

function renderLegacyRegisters(registers) {
  legacyQs("#legacy-register-table").innerHTML = registers.rows
    .map(
      (row) => `
        <tr>
          <th>${row.address}</th>
          <td>${row.name}</td>
          <td>${row.raw_value}</td>
          <td>${legacyFormat(row.engineering_value)}</td>
          <td>${row.unit}</td>
          <td>${row.description}</td>
          <td><span class="legacy-readonly">${row.writable ? "WRITE" : "NO"}</span></td>
        </tr>
      `,
    )
    .join("");
}

function renderLegacySituations(situations) {
  legacyQs("#legacy-situations").innerHTML = situations
    .map(
      (item) => `
        <article class="legacy-situation-card">
          <h3>${item.problem}</h3>
          <p>${item.solution}</p>
        </article>
      `,
    )
    .join("");
}

function renderLegacyEvents(events) {
  if (!events.length) {
    legacyQs("#legacy-event-table").innerHTML = `<tr><td colspan="6">No bridge events yet.</td></tr>`;
    return;
  }
  legacyQs("#legacy-event-table").innerHTML = events
    .map(
      (event) => `
        <tr>
          <td>${new Date(event.timestamp).toLocaleTimeString()}</td>
          <td>${event.event_type}</td>
          <td>${event.severity}</td>
          <td>${event.source}</td>
          <td>${event.message}</td>
          <td>${event.detail}</td>
        </tr>
      `,
    )
    .join("");
}

function renderRs232(lesson) {
  legacyQs("#legacy-rs232-card").innerHTML = `
    <h3>Simulated frame settings</h3>
    <div class="mini-table">
      <table>
        <tr><th>Library</th><td>${lesson.library}</td></tr>
        <tr><th>Port</th><td>${lesson.port}</td></tr>
        <tr><th>Baud</th><td>${lesson.baudrate}</td></tr>
        <tr><th>Parity</th><td>${lesson.parity}</td></tr>
        <tr><th>Stop bits</th><td>${lesson.stop_bits}</td></tr>
        <tr><th>Timeout</th><td>${lesson.timeout_seconds}s</td></tr>
        <tr><th>Request</th><td><code>${lesson.sample_frame}</code></td></tr>
        <tr><th>Response</th><td><code>${lesson.sample_response}</code></td></tr>
      </table>
    </div>
    <p>${lesson.meaning}</p>
    <p class="analytics-error-detail">${lesson.warning}</p>
  `;
}

function renderLegacyError(error) {
  const detail = error instanceof Error ? error.message : "Unknown Phase 4 API error";
  console.error("Phase 4 legacy bridge failed to load:", error);
  legacyQs("#legacy-health").textContent = "LEGACY API UNAVAILABLE";
  legacyQs("#legacy-generated-at").textContent = "restart server";
  legacyQs("#legacy-cards").innerHTML = `
    <article class="analytics-kpi-card alarm analytics-wide-card">
      <span>Legacy bridge data not loaded</span>
      <strong>NO DATA</strong>
      <b>API OFFLINE</b>
      <p>Restart the local FastAPI server so /api/legacy/* routes are active.</p>
      <p class="analytics-error-detail">${detail}</p>
    </article>
  `;
}

async function refreshLegacy() {
  try {
    const [summary, registers, events] = await Promise.all([
      legacyJson("/api/legacy/summary"),
      legacyJson("/api/legacy/registers"),
      legacyJson("/api/legacy/events?limit=10"),
    ]);
    legacyQs("#legacy-health").textContent = `${summary.communication.health} - ${summary.communication.quality_percent}% quality`;
    legacyQs("#legacy-generated-at").textContent = new Date(summary.generated_at).toLocaleTimeString();
    renderLegacyCards(summary.headline_cards);
    renderLegacyStation(summary);
    renderLegacyWorkflow(summary.workflow);
    renderLegacyRegisters(registers);
    renderLegacySituations(summary.real_situations);
    renderLegacyEvents(events.events);
    renderRs232(summary.rs232_lesson);
  } catch (error) {
    renderLegacyError(error);
  }
}

async function resetLegacy() {
  const button = legacyQs("#reset-legacy");
  button.disabled = true;
  button.textContent = "RESETTING";
  try {
    await legacyJson("/api/legacy/reset", { method: "POST" });
    await refreshLegacy();
  } catch (error) {
    renderLegacyError(error);
  } finally {
    button.textContent = "RESET LEGACY DEMO";
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

function renderLegacyWebsitePreview() {
  legacyQs("#legacy-health").textContent = "Preview: runs in the trainer";
  legacyQs("#legacy-generated-at").textContent = "not running here";
  legacyQs("#reset-legacy").hidden = true;
  legacyQs("#legacy-cards").innerHTML = `
    <article class="analytics-kpi-card analytics-wide-card">
      <span>Bridge preview</span>
      <strong>Live in the trainer</strong>
      <p>${PREVIEW_NOTE}</p>
    </article>
  `;
  const note = `<p class="legacy-preview-note">This part loads live from the trainer.</p>`;
  ["#legacy-station", "#legacy-workflow", "#legacy-situations", "#legacy-rs232-card"].forEach((id) => {
    legacyQs(id).innerHTML = note;
  });
  legacyQs("#legacy-register-table").innerHTML = `<tr><td colspan="7">Registers are shown live in the trainer.</td></tr>`;
  legacyQs("#legacy-event-table").innerHTML = `<tr><td colspan="6">Bridge events are shown live in the trainer.</td></tr>`;
}

legacyQs("#reset-legacy").addEventListener("click", resetLegacy);
// On the website, draw a sample recorded from the trainer (see
// scripts/build_dashboard_samples.py) with the same rendering code.
async function showLegacyWebsiteSample() {
  try {
    const sample = await (await fetch("sample-legacy.json")).json();
    legacyJson = async (url) => {
      if (!(url in sample)) throw new Error(`no sample for ${url}`);
      return sample[url];
    };
    await refreshLegacy();
    legacyQs("#legacy-health").textContent = "Sample data recorded from the trainer";
    legacyQs("#legacy-generated-at").textContent = "sample, not live";
    legacyQs("#reset-legacy").hidden = true;
  } catch (error) {
    renderLegacyWebsitePreview();
  }
}

if (onTrainerPage()) {
  refreshLegacy();
  setInterval(refreshLegacy, 5000);
} else {
  showLegacyWebsiteSample();
}
