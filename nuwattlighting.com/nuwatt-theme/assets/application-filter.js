// (() => {
//   const APPLICATION_PARAMETER =
//     "filter.p.m.custom.commercial_application";

//   function getSelectedApplicationValues() {
//     const url = new URL(window.location.href);
//     const parameterValue = url.searchParams.get(APPLICATION_PARAMETER);

//     if (!parameterValue) {
//       return [];
//     }

//     return parameterValue
//       .split(",")
//       .map((value) => value.trim())
//       .filter(Boolean);
//   }

//   function initializeApplicationFilter(root) {
//     if (
//       !root ||
//       root.dataset.applicationFilterInitialized === "true"
//     ) {
//       return;
//     }

//     root.dataset.applicationFilterInitialized = "true";

//     const form = root.querySelector(
//       "[data-application-filter-form]"
//     );

//     const clearButton = root.querySelector(
//       "[data-application-filter-clear]"
//     );

//     if (!form) {
//       return;
//     }

//     /*
//      * Restore checked values from the current URL.
//      */
//     const selectedValues = getSelectedApplicationValues();

//     form
//       .querySelectorAll("[data-application-product-type]")
//       .forEach((checkbox) => {
//         checkbox.checked = selectedValues.includes(
//           checkbox.value.trim()
//         );
//       });

//     /*
//      * Apply the Application metafield filter.
//      */
//     form.addEventListener("submit", (event) => {
//       event.preventDefault();

//       const selectedApplicationValues = Array.from(
//         form.querySelectorAll(
//           "[data-application-product-type]:checked"
//         )
//       ).map((checkbox) => checkbox.value.trim());

//       const url = new URL(window.location.href);

//       /*
//        * Preserve existing Shopify filters.
//        */
//       url.searchParams.delete(APPLICATION_PARAMETER);

//       /*
//        * Return to page one after changing filters.
//        */
//       url.searchParams.delete("page");

//       if (selectedApplicationValues.length > 0) {
//         /*
//          * Multiple values use OR logic:
//          *
//          * Panel Lights OR Flood Lights OR Tube Lights
//          */
//         url.searchParams.set(
//           APPLICATION_PARAMETER,
//           selectedApplicationValues.join(",")
//         );
//       }

//       window.location.href = url.toString();
//     });

//     /*
//      * Clear only the custom Application filter.
//      * Existing price and other filters remain active.
//      */
//     if (clearButton) {
//       clearButton.addEventListener("click", () => {
//         const url = new URL(window.location.href);

//         url.searchParams.delete(APPLICATION_PARAMETER);
//         url.searchParams.delete("page");

//         window.location.href = url.toString();
//       });
//     }
//   }

//   function initializeApplicationFilters() {
//     document
//       .querySelectorAll("[data-application-filter]")
//       .forEach(initializeApplicationFilter);
//   }

//   document.addEventListener(
//     "DOMContentLoaded",
//     initializeApplicationFilters
//   );

//   document.addEventListener(
//     "shopify:section:load",
//     initializeApplicationFilters
//   );

//   const observer = new MutationObserver(() => {
//     initializeApplicationFilters();
//   });

//   observer.observe(document.documentElement, {
//     childList: true,
//     subtree: true
//   });
// })();
