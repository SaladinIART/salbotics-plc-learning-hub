const INPUT_DESCRIPTIONS = {
  START: "Start pushbutton contact",
  STOP: "Stop pushbutton contact",
  PED_NS: "Pedestrian request for NS phase",
  PED_EW: "Pedestrian request for EW phase",
  VEHICLE_NS: "Vehicle sensor on NS road",
  VEHICLE_EW: "Vehicle sensor on EW road",
  EMERGENCY: "Emergency override input",
  NIGHT_MODE: "Night red-flash selector",
};

const OUTPUT_COLORS = {
  NS_RED: "red",
  NS_YELLOW: "yellow",
  NS_GREEN: "green",
  EW_RED: "red",
  EW_YELLOW: "yellow",
  EW_GREEN: "green",
};

let latestState = null;
let pollHandle = null;

function qs(selector) {
  return document.querySelector(selector);
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return response.json();
}

async function setInput(name, value) {
  latestState = await api(`/api/inputs/${name}`, {
    method: "POST",
    body: JSON.stringify({ value }),
  });
  render(latestState);
}

async function runCommand(command) {
  latestState = await api(`/api/commands/${command}`, { method: "POST" });
  render(latestState);
}

function fallbackRows(bits) {
  return Object.entries(bits).map(([name, value]) => ({
    address: name,
    name,
    description: INPUT_DESCRIPTIONS[name] || "PLC output coil",
    state: value,
    state_text: value ? "1" : "0",
  }));
}

function renderIoRows(rows, containerId, writable) {
  const container = qs(containerId);
  container.innerHTML = `
    <div class="io-row io-head">
      <span>Addr</span>
      <span>Name</span>
      <span>Desc</span>
      <span>State</span>
    </div>
  `;
  rows.forEach((bit) => {
    const row = document.createElement("div");
    row.className = `io-row ${bit.state ? "on" : ""}`;
    const pilotColor = OUTPUT_COLORS[bit.name] || "";
    const stateControl = writable
      ? `<button class="bit-toggle ${bit.state ? "on" : ""}" type="button" data-input="${bit.name}" aria-pressed="${bit.state}">${bit.state ? "1 / ON" : "0 / OFF"}</button>`
      : `<span class="io-state ${bit.state ? "on" : ""}">${bit.state ? "1" : "0"}</span>`;
    row.innerHTML = `
      <span class="io-address">${bit.address}</span>
      <span class="io-name"><i class="pilot ${pilotColor} ${bit.state ? "on" : ""}"></i>${bit.name}</span>
      <span class="io-desc">${bit.description}</span>
      ${stateControl}
    `;
    container.append(row);
  });

  if (writable) {
    container.querySelectorAll("[data-input]").forEach((button) => {
      button.addEventListener("click", () => {
        const name = button.dataset.input;
        const current = Boolean(latestState?.inputs?.[name]);
        setInput(name, !current).catch(showError);
      });
    });
  }
}

function renderRegisters(registers) {
  const container = qs("#register-list");
  container.innerHTML = "";
  Object.entries(registers).forEach(([name, value]) => {
    const row = document.createElement("div");
    row.className = "register-row";
    row.innerHTML = `<b>${name}</b><span class="state ${value ? "on" : ""}">${value ? "ON" : "OFF"}</span>`;
    container.append(row);
  });
}

function renderRegisterRows(rows, fallbackRegisters) {
  if (!rows) {
    renderRegisters(fallbackRegisters);
    return;
  }
  const container = qs("#register-list");
  container.innerHTML = `
    <div class="data-row data-head register-data-row">
      <span>Addr</span>
      <span>Name</span>
      <span>Type</span>
      <span>Dec</span>
      <span>Hex</span>
      <span>Description</span>
    </div>
  `;
  rows.forEach((register) => {
    const row = document.createElement("div");
    row.className = "data-row register-data-row";
    row.innerHTML = `
      <span class="data-address">${register.address}</span>
      <span class="data-name">${register.name}</span>
      <span>${register.type}</span>
      <span>${register.value_dec}</span>
      <span>${register.value_hex}</span>
      <span class="data-desc">${register.description}</span>
    `;
    container.append(row);
  });
}

function renderTimerRows(rows) {
  const container = qs("#timer-table");
  if (!rows) {
    container.innerHTML = "";
    return;
  }
  container.innerHTML = `
    <div class="data-row data-head timer-data-row">
      <span>Addr</span>
      <span>Name</span>
      <span>Type</span>
      <span>Preset</span>
      <span>Accum</span>
      <span>Status</span>
    </div>
  `;
  rows.forEach((timer) => {
    const row = document.createElement("div");
    row.className = `data-row timer-data-row ${timer.status !== "-" ? "active" : ""}`;
    row.innerHTML = `
      <span class="data-address">${timer.address}</span>
      <span class="data-name">${timer.name}</span>
      <span>${timer.type}</span>
      <span>${timer.preset_s.toFixed(1)}</span>
      <span>${timer.accum_s.toFixed(1)}</span>
      <span class="status-chip ${timer.status === "DN" ? "done" : timer.status === "EN" ? "enabled" : ""}">${timer.status}</span>
    `;
    container.append(row);
  });
}

function renderRungs(rungs) {
  const container = qs("#rung-list");
  container.innerHTML = "";
  rungs.forEach((rung) => {
    const match = rung.name.match(/^RUNG\s+(\d+)\s+(.+)$/);
    const number = match ? match[1] : "---";
    const title = match ? match[2] : rung.name;
    const circuit = rungCircuit(title);
    const row = document.createElement("div");
    row.className = `rung-row ${rung.energized ? "on" : ""}`;
    row.innerHTML = `
      <span class="rung-number">${number}</span>
      <div class="rung-circuit">
        <span class="rail"></span>
        ${circuit.contacts.map((contact) => `<span class="contact ${contact.closed ? "closed" : ""}">${contact.label}</span>`).join("")}
        <span class="coil ${rung.energized ? "on" : ""}">${circuit.coil}</span>
      </div>
      <div>
        <div class="rung-title">${title}</div>
        <div class="rung-desc">${rung.description}</div>
      </div>
      <span class="rung-power ${rung.energized ? "on" : ""}">${rung.energized ? "EN" : "OFF"}</span>
    `;
    container.append(row);
  });
}

function rungCircuit(title) {
  const circuits = {
    "RUN LATCH": {
      contacts: [
        { label: "START", closed: Boolean(latestState?.inputs?.START) },
        { label: "/STOP", closed: !latestState?.inputs?.STOP },
        { label: "/FAULT", closed: !latestState?.registers?.FAULT_ACTIVE },
      ],
      coil: "RUN_LATCH",
    },
    "STOP SAFE": {
      contacts: [
        { label: "STOP", closed: Boolean(latestState?.inputs?.STOP) },
        { label: "/RUN", closed: !latestState?.registers?.RUN_LATCH },
      ],
      coil: "ALL_RED",
    },
    EMERGENCY: {
      contacts: [{ label: "EMERGENCY", closed: Boolean(latestState?.inputs?.EMERGENCY) }],
      coil: "ALL_RED",
    },
    "NIGHT FLASH": {
      contacts: [{ label: "NIGHT_MODE", closed: Boolean(latestState?.inputs?.NIGHT_MODE) }],
      coil: "FLASH_RED",
    },
    "NS GREEN": {
      contacts: [
        { label: "PHASE_NS", closed: latestState?.phase === "NS_GREEN" },
        { label: "/EW_GREEN", closed: !latestState?.outputs?.EW_GREEN },
      ],
      coil: "NS_GREEN",
    },
    "EW GREEN": {
      contacts: [
        { label: "PHASE_EW", closed: latestState?.phase === "EW_GREEN" },
        { label: "/NS_GREEN", closed: !latestState?.outputs?.NS_GREEN },
      ],
      coil: "EW_GREEN",
    },
    "GREEN CONFLICT CHECK": {
      contacts: [
        { label: "/GREEN_PAIR", closed: !(latestState?.outputs?.NS_GREEN && latestState?.outputs?.EW_GREEN) },
      ],
      coil: "OK",
    },
  };
  return circuits[title] || { contacts: [{ label: "LOGIC", closed: false }], coil: title };
}

function renderField(outputs, inputs) {
  document.querySelectorAll("[data-field-lamp]").forEach((lamp) => {
    lamp.classList.toggle("on", Boolean(outputs[lamp.dataset.fieldLamp]));
  });
  document.querySelectorAll("[data-field-input]").forEach((marker) => {
    marker.classList.toggle("active", Boolean(inputs[marker.dataset.fieldInput]));
  });
}

function renderAlarms(alarms) {
  const container = qs("#alarm-list");
  container.innerHTML = "";
  if (!alarms.length) {
    const empty = document.createElement("div");
    empty.className = "alarm empty";
    empty.textContent = "No active alarms";
    container.append(empty);
    return;
  }
  alarms.forEach((alarm) => {
    const item = document.createElement("div");
    item.className = "alarm";
    item.textContent = alarm;
    container.append(item);
  });
}

function renderEvents(events) {
  const container = qs("#event-log");
  container.innerHTML = `
    <div class="event-row event-head">
      <span>Time</span>
      <span>Type</span>
      <span>Source</span>
      <span>Message</span>
      <span>Details</span>
    </div>
  `;
  events.slice(0, 40).forEach((event) => {
    const row = document.createElement("div");
    row.className = "event-row";
    row.innerHTML = `
      <span class="event-time">${event.time_s.toFixed(1)}s</span>
      <span class="event-kind">${event.kind}</span>
      <span>${event.kind.toUpperCase()}</span>
      <span>${event.message}</span>
      <span>${latestState?.phase || "--"}</span>
    `;
    container.append(row);
  });
}

function renderAlarmSummary(summary) {
  const container = qs("#alarm-summary");
  if (!summary) {
    container.innerHTML = "";
    return;
  }
  container.innerHTML = `
    <div class="summary-card alarm-count"><span>Alarms</span><strong>${summary.alarms}</strong></div>
    <div class="summary-card warning-count"><span>Warnings</span><strong>${summary.warnings}</strong></div>
    <div class="summary-card event-count"><span>Events</span><strong>${summary.events}</strong></div>
    <div class="summary-card total-count"><span>Total</span><strong>${summary.total}</strong></div>
  `;
}

function renderTimers(timers) {
  qs("#scan-time-header").textContent = `${timers.scan_interval_ms}ms`;
  qs("#scan-value").textContent = String(timers.scan_count);
}

function formatStatusLabel(value) {
  return String(value).replaceAll("_", " ");
}

function renderClock() {
  const now = new Date();
  qs("#clock-value").textContent = now.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function render(state) {
  latestState = state;
  document.body.dataset.mode = state.mode;
  document.body.dataset.phase = state.phase;
  document.body.dataset.warning = state.registers.VEHICLE_EXTENSION_ACTIVE ? "true" : "false";
  qs("#mode-value").textContent = formatStatusLabel(state.mode).toUpperCase();
  qs("#phase-value").textContent = formatStatusLabel(state.phase);
  qs("#night-value").textContent = state.inputs.NIGHT_MODE ? "ON" : "OFF";
  qs("#plc-status").textContent = state.registers.FAULT_ACTIVE ? "PLC FAULT" : "PLC CONNECTED";
  renderClock();
  renderTimers(state.timers);
  renderTimerRows(state.timer_rows);
  renderIoRows(state.input_rows || fallbackRows(state.inputs), "#input-list", true);
  renderIoRows(state.output_rows || fallbackRows(state.outputs), "#output-list", false);
  renderRegisterRows(state.register_rows, state.registers);
  renderRungs(state.ladder_rungs);
  renderField(state.outputs, state.inputs);
  renderAlarms(state.alarms);
  renderAlarmSummary(state.alarm_summary);
  renderEvents(state.event_log);
}

function showError(error) {
  console.error(error);
  const container = qs("#alarm-list");
  const item = document.createElement("div");
  item.className = "alarm";
  item.textContent = `Browser/API error: ${error.message}`;
  container.prepend(item);
}

async function poll() {
  try {
    const state = await api("/api/state");
    render(state);
  } catch (error) {
    showError(error);
  }
}

document.querySelectorAll("[data-command]").forEach((button) => {
  button.addEventListener("click", () => {
    runCommand(button.dataset.command).catch(showError);
  });
});

poll();
pollHandle = window.setInterval(poll, 500);
window.setInterval(renderClock, 1000);

window.addEventListener("beforeunload", () => {
  if (pollHandle) window.clearInterval(pollHandle);
});
