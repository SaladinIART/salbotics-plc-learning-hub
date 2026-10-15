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
    setOpen(section, false);
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

  window.addEventListener("hashchange", openFromHash);
  openFromHash();
})();
