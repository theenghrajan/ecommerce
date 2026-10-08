document.addEventListener("DOMContentLoaded", function() {
  const cards = document.querySelectorAll(".product-type-card");
  const isTouch = window.matchMedia("(hover: none)").matches;

  cards.forEach((card) => {
    if (isTouch) {
      card.addEventListener("click", () => {
        if (!card.classList.contains("is-open")) {
          cards.forEach((c) => c.classList.remove("is-open"));
          card.classList.add("is-open");
        }
      });
    } else {
      card.addEventListener("mouseenter", () => {
        cards.forEach((c) => c.classList.remove("is-open"));
        card.classList.add("is-open");
      });
    }
  });
});