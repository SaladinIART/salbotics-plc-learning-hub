// Phone-friendly top bar: collapses the page links behind a MENU button.
// Without JavaScript the links simply stay visible (progressive enhancement).
(function () {
  var topbar = document.querySelector(".topbar");
  var actions = topbar && topbar.querySelector(".top-actions");
  var brand = topbar && topbar.querySelector(".brand-block");
  if (!topbar || !actions || !brand) return;

  document.documentElement.classList.add("js-nav");
  if (!actions.id) actions.id = "top-actions-menu";

  var button = document.createElement("button");
  button.type = "button";
  button.className = "menu-toggle";
  button.setAttribute("aria-controls", actions.id);
  button.setAttribute("aria-expanded", "false");
  button.textContent = "MENU";
  brand.appendChild(button);

  function setOpen(open) {
    topbar.classList.toggle("menu-open", open);
    button.setAttribute("aria-expanded", open ? "true" : "false");
    button.textContent = open ? "CLOSE" : "MENU";
  }

  button.addEventListener("click", function () {
    setOpen(!topbar.classList.contains("menu-open"));
  });
  actions.addEventListener("click", function (event) {
    if (event.target.closest("a")) setOpen(false);
  });
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") setOpen(false);
  });
})();

// Long guide pages: collapsible sections plus a compact "Jump to" menu.
// Opt-in per page with <main data-collapsible-sections>. Collapsing only
// takes visual effect on phones (see guide.css); desktop shows everything.
(function () {
  var main = document.querySelector("main[data-collapsible-sections]");
  if (!main) return;
  document.documentElement.classList.add("js-sections");

  var sections = Array.prototype.filter.call(
    main.querySelectorAll(":scope > section[id]"),
    function (section) { return section.querySelector(":scope > .panel-heading"); }
  );

  function setOpen(section, open) {
    section.classList.toggle("section-collapsed", !open);
    section.querySelector(":scope > .panel-heading").setAttribute("aria-expanded", open ? "true" : "false");
  }

  sections.forEach(function (section) {
    var heading = section.querySelector(":scope > .panel-heading");
    heading.setAttribute("role", "button");
    heading.setAttribute("tabindex", "0");
    heading.addEventListener("click", function () {
      setOpen(section, section.classList.contains("section-collapsed"));
    });
    heading.addEventListener("keydown", function (event) {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        setOpen(section, section.classList.contains("section-collapsed"));
      }
    });
    // A lesson can keep its key picture visible with data-start-open.
    setOpen(section, section.hasAttribute("data-start-open"));
  });

  function openFromHash() {
    var id = decodeURIComponent(location.hash.slice(1));
    var target = id && document.getElementById(id);
    if (!target) return;
    var section = target.closest("section[id]");
    if (section && sections.indexOf(section) !== -1) {
      setOpen(section, true);
      section.scrollIntoView();
    }
  }

  // Compact jump menu built from the page's own section navigation.
  var nav = main.querySelector(":scope > nav.scenario-nav");
  if (nav) {
    var label = document.createElement("label");
    label.className = "section-jump";
    var text = document.createElement("span");
    text.textContent = "Jump to section";
    var select = document.createElement("select");
    var first = document.createElement("option");
    first.value = "";
    first.textContent = "Choose a section...";
    select.appendChild(first);
    Array.prototype.forEach.call(nav.querySelectorAll("a[href^='#']"), function (link) {
      var option = document.createElement("option");
      option.value = link.getAttribute("href");
      option.textContent = link.textContent.trim();
      select.appendChild(option);
    });
    select.addEventListener("change", function () {
      if (select.value) {
        location.hash = select.value;
        openFromHash();
      }
    });
    label.appendChild(text);
    label.appendChild(select);
    nav.parentNode.insertBefore(label, nav);
  }

  // One button to open or fold every topic at once.
  if (sections.length > 1) {
    var tools = document.createElement("div");
    tools.className = "section-tools";
    var toggle = document.createElement("button");
    toggle.type = "button";
    var allOpen = function () {
      return sections.every(function (s) { return !s.classList.contains("section-collapsed"); });
    };
    var label = function () {
      toggle.textContent = allOpen() ? "Fold all topics" : "Open all topics";
    };
    toggle.addEventListener("click", function () {
      var open = !allOpen();
      sections.forEach(function (s) { setOpen(s, open); });
      label();
    });
    sections.forEach(function (s) {
      s.querySelector(":scope > .panel-heading").addEventListener("click", function () {
        setTimeout(label, 0);
      });
    });
    tools.appendChild(toggle);
    sections[0].parentNode.insertBefore(tools, sections[0]);
    label();
  }

  window.addEventListener("hashchange", openFromHash);
  openFromHash();
})();

// Wide diagrams and tables: on phones, show a "swipe sideways" hint above any
// box that scrolls horizontally, and hide it once the reader has swiped.
(function () {
  var phone = window.matchMedia("(max-width: 760px)");

  function scrollsSideways(el) {
    var overflow = getComputedStyle(el).overflowX;
    // Ignore boxes that overflow by only a few pixels.
    return (overflow === "auto" || overflow === "scroll") && el.scrollWidth > el.clientWidth + 32;
  }

  function addHints() {
    if (!phone.matches) return;
    var candidates = document.querySelectorAll("main *");
    Array.prototype.forEach.call(candidates, function (el) {
      if (el.dataset.swipeHint || !scrollsSideways(el)) return;
      if (el.parentElement && el.parentElement.closest("[data-swipe-hint]")) return;
      el.dataset.swipeHint = "1";
      el.classList.add("has-swipe");
      var hint = document.createElement("p");
      hint.className = "swipe-hint";
      hint.setAttribute("aria-hidden", "true");
      hint.textContent = "Swipe sideways to see more \u2192";
      el.parentNode.insertBefore(hint, el);
      el.addEventListener("scroll", function onScroll() {
        if (el.scrollLeft > Math.min(24, (el.scrollWidth - el.clientWidth) / 2)) {
          hint.classList.add("swipe-hint-done");
          el.classList.add("swipe-seen");
          el.removeEventListener("scroll", onScroll);
        }
      }, { passive: true });
    });
  }

  if (document.readyState === "complete") addHints();
  else window.addEventListener("load", addHints);
  // Collapsed sections (M-4) only become measurable when opened.
  document.addEventListener("click", function () { setTimeout(addHints, 50); });
  window.addEventListener("hashchange", function () { setTimeout(addHints, 50); });
  if (phone.addEventListener) phone.addEventListener("change", addHints);
})();
