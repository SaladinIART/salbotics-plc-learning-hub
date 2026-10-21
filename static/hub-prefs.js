// Reader preferences shared by the start page and every lesson:
// colour theme (follows the device by default) and, in a later step, language.
// Loaded in <head> without "defer" so the saved theme applies before the page
// is drawn (no white flash in dark mode). Everything else waits for the DOM.
(function () {
  var THEME_KEY = "salbotics-hub-theme";
  var root = document.documentElement;

  function read(key) {
    try { return localStorage.getItem(key); } catch (error) { return null; }
  }
  function write(key, value) {
    try { localStorage.setItem(key, value); } catch (error) { /* private mode */ }
  }

  // ---------- Theme: "auto" follows the device, or force light / dark ----------
  var THEMES = ["auto", "light", "dark"];
  function applyTheme(theme) {
    if (theme === "light" || theme === "dark") root.setAttribute("data-theme", theme);
    else root.removeAttribute("data-theme");
  }
  var theme = read(THEME_KEY);
  if (THEMES.indexOf(theme) === -1) theme = "auto";
  applyTheme(theme);

  var THEME_LABEL = { auto: "Auto", light: "Light", dark: "Dark" };
  var THEME_ICON = { auto: "◐", light: "☀", dark: "☾" };

  function buildControls() {
    var bar = document.querySelector(".topbar");
    if (!bar || bar.querySelector(".hub-prefs")) return;
    var group = document.createElement("div");
    group.className = "hub-prefs";

    var themeButton = document.createElement("button");
    themeButton.type = "button";
    themeButton.className = "hub-theme";
    function paint() {
      themeButton.textContent = THEME_ICON[theme];
      var label = "Colour theme: " + THEME_LABEL[theme] +
        (theme === "auto" ? " (follows your device)" : "") + ". Tap to change.";
      themeButton.setAttribute("aria-label", label);
      themeButton.title = label;
    }
    themeButton.addEventListener("click", function () {
      theme = THEMES[(THEMES.indexOf(theme) + 1) % THEMES.length];
      write(THEME_KEY, theme);
      applyTheme(theme);
      paint();
    });
    paint();
    group.appendChild(themeButton);
    bar.appendChild(group);
    root.dispatchEvent(new CustomEvent("hub:prefs-ready", { detail: { group: group } }));
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", buildControls);
  else buildControls();
})();
