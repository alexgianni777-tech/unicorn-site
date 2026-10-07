(() => {
  document.addEventListener("click", event => {
    const link = event.target.closest("a[href]");
    if (!link || typeof window.gtag !== "function") return;
    let url;
    try { url = new URL(link.href, window.location.href); } catch (_) { return; }
    const host = url.hostname.toLowerCase().replace(/^www\./, "");
    const isAmazon = host === "amzn.to" || host === "amazon.com" || host.startsWith("amazon.") || host.includes(".amazon.");
    if (!isAmazon) return;
    const payload = {
      link_url: url.href,
      link_text: (link.textContent || "").trim().slice(0, 120),
      page_path: window.location.pathname
    };
    if (url.pathname.includes("/dp/")) window.gtag("event", "amazon_exact_click", payload);
    else if (url.pathname === "/s" || url.searchParams.has("k")) window.gtag("event", "amazon_search_click", payload);
  });
})();

(() => {
  const cfg = window.UNICORN_ADSENSE || {};
  const publisherId = (cfg.publisherId || "").trim();
  const slots = cfg.slots || {};
  if (!publisherId || !publisherId.startsWith("ca-pub-")) return;

  const active = [...document.querySelectorAll(".ad-slot[data-ad-key]")].filter(node => {
    const slot = (slots[node.dataset.adKey] || "").trim();
    if (!slot) return false;
    node.hidden = false;
    const mount = node.querySelector(".ad-mount");
    const ins = document.createElement("ins");
    ins.className = "adsbygoogle";
    ins.style.display = "block";
    ins.dataset.adClient = publisherId;
    ins.dataset.adSlot = slot;
    ins.dataset.adFormat = "auto";
    ins.dataset.fullWidthResponsive = "true";
    mount.appendChild(ins);
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
