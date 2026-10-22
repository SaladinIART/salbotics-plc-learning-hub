// Learning path shared by every lesson page.
// One ordered list of lessons drives: the "Lesson X of 10" progress bar at the
// top, the "Up next" card at the bottom, the current stage in the top menu, and
// a friendly note on pages whose live dashboard needs the local trainer.
// Each lesson page opts in with <body data-lesson="file.html">.
(function () {
  var STAGES = [
    { id: "basics", name: "The basics" },
    { id: "skills", name: "Real skills" },
    { id: "factory", name: "A real factory" },
    { id: "data", name: "Data and networks" },
    { id: "safety", name: "Safety career" }
  ];

  var LESSONS = [
    { file: "beginner-guide.html", stage: "basics", title: "Beginner guide",
      blurb: "PLC ideas through a washer, lift, gate and rice cooker." },
    { file: "how-it-works.html", stage: "basics", title: "How the traffic light works",
      blurb: "Follow the trainer's rules, one scenario at a time." },
    { file: "plc-programming-methods.html", stage: "skills", title: "Writing a reliable program",
      blurb: "Plan with a flowchart first, then write Ladder." },
    { file: "industrial-situations.html", stage: "skills", title: "Real industrial situations",
      blurb: "Brands, sensors, motor drives and common cabinet faults." },
    { file: "oil-palm-industrial-environment.html", stage: "factory", title: "Inside a palm-oil mill",
      blurb: "Follow fruit bunches all the way to crude palm oil." },
    { file: "oil-palm-control-stack-analysis.html", stage: "factory", title: "Choosing the right controller",
      blurb: "PLC, PAC, Raspberry Pi or Arduino: which job suits which?" },
    { file: "phase-2-start-here.html", stage: "data", title: "Control rooms and networks",
      blurb: "How machines, screens and servers share information." },
    { file: "phase-3-data-analytics.html", stage: "data", title: "Factory data and dashboards",
      blurb: "Turn machine signals into numbers managers can use." },
    { file: "phase-4-legacy-ot-recovery.html", stage: "data", title: "Rescuing old machines",
      blurb: "Read data safely from old equipment that must keep running." },
    { file: "risk-assessment-certification.html", stage: "safety", title: "Becoming safety qualified",
      blurb: "What machine-safety training means, and how to get it." }
  ];

  var DOWNLOAD_URL = "https://github.com/SaladinIART/salbotics-plc-learning-hub#download-and-open-on-windows";

  var current = document.body && document.body.getAttribute("data-lesson");
  var index = -1;
  for (var i = 0; i < LESSONS.length; i++) {
    if (LESSONS[i].file === current) index = i;
  }
  var main = document.querySelector("main");
  if (index === -1 || !main) return;

  // Local trainer serves pages from /static/ (and short routes like /beginner-guide);
  // the public website serves them side by side. Build links that work in both.
  var path = location.pathname;
  var local = /^\/static\//.test(path) || !/(\.html|\/)$/.test(path);
  function href(file) { return (local ? "/static/" : "") + file; }

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text) node.textContent = text;
    return node;
  }

  // Finished lessons are remembered only in this browser (start page reads it too).
  var KEY = "salbotics-hub-progress";
  function loadProgress() {
    try {
      var saved = JSON.parse(localStorage.getItem(KEY) || "{}");
      return { done: Array.isArray(saved.done) ? saved.done : [],
               last: typeof saved.last === "string" ? saved.last : "" };
    } catch (error) {
      return { done: [], last: "" };
    }
  }
  function saveProgress(p) {
    try { localStorage.setItem(KEY, JSON.stringify(p)); } catch (error) { /* private mode */ }
  }
  var saved = loadProgress();
  saved.last = current;
  saveProgress(saved);
  function doneCount() {
    return LESSONS.filter(function (l) { return saved.done.indexOf(l.file) !== -1; }).length;
  }

  var lesson = LESSONS[index];
  var words = (main.textContent || "").split(/\s+/).length;
  var minutes = Math.max(2, Math.round(words / 200));

  // Text in the reader's language (hub-prefs.js); English when no translation.
  function T(key, english, vars) {
    return window.hubT ? window.hubT(key, english, vars) : english;
  }
  function base(file) { return file.replace(/\.html$/, ""); }
  function lessonTitle(item) { return T("lesson." + base(item.file) + ".title", item.title); }
  function lessonBlurb(item) { return T("lesson." + base(item.file) + ".blurb", item.blurb); }
  function stageName(st) { return T("stage." + st.id, st.name); }
  function stageOf(item) {
    for (var s = 0; s < STAGES.length; s++) {
      if (STAGES[s].id === item.stage) return { number: s + 1, id: STAGES[s].id, name: stageName(STAGES[s]) };
    }
    return { number: 0, id: "", name: "" };
  }

  // Highlight the current stage in the top menu.
  Array.prototype.forEach.call(document.querySelectorAll(".top-actions a[data-stage]"), function (a) {
    if (a.getAttribute("data-stage") === lesson.stage) a.setAttribute("aria-current", "true");
  });

  var built = [];
  var observer = null;

  function render() {
    built.forEach(function (node) { if (node.parentNode) node.parentNode.removeChild(node); });
    built = [];
    if (observer) observer.disconnect();
    var stage = stageOf(lesson);

    // 1. Progress bar at the top of the page.
    var progress = el("nav", "hub-progress");
    progress.setAttribute("aria-label", T("js.path", "Learning path"));
    var top = el("div", "hub-progress-top");
    top.appendChild(el("span", "hub-stage", T("js.stage", "Stage {n} of {total} · {name}",
      { n: stage.number, total: STAGES.length, name: stage.name })));
    var step = el("span", "hub-step");
    function stepText() {
      var count = doneCount();
      step.textContent = T("js.lessonstep", "Lesson {n} of {total} · about {min} min read",
        { n: index + 1, total: LESSONS.length, min: minutes }) +
        (count ? T("js.finishedcount", " · {n} finished", { n: count }) : "");
    }
    stepText();
    top.appendChild(step);
    var tools = el("span", "hub-progress-links");
    var find = el("a", "hub-map-link", T("js.search", "Search"));
    find.href = href("start.html") + "#search";
    var map = el("a", "hub-map-link", T("js.alllessons", "All lessons"));
    map.href = href("start.html") + "#path";
    tools.appendChild(find);
    tools.appendChild(map);
    top.appendChild(tools);
    progress.appendChild(top);

    var bar = el("ol", "hub-progress-bar");
    LESSONS.forEach(function (item, n) {
      var isDone = saved.done.indexOf(item.file) !== -1;
      var li = el("li", (isDone ? "is-done " : "") + (n === index ? "is-current" : ""));
      var a = el("a");
      a.href = href(item.file);
      var label = T("js.lessonlabel", "Lesson {n}: {title}", { n: n + 1, title: lessonTitle(item) });
      a.title = label;
      a.appendChild(el("span", "hub-sr", label + (isDone ? T("js.finishedsuffix", " (finished)") : "")));
      if (n === index) a.setAttribute("aria-current", "page");
      li.appendChild(a);
      bar.appendChild(li);
    });
    progress.appendChild(bar);
    main.insertBefore(progress, main.firstChild);
    built.push(progress);

    // 2. Friendly note where the page's live dashboard needs the local trainer.
    if (document.body.hasAttribute("data-needs-trainer") && !local) {
      var note = el("div", "hub-offline");
      note.setAttribute("role", "note");
      note.appendChild(el("strong", "", T("js.offline.title", "Live numbers need the free trainer.") + " "));
      note.appendChild(document.createTextNode(T("js.offline.text",
        "This page shows a dashboard from the Windows trainer. On this website you see sample numbers recorded from it.") + " "));
      var dl = el("a", "", T("js.offline.link", "How to download the trainer"));
      dl.href = DOWNLOAD_URL;
      note.appendChild(dl);
      main.insertBefore(note, progress.nextSibling);
      built.push(note);
    }

    // 3. "Up next" card at the end of the page.
    var next = el("nav", "hub-next");
    next.setAttribute("aria-label", T("js.whatnext", "What to learn next"));
    if (index + 1 < LESSONS.length) {
      var upcoming = LESSONS[index + 1];
      var upcomingStage = stageOf(upcoming);
      next.appendChild(el("p", "hub-next-label",
        T("js.upnext", "Up next · Lesson {n} of {total}", { n: index + 2, total: LESSONS.length }) +
        (upcomingStage.number !== stage.number ? T("js.newstage", " · new stage: {name}", { name: upcomingStage.name }) : "")));
      var card = el("a", "hub-next-card");
      card.href = href(upcoming.file);
      card.appendChild(el("strong", "", lessonTitle(upcoming)));
      card.appendChild(el("span", "", lessonBlurb(upcoming)));
      card.appendChild(el("span", "hub-next-go", T("js.startlesson", "Start this lesson →")));
      next.appendChild(card);
    } else {
      next.appendChild(el("p", "hub-next-label", T("js.endpath", "You reached the end of the learning path")));
      var done = el("a", "hub-next-card");
      done.href = DOWNLOAD_URL;
      done.appendChild(el("strong", "", T("js.practise", "Practise with the full trainer")));
      done.appendChild(el("span", "", T("js.practisetext", "Press the buttons yourself in the free Windows simulator.")));
      done.appendChild(el("span", "hub-next-go", T("js.download", "How to download →")));
      next.appendChild(done);
    }
    var links = el("div", "hub-next-links");
    if (index > 0) {
      var back = el("a", "", T("js.back", "← Back: {title}", { title: lessonTitle(LESSONS[index - 1]) }));
      back.href = href(LESSONS[index - 1].file);
      links.appendChild(back);
    }
    var all = el("a", "", T("js.seeall", "See all lessons"));
    all.href = href("start.html") + "#path";
    links.appendChild(all);
    next.appendChild(links);
    main.appendChild(next);
    built.push(next);

    // Reaching the "Up next" card counts as finishing this lesson.
    var finished = el("p", "hub-finished", T("js.finished", "✓ Lesson finished. Your progress is saved in this browser."));
    finished.hidden = saved.done.indexOf(current) === -1;
    next.insertBefore(finished, next.firstChild);
    function markDone() {
      saved = loadProgress();
      if (saved.done.indexOf(current) === -1) saved.done.push(current);
      saved.last = current;
      saveProgress(saved);
      finished.hidden = false;
      var seg = bar.children[index];
      if (seg) seg.classList.add("is-done");
      stepText();
    }
    if ("IntersectionObserver" in window) {
      observer = new IntersectionObserver(function (entries) {
        if (entries.some(function (e) { return e.isIntersecting; })) {
          markDone();
          observer.disconnect();
        }
      }, { threshold: 0.6 });
      observer.observe(next);
    }
    next.addEventListener("click", function (event) {
      if (event.target.closest(".hub-next-card")) markDone();
    });
  }

  render();
  // Redraw in the new language when the reader switches (hub-prefs.js).
  document.addEventListener("hub:lang", render);
})();
