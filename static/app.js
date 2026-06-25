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

function renderRungs(rungs) {
  const container = qs("#rung-list");
  container.innerHTML = "";
  rungs.forEach((rung) => {
    const row = document.createElement("div");
    row.className = "rung-row";
    row.innerHTML = `
      <span class="rung-power ${rung.energized ? "on" : ""}">${rung.energized ? "TRUE" : "FALSE"}</span>
      <div>
        <div class="rung-title">${rung.name}</div>
        <div class="rung-desc">${rung.description}</div>
      </div>
    `;
    container.append(row);
  });
}

function renderField(outputs) {
  const map = {
    "field-ns-red": outputs.NS_RED,
    "field-ns-yellow": outputs.NS_YELLOW,
    "field-ns-green": outputs.NS_GREEN,
    "field-ew-red": outputs.EW_RED,
    "field-ew-yellow": outputs.EW_YELLOW,
    "field-ew-green": outputs.EW_GREEN,
  };
  Object.entries(map).forEach(([id, value]) => {
    qs(`#${id}`).classList.toggle("on", Boolean(value));
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
  container.innerHTML = "";
  events.slice(0, 40).forEach((event) => {
    const row = document.createElement("div");
    row.className = "event-row";
    row.innerHTML = `
      <span class="event-time">${event.time_s.toFixed(1)}s</span>
      <span class="event-kind">${event.kind}</span>
      <span>${event.message}</span>
    `;
    container.append(row);
  });
}

function renderTimers(timers) {
  qs("#elapsed-value").textContent = `${timers.phase_elapsed_s.toFixed(1)}s`;
  qs("#target-value").textContent = `${timers.phase_target_s.toFixed(1)}s`;
  qs("#remaining-value").textContent = `${timers.phase_remaining_s.toFixed(1)}s`;
  qs("#scan-time-value").textContent = `${timers.scan_interval_ms}ms`;
  qs("#scan-time-header").textContent = `${timers.scan_interval_ms}ms`;
  qs("#scan-value").textContent = String(timers.scan_count);
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
  qs("#mode-value").textContent = state.mode.toUpperCase();
  qs("#phase-value").textContent = state.phase;
  qs("#night-value").textContent = state.inputs.NIGHT_MODE ? "ON" : "OFF";
  qs("#plc-status").textContent = state.registers.FAULT_ACTIVE ? "PLC FAULT" : "PLC CONNECTED";
  renderClock();
  renderTimers(state.timers);
  renderIoRows(state.input_rows || fallbackRows(state.inputs), "#input-list", true);
  renderIoRows(state.output_rows || fallbackRows(state.outputs), "#output-list", false);
  renderRegisters(state.registers);
  renderRungs(state.ladder_rungs);
  renderField(state.outputs);
  renderAlarms(state.alarms);
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
