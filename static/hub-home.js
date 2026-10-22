// Start page helpers:
// 1. "Welcome back" banner and ticks on finished lessons (progress is kept only
//    in this browser, written by hub-flow.js on the lesson pages).
// 2. Search across lessons, topics and glossary words (static/search-index.js).
(function () {
  var KEY = "salbotics-hub-progress";
  var data = window.HUB_SEARCH || { lessons: [], topics: [], words: [] };

  var path = location.pathname;
  var local = /^\/static\//.test(path) || !/(\.html|\/)$/.test(path);
  function href(file) { return (local ? "/static/" : "") + file; }

  function loadProgress() {
    try {
      var saved = JSON.parse(localStorage.getItem(KEY) || "{}");
      return {
        done: Array.isArray(saved.done) ? saved.done : [],
        last: typeof saved.last === "string" ? saved.last : ""
      };
    } catch (error) {
      return { done: [], last: "" };
    }
  }

  function saveProgress(progress) {
    try { localStorage.setItem(KEY, JSON.stringify(progress)); } catch (error) { /* private mode */ }
  }

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text) node.textContent = text;
    return node;
  }

  // Text in the reader's language (hub-prefs.js); English when no translation.
  function T(key, english, vars) {
    return window.hubT ? window.hubT(key, english, vars) : english;
  }
  function lang() { return window.hubLang ? window.hubLang() : "en"; }
  // A field of a search-index entry in the current language (falls back to English).
  function loc(item, field) {
    var tr = item.tr && item.tr[lang()];
    return (tr && tr[field]) || item[field];
  }

  // ---------- 1. Progress: ticks on the lesson map + welcome back ----------
  var progress = loadProgress();
  var lessons = data.lessons;

  function paintTicks() {
    Array.prototype.forEach.call(document.querySelectorAll("#path .sp-lessons a"), function (a) {
      var file = (a.getAttribute("href") || "").split("/").pop();
      if (progress.done.indexOf(file) !== -1) {
        a.classList.add("is-done");
        var no = a.querySelector(".sp-lesson-no");
        if (no) no.textContent = "✓";
        a.removeAttribute("aria-label");
        a.setAttribute("aria-label", a.textContent.trim() + T("js.finishedsuffix", " (finished)"));
      }
    });
  }

  var banner = document.getElementById("continue");
  function renderBanner() {
    if (!banner || !lessons.length || !(progress.done.length || progress.last)) return;
    banner.textContent = "";
    var doneCount = lessons.filter(function (l) { return progress.done.indexOf(l.file) !== -1; }).length;
    var next = null;
    lessons.forEach(function (l) {
      if (!next && l.file === progress.last && progress.done.indexOf(l.file) === -1) next = l;
    });
    lessons.forEach(function (l) {
      if (!next && progress.done.indexOf(l.file) === -1) next = l;
    });
    banner.appendChild(el("p", "sp-continue-title",
      !next ? T("js.welcome.all", "You finished all {total} lessons. Well done!", { total: lessons.length })
            : doneCount ? T("js.welcome.some", "Welcome back! You have finished {n} of {total} lessons.",
                            { n: doneCount, total: lessons.length })
            : T("js.welcome.none", "Welcome back! Pick up where you left off.")));
    var row = el("div", "sp-continue-row");
    if (next) {
      var go = el("a", "sp-button sp-button-main",
        T("js.continue", "Continue: Lesson {n} · {title} →", { n: next.number, title: loc(next, "title") }));
      go.href = href(next.file);
      row.appendChild(go);
    }
    var reset = el("button", "sp-continue-reset", T("js.startover", "Start over"));
    reset.type = "button";
    reset.addEventListener("click", function () {
      saveProgress({ done: [], last: "" });
      location.reload();
    });
    row.appendChild(reset);
    banner.appendChild(row);
    banner.hidden = false;
  }

  paintTicks();
  renderBanner();

  // ---------- 2. Search ----------
  var box = document.getElementById("search");
  var input = document.getElementById("hub-search-input");
  var list = document.getElementById("hub-search-results");
  if (!box || !input || !list) {
    document.addEventListener("hub:lang", function () { paintTicks(); renderBanner(); });
    return;
  }
  box.hidden = false;

  function lower(s) { return (s || "").toLowerCase(); }
  function stripNumber(title) { return title.replace(/^(\d+\.|Scenario \d+:|Situation \d+:|Case Study \d+:)\s*/, ""); }
  var lessonNumber = {};
  lessons.forEach(function (l) { lessonNumber[l.file] = l.number; });
  var lessonByFile = {};
  lessons.forEach(function (l) { lessonByFile[l.file] = l; });

  // Matches English and the reader's language, so "sensor" and "penderia" both work.
  function both(item, fields) {
    var out = [];
    fields.forEach(function (f) {
      var v = item[f];
      out.push(Array.isArray(v) ? v.join(" ") : v);
      var tr = item.tr && item.tr[lang()];
      if (tr && tr[f]) out.push(Array.isArray(tr[f]) ? tr[f].join(" ") : tr[f]);
    });
    return lower(out.join(" "));
  }

  function search(query) {
    var tokens = lower(query).split(/\s+/).filter(function (t) { return t.length > 1; });
    if (!tokens.length) return [];
    function all(hay) { return tokens.every(function (t) { return hay.indexOf(t) !== -1; }); }
    var results = [];
    data.words.forEach(function (w) {
      var term = lower(w.term);
      var score = term === lower(query.trim()) ? 100 : tokens.some(function (t) { return term.indexOf(t) === 0; }) ? 40 : 0;
      if (!score && all(both(w, ["meaning"]))) score = 8;
      if (score) results.push({ kind: "word", score: score, item: w });
    });
    data.topics.forEach(function (t) {
      var hay = both(t, ["title", "sub", "plain", "lesson"]);
      if (!all(hay)) return;
      var score = 10 + (all(both(t, ["title"])) ? 20 : 0) + (all(both(t, ["plain"])) ? 5 : 0);
      results.push({ kind: "topic", score: score, item: t });
    });
    lessons.forEach(function (l) {
      var hay = both(l, ["title", "blurb", "stage", "summary"]);
      if (!all(hay)) return;
      results.push({ kind: "lesson", score: 12 + (all(both(l, ["title"])) ? 25 : 0), item: l });
    });
    results.sort(function (a, b) { return b.score - a.score; });
    return results.slice(0, 8);
  }

  function render(query) {
    list.textContent = "";
    if (!query.trim()) return;
    var results = search(query);
    if (!results.length) {
      list.appendChild(el("li", "sp-search-empty",
        T("js.search.none", "No match yet. Try a simpler word, such as motor, sensor or alarm.")));
      return;
    }
    results.forEach(function (r) {
      var li = el("li", "sp-search-" + r.kind);
      if (r.kind === "word") {
        li.appendChild(el("strong", "", r.item.term));
        li.appendChild(el("span", "", loc(r.item, "meaning")));
      } else {
        var a = el("a");
        if (r.kind === "topic") {
          var plain = loc(r.item, "plain");
          a.href = href(r.item.file) + "#" + r.item.id;
          a.appendChild(el("strong", "", stripNumber(loc(r.item, "title"))));
          a.appendChild(el("small", "", T("js.lessonlabel", "Lesson {n}: {title}",
            { n: lessonNumber[r.item.file], title: loc(lessonByFile[r.item.file], "title") }) +
            (plain ? " — " + plain : "")));
        } else {
          a.href = href(r.item.file);
          a.appendChild(el("strong", "", T("js.lessonlabel", "Lesson {n}: {title}",
            { n: r.item.number, title: loc(r.item, "title") })));
          a.appendChild(el("small", "", loc(r.item, "blurb")));
        }
        li.appendChild(a);
      }
      list.appendChild(li);
    });
  }

  var timer = null;
  input.addEventListener("input", function () {
    clearTimeout(timer);
    timer = setTimeout(function () { render(input.value); }, 120);
  });

  document.addEventListener("hub:lang", function () {
    paintTicks();
    renderBanner();
    render(input.value);
  });

  function focusFromHash() {
    if (location.hash === "#search") {
      box.scrollIntoView({ block: "center" });
      input.focus({ preventScroll: true });
    }
  }
  window.addEventListener("hashchange", focusFromHash);
  focusFromHash();
})();
