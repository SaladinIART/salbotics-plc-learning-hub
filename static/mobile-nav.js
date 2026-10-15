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
