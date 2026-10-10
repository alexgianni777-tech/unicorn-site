// Keep the calculated list and its useful links available outside the page.
function addPlanDownload(result, title, filename, source) {
  const links = [...result.querySelectorAll('a[href]')].map(link =>
    link.textContent.trim() + ': ' + new URL(link.getAttribute('href'), source).href
  );
  const text = title + '\n\n' + result.innerText +
    (links.length ? '\n\nUseful links:\n' + [...new Set(links)].join('\n') : '') +
    '\n\nSource: ' + source + '\nEstimates only. Check sizes, quantities and current retailer details before buying.\n';
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'button pc-button plan-download';
  button.textContent = 'Download shopping list (.txt)';
  button.addEventListener('click', () => {
    const url = URL.createObjectURL(new Blob([text], {type: 'text/plain;charset=utf-8'}));
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 30000);
  });
  result.append(button);
  if (typeof navigator !== 'undefined' && navigator.clipboard && navigator.clipboard.writeText) {
    const copy = document.createElement('button');
    copy.type = 'button';
    copy.className = 'button pc-button plan-download';
    copy.textContent = 'Copy shopping list';
    const status = document.createElement('p');
    status.className = 'plan-download';
    status.setAttribute('role', 'status');
    copy.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(text);
        status.textContent = 'Copied. Paste your list into notes or a message.';
      } catch (_) {
        status.textContent = 'Copy was unavailable. Use Download shopping list to keep a copy.';
      }
    });
    result.append(document.createTextNode(' '), copy, status);
  }
}

// All figures are estimates based only on visitor-entered numbers.
function estimateParty({ guests, hosts, buffer, food, favor, cake, decor, activities, other = 0 }) {
  const people = guests + hosts;
  return {
    people,
    placeSettings: Math.ceil(people * (1 + buffer / 100)),
    favors: guests,
    total: food * people + favor * guests + cake + decor + activities + other,
  };
}

function estimatePacks(quantity, packSize) {
  const packs = Math.ceil(quantity / packSize);
  return { packs, supplied: packs * packSize, spare: packs * packSize - quantity };
}

if (typeof document !== "undefined") {
  const form = document.getElementById("party-planner");
  const result = document.getElementById("party-result");
  const printButton = document.getElementById("party-print");

  function value(id) {
    const raw = document.getElementById(id).value;
    return raw === "" ? 0 : Number(raw);
  }

  function update() {
    if (!form.checkValidity()) {
      result.innerHTML = "<h2>Your starting list</h2><p>Check the fields above. Guests and pack sizes must be positive whole numbers; other counts and costs cannot be negative.</p>";
      return;
    }

    const guests = value("party-guests");
    const hosts = value("party-hosts");
    const estimate = estimateParty({
      guests,
      hosts,
      buffer: value("party-buffer"),
      food: value("party-food"),
      favor: value("party-favor"),
      cake: value("party-cake"),
      decor: value("party-decor"),
      activities: value("party-activities"),
      other: value("party-other"),
    });
    const currency = document.getElementById("party-currency").value;
    const money = new Intl.NumberFormat(undefined, { style: "currency", currency });
    const hasCosts = ["party-food", "party-favor", "party-cake", "party-decor", "party-activities", "party-other"]
      .some((id) => document.getElementById(id).value !== "");

    const packs = [
      ["Plates", estimate.placeSettings, value("party-plate-pack")],
      ["Cups", estimate.placeSettings, value("party-cup-pack")],
      ["Favor bags", estimate.favors, value("party-bag-pack")],
    ].map(([name, needed, size]) => {
      const count = estimatePacks(needed, size);
      return `<li><strong>${name}: ${count.packs} pack${count.packs === 1 ? "" : "s"} of ${size}</strong><br>${needed} needed · ${count.supplied} supplied · ${count.spare} spare beyond your planned count.</li>`;
    }).join("");
    const hasTarget = document.getElementById("party-target").value !== "";
    const remaining = value("party-target") - estimate.total;
    const budgetStatus = hasTarget ? `<p class="budget-status">${hasCosts ? (remaining >= 0 ? `${money.format(remaining)} left within your target` : `${money.format(-remaining)} over your target`) : "Enter estimated costs to compare with your target"}. Blank costs count as zero; include delivery and tax in your estimates.</p>` : "";
    result.innerHTML = `<h2>Your starting list</h2>
      <p><strong>${estimate.people} people</strong> including ${guests} invited guests and ${hosts} other people.</p>
      <ul><li><strong>${estimate.placeSettings} plates and ${estimate.placeSettings} cups</strong> if using one of each per person, with your chosen extra allowance.</li>
      <li><strong>${estimate.favors} favors</strong> if giving one to each invited guest.</li></ul>
      <h3>Packs to compare</h3><ul class="pack-list">${packs}</ul>
      <p><strong>Estimated budget: ${hasCosts ? money.format(estimate.total) : "add your own costs above"}</strong>${hasCosts ? ` · ${money.format(estimate.total / estimate.people)} per person` : ""}.</p>
      ${budgetStatus}
      <h3>Your next step</h3>
      <p>${hasTarget && hasCosts && remaining < 0 ? "Your estimate is over your target. Check reusable tableware and reduce optional favors or decorations before ordering." : "Check what you already own, then compare the pack counts above with each listing. Mixed sets may contain different numbers of plates, cups and bags."}</p>
      <p><a class="button" href="#party-shopping">Check supplies and Amazon options</a> · <a href="/tools/unicorn-party-games.html">Use free printable party games</a></p>
      <p class="field-help">This is a starting count, not a package recommendation or a current retailer quote. Check servings, extra adults, reusable items and pack sizes.</p>`;
    addPlanDownload(result, "Unicorn party shopping list", "unicorn-party-shopping-list.txt", "https://unicornsite.online/tools/unicorn-party-planner.html");
  }

  form.addEventListener("input", update);
  form.addEventListener("change", update);
  form.addEventListener("submit", (event) => event.preventDefault());
  printButton.addEventListener("click", () => window.print());
  update();
}


// Saving is opt-in and stays in this browser; no plan values are sent to a server.
(() => {
  if (typeof document === 'undefined') return;
  const form = document.getElementById('party-planner');
  if (!form) return;
  const key = 'unicorn-party-calculator-v1';
  const fields = [...form.querySelectorAll('input[id], select[id]')]
    .filter(field => field.type === 'number' || field.tagName === 'SELECT');
  const panel = document.createElement('section');
  panel.className = 'plan-save-controls';
  panel.setAttribute('aria-label', 'Save your calculator');
  const help = document.createElement('p');
  help.textContent = 'Coming back later? Save your calculator values in this browser. Checklist ticks are not saved. Nothing is uploaded; clearing browser data removes the saved plan.';
  const save = document.createElement('button');
  save.type = 'button'; save.className = 'button'; save.textContent = 'Save calculator';
  const forget = document.createElement('button');
  forget.type = 'button'; forget.className = 'button'; forget.textContent = 'Forget saved calculator';
  const status = document.createElement('p');
  status.setAttribute('role', 'status');
  panel.append(help, save, document.createTextNode(' '), forget, status);
  form.after(panel);
  const style = document.createElement('style');
  style.textContent = '.plan-save-controls{margin:1rem 0;padding:1rem;border:1px solid currentColor;border-radius:12px}.plan-save-controls button{margin:.25rem;min-height:44px}.plan-save-controls p{margin:.5rem 0}@media print{.plan-save-controls,.plan-download{display:none}}';
  document.head.append(style);
  let saved = false;
  try {
    const raw = localStorage.getItem(key);
    if (raw) {
      const data = JSON.parse(raw);
      if (data.version !== 1 || !data.values || typeof data.values !== 'object') throw new Error('Invalid saved plan');
      const originals = fields.map(field => field.value);
      for (const field of fields) {
        const val = data.values[field.id];
        if (typeof val !== 'string' || val.length > 32) continue;
        if (field.tagName === 'SELECT' && ![...field.options].some(option => option.value === val)) continue;
        if (field.type === 'number' && val !== '' && !Number.isFinite(Number(val))) continue;
        field.value = val;
      }
      if (!form.checkValidity()) {
        fields.forEach((field, index) => { field.value = originals[index]; });
        throw new Error('Invalid saved plan');
      }
      form.dispatchEvent(new Event('input', {bubbles: true}));
      form.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
      saved = true;
      status.textContent = 'Saved calculator restored. Save again after changing values.';
    }
  } catch (_) {
    status.textContent = 'The saved calculator could not be restored. You can still calculate and print.';
  }
  save.addEventListener('click', () => {
    if (!form.reportValidity()) return;
    try {
      localStorage.setItem(key, JSON.stringify({version: 1, values: Object.fromEntries(fields.map(field => [field.id, field.value]))}));
      saved = true;
      status.textContent = 'Saved in this browser. Return to this page to continue.';
    } catch (_) {
      status.textContent = 'This browser could not save the calculator. Print your plan to keep a copy.';
    }
  });
  forget.addEventListener('click', () => {
    try {
      localStorage.removeItem(key);
      saved = false;
      status.textContent = 'Saved copy removed. Your current values stay on screen until you leave.';
    } catch (_) {
      status.textContent = 'The saved copy could not be removed. Use your browser settings to clear this site’s data.';
    }
  });
  form.addEventListener('input', () => {
    if (saved) status.textContent = 'Changes are not saved yet. Select Save calculator to keep them.';
  });
})();
