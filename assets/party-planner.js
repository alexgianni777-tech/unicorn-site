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
      <p class="field-help">This is a starting count, not a package recommendation or a current retailer quote. Check servings, extra adults, reusable items and pack sizes.</p>`;
  }

  form.addEventListener("input", update);
  form.addEventListener("change", update);
  form.addEventListener("submit", (event) => event.preventDefault());
  printButton.addEventListener("click", () => window.print());
  update();
}
