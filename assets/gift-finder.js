const MODES = {
  everyday: {
    title: "Everyday gift ideas",
    text: "These are easy to understand because they fit familiar routines. Check the exact size, design and care instructions before buying.",
    products: ["mug-set", "tumbler", "sculpted-mug"],
  },
  glow: {
    title: "Room glow ideas",
    text: "Choose between a compact local light, a larger projection effect, or a broader Amazon comparison.",
    products: ["cloud-lamp", "projector", "night-light-search"],
  },
  creative: {
    title: "Creative and room-decor ideas",
    text: "These work best when the recipient enjoys making, styling or changing a space. Check dimensions and included parts.",
    products: ["planters", "wall-art", "pillow-cover"],
  },
  small: {
    title: "Small surprise ideas",
    text: "Useful when you want a smaller present and do not want to guess too much about room size or decor.",
    products: ["keychain", "mug-set", "pillow-cover"],
  },
};

const CHOICE_HELP = {
 everyday: 'Compare by routine: a mug set for a gift box, a tumbler for carrying drinks, or a sculpted mug for a decorative desk gift.',
 glow: 'Compare by effect: a compact lamp for a local glow, a projector for patterns across the room, or search results to explore more styles.',
 creative: 'Compare by activity: planters for a hands-on idea, wall art for an empty wall, or a pillow cover for an existing cushion.',
 small: 'Compare by fit: a keychain for a bag, a mug set for a small gift box, or a pillow cover when you know the cushion size. Small does not necessarily mean low-priced.',
};

if (typeof document !== "undefined") {
  const result = document.getElementById("finder-result");
  const templates = document.getElementById("finder-products");
  const buttons = [...document.querySelectorAll(".finder-choice")];

  function render(mode) {
    const config = MODES[mode];
    if (!config || !result || !templates) return;

    const picks = config.products.map((id) => {
      const template = templates.querySelector(`template[data-product="${id}"]`);
      return template ? template.innerHTML : "";
    }).join("");

    result.innerHTML = `<h2>${config.title}</h2><p>${config.text}</p><p class="finder-check"><strong>How to choose:</strong> ${CHOICE_HELP[mode]}</p><div class="finder-picks">${picks}</div>`;

    buttons.forEach((button) => {
      const active = button.dataset.mode === mode;
      button.setAttribute("aria-pressed", active ? "true" : "false");
    });
  }

  function fromAddress() {
    const mode = location.hash.slice(1);
    render(Object.hasOwn(MODES, mode) ? mode : "everyday");
  }
  fromAddress();
  window.addEventListener("hashchange", fromAddress);
  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      const mode = button.dataset.mode;
      history.replaceState(null, "", `#${mode}`);
      render(mode);
    });
  });
}
