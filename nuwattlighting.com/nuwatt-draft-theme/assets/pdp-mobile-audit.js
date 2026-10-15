/* Task #150 - mobile product page audit (client PDF, AC comment #83; pack buttons #84; Stamped reviews #87).
   Loaded on product templates only (layout/theme.liquid). Numbers in brackets = audit point. */
(function () {
  var mobile = window.matchMedia('(max-width: 749px)');

  function text(el) {
    return el ? el.textContent.replace(/\s+/g, ' ').trim() : '';
  }

  /* (8) "Pack Size: <selected>" label follows the selected pack button */
  document.addEventListener('change', function (e) {
    var input = e.target;
    if (!input.matches || !input.matches('.variant-input-wrap[data-handle="pack-size"] input[type="radio"]')) return;
    var wrapper = input.closest('.variant-wrapper');
    var label = wrapper && wrapper.querySelector('[data-pack-size-selected]');
    if (label) label.textContent = input.value;
    updateStickyBar();
  });

  /* (2) Sticky Add to Cart on mobile, shown once the main Add to Cart button has scrolled away */
  var bar, barPack, barPrice, barButton, mainButton;

  function updateStickyBar() {
    if (!bar || !mainButton) return;
    var pack = document.querySelector('[data-pack-size-selected]');
    barPack.textContent = pack ? 'Pack Size: ' + text(pack) : '';
    barPack.hidden = !pack;
    // same markup as the buy-box price ($24<sup>99</sup>)
    var price = document.querySelector('.product-single__buy-box [data-product-price]');
    barPrice.innerHTML = price ? price.innerHTML.trim() : '';
    barButton.disabled = mainButton.disabled;
    barButton.textContent = text(mainButton.querySelector('[data-add-to-cart-text]')) || text(mainButton);
  }

  function initStickyBar() {
    mainButton = document.querySelector('.product-grid__item--buybox button[name="add"]') ||
      document.querySelector('.page-content--product form[action*="/cart/add"] button[name="add"]');
    if (!mainButton) return;

    bar = document.createElement('div');
    bar.className = 'nw-sticky-atc';
    bar.setAttribute('aria-hidden', 'true');
    bar.innerHTML =
      '<div class="nw-sticky-atc__info"><span class="nw-sticky-atc__pack"></span><span class="nw-sticky-atc__price"></span></div>' +
      '<button type="button" class="btn nw-sticky-atc__button" tabindex="-1"></button>';
    document.body.appendChild(bar);
    barPack = bar.querySelector('.nw-sticky-atc__pack');
    barPrice = bar.querySelector('.nw-sticky-atc__price');
    barButton = bar.querySelector('.nw-sticky-atc__button');
    // uses the theme's own product form, so cart behaviour (drawer, quantity, variant) is unchanged
    barButton.addEventListener('click', function () {
      mainButton.click();
    });

    // Position check on scroll (not an IntersectionObserver): a jump link such as the calculator teaser
    // moves straight past the button without it ever intersecting, which an observer would never report.
    var ticking = false;
    function show() {
      ticking = false;
      // only once the shopper is past the button, not while it is still below the fold
      var on = mobile.matches && mainButton.getBoundingClientRect().bottom < 0;
      if (on === bar.classList.contains('is-visible')) return;
      if (on) updateStickyBar();
      bar.classList.toggle('is-visible', on);
      bar.setAttribute('aria-hidden', on ? 'false' : 'true');
      barButton.tabIndex = on ? 0 : -1;
      document.body.classList.toggle('nw-sticky-atc-on', on);
    }
    function requestShow() {
      if (!ticking) {
        ticking = true;
        window.requestAnimationFrame(show);
      }
    }
    window.addEventListener('scroll', requestShow, { passive: true });
    window.addEventListener('resize', requestShow);
    if (mobile.addEventListener) mobile.addEventListener('change', requestShow);
    requestShow();

    // price, availability and button text change with the variant - keep the bar in step
    var buyBox = document.querySelector('.product-single__buy-box');
    if (buyBox) {
      new MutationObserver(updateStickyBar).observe(buyBox, { subtree: true, childList: true, characterData: true, attributes: true, attributeFilter: ['disabled'] });
    }
    updateStickyBar();
  }

  /* (10) Stamped reviews: first 3, then "See all reviews" */
  function initReviews() {
    var tries = 0;
    var timer = setInterval(function () {
      var widget = document.querySelector('#stamped-main-widget, .stamped-main-widget');
      var list = widget && widget.querySelector('.stamped-reviews');
      tries++;
      if (!list && tries < 40) return;
      clearInterval(timer);
      if (!list) return;
      if (list.querySelectorAll('.stamped-review').length <= 3 && !widget.querySelector('.stamped-pagination li')) return;
      widget.classList.add('nw-reviews-limited');
      var more = document.createElement('div');
      more.className = 'nw-reviews-more';
      more.innerHTML = '<button type="button" class="btn btn--secondary">See all reviews</button>';
      list.parentNode.insertBefore(more, list.nextSibling);
      more.querySelector('button').addEventListener('click', function () {
        widget.classList.remove('nw-reviews-limited');
        more.remove();
      });
    }, 500);
  }

  function init() {
    initStickyBar();
    initReviews();
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
