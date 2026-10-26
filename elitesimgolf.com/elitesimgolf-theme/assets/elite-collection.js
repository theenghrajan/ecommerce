document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-elite-filter-open]').forEach((button) => {
    const drawer = document.getElementById(button.dataset.eliteFilterOpen);
    button.addEventListener('click', () => drawer.setAttribute('open', ''));
  });
  document.querySelectorAll('[data-elite-filter-close]').forEach((button) => {
    button.addEventListener('click', () => document.getElementById(button.dataset.eliteFilterClose).removeAttribute('open'));
  });
});