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
    updateUnitPrice();
  });

  /* (Gary, AC #90) Per-unit price under the total price, e.g. "$4.17 / piece" for "6 Pieces" ($24.99 total).
     Shown on mobile and desktop (AC #106). The pack count comes from the selected pack ("6 Pieces" = 6), the total from the
     buy-box price, so it follows every variant change. */
  var unitEl, variantPrices = null;

  function selectedVariantId() {
    var form = document.querySelector('.product-single__buy-box form[action*="/cart/add"], form[action*="/cart/add"][id^="AddToCartForm"]');
    var id = form && form.querySelector('[name="id"]');
    return id ? String(id.value) : '';
  }

  function updateUnitPrice() {
    if (!unitEl || !variantPrices) return;
    var pack = document.querySelector('.variant-input-wrap[data-handle="pack-size"] input[type="radio"]:checked');
    var count = pack ? parseInt(pack.value, 10) : NaN;
    var cents = variantPrices[selectedVariantId()];
    // only touch the DOM when something changed: the buy-box observer below would otherwise re-trigger itself
    if (!count || cents == null) {
      if (!unitEl.hidden) unitEl.hidden = true;
      return;
    }
    var unit = Math.round(cents / count) / 100;
    var label = '$' + unit.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' / piece';
    if (unitEl.textContent !== label) unitEl.textContent = label;
    if (unitEl.hidden) unitEl.hidden = false;
  }

  function initUnitPrice() {
    var priceBlock = document.querySelector('.product-single__buy-box .product-price');
    if (!priceBlock || !document.querySelector('.variant-input-wrap[data-handle="pack-size"]')) return;
    unitEl = document.createElement('div');
    unitEl.className = 'nw-unit-price';
    unitEl.hidden = true;
    priceBlock.appendChild(unitEl);
    // variant prices (cents) from the product JSON, so the unit price never depends on how the theme formats the total
    var handle = window.location.pathname.split('/products/')[1];
    if (!handle) return;
    fetch('/products/' + handle.split('/')[0].split('?')[0] + '.js')
      .then(function (r) { return r.json(); })
      .then(function (product) {
        variantPrices = {};
        product.variants.forEach(function (v) { variantPrices[String(v.id)] = v.price; });
        updateUnitPrice();
      })
      .catch(function () {});
    // the theme updates the hidden variant id and the price after a pack change
    var buyBox = document.querySelector('.product-single__buy-box');
    if (buyBox) new MutationObserver(updateUnitPrice).observe(buyBox, { subtree: true, childList: true, characterData: true, attributes: true, attributeFilter: ['value'] });
    document.addEventListener('change', function () { setTimeout(updateUnitPrice, 50); });
  }

  /* (Gary, AC #90) "Not Sure How Many You Need?" lands the calculator exactly under the sticky header: the fixed
     scroll-margin (150px) was taller than the mobile header and left a strip of the section above showing. */
  function headerBottom() {
    var header = document.querySelector('.header-section');
    if (!header) return 0;
    var r = header.getBoundingClientRect();
    return r.bottom > 0 ? Math.floor(r.bottom) : 0;
  }

  function scrollToCalculator(smooth) {
    var target = document.getElementById('lighting-layout-tool');
    if (!target) return;
    // +1px: the section's top edge tucks just under the header, so no sub-pixel strip of the section above can show
    var y = target.getBoundingClientRect().top + window.pageYOffset - headerBottom() + 1;
    window.scrollTo({ top: Math.max(0, y), behavior: smooth ? 'smooth' : 'auto' });
  }

  document.addEventListener('click', function (e) {
    var link = e.target.closest && e.target.closest('a[href="#lighting-layout-tool"]');
    if (!link || !document.getElementById('lighting-layout-tool')) return;
    e.preventDefault();
    scrollToCalculator(true);
    // the header can change height while scrolling (announcement bar, sticky state): settle on the exact position
    setTimeout(function () { scrollToCalculator(false); }, 900);
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
    initUnitPrice();
    initStickyBar();
    initReviews();
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
