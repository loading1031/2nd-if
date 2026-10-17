function renderGuide(): void {
  const key = location.hash.slice(1) || 'overview';
  const target = document.getElementById(key)?.matches('[data-guide-page]') ? key : 'overview';
  document.querySelectorAll<HTMLElement>('[data-guide-page]').forEach(page => { page.hidden = page.id !== target; });
  document.querySelectorAll<HTMLAnchorElement>('[data-guide-nav]').forEach(link => {
    const active = link.dataset.guideNav === target;
    link.classList.toggle('menu-active', active);
    if (active) link.setAttribute('aria-current', 'page');
    else link.removeAttribute('aria-current');
  });
  const title = document.getElementById(target)?.querySelector('h1')?.textContent;
  const breadcrumb = document.getElementById('guide-crumb');
  if (breadcrumb) breadcrumb.textContent = `화면 / ${title ?? '전체 IA'}`;
  window.scrollTo(0, 0);
}
window.addEventListener('hashchange', renderGuide);
renderGuide();
