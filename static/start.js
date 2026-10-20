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
      button.textContent = paused ? "▶ Play" : "❚❚ Pause";
    }

    button.addEventListener("click", function () {
      setPaused(!scene.classList.contains("is-paused"));
    });
    setPaused(reduce);
  });
})();
