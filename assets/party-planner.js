// All figures are estimates based only on visitor-entered numbers.
function estimateParty({ guests, hosts, buffer, food, favor, cake, decor, activities }) {
  const people = guests + hosts;
  return {
    people,
    placeSettings: Math.ceil(people * (1 + buffer / 100)),
    favors: guests,
    total: food * people + favor * guests + cake + decor + activities,
  };
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
      result.innerHTML = "<h2>Your starting list</h2><p>Use whole, non-negative numbers for people and supplies, and non-negative amounts for costs.</p>";
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
    });
    const currency = document.getElementById("party-currency").value;
    const money = new Intl.NumberFormat(undefined, { style: "currency", currency });
    const hasCosts = ["party-food", "party-favor", "party-cake", "party-decor", "party-activities"]
      .some((id) => document.getElementById(id).value !== "");

    result.innerHTML = `<h2>Your starting list</h2>
      <p><strong>${estimate.people} people</strong> including ${guests} invited guests and ${hosts} other people.</p>
      <ul><li><strong>${estimate.placeSettings} plates and ${estimate.placeSettings} cups</strong> if using one of each per person, with your chosen extra allowance.</li>
      <li><strong>${estimate.favors} favors</strong> if giving one to each invited guest.</li></ul>
      <p><strong>Estimated budget: ${hasCosts ? money.format(estimate.total) : "add your own costs above"}</strong>${hasCosts ? ` · ${money.format(estimate.total / estimate.people)} per person` : ""}.</p>
      <p class="field-help">This is a starting count, not a package recommendation or a current retailer quote. Check servings, extra adults, reusable items and pack sizes.</p>`;
  }

  form.addEventListener("input", update);
  form.addEventListener("change", update);
  form.addEventListener("submit", (event) => event.preventDefault());
  printButton.addEventListener("click", () => window.print());
  update();
}
