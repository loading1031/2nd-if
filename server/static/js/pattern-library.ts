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
