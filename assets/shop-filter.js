(() => {
  const form = document.getElementById('shop-filter');
  if (!form) return;
  const search = document.getElementById('shop-search');
  const type = document.getElementById('shop-type');
  const status = document.getElementById('shop-count');
  const empty = document.getElementById('shop-empty');
  const sections = [...document.querySelectorAll('#shop .category')];
  const cards = sections.flatMap(section => [...section.querySelectorAll('.product')].map(card => ({card, section, text: card.querySelector('.product-content').textContent.toLowerCase()})));
  function update() {
    const words = search.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
    let count = 0;
    cards.forEach(({card, section, text}) => {
      card.hidden = (type.value !== 'all' && section.id !== type.value) || !words.every(word => text.includes(word));
      if (!card.hidden) count++;
    });
    sections.forEach(section => { section.hidden = !cards.some(item => item.section === section && !item.card.hidden); });
    status.textContent = `${count} of ${cards.length} gift ideas shown`;
    empty.hidden = count !== 0;
  }
  function clear() { search.value = ''; type.value = 'all'; update(); }
  function revealAnchor() {
    const id = location.hash.slice(1);
    if (!cards.some(item => item.card.id === id || item.section.id === id)) return;
    clear();
    document.getElementById(id).scrollIntoView({block:'start'});
  }
  form.hidden = false;
  form.addEventListener('submit', event => event.preventDefault());
  search.addEventListener('input', update);
  type.addEventListener('change', update);
  document.getElementById('shop-clear').addEventListener('click', () => {clear();search.focus();});
  window.addEventListener('hashchange', revealAnchor);
  // A repeated click on the same fragment does not cause hashchange.
  document.querySelectorAll('a[href^="#"]').forEach(link => link.addEventListener('click', () => {
    const id = link.getAttribute('href').slice(1);
    if (cards.some(item => item.card.id === id || item.section.id === id)) clear();
  }));
  update();
  if (location.hash) revealAnchor();
})();
