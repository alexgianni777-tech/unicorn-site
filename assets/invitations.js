(() => {
  const form = document.querySelector('#invite-form');
  const fields = ['name', 'date', 'time', 'place', 'rsvp', 'note'];
  function update() {
    fields.forEach(key => {
      const value = document.getElementById(`invite-${key}`).value.trim();
      const fallback = key === 'name' ? 'To a unicorn birthday party' : key === 'note' ? "We can't wait to celebrate with you!" : '________________________________';
      document.getElementById(`preview-${key}`).textContent = value ? (key === 'name' ? `Celebrate ${value}'s birthday!` : value) : fallback;
    });
  }
  form.addEventListener('input', update);
  form.addEventListener('submit', event => event.preventDefault());
  form.addEventListener('reset', () => setTimeout(update, 0));
  const print = document.getElementById('invite-print');
  print.hidden = false;
  print.addEventListener('click', () => { update(); window.print(); });
  update();
})();
