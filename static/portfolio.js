function openSectionFromHash() {
  const id = decodeURIComponent(window.location.hash.slice(1));
  if (!id) return;
  const section = document.getElementById(id);
  if (section?.matches('details.page-section')) section.open = true;
}

window.addEventListener('hashchange', openSectionFromHash);
openSectionFromHash();
