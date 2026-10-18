(() => {
  // server/static/js/pattern-library.ts
  document.querySelectorAll("[data-token-value]").forEach((element) => {
    const name = element.dataset.tokenValue;
    element.textContent = getComputedStyle(element).getPropertyValue(name).trim() || "\uBBF8\uC815";
  });
  document.querySelectorAll("[data-catalog-dialog]").forEach((button) => {
    button.addEventListener("click", () => {
      const dialog = document.getElementById(button.dataset.catalogDialog);
      if (dialog instanceof HTMLDialogElement) dialog.showModal();
    });
  });
  document.querySelectorAll("[data-catalog-update-dialog]").forEach((example) => {
    const button = example.querySelector("[data-review-update]");
    const dialog = document.getElementById(example.dataset.catalogUpdateDialog);
    if (button && dialog instanceof HTMLDialogElement) {
      button.setAttribute("aria-controls", dialog.id);
      button.setAttribute("aria-haspopup", "dialog");
      button.addEventListener("click", () => dialog.showModal());
    }
  });
})();
