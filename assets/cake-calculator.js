function estimateCake(guests, buffer, servings) {
  if (![guests, buffer, servings].every(Number.isFinite) ||
      !Number.isInteger(guests) || guests < 1 || guests > 1000 ||
      !Number.isInteger(buffer) || buffer < 0 || buffer > 100 ||
      !Number.isInteger(servings) || servings < 1 || servings > 1000) {
    throw new RangeError('Enter whole numbers within the stated limits.');
  }
  const target = Math.ceil(guests * (100 + buffer) / 100);
  const cakes = Math.ceil(target / servings);
  return { target, cakes, total: cakes * servings, spare: cakes * servings - guests };
}
if (typeof module !== 'undefined') module.exports = { estimateCake };
if (typeof document !== 'undefined') {
  const form = document.getElementById('cake-calculator');
  const result = document.getElementById('cake-result');
  const print = document.getElementById('cake-print');
  function update() {
    if (!form.checkValidity()) {
      result.textContent = 'Enter whole numbers: 1–1,000 people, 0–100% extra and 1–1,000 servings per cake.';
      print.hidden = true;
      return;
    }
    const guests = Number(document.getElementById('cake-guests').value);
    const buffer = Number(document.getElementById('cake-buffer').value);
    const servings = Number(document.getElementById('cake-servings').value);
    const plan = estimateCake(guests, buffer, servings);
    result.innerHTML = `<h2>Order ${plan.cakes} ${plan.cakes === 1 ? 'cake' : 'cakes'} at ${servings} servings each</h2><p>For ${guests} people plus ${buffer}% extra, plan <strong>${plan.target} servings</strong>.</p><p>Your order provides ${plan.total} servings: ${plan.spare} beyond one per person, including your allowance and any rounding up to whole cakes.</p><p>Confirm these serving sizes with your baker before ordering.</p>`;
    print.hidden = false;
  }
  form.addEventListener('input', update);
  form.addEventListener('submit', event => event.preventDefault());
  print.addEventListener('click', () => window.print());
  update();
}
