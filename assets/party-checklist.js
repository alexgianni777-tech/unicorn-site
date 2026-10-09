(() => {
  const heading = document.getElementById('party-supplies-checklist');
  if (!heading) return;
  const inputs = [];
  let node = heading.nextElementSibling;
  while (node && node.tagName !== 'H2') {
    if (node.tagName === 'UL') {
      node.classList.add('party-tick-list');
      node.querySelectorAll('li').forEach(item => {
        const label = document.createElement('label');
        const input = document.createElement('input');
        input.type = 'checkbox';
        const text = document.createElement('span');
        text.textContent = item.textContent;
        label.append(input, text);
        item.replaceChildren(label);
        inputs.push(input);
      });
    }
    node = node.nextElementSibling;
  }
  const status = document.createElement('p');
  status.setAttribute('role', 'status');
  status.setAttribute('aria-live', 'polite');
  const note = document.createElement('p');
  note.textContent = 'Tick items as you arrange them. Optional items can stay unticked. Progress lasts until you reload this page.';
  const update = () => {
    status.textContent = inputs.filter(input => input.checked).length + ' of ' + inputs.length + ' items arranged';
  };
  inputs.forEach(input => input.addEventListener('change', update));
  heading.after(note, status);
  const style = document.createElement('style');
  style.textContent = '.party-tick-list{list-style:none;padding-left:0}.party-tick-list label{display:flex;align-items:flex-start;gap:.75rem;padding:.6rem 0;cursor:pointer}.party-tick-list input{flex-shrink:0;width:1.2rem;height:1.2rem;margin-top:.2rem;accent-color:#713664}.party-tick-list input:checked+span{text-decoration:line-through;color:#655769}.party-tick-list input:focus-visible{outline:3px solid #713664;outline-offset:3px}';
  document.head.append(style);
  update();
})();
