// ../../node_modules/@archetype-themes/next/sections/background-image-text/src/scripts/index.js


var BackgroundImage = class extends HTMLElement {
  constructor() {
    super();
    this.el = this.querySelector('[data-section-type="background-image"]');
    this.sectionId = this.el.dataset.sectionId;
    theme.initWhenVisible({
      element: this.el,
      callback: this.init.bind(this)
    });
  }
  init() {
    this.el.classList.remove("loading", "loading--delayed");
    this.el.classList.add("loaded");
  }
};
customElements.define("background-image", BackgroundImage);

// ../../node_modules/@archetype-themes/next/sections/faq/src/scripts/index.js
var FAQ = class extends HTMLElement {
  constructor() {
    super();
    theme.collapsibles = function() {
      var selectors = {
        trigger: ".collapsible-trigger",
        module: ".collapsible-content",
        moduleInner: ".collapsible-content__inner",
        tabs: ".collapsible-trigger--tab"
      };
      var classes = {
        hide: "hide",
        open: "is-open",
        autoHeight: "collapsible--auto-height",
        tabs: "collapsible-trigger--tab"
      };
      var namespace = ".collapsible";
      var isTransitioning = false;
      function init(scope) {
        var el = scope ? scope : document;
        el.querySelectorAll(selectors.trigger).forEach((trigger) => {
          var state = trigger.classList.contains(classes.open);
          trigger.setAttribute("aria-expanded", state);
          trigger.off("click" + namespace);
          trigger.on("click" + namespace, toggle);
        });
      }
      function toggle(evt) {
        if (isTransitioning) {
          return;
        }
        isTransitioning = true;
        var el = evt.currentTarget;
        var isOpen = el.classList.contains(classes.open);
        var isTab = el.classList.contains(classes.tabs);
        var moduleId = el.getAttribute("aria-controls");
        var container = document.getElementById(moduleId);
        if (!moduleId) {
          moduleId = el.dataset.controls;
        }
        if (!moduleId) {
          return;
        }
        if (!container) {
          var multipleMatches = document.querySelectorAll('[data-id="' + moduleId + '"]');
          if (multipleMatches.length > 0) {
            container = el.parentNode.querySelector('[data-id="' + moduleId + '"]');
          }
        }
        if (!container) {
          isTransitioning = false;
          return;
        }
        var height = container.querySelector(selectors.moduleInner).offsetHeight;
        var isAutoHeight = container.classList.contains(classes.autoHeight);
        var parentCollapsibleEl = container.parentNode.closest(selectors.module);
        var childHeight = height;
        if (isTab) {
          if (isOpen) {
            isTransitioning = false;
            return;
          }
          var newModule;
          document.querySelectorAll(selectors.tabs + '[data-id="' + el.dataset.id + '"]').forEach((el2) => {
            el2.classList.remove(classes.open);
            newModule = document.querySelector("#" + el2.getAttribute("aria-controls"));
            setTransitionHeight(newModule, 0, true);
          });
        }
        if (isOpen && isAutoHeight) {
          setTimeout(function() {
            height = 0;
            setTransitionHeight(container, height, isOpen, isAutoHeight);
          }, 0);
        }
        if (isOpen && !isAutoHeight) {
          height = 0;
        }
        el.setAttribute("aria-expanded", !isOpen);
        if (isOpen) {
          el.classList.remove(classes.open);
        } else {
          el.classList.add(classes.open);
        }
        setTransitionHeight(container, height, isOpen, isAutoHeight);
        if (parentCollapsibleEl) {
          var parentHeight = parentCollapsibleEl.style.height;
          if (isOpen && parentHeight === "auto") {
            childHeight = 0;
          }
          var totalHeight = isOpen ? parentCollapsibleEl.offsetHeight - childHeight : height + parentCollapsibleEl.offsetHeight;
          setTransitionHeight(parentCollapsibleEl, totalHeight, false, false);
        }
        if (window.SPR) {
          var btn = container.querySelector(".spr-summary-actions-newreview");
          if (!btn) {
            return;
          }
          btn.off("click" + namespace);
          btn.on("click" + namespace, function() {
            height = container.querySelector(selectors.moduleInner).offsetHeight;
            setTransitionHeight(container, height, isOpen, isAutoHeight);
          });
        }
      }
      function setTransitionHeight(container, height, isOpen, isAutoHeight) {
        container.classList.remove(classes.hide);
        theme.utils.prepareTransition(container, function() {
          container.style.height = height + "px";
          if (isOpen) {
            container.classList.remove(classes.open);
          } else {
            container.classList.add(classes.open);
          }
        });
        if (!isOpen && isAutoHeight) {
          var o = container;
          window.setTimeout(function() {
            o.css("height", "auto");
            isTransitioning = false;
          }, 500);
        } else {
          isTransitioning = false;
        }
      }
      return {
        init
      };
    }();
  }
  connectedCallback() {
    theme.collapsibles.init(this);
  }
};
customElements.define("collapsible-elements", FAQ);

// ../../node_modules/@archetype-themes/next/sections/image-compare/src/scripts/index.js
var ImageCompare = class extends HTMLElement {
  constructor() {
    super();
    this.el = this;
    this.sectionId = this.dataset.sectionId;
    this.button = this.querySelector("[data-button]");
    this.draggableContainer = this.querySelector("[data-draggable]");
    this.primaryImage = this.querySelector("[data-primary-image]");
    this.secondaryImage = this.querySelector("[data-secondary-image]");
    this.calculateSizes();
    this.active = false;
    this.currentX = 0;
    this.initialX = 0;
    this.xOffset = 0;
    this.buttonOffset = this.button.offsetWidth / 2;
    this.el.addEventListener("touchstart", this.dragStart, false);
    this.el.addEventListener("touchend", this.dragEnd, false);
    this.el.addEventListener("touchmove", this.drag, false);
    this.el.addEventListener("mousedown", this.dragStart, false);
    this.el.addEventListener("mouseup", this.dragEnd, false);
    this.el.addEventListener("mousemove", this.drag, false);
    window.on("resize", theme.utils.debounce(250, () => {
      this.calculateSizes(true);
    }));
    document.addEventListener("shopify:section:load", (event) => {
      if (event.detail.sectionId === this.sectionId && this.primaryImage !== null) {
        this.calculateSizes();
      }
    });
  }
  calculateSizes(hasResized = false) {
    this.active = false;
    this.currentX = 0;
    this.initialX = 0;
    this.xOffset = 0;
    this.buttonOffset = this.button.offsetWidth / 2;
    this.elWidth = this.el.offsetWidth;
    this.button.style.transform = `translate(-${this.buttonOffset}px, -50%)`;
    if (this.primaryImage) {
      this.primaryImage.style.width = `${this.elWidth}px`;
    }
    if (hasResized)
      this.draggableContainer.style.width = `${this.elWidth / 2}px`;
  }
  dragStart(e) {
    if (e.type === "touchstart") {
      this.initialX = e.touches[0].clientX - this.xOffset;
    } else {
      this.initialX = e.clientX - this.xOffset;
    }
    if (e.target === this.button) {
      this.active = true;
    }
  }
  dragEnd(e) {
    this.initialX = this.currentX;
    this.active = false;
  }
  drag(e) {
    if (this.active) {
      e.preventDefault();
      if (e.type === "touchmove") {
        this.currentX = e.touches[0].clientX - this.initialX;
      } else {
        this.currentX = e.clientX - this.initialX;
      }
      this.xOffset = this.currentX;
      this.setTranslate(this.currentX, this.button);
    }
  }
  setTranslate(xPos, el) {
    let newXpos = xPos - this.buttonOffset;
    let newVal = this.elWidth / 2 + xPos;
    const boundaryPadding = 50;
    const XposMin = (this.elWidth / 2 + this.buttonOffset) * -1;
    const XposMax = this.elWidth / 2 - this.buttonOffset;
    if (newXpos < XposMin + boundaryPadding) {
      newXpos = XposMin + boundaryPadding;
      newVal = boundaryPadding;
    } else if (newXpos > XposMax - boundaryPadding) {
      newXpos = XposMax - boundaryPadding;
      newVal = this.elWidth - boundaryPadding;
    }
    el.style.transform = `translate(${newXpos}px, -50%)`;
    this.draggableContainer.style.width = `${newVal}px`;
  }
};
customElements.define("image-compare", ImageCompare);

// ../../node_modules/@archetype-themes/next/sections/countdown/src/scripts/index.js
var CountdownTimer = class extends HTMLElement {
  constructor() {
    super();
    this.el = this;
    this.display = this.querySelector("[data-time-display]");
    this.block = this.closest(".countdown__block--timer");
    this.year = this.el.dataset.year;
    this.month = this.el.dataset.month;
    this.day = this.el.dataset.day;
    this.hour = this.el.dataset.hour;
    this.minute = this.el.dataset.minute;
    this.daysPlaceholder = this.querySelector("[date-days-placeholder]");
    this.hoursPlaceholder = this.querySelector("[date-hours-placeholder]");
    this.minutesPlaceholder = this.querySelector("[date-minutes-placeholder]");
    this.secondsPlaceholder = this.querySelector("[date-seconds-placeholder]");
    this.messagePlaceholder = this.querySelector("[data-message-placeholder]");
    this.hideTimerOnComplete = this.el.dataset.hideTimer;
    this.completeMessage = this.el.dataset.completeMessage;
    this.timerComplete = false;
    this.init();
  }
  init() {
    setInterval(() => {
      if (!this.timerComplete) {
        this._calculate();
      }
    }, 1e3);
  }
  _calculate() {
    const timeDifference = +(/* @__PURE__ */ new Date(`${this.month}/${this.day}/${this.year} ${this.hour}:${this.minute}:00`)).getTime() - +(/* @__PURE__ */ new Date()).getTime();
    if (timeDifference > 0) {
      const intervals = {
        days: Math.floor(timeDifference / (1e3 * 60 * 60 * 24)),
        hours: Math.floor(timeDifference / (1e3 * 60 * 60) % 24),
        minutes: Math.floor(timeDifference / 1e3 / 60 % 60),
        seconds: Math.floor(timeDifference / 1e3 % 60)
      };
      this.daysPlaceholder.innerHTML = intervals.days;
      this.hoursPlaceholder.innerHTML = intervals.hours;
      this.minutesPlaceholder.innerHTML = intervals.minutes;
      this.secondsPlaceholder.innerHTML = intervals.seconds;
    } else {
      if (this.completeMessage && this.messagePlaceholder) {
        this.messagePlaceholder.classList.add("countdown__timer-message--visible");
      }
      if (this.hideTimerOnComplete === "true") {
        this.display.classList.remove("countdown__display--visible");
        this.display.classList.add("countdown__display--hidden");
      }
      if (!this.completeMessage && this.hideTimerOnComplete === "true") {
        this.block.classList.add("countdown__block--hidden");
      }
      this.timerComplete = true;
    }
  }
};
customElements.define("countdown-timer", CountdownTimer);

// ../../node_modules/@archetype-themes/next/sections/age-verification-popup/src/scripts/index.js
var AgeVerificationPopup = class extends HTMLElement {
  constructor() {
    super();
    this.cookieName = this.id;
    this.cookie = Cookies.get(this.cookieName);
    this.classes = {
      activeContent: "age-verification-popup__content--active",
      inactiveContent: "age-verification-popup__content--inactive",
      inactiveDeclineContent: "age-verification-popup__decline-content--inactive",
      activeDeclineContent: "age-verification-popup__decline-content--active"
    };
    this.declineButton = this.querySelector("[data-age-verification-popup-decline-button]");
    this.declineContent = this.querySelector("[data-age-verification-popup-decline-content]");
    this.content = this.querySelector("[data-age-verification-popup-content]");
    this.returnButton = this.querySelector("[data-age-verification-popup-return-button]");
    this.exitButton = this.querySelector("[data-age-verification-popup-exit-button]");
    this.backgroundImage = this.querySelector("[data-background-image]");
    this.mobileBackgroundImage = this.querySelector("[data-mobile-background-image]");
    if (Shopify.designMode) {
      document.addEventListener("shopify:section:select", (event) => {
        if (event.detail.sectionId === this.dataset.sectionId) {
          this.init();
        }
      });
      document.addEventListener("shopify:section:load", (event) => {
        if (event.detail.sectionId === this.dataset.sectionId) {
          this.init();
          if (this.dataset.testMode === "true" && this.cookie) {
            Cookies.remove(this.cookieName);
          }
          const secondViewVisited = sessionStorage.getItem(this.id);
          if (!secondViewVisited)
            return;
          this.showDeclineContent();
        }
      });
      document.addEventListener("shopify:section:unload", (event) => {
        if (event.detail.sectionId === this.dataset.sectionId) {
          this.modal.close();
        }
      });
    }
    if (this.cookie && this.dataset.testMode === "false")
      return;
    this.init();
  }
  init() {
    this.modal = new theme.Modals(this.id, "age-verification-popup-modal", {
      closeOffContentClick: false
    });
    if (this.backgroundImage) {
      this.backgroundImage.style.display = "block";
    }
    if (theme.config.bpSmall && this.mobileBackgroundImage) {
      this.mobileBackgroundImage.style.display = "block";
    }
    this.modal.open();
    theme.a11y.lockMobileScrolling(`#${this.id}`, document.querySelector("#MainContent"));
    if (this.declineButton) {
      this.declineButton.addEventListener("click", (e) => {
        e.preventDefault();
        this.showDeclineContent();
        if (Shopify.designMode) {
          sessionStorage.setItem(this.id, "second-view");
        }
      });
    }
    if (this.returnButton) {
      this.returnButton.addEventListener("click", (e) => {
        e.preventDefault();
        this.hideDeclineContent();
        const secondViewVisited = sessionStorage.getItem(this.id);
        if (Shopify.designMode && secondViewVisited) {
          sessionStorage.removeItem(this.id);
        }
      });
    }
    if (this.exitButton) {
      this.exitButton.addEventListener("click", (e) => {
        e.preventDefault();
        if (this.dataset.testMode === "false") {
          Cookies.set(this.cookieName, "entered", { expires: 30, sameSite: "none", secure: true });
        }
        if (this.backgroundImage) {
          this.backgroundImage.style.display = "none";
        }
        if (theme.config.bpSmall && this.mobileBackgroundImage) {
          this.mobileBackgroundImage.style.display = "none";
        }
        this.modal.close();
        theme.a11y.unlockMobileScrolling(`#${this.id}`, document.querySelector("#MainContent"));
      });
    }
  }
  showDeclineContent() {
    this.declineContent.classList.remove(this.classes.inactiveDeclineContent);
    this.declineContent.classList.add(this.classes.activeDeclineContent);
    this.content.classList.add(this.classes.inactiveContent);
    this.content.classList.remove(this.classes.activeContent);
  }
  hideDeclineContent() {
    this.declineContent.classList.add(this.classes.inactiveDeclineContent);
    this.declineContent.classList.remove(this.classes.activeDeclineContent);
    this.content.classList.remove(this.classes.inactiveContent);
    this.content.classList.add(this.classes.activeContent);
  }
};
customElements.define("age-verification-popup", AgeVerificationPopup);
//# sourceMappingURL=next.js.map
