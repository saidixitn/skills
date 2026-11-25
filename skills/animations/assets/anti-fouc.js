// Anti-flash script for direct route reloads
// Add inline inside the <head> before stylesheets or body rendering
(function () {
  var path = (window.location.pathname || "/").replace(/\/$/, "") || "/";
  var page = path.split("/").pop() || "index";
  document.documentElement.setAttribute("data-current-page", page);
  document.documentElement.classList.add("js-ready");
})();
