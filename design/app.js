(() => {
  // design/app.ts
  function renderGuide() {
    const key = location.hash.slice(1) || "overview";
    const target = document.getElementById(key)?.matches("[data-guide-page]") ? key : "overview";
    document.querySelectorAll("[data-guide-page]").forEach((page) => {
      page.hidden = page.id !== target;
    });
    document.querySelectorAll("[data-guide-nav]").forEach((link) => {
      const active = link.dataset.guideNav === target;
      link.classList.toggle("menu-active", active);
      if (active) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
    });
    const title = document.getElementById(target)?.querySelector("h1")?.textContent;
    const breadcrumb = document.getElementById("guide-crumb");
    if (breadcrumb) breadcrumb.textContent = `\uD654\uBA74 / ${title ?? "\uC804\uCCB4 IA"}`;
    window.scrollTo(0, 0);
  }
  window.addEventListener("hashchange", renderGuide);
  renderGuide();
})();
