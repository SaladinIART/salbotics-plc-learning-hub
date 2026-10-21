// Lesson pages: two small helpers for non-technical readers.
// 1. Tap-to-explain words: the first time a jargon word appears on a page it
//    gets a dotted underline; tapping it shows a one-line plain meaning.
// 2. Phone-friendly tables: each cell learns its column name, so on phones
//    tables turn into stacked cards instead of scrolling sideways (hub.css).
(function () {
  var GLOSSARY = [
    ["PLC", "A tough little computer that controls machines by following written rules."],
    ["PAC", "A more powerful industrial controller, used for large or critical plants."],
    ["HMI", "The screen an operator uses to watch and control one machine."],
    ["SCADA", "Control-room software that watches the whole plant, with alarms and charts."],
    ["VFD", "A motor drive that sets how fast a motor turns."],
    ["FFB", "Fresh fruit bunches: the palm fruit that arrives at the mill."],
    ["CPO", "Crude palm oil: the mill's main product."],
    ["EFB", "Empty fruit bunch: what is left after the fruit is removed."],
    ["POME", "Palm oil mill effluent: the mill's waste water, which must be treated."],
    ["OER", "Oil extraction rate: how much oil the mill gets from the fruit."],
    ["I/O", "Inputs and outputs: what a PLC senses (buttons, sensors) and controls (motors, lamps)."],
    ["NPN", "A sensor wiring type that switches to 0 V. It must match the PLC input wiring."],
    ["PNP", "A sensor wiring type that switches to +24 V. Common on modern PLC inputs."],
    ["4-20mA", "A common smooth signal: 4 mA means the lowest value, 20 mA the highest."],
    ["analog", "A signal that changes smoothly, like temperature, instead of just on or off."],
    ["Ladder", "A PLC programming style that looks like an electrical wiring drawing."],
    ["LAD", "Ladder: a PLC programming style that looks like an electrical wiring drawing."],
    ["FBD", "Function block diagram: a PLC style that connects ready-made blocks."],
    ["SFC", "Sequential function chart: a PLC style for step-by-step sequences."],
    ["interlock", "A rule that blocks an action unless something else is safe or ready."],
    ["permissive", "A condition that must be true before a machine is allowed to start."],
    ["latch", "A memory that stays on after the button is released."],
    ["setpoint", "The target value, such as the temperature you want."],
    ["PID", "Automatic control that holds a value steady, like cruise control in a car."],
    ["E-stop", "The red emergency stop button."],
    ["historian", "A database that records machine values over time."],
    ["Modbus", "A simple, widely used way for machines to exchange numbers."],
    ["OPC UA", "A modern standard way for industrial systems to share data securely."],
    ["MQTT", "A lightweight messaging method often used to send factory data to dashboards."],
    ["RS-232", "An old serial cable link between two devices."],
    ["RS-485", "A serial cable link shared by several devices on one line."],
    ["IIoT", "Industrial internet of things: connected factory sensors and machines."],
    ["MES", "Software that plans and tracks production on the factory floor."],
    ["ERP", "Business software for orders, stock and accounts."],
    ["MCC", "Motor control centre: the cabinet that powers the plant's motors."],
    ["FAT", "Factory acceptance test: proving the system works before delivery."],
    ["SAT", "Site acceptance test: proving the system works once installed on site."],
    ["DOSH", "Malaysia's Department of Occupational Safety and Health."],
    ["SIL", "Safety integrity level: how reliable a safety function must be."],
    ["RTD", "A temperature sensor whose resistance changes with heat."],
    ["watchdog", "A timer that stops the PLC safely if the program gets stuck."],
    ["SQLite", "A small database kept in a single file."]
  ];

  var main = document.querySelector("main");
  if (!main) return;

  // ---------- 1. Tap-to-explain words ----------
  var SKIP = "a, button, code, pre, svg, h1, h2, h3, h4, summary, label, select, script, style, " +
             ".ladder-diagram, .ladder-track, .phase-strip, .term, .term-tip, .hub-progress, .hub-next";
  var ALLOWED = "p, li, td, dd";

  function escapeRe(s) { return s.replace(/[.*+?^${}()|[\]\\/]/g, "\\$&"); }
  var lowercaseWord = function (term) { return term === term.toLowerCase(); };
  function patternFor(term) {
    var flags = lowercaseWord(term) || term === "Ladder" ? "i" : "";
    return new RegExp("(^|[^\\w/-])(" + escapeRe(term) + ")(?![\\w/-])", flags);
  }
  // Meaning in the reader's language (hub-prefs.js); English when no translation.
  function meaning(entry) {
    return window.hubT ? window.hubT("gl." + entry[0], entry[1]) : entry[1];
  }

  var tipCount = 0;

  // Remove earlier marks (after a language switch the text may have changed).
  function unmark() {
    Array.prototype.forEach.call(main.querySelectorAll(".term-tip"), function (tip) {
      tip.parentNode.removeChild(tip);
    });
    Array.prototype.forEach.call(main.querySelectorAll("button.term"), function (button) {
      var parent = button.parentNode;
      parent.replaceChild(document.createTextNode(button.textContent), button);
      parent.normalize();
    });
  }

  function markTerms() {
    unmark();
    var pending = GLOSSARY.slice().sort(function (a, b) { return b[0].length - a[0].length; });
    var walker = document.createTreeWalker(main, NodeFilter.SHOW_TEXT, {
      acceptNode: function (node) {
        var parent = node.parentElement;
        if (!parent || !node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
        if (parent.closest(SKIP) || !parent.closest(ALLOWED)) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    var textNodes = [];
    while (walker.nextNode()) textNodes.push(walker.currentNode);

    textNodes.forEach(function (node) {
      for (var i = 0; i < pending.length && node; i++) {
        var term = pending[i][0];
        var match = patternFor(term).exec(node.nodeValue);
        if (!match) continue;
        var start = match.index + match[1].length;
        var word = match[2];
        var after = node.splitText(start);
        var rest = after.splitText(word.length);
        var button = document.createElement("button");
        button.type = "button";
        button.className = "term";
        button.textContent = word;
        button.setAttribute("aria-expanded", "false");
        var tip = document.createElement("span");
        tip.className = "term-tip";
        tip.id = "term-tip-" + (++tipCount);
        tip.setAttribute("role", "note");
        tip.hidden = true;
        tip.textContent = meaning(pending[i]);
        button.setAttribute("aria-controls", tip.id);
        after.parentNode.replaceChild(button, after);
        button.parentNode.insertBefore(tip, rest);
        pending.splice(i, 1); // only the first use on each page
        i = -1;
        node = rest;          // keep looking for other words after this one
      }
    });
  }

  markTerms();
  document.addEventListener("hub:lang", markTerms);

  main.addEventListener("click", function (event) {
    var button = event.target.closest(".term");
    if (!button) return;
    var tip = document.getElementById(button.getAttribute("aria-controls"));
    var open = button.getAttribute("aria-expanded") !== "true";
    button.setAttribute("aria-expanded", open ? "true" : "false");
    tip.hidden = !open;
  });

  // ---------- 2. Phone-friendly tables ----------
  function labelTable(table) {
    var heads = table.querySelectorAll("thead th");
    if (!heads.length) {
      // Tables without a heading row (label | value, or address | name | meaning): stack each row.
      var rows = table.querySelectorAll("tr");
      var pairs = rows.length && Array.prototype.every.call(rows, function (r) { return r.children.length <= 3; });
      if (pairs) table.classList.add("pairs-on-phone");
      return;
    }
    var names = Array.prototype.map.call(heads, function (th) { return th.textContent.trim(); });
    table.classList.add("stack-on-phone");
    Array.prototype.forEach.call(table.querySelectorAll("tbody tr"), function (row) {
      var col = 0;
      Array.prototype.forEach.call(row.children, function (cell) {
        if (names[col] && !cell.hasAttribute("data-label")) cell.setAttribute("data-label", names[col]);
        col += cell.colSpan || 1;
      });
    });
  }

  Array.prototype.forEach.call(main.querySelectorAll("table"), function (table) {
    labelTable(table);
    // Live dashboards add rows later; label those too.
    var body = table.querySelector("tbody");
    if (body && window.MutationObserver) {
      new MutationObserver(function () { labelTable(table); }).observe(body, { childList: true });
    }
  });

  // ---------- 3. Keyboard access to boxes that scroll sideways ----------
  // A table wider than its box can be scrolled with the arrow keys once it has focus.
  function focusScrollBoxes() {
    Array.prototype.forEach.call(main.querySelectorAll(".mini-table"), function (box) {
      var scrolls = box.scrollWidth > box.clientWidth + 1;
      if (scrolls && !box.hasAttribute("tabindex")) {
        box.setAttribute("tabindex", "0");
        box.setAttribute("role", "region");
        var cap = box.querySelector("caption, th");
        box.setAttribute("aria-label", cap ? cap.textContent.trim() : "Table");
        box.setAttribute("data-scroll-focus", "");
      } else if (!scrolls && box.hasAttribute("data-scroll-focus")) {
        ["tabindex", "role", "aria-label", "data-scroll-focus"].forEach(function (a) { box.removeAttribute(a); });
      }
    });
  }
  focusScrollBoxes();
  window.addEventListener("resize", focusScrollBoxes);
  // Live dashboards (Phase 4) draw their tables after loading data.
  if (window.MutationObserver) {
    var pending = false;
    new MutationObserver(function () {
      if (pending) return;
      pending = true;
      setTimeout(function () { pending = false; focusScrollBoxes(); }, 200);
    }).observe(main, { childList: true, subtree: true });
  }
  document.addEventListener("hub:lang", focusScrollBoxes);
})();
