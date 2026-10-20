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

  function stageOf(lesson) {
    for (var s = 0; s < STAGES.length; s++) {
      if (STAGES[s].id === lesson.stage) return { number: s + 1, name: STAGES[s].name };
    }
    return { number: 0, name: "" };
  }

  var lesson = LESSONS[index];
  var stage = stageOf(lesson);
  var words = (main.textContent || "").split(/\s+/).length;
  var minutes = Math.max(2, Math.round(words / 200));

  // Highlight the current stage in the top menu.
  Array.prototype.forEach.call(document.querySelectorAll(".top-actions a[data-stage]"), function (a) {
    if (a.getAttribute("data-stage") === lesson.stage) a.setAttribute("aria-current", "true");
  });

  // 1. Progress bar at the top of the page.
  var progress = el("nav", "hub-progress");
  progress.setAttribute("aria-label", "Learning path");
  var top = el("div", "hub-progress-top");
  top.appendChild(el("span", "hub-stage", "Stage " + stage.number + " of " + STAGES.length + " · " + stage.name));
  top.appendChild(el("span", "hub-step",
    "Lesson " + (index + 1) + " of " + LESSONS.length + " · about " + minutes + " min read"));
  var map = el("a", "hub-map-link", "All lessons");
  map.href = href("start.html") + "#path";
  top.appendChild(map);
  progress.appendChild(top);

  var bar = el("ol", "hub-progress-bar");
  LESSONS.forEach(function (item, n) {
    var li = el("li", n < index ? "is-done" : n === index ? "is-current" : "");
    var a = el("a");
    a.href = href(item.file);
    a.title = "Lesson " + (n + 1) + ": " + item.title;
    a.appendChild(el("span", "hub-sr", "Lesson " + (n + 1) + ": " + item.title));
    if (n === index) a.setAttribute("aria-current", "page");
    li.appendChild(a);
    bar.appendChild(li);
  });
  progress.appendChild(bar);
  main.insertBefore(progress, main.firstChild);

  // 2. Friendly note where the page's live dashboard needs the local trainer.
  if (document.body.hasAttribute("data-needs-trainer") && !local) {
    var note = el("div", "hub-offline");
    note.setAttribute("role", "note");
    note.appendChild(el("strong", "", "Live numbers need the free trainer. "));
    note.appendChild(document.createTextNode(
      "This page shows a dashboard from the Windows trainer. On this website you see a preview only. "));
    var dl = el("a", "", "How to download the trainer");
    dl.href = DOWNLOAD_URL;
    note.appendChild(dl);
    main.insertBefore(note, progress.nextSibling);
  }

  // 3. "Up next" card at the end of the page.
  var next = el("nav", "hub-next");
  next.setAttribute("aria-label", "What to learn next");
  if (index + 1 < LESSONS.length) {
    var upcoming = LESSONS[index + 1];
    var upcomingStage = stageOf(upcoming);
    next.appendChild(el("p", "hub-next-label",
      "Up next · Lesson " + (index + 2) + " of " + LESSONS.length +
      (upcomingStage.number !== stage.number ? " · new stage: " + upcomingStage.name : "")));
    var card = el("a", "hub-next-card");
    card.href = href(upcoming.file);
    card.appendChild(el("strong", "", upcoming.title));
    card.appendChild(el("span", "", upcoming.blurb));
    card.appendChild(el("span", "hub-next-go", "Start this lesson →"));
    next.appendChild(card);
  } else {
    next.appendChild(el("p", "hub-next-label", "You reached the end of the learning path"));
    var done = el("a", "hub-next-card");
    done.href = DOWNLOAD_URL;
    done.appendChild(el("strong", "", "Practise with the full trainer"));
    done.appendChild(el("span", "", "Press the buttons yourself in the free Windows simulator."));
    done.appendChild(el("span", "hub-next-go", "How to download →"));
    next.appendChild(done);
  }
  var links = el("div", "hub-next-links");
  if (index > 0) {
    var back = el("a", "", "← Back: " + LESSONS[index - 1].title);
    back.href = href(LESSONS[index - 1].file);
    links.appendChild(back);
  }
  var all = el("a", "", "See all lessons");
  all.href = href("start.html") + "#path";
  links.appendChild(all);
  next.appendChild(links);
  main.appendChild(next);
})();
