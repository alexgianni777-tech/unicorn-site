(() => {
  const cfg = window.KPOP_ADSENSE || {};
  const publisherId = (cfg.publisherId || "").trim();
  const slots = cfg.slots || {};
  if (!publisherId || !publisherId.startsWith("ca-pub-")) return;

  const active = [...document.querySelectorAll(".ad-slot[data-ad-key]")].filter(node => {
    const slot = (slots[node.dataset.adKey] || "").trim();
    if (!slot) return false;
    node.hidden = false;
    const ins = document.createElement("ins");
    ins.className = "adsbygoogle";
    ins.style.display = "block";
    ins.dataset.adClient = publisherId;
    ins.dataset.adSlot = slot;
    ins.dataset.adFormat = "auto";
    ins.dataset.fullWidthResponsive = "true";
    node.querySelector(".ad-mount").appendChild(ins);
    return true;
  });
  if (!active.length) return;

  const script = document.createElement("script");
  script.async = true;
  script.crossOrigin = "anonymous";
  script.src = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=" + encodeURIComponent(publisherId);
  script.onload = () => active.forEach(() => {
    try { (window.adsbygoogle = window.adsbygoogle || []).push({}); } catch (_) {}
  });
  document.head.appendChild(script);
})();
