(() => {
  const form = document.getElementById('shop-filter');
  if (!form) return;
  const search = document.getElementById('shop-search');
  const type = document.getElementById('shop-type');
  const status = document.getElementById('shop-count');
  const empty = document.getElementById('shop-empty');
  const sections = [...document.querySelectorAll('#shop .category')];
  const cards = sections.flatMap(section => [...section.querySelectorAll('.product')].map(card => ({card, section, text: card.querySelector('.product-content').textContent.toLowerCase()})));

  // Ordinary URLs let visitors bookmark or share the exact visible selection.
  const resultLink = document.createElement('a');
  resultLink.textContent = 'Link to these results';
  resultLink.className = 'button';
  const linkHelp = document.createElement('p');
  linkHelp.textContent = 'Open this link to bookmark your selection, or copy the link to share it.';
  linkHelp.append(document.createTextNode(' '), resultLink);
  form.append(linkHelp);
  const incoming = new URLSearchParams(location.search);
  search.value = (incoming.get('q') || '').slice(0, 120);
  const requestedFilter = incoming.get('type');
  if ([...type.options].map(option => option.value).includes(requestedFilter)) type.value = requestedFilter;
  function updateResultLink() {
    const url = new URL(location.pathname, location.origin);
    const text = search.value.trim().slice(0, 120);
    if (text) url.searchParams.set('q', text);
    if (type.value !== 'all') url.searchParams.set('type', type.value);
    url.hash = 'shop';
    resultLink.href = url.href;
  }
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
    updateResultLink();
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
