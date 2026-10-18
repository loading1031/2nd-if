// Catalog only: read resolved theme values and open the real dialog component.
document.querySelectorAll<HTMLElement>('[data-token-value]').forEach(element => {
  const name = element.dataset.tokenValue!;
  element.textContent = getComputedStyle(element).getPropertyValue(name).trim() || '미정';
});
document.querySelectorAll<HTMLButtonElement>('[data-catalog-dialog]').forEach(button => {
  button.addEventListener('click', () => {
    const dialog = document.getElementById(button.dataset.catalogDialog!);
    if (dialog instanceof HTMLDialogElement) dialog.showModal();
  });
});

// A composed example opens only the dialog belonging to this setting-book row.
document.querySelectorAll<HTMLElement>('[data-catalog-update-dialog]').forEach(example => {
  const button = example.querySelector<HTMLButtonElement>('[data-review-update]');
  const dialog = document.getElementById(example.dataset.catalogUpdateDialog!);
  if (button && dialog instanceof HTMLDialogElement) {
    button.setAttribute('aria-controls', dialog.id);
    button.setAttribute('aria-haspopup', 'dialog');
    button.addEventListener('click', () => dialog.showModal());
  }
});
