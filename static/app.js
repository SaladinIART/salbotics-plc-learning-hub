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

function ensureBitRow(container, name, writable) {
  let row = container.querySelector(`[data-bit-row="${name}"]`);
  if (row) return row;

  row = document.createElement("div");
  row.className = "bit-row";
  row.dataset.bitRow = name;

  const pilot = document.createElement("span");
  pilot.className = `pilot ${OUTPUT_COLORS[name] || ""}`;
  pilot.dataset.pilot = name;

  const label = document.createElement("div");
  label.innerHTML = `<div class="bit-name">${name}</div><div class="bit-desc">${INPUT_DESCRIPTIONS[name] || "PLC output coil"}</div>`;

  row.append(pilot, label);

  if (writable) {
    const button = document.createElement("button");
    button.className = "bit-toggle";
    button.type = "button";
    button.dataset.input = name;
    button.addEventListener("click", () => {
      const current = Boolean(latestState?.inputs?.[name]);
      setInput(name, !current).catch(showError);
    });
    row.append(button);
  } else {
    const state = document.createElement("strong");
    state.className = "bit-desc";
    state.dataset.outputState = name;
    row.append(state);
  }

  container.append(row);
  return row;
}

function renderBits(bits, containerId, writable) {
  const container = qs(containerId);
  Object.entries(bits).forEach(([name, value]) => {
    const row = ensureBitRow(container, name, writable);
    row.querySelector("[data-pilot]").classList.toggle("on", value);
    const button = row.querySelector("[data-input]");
    if (button) {
      button.classList.toggle("on", value);
      button.textContent = value ? "ON" : "OFF";
      button.setAttribute("aria-pressed", String(value));
    }
    const state = row.querySelector("[data-output-state]");
    if (state) {
      state.textContent = value ? "ENERGIZED" : "OFF";
    }
  });
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
  qs("#scan-value").textContent = String(timers.scan_count);
}

function render(state) {
  latestState = state;
  qs("#mode-value").textContent = state.mode.toUpperCase();
  qs("#phase-value").textContent = state.phase;
  renderTimers(state.timers);
  renderBits(state.inputs, "#input-list", true);
  renderBits(state.outputs, "#output-list", false);
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

window.addEventListener("beforeunload", () => {
  if (pollHandle) window.clearInterval(pollHandle);
});

