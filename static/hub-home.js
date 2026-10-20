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

  // ---------- 1. Progress: ticks on the lesson map + welcome back ----------
  var progress = loadProgress();

  Array.prototype.forEach.call(document.querySelectorAll("#path .sp-lessons a"), function (a) {
    var file = (a.getAttribute("href") || "").split("/").pop();
    if (progress.done.indexOf(file) !== -1) {
      a.classList.add("is-done");
      var no = a.querySelector(".sp-lesson-no");
      if (no) no.textContent = "✓";
      a.setAttribute("aria-label", a.textContent.trim() + " (finished)");
    }
  });

  var banner = document.getElementById("continue");
  var lessons = data.lessons;
  if (banner && lessons.length && (progress.done.length || progress.last)) {
    var doneCount = lessons.filter(function (l) { return progress.done.indexOf(l.file) !== -1; }).length;
    var next = null;
    lessons.forEach(function (l) {
      if (!next && l.file === progress.last && progress.done.indexOf(l.file) === -1) next = l;
    });
    lessons.forEach(function (l) {
      if (!next && progress.done.indexOf(l.file) === -1) next = l;
    });
    banner.appendChild(el("p", "sp-continue-title",
      next ? "Welcome back! You have finished " + doneCount + " of " + lessons.length + " lessons."
           : "You finished all " + lessons.length + " lessons. Well done!"));
    var row = el("div", "sp-continue-row");
    if (next) {
      var go = el("a", "sp-button sp-button-main", "Continue: Lesson " + next.number + " · " + next.title + " →");
      go.href = href(next.file);
      row.appendChild(go);
    }
    var reset = el("button", "sp-continue-reset", "Start over");
    reset.type = "button";
    reset.addEventListener("click", function () {
      saveProgress({ done: [], last: "" });
      location.reload();
    });
    row.appendChild(reset);
    banner.appendChild(row);
    banner.hidden = false;
  }

  // ---------- 2. Search ----------
  var box = document.getElementById("search");
  var input = document.getElementById("hub-search-input");
  var list = document.getElementById("hub-search-results");
  if (!box || !input || !list) return;
  box.hidden = false;

  function lower(s) { return (s || "").toLowerCase(); }
  function stripNumber(title) { return title.replace(/^(\d+\.|Scenario \d+:|Situation \d+:|Case Study \d+:)\s*/, ""); }
  var lessonNumber = {};
  lessons.forEach(function (l) { lessonNumber[l.file] = l.number; });

  function search(query) {
    var tokens = lower(query).split(/\s+/).filter(function (t) { return t.length > 1; });
    if (!tokens.length) return [];
    function all(hay) { return tokens.every(function (t) { return hay.indexOf(t) !== -1; }); }
    var results = [];
    data.words.forEach(function (w) {
      var term = lower(w.term);
      var score = term === lower(query.trim()) ? 100 : tokens.some(function (t) { return term.indexOf(t) === 0; }) ? 40 : 0;
      if (!score && all(lower(w.meaning))) score = 8;
      if (score) results.push({ kind: "word", score: score, item: w });
    });
    data.topics.forEach(function (t) {
      var hay = lower([t.title, t.sub, t.plain, t.lesson].join(" "));
      if (!all(hay)) return;
      var score = 10 + (all(lower(t.title)) ? 20 : 0) + (all(lower(t.plain)) ? 5 : 0);
      results.push({ kind: "topic", score: score, item: t });
    });
    lessons.forEach(function (l) {
      var hay = lower([l.title, l.blurb, l.stage].concat(l.summary).join(" "));
      if (!all(hay)) return;
      results.push({ kind: "lesson", score: 12 + (all(lower(l.title)) ? 25 : 0), item: l });
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
        "No match yet. Try a simpler word, such as motor, sensor or alarm."));
      return;
    }
    results.forEach(function (r) {
      var li = el("li", "sp-search-" + r.kind);
      if (r.kind === "word") {
        li.appendChild(el("strong", "", r.item.term));
        li.appendChild(el("span", "", r.item.meaning));
      } else {
        var a = el("a");
        if (r.kind === "topic") {
          a.href = href(r.item.file) + "#" + r.item.id;
          a.appendChild(el("strong", "", stripNumber(r.item.title)));
          a.appendChild(el("small", "", "Lesson " + lessonNumber[r.item.file] + " · " + r.item.lesson +
            (r.item.plain ? " — " + r.item.plain : "")));
        } else {
          a.href = href(r.item.file);
          a.appendChild(el("strong", "", "Lesson " + r.item.number + ": " + r.item.title));
          a.appendChild(el("small", "", r.item.blurb));
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

  function focusFromHash() {
    if (location.hash === "#search") {
      box.scrollIntoView({ block: "center" });
      input.focus({ preventScroll: true });
    }
  }
  window.addEventListener("hashchange", focusFromHash);
  focusFromHash();
})();
