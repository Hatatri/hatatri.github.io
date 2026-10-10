/*
 * Filtres de la page /projets/ : recherche plein texte, catégorie et tags.
 * Amélioration progressive : sans JavaScript, tous les projets restent visibles.
 * Les filtres sont reflétés dans l'URL (?q=…&categorie=…&tag=…) pour être partageables.
 */
(function () {
  "use strict";

  var panel = document.getElementById("filters");
  var grid = document.getElementById("repo-grid");
  if (!panel || !grid) return;

  var cards = Array.prototype.slice.call(grid.querySelectorAll(".repo-card"));
  var search = document.getElementById("filter-search");
  var count = document.getElementById("filter-count");
  var empty = document.getElementById("filter-empty");
  var categoryButtons = panel.querySelectorAll("[data-filter-category]");
  var tagButtons = panel.querySelectorAll("[data-filter-tag]");

  var state = { q: "", category: "", tags: [] };

  function readUrl() {
    var params = new URLSearchParams(window.location.search);
    state.q = params.get("q") || "";
    state.category = params.get("categorie") || "";
    state.tags = params.getAll("tag");
  }

  function writeUrl() {
    var params = new URLSearchParams();
    if (state.q) params.set("q", state.q);
    if (state.category) params.set("categorie", state.category);
    state.tags.forEach(function (t) { params.append("tag", t); });
    var query = params.toString();
    window.history.replaceState(null, "", window.location.pathname + (query ? "?" + query : "") + window.location.hash);
  }

  function render() {
    var q = state.q.trim().toLowerCase();
    var visible = 0;
    cards.forEach(function (card) {
      var tags = (card.dataset.tags || "").split(" ");
      var ok = (!state.category || card.dataset.category === state.category) &&
               state.tags.every(function (t) { return tags.indexOf(t) !== -1; }) &&
               (!q || (card.dataset.search || "").indexOf(q) !== -1);
      card.hidden = !ok;
      if (ok) visible += 1;
    });
    count.textContent = visible;
    empty.hidden = visible !== 0;

    Array.prototype.forEach.call(categoryButtons, function (b) {
      var active = b.dataset.filterCategory === state.category;
      b.classList.toggle("is-active", active);
      b.setAttribute("aria-pressed", active);
    });
    Array.prototype.forEach.call(tagButtons, function (b) {
      var active = state.tags.indexOf(b.dataset.filterTag) !== -1;
      b.classList.toggle("is-active", active);
      b.setAttribute("aria-pressed", active);
    });
    writeUrl();
  }

  Array.prototype.forEach.call(categoryButtons, function (b) {
    b.addEventListener("click", function () {
      state.category = b.dataset.filterCategory;
      render();
    });
  });
  Array.prototype.forEach.call(tagButtons, function (b) {
    b.addEventListener("click", function () {
      var t = b.dataset.filterTag;
      var i = state.tags.indexOf(t);
      if (i === -1) state.tags.push(t); else state.tags.splice(i, 1);
      render();
    });
  });
  search.addEventListener("input", function () {
    state.q = search.value;
    render();
  });

  readUrl();
  search.value = state.q;
  panel.hidden = false;
  render();
})();
