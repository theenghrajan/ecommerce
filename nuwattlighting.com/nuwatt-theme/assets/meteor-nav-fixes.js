/* Meteor menu, touch screens (#167).
   Meteor turns a tap on a top-level link into an open/close toggle and never
   follows the link. First tap opens the dropdown, a tap on the open item now
   goes to its collection. Mouse users are untouched. */
(function () {
  var LINK = 'a.Meteor-Navigation__Link__desktop[aria-haspopup="true"]';
  var touched = null;
  var wasOpen = false;

  function isOpen(li) {
    return li.getAttribute('data-active-with-content') === 'true';
  }

  document.addEventListener('touchstart', function (e) {
    var link = e.target.closest && e.target.closest(LINK);
    touched = link;
    wasOpen = !!link && isOpen(link.parentElement);
  }, { capture: true, passive: true });

  document.addEventListener('click', function (e) {
    var link = e.target.closest && e.target.closest(LINK);
    if (!link || link !== touched) return;
    touched = null;

    // Keep Meteor's own click handler out of it.
    e.stopPropagation();
    if (wasOpen) return;

    e.preventDefault();
    var li = link.parentElement;
    if (!isOpen(li)) li.dispatchEvent(new MouseEvent('mouseover', { bubbles: true }));
  }, true);
})();
