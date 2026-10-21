// Reader preferences shared by the start page and every lesson:
//   - colour theme: Auto (follows the device), Light or Dark
//   - language: English (default), Bahasa Malaysia or Deutsch
// Loaded in <head> without "defer" so the saved theme applies before the page
// is drawn (no white flash in dark mode).
//
// Translations: elements with data-i18n="key" (text) or data-i18n-html="key"
// (text with simple markup) are replaced from static/lang/<lang>.json.
// data-i18n-attr="placeholder:key" translates an attribute. English always stays
// in the HTML. Scripts get text through window.hubT(key, english, vars) and
// redraw on the "hub:lang" event.
(function () {
  var THEME_KEY = "salbotics-hub-theme";
  var LANG_KEY = "salbotics-hub-lang";
  var root = document.documentElement;

  function read(key) {
    try { return localStorage.getItem(key); } catch (error) { return null; }
  }
  function write(key, value) {
    try { localStorage.setItem(key, value); } catch (error) { /* private mode */ }
  }

  // ---------- Theme ----------
  var THEMES = ["auto", "light", "dark"];
  function applyTheme(theme) {
    if (theme === "light" || theme === "dark") root.setAttribute("data-theme", theme);
    else root.removeAttribute("data-theme");
  }
  var theme = read(THEME_KEY);
  if (THEMES.indexOf(theme) === -1) theme = "auto";
  applyTheme(theme);

  // ---------- Language ----------
  var LANGS = [
    { code: "en", short: "EN", name: "English" },
    { code: "ms", short: "BM", name: "Bahasa Malaysia" },
    { code: "de", short: "DE", name: "Deutsch" }
  ];
  var lang = read(LANG_KEY);
  if (!LANGS.some(function (l) { return l.code === lang; })) lang = "en";
  root.setAttribute("lang", lang);
  var dict = {};

  var path = location.pathname;
  var local = /^\/static\//.test(path) || !/(\.html|\/)$/.test(path);
  function langUrl(code) { return (local ? "/static/" : "") + "lang/" + code + ".json?v=lang-20261021"; }

  // Text for scripts: hubT("js.key", "English text with {n}", { n: 3 })
  window.hubT = function (key, english, vars) {
    var text = (lang !== "en" && dict[key]) || english;
    if (vars) {
      Object.keys(vars).forEach(function (name) {
        text = text.split("{" + name + "}").join(vars[name]);
      });
    }
    return text;
  };
  window.hubLang = function () { return lang; };

  // Keep the English of every keyed element before other scripts change the page.
  var originals = [];
  function capture() {
    if (originals.length) return;
    Array.prototype.forEach.call(document.querySelectorAll("[data-i18n], [data-i18n-html], [data-i18n-attr]"), function (el) {
      var entry = { el: el };
      if (el.hasAttribute("data-i18n")) entry.text = el.textContent;
      if (el.hasAttribute("data-i18n-html")) entry.html = el.innerHTML;
      if (el.hasAttribute("data-i18n-attr")) {
        entry.attrs = el.getAttribute("data-i18n-attr").split(";").map(function (pair) {
          var bits = pair.split(":");
          return { name: bits[0].trim(), key: (bits[1] || "").trim(), value: el.getAttribute(bits[0].trim()) };
        });
      }
      originals.push(entry);
    });
  }

  function applyLanguage() {
    capture();
    originals.forEach(function (o) {
      var el = o.el;
      if (o.text !== undefined) {
        var t = lang !== "en" && dict[el.getAttribute("data-i18n")];
        el.textContent = t || o.text;
      }
      if (o.html !== undefined) {
        var h = lang !== "en" && dict[el.getAttribute("data-i18n-html")];
        el.innerHTML = h || o.html;   // our own translation files only
      }
      (o.attrs || []).forEach(function (a) {
        var v = lang !== "en" && dict[a.key];
        if (a.value !== null) el.setAttribute(a.name, v || a.value);
      });
    });
    document.dispatchEvent(new CustomEvent("hub:lang", { detail: { lang: lang } }));
    paintLangButtons();
  }

  function loadLanguage(code, done) {
    if (code === "en") { dict = {}; done(); return; }
    fetch(langUrl(code))
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (data) { dict = data; done(); })
      .catch(function () { lang = "en"; root.setAttribute("lang", "en"); dict = {}; done(); });
  }

  function setLanguage(code) {
    lang = code;
    write(LANG_KEY, code);
    root.setAttribute("lang", code);
    loadLanguage(code, applyLanguage);
  }

  // ---------- Controls in the top bar ----------
  var THEME_ICON = { auto: "◐", light: "☀", dark: "☾" };
  var themeButton = null;
  var langButtons = [];

  function paintTheme() {
    if (!themeButton) return;
    var names = { auto: hubT("js.theme.auto", "Auto"), light: hubT("js.theme.light", "Light"), dark: hubT("js.theme.dark", "Dark") };
    themeButton.textContent = THEME_ICON[theme];
    var label = hubT("js.theme.label", "Colour theme: {name}. Tap to change.", { name: names[theme] });
    themeButton.setAttribute("aria-label", label);
    themeButton.title = label;
  }

  function paintLangButtons() {
    langButtons.forEach(function (b) {
      b.setAttribute("aria-pressed", b.getAttribute("data-lang") === lang ? "true" : "false");
    });
    paintTheme();
  }

  function buildControls() {
    var bar = document.querySelector(".topbar");
    if (!bar || bar.querySelector(".hub-prefs")) return;
    var group = document.createElement("div");
    group.className = "hub-prefs";

    var langGroup = document.createElement("div");
    langGroup.className = "hub-lang";
    langGroup.setAttribute("role", "group");
    langGroup.setAttribute("aria-label", "Language / Bahasa / Sprache");
    LANGS.forEach(function (l) {
      var b = document.createElement("button");
      b.type = "button";
      b.textContent = l.short;
      b.lang = l.code;
      b.title = l.name;
      b.setAttribute("aria-label", l.name);
      b.setAttribute("data-lang", l.code);
      b.addEventListener("click", function () { if (l.code !== lang) setLanguage(l.code); });
      langButtons.push(b);
      langGroup.appendChild(b);
    });
    group.appendChild(langGroup);

    themeButton = document.createElement("button");
    themeButton.type = "button";
    themeButton.className = "hub-theme";
    themeButton.addEventListener("click", function () {
      theme = THEMES[(THEMES.indexOf(theme) + 1) % THEMES.length];
      write(THEME_KEY, theme);
      applyTheme(theme);
      paintTheme();
    });
    group.appendChild(themeButton);
    bar.appendChild(group);
    paintLangButtons();
  }

  // Keep English before the page scripts (deferred) start changing the DOM.
  document.addEventListener("readystatechange", function () {
    if (document.readyState === "interactive") capture();
  });

  // "Skip to content" link: the first stop for keyboard users, jumps past the menus.
  var skipLink = null;
  function buildSkipLink() {
    var target = document.querySelector("main h1") || document.querySelector("main");
    if (!target || document.querySelector(".hub-skip")) return;
    if (!target.id) target.id = "hub-content";
    if (!target.hasAttribute("tabindex")) target.setAttribute("tabindex", "-1");
    skipLink = document.createElement("a");
    skipLink.className = "hub-skip";
    skipLink.href = "#" + target.id;
    paintSkipLink();
    document.body.insertBefore(skipLink, document.body.firstChild);
  }
  function paintSkipLink() {
    if (skipLink) skipLink.textContent = hubT("js.skip", "Skip to content");
  }
  document.addEventListener("hub:lang", paintSkipLink);

  function ready() {
    capture();
    buildSkipLink();
    buildControls();
    if (lang !== "en") loadLanguage(lang, applyLanguage);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", ready);
  else ready();
})();
