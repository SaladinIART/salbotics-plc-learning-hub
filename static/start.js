// Start page: play / pause buttons for the animated scenes.
// Scenes start paused for people who ask their device for reduced motion.
(function () {
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  document.documentElement.classList.add("js-anim");

  Array.prototype.forEach.call(document.querySelectorAll(".sp-scene"), function (scene) {
    var button = scene.querySelector(".sp-play");
    if (!button) return;

    function setPaused(paused) {
      scene.classList.toggle("is-paused", paused);
      var T = window.hubT || function (k, e) { return e; };
      button.textContent = paused ? T("js.play", "\u25B6 Play") : T("js.pause", "\u275A\u275A Pause");
    }

    button.addEventListener("click", function () {
      setPaused(!scene.classList.contains("is-paused"));
    });
    setPaused(reduce);
    document.addEventListener("hub:lang", function () { setPaused(scene.classList.contains("is-paused")); });
  });
})();
