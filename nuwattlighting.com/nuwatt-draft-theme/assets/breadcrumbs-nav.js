/**
 * assets/breadcrumbs.js
 *
 * Progressive enhancement for the visible breadcrumb trail only.
 * The JSON-LD in breadcrumbs.liquid stays static/hierarchical always —
 * this script never touches it.
 *
 * Rule:
 *   - If the last page in sessionStorage's trail matches this page's
 *     "parent" (ctx.parentUrl), the user moved down a level: APPEND.
 *   - Otherwise (direct visit, unrelated click, jumped sideways/up):
 *     RESET to the static/hierarchical trail Liquid already rendered.
 *
 * This single rule also covers:
 *   - Deep-linking straight to a collection (no previous page at all
 *     -> falls to the static trail, i.e. the "fallback" is just the
 *     default branch, not separate code).
 *   - Tag-filtered collection pages: ctx.parentUrl already points at
 *     the base collection (set server-side in breadcrumbs.liquid),
 *     so a tag click from its base collection page appends correctly,
 *     and a direct visit to a filtered URL resets to the static trail
 *     (which already includes the base collection + tag, see liquid file).
 */
(function () {
  var STORAGE_KEY = "breadcrumbTrail";

  var ctxEl = document.getElementById("breadcrumb-context");
  if (!ctxEl) return;

  var ctx;
  try {
    ctx = JSON.parse(ctxEl.textContent);
  } catch (e) {
    return;
  }

  var stored = null;
  try {
    stored = JSON.parse(sessionStorage.getItem(STORAGE_KEY));
  } catch (e) {
    stored = null;
  }

  var previous = stored && stored.length ? stored[stored.length - 1] : null;
  var movedDownALevel = !!(
    previous &&
    ctx.parentUrl &&
    previous.url === ctx.parentUrl
  );

  var trail;
  if (movedDownALevel) {
    // Avoid double-adding if the user hit back/forward and landed
    // on a page already at the end of the stored trail.
    var alreadyLast = stored[stored.length - 1].url === ctx.currentUrl;
    trail = alreadyLast
      ? stored
      : stored.concat([{ url: ctx.currentUrl, title: ctx.currentTitle }]);
  } else {
    // No relation to the previous page -> static/hierarchical trail wins.
    trail = ctx.staticTrail;
  }

  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(trail));
  } catch (e) {
    /* sessionStorage unavailable (private mode, etc.) — trail still renders below */
  }

  renderTrail(trail);

  function renderTrail(trail) {
    var list = document.querySelector(".breadcrumbs__list");
    if (!list || !trail || !trail.length) return;

    list.innerHTML = "";

    trail.forEach(function (node, idx) {
      var isLast = idx === trail.length - 1;
      var li = document.createElement("li");
      li.className =
        "breadcrumbs__item" + (isLast ? " breadcrumbs__item--current" : "");
      li.setAttribute("itemprop", "itemListElement");
      li.setAttribute("itemscope", "");
      li.setAttribute("itemtype", "https://schema.org/ListItem");
      if (isLast) li.setAttribute("aria-current", "page");

      li.innerHTML = isLast
        ? '<span itemprop="name">' + escapeHtml(node.title) + "</span>"
        : '<a href="' +
          node.url +
          '" itemprop="item"><span itemprop="name">' +
          escapeHtml(node.title) +
          "</span></a>";
      li.innerHTML += '<meta itemprop="position" content="' + (idx + 1) + '">';

      list.appendChild(li);
    });
  }

  function escapeHtml(str) {
    var div = document.createElement("div");
    div.textContent = str == null ? "" : str;
    return div.innerHTML;
  }
})();
