// No data is saved or transmitted by this printable game.
document.querySelectorAll('[data-hunt-print]').forEach(button => {
  button.hidden = false;
  button.addEventListener('click', () => {
    document.body.dataset.huntMode = button.dataset.huntPrint;
    window.print();
  });
});
window.addEventListener('afterprint', () => { delete document.body.dataset.huntMode; });
