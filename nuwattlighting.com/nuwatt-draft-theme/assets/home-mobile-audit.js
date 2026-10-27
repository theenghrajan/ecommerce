/* Task #151 - mobile home page audit (designer PDF and Gary's notes, AC comments #45/#46).
   Loaded on the home template only (layout/theme.liquid). Numbers in brackets = audit point. */
(function () {
  /* (7) SEO text: keep each block's heading and first paragraph, fold the rest behind
     "Read more". Only display changes, so the copy stays in the HTML for search engines.
     home-mobile-audit.css limits the collapse to phones. */
  var count = 0;

  function fold(rte) {
    var first = rte.querySelector(':scope > p');
    if (!first) return;
    var rest = [];
    for (var el = first.nextElementSibling; el; el = el.nextElementSibling) rest.push(el);
    if (!rest.length) return;

    var body = document.createElement('div');
    body.className = 'hm-more__body';
    body.id = 'hm-more-' + (++count);
    body.hidden = true;
    rest.forEach(function (el) { body.appendChild(el); });

    var toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'hm-more__toggle';
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-controls', body.id);
    toggle.textContent = 'Read more';
    toggle.addEventListener('click', function () {
      var open = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!open));
      toggle.textContent = open ? 'Read more' : 'Read less';
      body.hidden = open;
    });

    first.insertAdjacentElement('afterend', toggle);
    toggle.insertAdjacentElement('afterend', body);
  }

  /* Design-driven cards (snippets/dd-card.liquid): image, title and intro stay; the
     list of product lines folds behind "Read more" */
  function foldCard(card) {
    var head = card.querySelector('.dd-card__head');
    var list = card.querySelector('.dd-card__list');
    if (!head || !list) return;
    var body = document.createElement('div');
    body.className = 'hm-more__body';
    body.id = 'hm-more-' + (++count);
    body.hidden = true;
    list.parentNode.insertBefore(body, list);
    body.appendChild(list);
    var toggle = makeToggle(body);
    head.insertAdjacentElement('afterend', toggle);
  }

  function makeToggle(body) {
    var toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'hm-more__toggle';
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-controls', body.id);
    toggle.textContent = 'Read more';
    toggle.addEventListener('click', function () {
      var open = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!open));
      toggle.textContent = open ? 'Read more' : 'Read less';
      body.hidden = open;
    });
    return toggle;
  }

  function init() {
    var blocks = document.querySelectorAll('.template-index .richtext-intro__text .theme-block:last-child .rte');
    Array.prototype.forEach.call(blocks, fold);
    Array.prototype.forEach.call(document.querySelectorAll('.template-index .dd-card'), foldCard);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
