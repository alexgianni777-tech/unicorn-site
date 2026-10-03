"""Build the static Unicorn Finds site with Python's standard library.

Product titles and links live in products.json. Only publish a product after a
human has checked its destination against the label and image. No prices,
availability, Amazon ratings or customer reviews are stored here.
"""

from __future__ import annotations

import html
import json
from pathlib import Path
from urllib.parse import urlparse
from xml.sax.saxutils import escape as xml_escape


ROOT = Path(__file__).resolve().parent
BASE = "https://unicornsite.online"
PRODUCTS = json.loads((ROOT / "products.json").read_text(encoding="utf-8"))
BY_ID = {product["id"]: product for product in PRODUCTS}
assert len(PRODUCTS) == len(BY_ID) == 10
for product in PRODUCTS:
    assert urlparse(product["url"]).scheme == "https"
    assert urlparse(product["url"]).hostname in {"amzn.to", "www.amazon.com"}


def esc(value: str) -> str:
    return html.escape(str(value), quote=True)


def affiliate_note() -> str:
    return (
        '<aside class="disclosure" aria-label="Affiliate disclosure">'
        '<strong>Affiliate disclosure</strong>'
        '<p>Some product links are paid links. As an Amazon Associate I earn from '
        'qualifying purchases. Your price does not change because you use these '
        'links. Product details, prices and availability should be checked on Amazon.</p>'
        '</aside>'
    )


def header(active: str = "") -> str:
    links = [
        ("Shop", "/#shop"),
        ("Gift guides", "/guides/index.html"),
        ("Gift finder", "/tools/unicorn-gift-finder.html"),
        ("Party planner", "/tools/unicorn-party-planner.html"),
        ("Night lights", "/guides/unicorn-night-lights.html"),
        ("Our approach", "/about.html"),
    ]
    items = "".join(
        f'<a href="{href}"' + (' aria-current="page"' if active == href else "") + f'>{label}</a>'
        for label, href in links
    )
    return (
        '<a class="skip" href="#main">Skip to content</a>'
        '<div class="topline">A little wonder for everyday spaces ✦</div>'
        '<header class="site-header"><div class="header-inner">'
        '<a class="brand" href="/" aria-label="Unicorn Finds home">'
        '<span class="brand-mark" aria-hidden="true">🦄</span>Unicorn Finds</a>'
        f'<nav class="nav" aria-label="Main navigation">{items}</nav>'
        '</div></header>'
    )


def footer() -> str:
    return '''<footer class="site-footer"><div class="wrap">
      <div class="footer-grid">
        <div><a class="brand" href="/">Unicorn Finds</a>
          <p>Thoughtful ideas for unicorn gifts and decor. We organise options and explain what to check before you choose. We do not sell or ship products.</p></div>
        <div class="footer-links"><strong>Explore</strong>
          <a href="/#shop">All picks</a><a href="/guides/index.html">All gift guides</a><a href="/tools/unicorn-gift-finder.html">Gift finder</a>
          <a href="/guides/unicorn-birthday-gifts.html">Birthday gifts</a><a href="/guides/unicorn-gifts-for-kids.html">Gifts for kids</a>
          <a href="/guides/unicorn-gifts-for-teens.html">Gifts for teens</a><a href="/guides/unicorn-gifts-for-adults.html">Gifts for adults</a>
          <a href="/guides/unicorn-gift-basket-ideas.html">Gift baskets</a><a href="/guides/small-unicorn-gifts-stocking-stuffers.html">Small gifts</a>
          <a href="/guides/unicorn-party-favor-ideas.html">Party favors</a><a href="/guides/unicorn-night-lights.html">Night lights</a>
          <a href="/guides/unicorn-room-decor.html">Room decor</a><a href="/guides/unicorn-bedroom-ideas.html">Bedroom ideas</a>
          <a href="/tools/unicorn-party-planner.html">Free party planner</a></div>
        <div class="footer-links"><strong>Information</strong>
          <a href="/about.html">About and affiliate disclosure</a><a href="/privacy.html">Privacy</a></div>
      </div><div class="footer-bottom">As an Amazon Associate I earn from qualifying purchases. © 2026 Unicorn Finds. Independent site; not affiliated with Amazon, Hasbro or Netflix.</div>
    </div></footer>'''


def page(title: str, description: str, path: str, body: str, *, active: str = "", kind: str = "website",
         image: str | None = None, published: str | None = None, modified: str | None = None) -> str:
    canonical = BASE + path
    json_ld = {
        "@context": "https://schema.org",
        "@type": "WebPage" if kind == "website" else "Article",
        "name": title,
        "description": description,
        "url": canonical,
        "isPartOf": {"@type": "WebSite", "name": "Unicorn Finds", "url": BASE + "/"},
    }
    if kind == "article":
        json_ld.update({
            "headline": title.split(" | ")[0],
            "image": [BASE + (image or "/assets/decor.svg")],
            "datePublished": published or "2026-09-29",
            "dateModified": modified or published or "2026-09-29",
            "author": {
                "@type": "Organization",
                "name": "Unicorn Finds",
                "url": BASE + "/about.html",
                "logo": {
                    "@type": "ImageObject",
                    "url": BASE + "/assets/favicon.svg",
                },
            },
        })
    structured = json.dumps(json_ld, ensure_ascii=False).replace("<", "\\u003c")
    social_image = BASE + image if image else ""
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="theme-color" content="#40204f">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{esc(canonical)}">
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="/assets/style.css">
  <meta property="og:type" content="{kind}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(canonical)}">
  {f'<meta property="og:image" content="{esc(social_image)}">' if social_image else ''}
  <meta name="twitter:card" content="{'summary_large_image' if social_image else 'summary'}">
  {f'<meta name="twitter:image" content="{esc(social_image)}">' if social_image else ''}
  <script type="application/ld+json">{structured}</script>
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8108579336605864" crossorigin="anonymous"></script>
  <script src="/assets/ads-config.js"></script>
  <script src="/assets/ads.js" defer></script>
</head>
<body>
{header(active)}
{body}
{footer()}
</body>
</html>
'''


def ad_slot(label: str, key: str) -> str:
    return f'''<aside class="ad-slot" data-ad-key="{esc(key)}" aria-label="Advertisement" hidden>
      <span class="ad-label">Advertisement</span>
      <div class="ad-mount" data-ad-label="{esc(label)}"></div>
    </aside>'''


def product_card(product: dict) -> str:
    browse = "/s?" in product["url"]
    cta = "Browse similar on Amazon" if browse else "View on Amazon"
    return f'''<article class="product" id="{esc(product['id'])}">
      <a class="product-picture" href="{esc(product['url'])}" rel="sponsored nofollow noopener noreferrer" target="_blank" aria-label="{esc(cta + ': ' + product['title'])}">
        <img src="/{esc(product['image'])}" alt="{esc(product['alt'])}" loading="lazy" width="560" height="500">
        <span class="product-type">{esc(product['label'])}</span>
      </a>
      <div class="product-content"><h3>{esc(product['title'])}</h3>
        <p>{esc(product['description'])}</p>
        <a class="button product-cta" href="{esc(product['url'])}" rel="sponsored nofollow noopener noreferrer" target="_blank">{esc(cta)} <span aria-hidden="true">↗</span></a>
        <span class="product-footnote">Paid link · Check the selected item, seller and current details on Amazon</span>
      </div>
    </article>'''


def inline_pick(product_id: str, why: str) -> str:
    product = BY_ID[product_id]
    return f'''<aside class="inline-pick">
      <img src="/{esc(product['image'])}" alt="{esc(product['alt'])}" loading="lazy" width="90" height="90">
      <div><strong>{esc(product['title'])}</strong><p>{esc(why)}</p>
      <a href="{esc(product['url'])}" target="_blank" rel="sponsored nofollow noopener noreferrer">{('Browse similar on Amazon' if '/s?' in product['url'] else 'View on Amazon')} ↗ (paid link)</a></div>
    </aside>'''


def category(category_id: str, heading: str, intro: str) -> str:
    cards = "".join(product_card(product) for product in PRODUCTS if product["section"] == category_id)
    return f'''<section class="category" id="{category_id}">
      <h2>{heading}</h2><p class="category-intro">{intro}</p>
      <div class="product-grid">{cards}</div>
    </section>'''


def quick_pick(product_id: str, badge: str, why: str) -> str:
    product = BY_ID[product_id]
    cta = "Browse similar on Amazon" if "/s?" in product["url"] else "View on Amazon"
    return f'''<article class="quick-pick">
      <div class="quick-pick-icon"><img src="/{esc(product['image'])}" alt="{esc(product['alt'])}" loading="lazy" width="88" height="78"></div>
      <div class="quick-pick-copy"><span class="quick-badge">{esc(badge)}</span><h3>{esc(product['title'])}</h3>
        <p>{esc(why)}</p>
        <a class="quick-link" href="{esc(product['url'])}" target="_blank" rel="sponsored nofollow noopener noreferrer">{cta} <span aria-hidden="true">↗</span></a>
      </div>
    </article>'''


def comparison_row(product_id: str, fit: str, check: str) -> str:
    product = BY_ID[product_id]
    return f'''<tr>
      <th scope="row"><a href="#{esc(product['id'])}">{esc(product['title'])}</a></th>
      <td>{esc(fit)}</td><td>{esc(check)}</td>
      <td><a class="table-cta" href="{esc(product['url'])}" target="_blank" rel="sponsored nofollow noopener noreferrer">Amazon ↗</a></td>
    </tr>'''


def home() -> str:
    body = f'''<main id="main">
      <section class="hero"><div class="hero-inner">
        <div><div class="eyebrow">Ten gift ideas · real product photos</div>
          <h1>Give a little magic <em>they’ll actually use.</em></h1>
          <p class="hero-lede">Skip the endless scrolling. Start with four gift-ready shortcuts, compare the details that matter, then jump to Amazon when a mug, light or room accent feels right.</p>
          <div class="hero-actions"><a class="button" href="#quick-picks">Find a gift ↓</a><a class="button button-light" href="#shop">See all ten ideas</a></div>
          <p class="hero-note">Independent gift guide · clear paid-link disclosure · current Amazon details checked before you buy</p>
        </div>
        <div class="hero-collage" aria-label="Unicorn gift product photos">
          <div class="hero-image"><img src="/assets/products/cloud-lamp.jpg" alt="Unicorn lamp on a cloud base" width="560" height="500" fetchpriority="high"></div>
          <div class="hero-image"><img src="/assets/products/sculpted-mug.jpg" alt="Sculpted unicorn mug with lid" width="560" height="500"></div>
          <span class="hero-stamp" aria-hidden="true">Cute. Useful. Gift-ready. ✦</span>
        </div>
      </div></section>
      <div class="jump wrap" aria-label="Jump to a category"><span>Browse by mood</span>
        <a href="#drinkware">☕ Mugs &amp; drinkware</a><a href="#lights">✦ Night lights</a><a href="#decor">♡ Decor &amp; little gifts</a>
      </div>
      <section class="section wrap quick-section" id="quick-picks">
        <div class="section-heading"><span class="eyebrow">Short on time?</span><h2>Four gifts with instant visual appeal</h2>
          <p>Choose the kind of reaction you want: a fun coffee break, a softer bedside glow, a full-room effect or a small surprise that is easy to give.</p></div>
        <p class="quick-disclosure">As an Amazon Associate I earn from qualifying purchases. These are editorial shortcuts, not hands-on reviews; Amazon links below are paid links.</p>
        <div class="quick-grid">
          {quick_pick('sculpted-mug','Coffee-break smile','A playful desk or kitchen gift with more personality than a plain mug.')}
          {quick_pick('cloud-lamp','Cosy bedside glow','A compact room accent that can make a shelf or bedside table feel instantly more special.')}
          {quick_pick('projector','Big room moment','For someone who would enjoy a ceiling or wall effect rather than one small decorative light.')}
          {quick_pick('keychain','Easy little surprise','A small, portable gift for a backpack, handbag or keys when you do not want to guess at room style.')}
        </div>
        <div class="compare-block">
          <div class="compare-heading"><h3>Compare the quick picks</h3><p>Use the last column to check the current Amazon listing before deciding.</p></div>
          <div class="table-scroll"><table class="pick-table">
            <thead><tr><th>Pick</th><th>Good when you want…</th><th>Check before buying</th><th>Current listing</th></tr></thead>
            <tbody>
              {comparison_row('sculpted-mug','a playful coffee or tea gift','capacity, lid and care instructions')}
              {comparison_row('cloud-lamp','a compact bedside accent','power method and dimensions')}
              {comparison_row('projector','a room-wide lighting effect','projection distance and controls')}
              {comparison_row('keychain','a small portable surprise','size and attachment style')}
            </tbody>
          </table></div>
        </div>
      </section>
      {ad_slot('Homepage banner after quick picks', 'home_top')}
      <section class="section section-tint" id="guides"><div class="wrap">
        <div class="section-heading"><span class="eyebrow">Start with an idea</span><h2>Find the right kind of magic</h2>
          <p>Pick a recipient or occasion, or use the free gift finder to narrow the ten-item collection in seconds.</p></div>
        <div class="guide-grid">
          <a class="guide-tile" href="/tools/unicorn-gift-finder.html"><span class="tile-icon" aria-hidden="true">✨</span><h3>Unicorn gift finder</h3><p>Choose the kind of gift you want and get three relevant starting points.</p><span class="tile-link">Find a gift →</span></a>
          <a class="guide-tile" href="/guides/unicorn-birthday-gifts.html"><span class="tile-icon" aria-hidden="true">🎂</span><h3>Unicorn birthday gifts</h3><p>Pick a birthday present by use: everyday, creative, room decor or a small surprise.</p><span class="tile-link">Browse birthday ideas →</span></a>
          <a class="guide-tile" href="/guides/unicorn-gifts-for-kids.html"><span class="tile-icon" aria-hidden="true">🌈</span><h3>Unicorn gifts for kids</h3><p>Compare playful ideas while checking age guidance, size and practical details.</p><span class="tile-link">Read the kids guide →</span></a>
          <a class="guide-tile" href="/guides/unicorn-gifts-for-adults.html"><span class="tile-icon" aria-hidden="true">🎁</span><h3>Unicorn gifts for adults</h3><p>How to pick a present that feels personal without guessing at size or style.</p><span class="tile-link">Read the gift guide →</span></a>
          <a class="guide-tile" href="/guides/unicorn-night-lights.html"><span class="tile-icon" aria-hidden="true">🌙</span><h3>Choosing a night light</h3><p>Compare a bedside glow, an accent lamp and a room projector.</p><span class="tile-link">Compare lighting →</span></a>
          <a class="guide-tile" href="/guides/unicorn-room-decor.html"><span class="tile-icon" aria-hidden="true">🏡</span><h3>Unicorn room decor</h3><p>Build a playful room with a few pieces that work together.</p><span class="tile-link">Explore room ideas →</span></a>
          <a class="guide-tile" href="/guides/unicorn-gift-basket-ideas.html"><span class="tile-icon" aria-hidden="true">🧺</span><h3>Unicorn gift basket ideas</h3><p>Build a useful themed bundle without filling it with random extras.</p><span class="tile-link">Build a gift basket →</span></a>
          <a class="guide-tile" href="/guides/unicorn-gifts-for-teens.html"><span class="tile-icon" aria-hidden="true">💫</span><h3>Unicorn gifts for teens</h3><p>Choose something playful that still fits a teen's room, desk or daily routine.</p><span class="tile-link">Read the teen guide →</span></a>
          <a class="guide-tile" href="/guides/unicorn-party-favor-ideas.html"><span class="tile-icon" aria-hidden="true">🎈</span><h3>Unicorn party favor ideas</h3><p>Plan small take-home gifts by usefulness, quantity and age guidance.</p><span class="tile-link">Plan party favors →</span></a>
          <a class="guide-tile" href="/guides/unicorn-bedroom-ideas.html"><span class="tile-icon" aria-hidden="true">🛏️</span><h3>Unicorn bedroom ideas</h3><p>Plan a calmer themed bedroom by zones, scale and repeatable colours.</p><span class="tile-link">Plan the room →</span></a>
          <a class="guide-tile" href="/guides/small-unicorn-gifts-stocking-stuffers.html"><span class="tile-icon" aria-hidden="true">🧦</span><h3>Small unicorn gifts</h3><p>Stocking-stuffer and little-surprise ideas with size and usefulness in mind.</p><span class="tile-link">See small gift ideas →</span></a>
          <a class="guide-tile" href="/tools/unicorn-party-planner.html"><span class="tile-icon" aria-hidden="true">🎉</span><h3>Free unicorn party planner</h3><p>Work out guest supplies and your own budget, then print a simple party plan.</p><span class="tile-link">Plan a party →</span></a>
        </div>
      </div></section>
      <section class="section wrap" id="shop">
        <div class="section-heading"><span class="eyebrow">The full collection</span><h2>All ten unicorn finds</h2>
          <p>Browse by use, then check the exact listing on Amazon. These are curated starting points, not hands-on reviews or promises of current price, rating, stock or delivery.</p></div>
        {affiliate_note()}
        {category('drinkware','Unicorn mugs &amp; drinkware','For a desk, a morning routine or a themed gift box. Think about how the recipient will use it before choosing a decorative shape.')}
        {category('lights','Night lights &amp; glowing rooms','A gentle bedside light, a decorative lamp and a projector create very different effects. The lighting guide helps you compare them.')}
        {category('decor','Decor &amp; small gifts','A wall, a sofa, a shelf or a backpack can carry the theme. Check sizes and what the listing actually includes.')}
      </section>
      {ad_slot('Homepage banner after collection', 'home_mid')}
      <section class="section section-tint"><div class="wrap">
        <div class="section-heading"><span class="eyebrow">Why this guide exists</span><h2>Small details make a better pick</h2></div>
        <div class="principles"><div class="principle"><h3>Choose for the person</h3><p>Start with the recipient's taste and how they will use the gift, rather than a star count.</p></div>
          <div class="principle"><h3>Check the listing</h3><p>Verify dimensions, materials, included parts, seller and returns on Amazon before you buy.</p></div>
          <div class="principle"><h3>Know what we do</h3><p>We organise existing product links and write buying guidance. We have not personally tested these products.</p></div></div>
      </div></section>
      <section class="section wrap faq" aria-label="Frequently asked questions"><h2>Good to know</h2>
        <details><summary>Do you sell these products?</summary><p>No. You choose a product here and complete any purchase on Amazon. The seller handles availability, checkout and delivery.</p></details>
        <details><summary>Are the prices and ratings current?</summary><p>We do not display prices or Amazon customer ratings. They can change, so check the current listing before deciding.</p></details>
        <details><summary>Are these hands-on reviews?</summary><p>No. These are curated starting points with buying considerations, not claims that we tested the products ourselves.</p></details>
        <details><summary>Is this an official My Little Pony store?</summary><p>No. My Little Pony is a Hasbro brand. A generic unicorn item is different from a licensed character product; check the manufacturer and packaging if the recipient wants a specific character.</p></details>
      </section>
    </main>'''
    return page(
        "Unicorn Gifts: 10 Gift Ideas & Decor | Unicorn Finds",
        "Find unicorn gift ideas faster with four quick picks, a simple comparison and ten curated mugs, lights and room decor ideas with clearly marked Amazon links.",
        "/", body,
    )


def guide_page(title: str, description: str, path: str, intro: str, article: str) -> str:
    article_meta = {
        "/guides/unicorn-birthday-gifts.html": ("/assets/decor.svg", "2026-10-02"),
        "/guides/unicorn-gifts-for-kids.html": ("/assets/decor.svg", "2026-10-02"),
        "/guides/unicorn-gifts-for-adults.html": ("/assets/mugs.svg", "2026-09-29"),
        "/guides/unicorn-night-lights.html": ("/assets/lights.svg", "2026-09-29"),
        "/guides/unicorn-room-decor.html": ("/assets/decor.svg", "2026-09-29"),
        "/guides/unicorn-gift-basket-ideas.html": ("/assets/mugs.svg", "2026-10-02"),
        "/guides/unicorn-gifts-for-teens.html": ("/assets/decor.svg", "2026-10-02"),
        "/guides/unicorn-party-favor-ideas.html": ("/assets/decor.svg", "2026-10-02"),
        "/guides/unicorn-bedroom-ideas.html": ("/assets/decor.svg", "2026-10-02"),
        "/guides/small-unicorn-gifts-stocking-stuffers.html": ("/assets/decor.svg", "2026-10-02"),
    }
    article_image, article_published = article_meta.get(path, ("/assets/decor.svg", "2026-09-29"))
    related = '''<nav class="related-guides" aria-label="Related unicorn guides">
      <h2>Keep exploring</h2>
      <div class="related-grid">
        <a href="/guides/unicorn-birthday-gifts.html"><strong>Birthday gifts</strong><span>Gift ideas by use and occasion →</span></a>
        <a href="/guides/unicorn-gifts-for-kids.html"><strong>Gifts for kids</strong><span>Age, size and practical checks →</span></a>
        <a href="/guides/unicorn-gifts-for-teens.html"><strong>Gifts for teens</strong><span>Practical ideas for rooms, desks and bags →</span></a>
        <a href="/guides/unicorn-gift-basket-ideas.html"><strong>Gift baskets</strong><span>Build a useful themed bundle →</span></a>
        <a href="/guides/small-unicorn-gifts-stocking-stuffers.html"><strong>Small gifts</strong><span>Compact gifts and stocking stuffers →</span></a>
        <a href="/guides/unicorn-party-favor-ideas.html"><strong>Party favors</strong><span>Plan small take-home gifts →</span></a>
        <a href="/guides/unicorn-bedroom-ideas.html"><strong>Bedroom ideas</strong><span>Plan a unicorn room by zones →</span></a>
        <a href="/guides/unicorn-night-lights.html"><strong>Night lights</strong><span>Compare lamps and projectors →</span></a>
        <a href="/guides/unicorn-room-decor.html"><strong>Room decor</strong><span>Build a balanced unicorn room →</span></a>
        <a href="/tools/unicorn-gift-finder.html"><strong>Gift finder</strong><span>Narrow the collection to three ideas →</span></a>
      </div>
    </nav>'''
    body = f'''<main id="main"><div class="page-intro"><div class="wrap">
      <div class="breadcrumbs"><a href="/">Home</a> / Guides</div>
      <span class="eyebrow">Unicorn Finds guide</span><h1>{esc(title.split(' | ')[0])}</h1><p>{esc(intro)}</p>
    </div></div><article class="article wrap">
      {affiliate_note()}
      {article}
      {ad_slot('Guide banner', 'article_mid')}
      <div class="callout"><p><strong>One last check:</strong> Retail listings can change. Confirm the exact item, size, seller, price, availability and return terms on Amazon before purchasing.</p></div>
      {related}
      <p><a class="button button-light" href="/#shop">Browse all ten picks →</a></p>
    </article></main>'''
    return page(
        title, description, path, body, kind="article",
        image=article_image, published=article_published, modified="2026-10-02",
    )


def gift_finder() -> str:
    body = '''<main id="main"><div class="page-intro"><div class="wrap">
      <div class="breadcrumbs"><a href="/">Home</a> / Free tools</div>
      <span class="eyebrow">A faster way to choose</span><h1>Unicorn gift finder</h1>
      <p>Choose the kind of gift you want. We will narrow the existing collection to three starting points, then you can check the current Amazon listings.</p>
    </div></div><div class="article wrap finder-page">
      ''' + affiliate_note() + '''
      <section class="finder-box" aria-labelledby="finder-heading"><h2 id="finder-heading">What kind of gift are you looking for?</h2>
        <p>There is no hidden scoring and no claim that these are hands-on reviews. The buttons simply match your choice to products already in this guide.</p>
        <div class="finder-choices" role="group" aria-label="Gift type">
          <button type="button" class="finder-choice" data-mode="everyday">Everyday gift</button>
          <button type="button" class="finder-choice" data-mode="glow">Room glow</button>
          <button type="button" class="finder-choice" data-mode="creative">Creative gift</button>
          <button type="button" class="finder-choice" data-mode="small">Small surprise</button>
        </div>
      </section>
      <section id="finder-result" class="finder-result" aria-live="polite">
        <h2>Your three starting points</h2>
        <p>Choose a gift type above to see three ideas.</p>
      </section>
      <div id="finder-products" hidden>
        <template data-product="mug-set">''' + inline_pick("mug-set", "A playful mug idea; check the current design, capacity and care instructions.") + '''</template>
        <template data-product="tumbler">''' + inline_pick("tumbler", "A drinkware option; verify capacity, lid design and cleaning instructions.") + '''</template>
        <template data-product="keychain">''' + inline_pick("keychain", "A compact bag or key accessory; check the size and attachment.") + '''</template>
        <template data-product="cloud-lamp">''' + inline_pick("cloud-lamp", "A compact accent light; check power details and dimensions.") + '''</template>
        <template data-product="projector">''' + inline_pick("projector", "A larger lighting effect; check projection distance, controls and power.") + '''</template>
        <template data-product="night-light-search">''' + inline_pick("night-light-search", "Compare several lamp styles and confirm the exact listing you choose.") + '''</template>
        <template data-product="planters">''' + inline_pick("planters", "A craft-style idea; check the set quantity and included supplies.") + '''</template>
        <template data-product="wall-art">''' + inline_pick("wall-art", "A room-decor idea; verify measurements and whether frames are included.") + '''</template>
        <template data-product="pillow-cover">''' + inline_pick("pillow-cover", "A small room refresh; check dimensions, fabric and whether an insert is included.") + '''</template>
        <template data-product="sculpted-mug">''' + inline_pick("sculpted-mug", "A more decorative mug; check size, cleaning advice and included parts.") + '''</template>
      </div>
      <p class="finder-next"><a href="/guides/unicorn-birthday-gifts.html">Shopping for a birthday? Read the birthday guide →</a></p>
    </div><script src="/assets/gift-finder.js" defer></script></main>'''
    return page(
        "Unicorn Gift Finder: Quick Gift Ideas | Unicorn Finds",
        "Use a free unicorn gift finder to narrow ten curated gift ideas to three starting points for everyday gifts, room lighting, creative gifts or small surprises.",
        "/tools/unicorn-gift-finder.html", body, active="/tools/unicorn-gift-finder.html",
    )


def party_planner() -> str:
    body = '''<main id="main"><div class="page-intro"><div class="wrap">
      <div class="breadcrumbs"><a href="/">Home</a> / Free tools</div>
      <span class="eyebrow">Plan, then play</span><h1>Free unicorn party planner</h1>
      <p>Estimate supplies and your own budget in one place. Print the result for a shopping trip or a conversation with another organiser.</p>
    </div></div><div class="article wrap party-page">
      <p>This planner runs in your browser. It does not send your numbers to us, save a guest list or assume current shop prices. Enter the prices you find and adjust the quantities for your particular party.</p>
      <form id="party-planner" class="planner-form">
        <fieldset><legend>People and supplies</legend><div class="planner-fields">
          <label>Invited guests <input id="party-guests" type="number" min="1" max="300" step="1" value="12" required></label>
          <label>Hosts and other people <input id="party-hosts" type="number" min="0" max="100" step="1" value="2" required></label>
          <label>Extra supplies (%) <input id="party-buffer" type="number" min="0" max="100" step="1" value="10" required></label>
        </div><p class="field-help">The supply estimate starts at one plate and one cup per person. Adjust it for reusable tableware, multiple servings and your guest list.</p></fieldset>
        <fieldset><legend>Enter your own estimated costs</legend><div class="planner-fields">
          <label>Currency <select id="party-currency"><option value="USD">USD ($)</option><option value="GBP">GBP (£)</option><option value="EUR">EUR (€)</option><option value="SEK">SEK (kr)</option></select></label>
          <label>Food and drink per person <input id="party-food" type="number" min="0" max="100000" step="0.01" inputmode="decimal" placeholder="0.00"></label>
          <label>Favor per invited guest <input id="party-favor" type="number" min="0" max="100000" step="0.01" inputmode="decimal" placeholder="0.00"></label>
          <label>Cake or dessert, total <input id="party-cake" type="number" min="0" max="100000" step="0.01" inputmode="decimal" placeholder="0.00"></label>
          <label>Decorations, total <input id="party-decor" type="number" min="0" max="100000" step="0.01" inputmode="decimal" placeholder="0.00"></label>
          <label>Activities, total <input id="party-activities" type="number" min="0" max="100000" step="0.01" inputmode="decimal" placeholder="0.00"></label>
        </div><p class="field-help">These are planning inputs, not quotes or live prices. Leaving an amount blank counts it as zero.</p></fieldset>
      </form>
      <section id="party-result" class="planner-result" aria-live="polite" aria-atomic="true">
        <h2>Your starting list</h2><p>For 12 guests and 2 other people, start with 16 plates and 16 cups if using one of each per person. Plan 12 favors. Add your own estimated costs above to see a budget.</p>
      </section>
      <button class="button planner-print" id="party-print" type="button">Print this plan</button>
      <h2>A flexible 90-minute party outline</h2>
      <ol><li><strong>First 15 minutes:</strong> Welcome guests and offer a simple arrival activity while everyone settles in.</li>
        <li><strong>Next 30 minutes:</strong> Run one main game or craft. Check the age guidance and parts of any supplies before choosing an activity.</li>
        <li><strong>Next 20 minutes:</strong> Pause for food, drinks and cake. Ask guests about dietary needs when planning the menu.</li>
        <li><strong>Last 25 minutes:</strong> Leave room for a quieter game, pictures and a relaxed goodbye. Keep a no-supplies backup activity ready.</li></ol>
      <p>This outline is an example, not a fixed schedule. Allow more time for setup, cleanup, travel or a larger group.</p>
      <h2>Before you buy</h2>
      <ul><li>Confirm how many people are actually coming, including adults who will eat.</li>
        <li>Check package counts, age guidance and what each set includes. The planner's plate and cup figures are only a starting point.</li>
        <li>Compare your entered costs with your target budget and keep a little room for forgotten supplies.</li>
        <li>If you choose a character theme such as My Little Pony, check that licensed goods really come from the named brand.</li></ul>
      <p>A paintable planter could be one craft idea if the listing's quantity and age guidance suit your group. Confirm whether paint, brushes and protective table covering are included.</p>
      ''' + affiliate_note() + inline_pick("planters", "A possible craft activity; verify the current pack size and included supplies before planning for a group.") + '''
      <p>Looking for a lasting room accent after the party? <a href="/guides/unicorn-room-decor.html">Read the room decor guide</a>. For a present, <a href="/guides/unicorn-gifts-for-adults.html">start with the gift guide</a>.</p>
    </div><script src="/assets/party-planner.js" defer></script></main>'''
    return page(
        "Free Unicorn Birthday Party Planner & Budget | Unicorn Finds",
        "Plan a unicorn party with a free guest supply and budget calculator, a printable list and a flexible 90-minute outline. No account or live prices needed.",
        "/tools/unicorn-party-planner.html", body, active="/tools/unicorn-party-planner.html",
    )


def write(path: str, contents: str) -> None:
    destination = ROOT / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(contents, encoding="utf-8")


def main() -> None:
    write("index.html", home())
    write("guides/unicorn-gifts-for-adults.html", guide_page(
        "Unicorn Gifts for Adults: Gift Guide | Unicorn Finds",
        "Choose a unicorn gift for an adult by use, style and care needs. Compare mugs, small accessories and decor without relying on changing prices or ratings.",
        "/guides/unicorn-gifts-for-adults.html",
        "A unicorn gift can be playful and still fit a grown-up's daily routine. Start with what the person actually uses.",
        '''<h2>Start with a habit, not just a theme</h2>
        <p>Does the recipient drink coffee at a desk, carry a water bottle, keep plants or enjoy decorating a room? A small detail that fits an existing habit is usually easier to enjoy than a large object that needs space. If their taste is minimal, look for one restrained accent rather than a full rainbow set.</p>
        <h2>For the tea or coffee person</h2>
        <p>A mug is easy to give, but the shape affects cleaning and storage. Compare capacity, handle comfort, dishwasher instructions and whether a lid is decorative or functional. A colour-changing finish may need special care, so check the current product instructions.</p>'''
        + inline_pick("mug-set", "A playful colour-changing idea; check the current design and care advice.")
        + inline_pick("sculpted-mug", "A more sculptural choice; check how it should be washed.")
        + '''<h2>For someone who likes a small surprise</h2>
        <p>If you are unsure about decor style, a bag charm can be easier to place than wall art. For a friend with a collection of plants, a tiny planter may be more personal. Check measurements in both cases; close-up photos make small objects look larger than they are.</p>'''
        + inline_pick("keychain", "A compact accessory; verify the attachment and size.")
        + inline_pick("planters", "For someone who enjoys craft projects; check included supplies and drainage.")
        + '''<h2>When the gift is for a My Little Pony fan</h2>
        <p>Ask whether they want a generic unicorn design or a specific My Little Pony character. My Little Pony is a Hasbro brand; a unicorn decoration should not be presented as licensed merchandise. Check official branding, the character name, age guidance and the seller before buying a character gift. This guide does not claim a Hasbro partnership.</p>
        <h2>Make the decision in five minutes</h2>
        <ol><li>Choose one use: drinking, decorating or carrying.</li><li>Check the recipient's available space and preferred colours.</li><li>Read the current listing for dimensions and care instructions.</li><li>Check which version, quantity and seller are selected.</li><li>Keep the receipt or review the return terms if this is a gift.</li></ol>'''
    ))
    write("guides/unicorn-birthday-gifts.html", guide_page(
        "Unicorn Birthday Gifts by Gift Type | Unicorn Finds",
        "Choose a unicorn birthday gift by how it will be used. Compare drinkware, creative gifts, lighting and small surprises with clearly marked Amazon links.",
        "/guides/unicorn-birthday-gifts.html",
        "A birthday gift is easier to choose when you start with how the person will use it rather than trying to find one universal 'best' unicorn present.",
        '''<h2>Start with the kind of birthday moment</h2>
        <p>For an everyday gift, drinkware is easy to understand and use. For someone who likes making things, a paintable item can turn the present into an activity. For a bedroom refresh, lighting or decor has a bigger visual effect. If you are unsure about their room or style, a smaller accessory is easier to place.</p>
        <h2>Everyday birthday ideas</h2>'''
        + inline_pick("mug-set", "A small everyday present; check the design, capacity and washing instructions.")
        + inline_pick("tumbler", "A cold-drink option; check lid style, capacity and cleaning instructions.")
        + '''<h2>Creative birthday ideas</h2>
        <p>A craft-style present works best when the recipient actually enjoys making or decorating things. Check the current listing for quantities, included materials and stated age guidance.</p>'''
        + inline_pick("planters", "A paintable project; verify how many pieces and supplies are included.")
        + '''<h2>For a room makeover</h2>
        <p>A compact lamp and a projector create very different effects. Measure the available space and confirm the power method before ordering.</p>'''
        + inline_pick("cloud-lamp", "A smaller bedside or shelf accent; check power method and dimensions.")
        + inline_pick("projector", "A room-wide effect; check projection distance, controls and included scenes.")
        + '''<h2>When you need a smaller surprise</h2>
        <p>If you do not know the recipient's room measurements or drinkware preferences, a small accessory may require less guessing. Still check the dimensions because close-up listing photos can make compact products appear larger.</p>'''
        + inline_pick("keychain", "A compact accessory; verify size and attachment style.")
        + '''<h2>Birthday checklist before checkout</h2>
        <ol><li>Confirm the exact version selected on Amazon.</li><li>Check dimensions, included parts and age guidance where relevant.</li><li>Check the seller, delivery estimate and return terms on the current listing.</li><li>If it is going straight to the recipient, confirm the shipping address and gift options during checkout.</li></ol>'''
    ))
    write("guides/unicorn-gifts-for-kids.html", guide_page(
        "Unicorn Gifts for Kids: Buying Guide | Unicorn Finds",
        "Explore unicorn gift ideas for kids while checking age guidance, size, small parts, power method and what is included before purchasing.",
        "/guides/unicorn-gifts-for-kids.html",
        "For a child's gift, the theme matters, but age guidance, size and how the item will actually be used matter more.",
        '''<h2>Choose by activity, not just appearance</h2>
        <p>Think about whether the child enjoys crafts, room decor, carrying small accessories or using a special cup. That narrows the choice more reliably than selecting whichever listing has the brightest photo.</p>
        <h2>For a child who likes making things</h2>
        <p>Craft products can be enjoyable when the stated age guidance, parts and supplies fit the child. Check what is included and whether adult help or surface protection is recommended.</p>'''
        + inline_pick("planters", "A paintable project idea; check age guidance, quantity and included painting supplies.")
        + '''<h2>For a bedroom or reading corner</h2>
        <p>With lighting, confirm the product's stated age guidance and safety instructions. Check power, controls and dimensions, and place electrical or fragile items according to the maker's instructions.</p>'''
        + inline_pick("cloud-lamp", "A compact room accent; verify power details, dimensions and current age guidance.")
        + inline_pick("night-light-search", "Compare different lamp styles and confirm the exact item before buying.")
        + '''<h2>For an older child who wants something useful</h2>
        <p>Drinkware can be practical, but check material, capacity, care instructions and whether the lid or straw suits the intended use.</p>'''
        + inline_pick("tumbler", "A drinkware option; verify material, capacity, lid and cleaning instructions.")
        + '''<h2>Safety and fit checklist</h2>
        <ul><li>Follow the manufacturer's current age guidance.</li><li>Check for small parts and included accessories.</li><li>Verify power requirements for lamps and projectors.</li><li>Measure the space for decor rather than judging size from photos.</li><li>Confirm the exact seller, version and return terms on Amazon.</li></ul>'''
    ))
    write("guides/unicorn-night-lights.html", guide_page(
        "How to Choose a Unicorn Night Light | Unicorn Finds",
        "Compare unicorn night lights, bedside lamps and projectors by brightness, power, controls and room use before choosing a gift.",
        "/guides/unicorn-night-lights.html",
        "A bedside glow and a room projector solve different problems. This guide helps you choose the effect first.",
        '''<h2>Decide what the light needs to do</h2>
        <p>For a bedside table, a compact lamp keeps the effect local. For a large wall or ceiling, a projector changes the whole room. If the light will be used at bedtime, check whether it can be dimmed or switched off easily. For a decorative display, colour choices may matter more than brightness.</p>
        <h2>Check the practical details</h2>
        <ul><li><strong>Power:</strong> confirm whether the product uses batteries, a USB cable or a mains adapter, and what is included.</li><li><strong>Controls:</strong> consider whether a child can operate the button, or whether a remote could be misplaced.</li><li><strong>Placement:</strong> compare dimensions with the shelf or bedside surface. For a projector, check the recommended distance.</li><li><strong>Cleaning and care:</strong> read the maker's instructions, especially for soft or shaped lamps.</li></ul>
        <p>For a child's room, follow the product's stated age guidance and safety instructions. Do not assume that every lamp or projector is suitable for unsupervised use.</p>
        <h2>Browse before committing to a style</h2>
        <p>The first link below opens search results for unicorn night lights, so it is useful for comparing different designs. It is not a link to one specific product.</p>'''
        + inline_pick("night-light-search", "Compare listings and confirm the exact lamp you choose.")
        + '''<h2>Two different effects</h2>
        <p>A shaped lamp can add a small pool of light beside the bed. A star projector is better suited to making a ceiling or wall part of the design. Product listings may differ in modes, accessories and power supplies, so compare those details rather than relying on the photo alone.</p>'''
        + inline_pick("cloud-lamp", "An accent light idea; verify the base and charging details.")
        + inline_pick("projector", "A room-wide effect; check included scenes and controls.")
        + '''<h2>A simple way to choose</h2>
        <p>If you want a soft local glow, start with a night light. If the goal is a dramatic room makeover, compare projectors. If you only need visual interest during the day, wall art or a pillow cover may be a better fit than an electrical item.</p>'''
    ))
    write("guides/unicorn-room-decor.html", guide_page(
        "Unicorn Room Decor Ideas Without the Clutter | Unicorn Finds",
        "Plan a unicorn-themed room with wall art, cushions, lighting and small accents. Use scale, colour and placement to keep the space balanced.",
        "/guides/unicorn-room-decor.html",
        "A unicorn theme works best when a few pieces share a colour palette and each has a clear place.",
        '''<h2>Choose one focal point</h2>
        <p>Pick the first thing you want someone to notice: a wall print, a glowing lamp or a cluster of small objects on a shelf. Giving every surface a different motif can make a room feel busy. One larger feature and two supporting accents usually give you more flexibility later.</p>
        <h2>Use a repeating colour, not identical prints</h2>
        <p>Look at the room's existing bedding, walls and furniture. A pastel pillow cover can echo a colour in a wall print; a light can provide a different texture. You do not need every object to show the same unicorn image. Leave some plain space around your focal piece.</p>'''
        + inline_pick("wall-art", "Check the measurements and whether the pieces arrive framed.")
        + inline_pick("pillow-cover", "A smaller change; confirm insert size and fabric.")
        + '''<h2>Think in zones</h2>
        <p>At a desk, a small planter can add the theme without using wall space. By a bed, a lamp makes more sense than another desk ornament. In a shared room, keep frequently used surfaces clear so the decorations remain easy to live with.</p>'''
        + inline_pick("planters", "A paintable shelf or desk accent; verify the number and size of pots.")
        + inline_pick("cloud-lamp", "For a bedside or display shelf; check the current power details.")
        + '''<h2>Measure before you order</h2>
        <p>Product photos rarely show how an item fits your exact room. Measure the free wall, shelf depth and cushion insert first. Check what comes in the box: wall art may be unframed, pillow covers may exclude inserts, and a planter set may exclude plants. That small step prevents most decor surprises.</p>
        <h2>If this is a child's room</h2>
        <p>Keep small accessories and electrical items appropriate to the child's age and follow the maker's instructions. Place fragile pieces where they cannot be knocked down during play. A pretty photo is only one part of a good room choice.</p>'''
    ))

    write("guides/unicorn-gift-basket-ideas.html", guide_page(
        "Unicorn Gift Basket Ideas | Unicorn Finds",
        "Build a unicorn gift basket around one useful anchor item, a supporting gift and a simple theme, with practical checks for size, care and presentation.",
        "/guides/unicorn-gift-basket-ideas.html",
        "A good unicorn gift basket feels coordinated because every item has a reason to be there, not because every surface is covered in unicorns.",
        '''<h2>Start with one anchor gift</h2>
        <p>The easiest way to avoid a basket full of filler is to choose one item that can stand on its own. Think about the recipient's routine first: a mug for someone who keeps a drink at a desk, a tumbler for cold drinks, a small lamp for a reading corner, or a creative item for someone who likes hands-on projects. Once the anchor is clear, the rest of the basket can support that use instead of competing with it.</p>
        <p>Keep the theme visible but not repetitive. One unicorn-shaped or illustrated item can carry the idea; the other pieces can simply match its colours or purpose. That makes the bundle easier to use after the wrapping is gone.</p>'''
        + inline_pick("mug-set", "A simple anchor for a cosy drink-themed basket; check the current design, capacity and care instructions.")
        + '''<h2>Use a three-part formula</h2>
        <p>A practical basket can be built from three roles: an anchor item, a smaller supporting item and something consumable or personal that you add yourself. For example, a mug can be paired with a small unicorn accessory and the recipient's preferred tea or cocoa. A craft item can be paired with a plain sketchbook or protective table mat. The goal is not to maximise the number of objects; it is to make the bundle feel deliberate.</p>
        <p>Before buying, compare the physical sizes. Listing photos often make small items look substantial, while a sculpted mug or lamp can take up more room than expected. Measure the container you plan to use and leave enough space for paper filler rather than forcing products together.</p>'''
        + inline_pick("keychain", "A compact supporting gift for a basket; verify its dimensions and attachment style on the current listing.")
        + '''<h2>Build around a hobby or place</h2>
        <p>A theme works better when it points to a real activity. A desk basket might use drinkware plus a small accessory. A bedroom basket could centre on one light or cushion cover and use plain coordinating items around it. A creative basket could start with paintable planters and add supplies only after you confirm what the current set already includes.</p>
        <p>If you are giving room decor, check what the recipient already owns. A cushion cover may require an insert, wall art may arrive without frames, and a lamp needs an appropriate place and power source. Those details matter more than adding another decorative object.</p>'''
        + inline_pick("planters", "A creative anchor idea; check the current pack quantity, included supplies and any stated age guidance.")
        + '''<h2>Keep the presentation easy to unpack</h2>
        <p>Choose a container that can be reused or recycled and avoid hiding essential product information. If an item has care instructions, age guidance or electrical information, keep that packaging with the gift. For fragile pieces, use enough padding that the recipient can lift each item out without pulling on another product.</p>
        <p>You do not need a traditional wicker basket. A gift bag, small storage box or plain reusable tote can work just as well. A restrained container also keeps the unicorn theme from becoming visually overwhelming.</p>
        <h2>Five checks before checkout</h2>
        <ol><li>Choose the anchor gift before buying supporting items.</li><li>Check the exact dimensions of every product and the container.</li><li>Confirm what is included so you do not duplicate accessories or supplies.</li><li>Read care, power and age guidance where relevant.</li><li>Check the selected seller, version, return terms and current availability on Amazon.</li></ol>
        <p>If you would rather choose one present than assemble a bundle, use the <a href="/tools/unicorn-gift-finder.html">unicorn gift finder</a>. For an occasion-specific approach, the <a href="/guides/unicorn-birthday-gifts.html">birthday gift guide</a> groups ideas by how they will be used.</p>'''
    ))
    write("guides/unicorn-gifts-for-teens.html", guide_page(
        "Unicorn Gifts for Teens: Practical Ideas | Unicorn Finds",
        "Choose a unicorn gift for a teen by daily use, room style and how bold the theme should be. Compare drinkware, lighting, decor and small accessories.",
        "/guides/unicorn-gifts-for-teens.html",
        "For a teen, the safest starting point is usually how they use their room, desk or bag—not an assumption that every unicorn design will suit their style.",
        '''<h2>Start with how visible the theme should be</h2>
        <p>Some teens enjoy a bold fantasy look; others prefer one small reference that fits into an otherwise neutral room or outfit. Before choosing, think about whether the gift will sit on a desk, travel in a bag, be used every day or become part of bedroom decor. A useful item with one playful detail can be easier to live with than a large themed object.</p>
        <p>Colour matters too. If you know the person's room or favourite colours, use that as a filter. If you do not, a smaller accessory or practical item usually requires less guessing than wall art or a large decorative piece.</p>
        <h2>For school, desk or everyday use</h2>
        <p>Drinkware can work when the recipient already uses a bottle or mug regularly. Check capacity, lid style, material and cleaning instructions instead of choosing only from the printed design. For anything carried to school or activities, think about whether the shape is easy to pack and whether the current listing describes the lid as suitable for the intended use.</p>'''
        + inline_pick("tumbler", "A practical everyday option; verify capacity, lid design, material and cleaning instructions.")
        + inline_pick("mug-set", "A desk or home-drink idea; check the current finish, capacity and care guidance.")
        + '''<h2>For a bedroom or gaming corner</h2>
        <p>Lighting changes the atmosphere of a room without using wall space. A compact lamp gives a local accent, while a projector can affect a much larger area. Measure the surface or projection distance and confirm power requirements before ordering. If the light is for overnight use, read the maker's controls and safety instructions rather than assuming every decorative light works as a night light.</p>'''
        + inline_pick("cloud-lamp", "A smaller room accent; check the current dimensions, power method and controls.")
        + inline_pick("projector", "A broader room effect; check projection distance, controls and power requirements.")
        + '''<h2>For someone who likes subtle accessories</h2>
        <p>A small keychain or bag charm can carry the theme without changing the whole room. Check the attachment style and dimensions because close-up product images can make a compact accessory look much larger. This type of gift also works when you are less certain about the person's decor preferences.</p>'''
        + inline_pick("keychain", "A compact option for a bag or keys; verify size and attachment style.")
        + '''<h2>Do not confuse generic unicorns with character merchandise</h2>
        <p>If the teen is specifically a My Little Pony fan, check that the product is actually licensed and shows the character or brand they want. A generic unicorn design is not the same thing. My Little Pony is a Hasbro brand, and Unicorn Finds is not affiliated with Hasbro.</p>
        <h2>A quick decision rule</h2>
        <p>If you know the teen's room well, lighting or decor can feel personal. If you know their routines but not their room, choose drinkware or a small accessory. If you know they enjoy crafts, a creative item may be more engaging than passive decor. In every case, confirm the selected version and current listing details before buying.</p>
        <p>For more room-specific planning, see the <a href="/guides/unicorn-bedroom-ideas.html">unicorn bedroom ideas guide</a>. If you need a smaller present, use the <a href="/guides/small-unicorn-gifts-stocking-stuffers.html">small unicorn gifts guide</a>.</p>'''
    ))
    write("guides/unicorn-party-favor-ideas.html", guide_page(
        "Unicorn Party Favor Ideas | Unicorn Finds",
        "Plan unicorn party favors by quantity, usefulness, age guidance and packing. Includes ideas for small accessories and creative take-home items.",
        "/guides/unicorn-party-favor-ideas.html",
        "A party favor works best when it is small enough to hand out easily, useful after the party and appropriate for the guests.",
        '''<h2>Decide whether you want one favor or a mini bag</h2>
        <p>Before shopping, choose the format. One small take-home item is simple to count and pack. A mini favor bag can feel fuller, but it also creates more decisions, more packaging and more chances to buy filler that nobody uses. For a themed party, the bag or tag can carry part of the unicorn look so every object inside does not need to be heavily themed.</p>
        <p>Start with the guest count from your invitation list and add only a small buffer for late changes or damaged packaging. The <a href="/tools/unicorn-party-planner.html">free unicorn party planner</a> can help you think through quantities separately from live retailer prices.</p>
        <h2>Small accessories are easy to distribute</h2>
        <p>A compact accessory can work as a single favor when its size and attachment suit the guests. Check the current dimensions and any stated age guidance. If the favor has a clip, ring or small detachable part, read the manufacturer's information before giving it to younger children.</p>'''
        + inline_pick("keychain", "A possible single-item favor; verify size, attachment style and any current age guidance.")
        + '''<h2>Creative favors can become part of the activity</h2>
        <p>A craft item can do two jobs: it can be an activity during the party and something guests take home. That only works when the pack quantity, materials and time required fit the group. Check exactly what is included. If paints or brushes are not supplied, add those costs and setup needs to your plan rather than discovering the gap on party day.</p>
        <p>For a group craft, protect the table and decide how wet or unfinished items will travel home. A favor that needs hours to dry may be less convenient than it first appears.</p>'''
        + inline_pick("planters", "A possible craft-and-take-home idea; confirm pack quantity, supplies and age guidance on the current listing.")
        + '''<h2>Avoid overfilling favor bags</h2>
        <p>Three useful small items are usually easier to appreciate than a bag full of random plastic pieces. One themed object, one plain consumable and one personalised note can create a complete favor without excess. If you include sweets or food, handle dietary information separately and do not use this site as a source for allergy advice.</p>
        <p>Keep packaging simple. Paper bags, recyclable boxes or reusable pouches are easier to label and transport than elaborate containers that become another thing to manage.</p>
        <h2>Match the favor to the party age and setting</h2>
        <p>For younger guests, small parts and craft materials need closer attention. For older children or teens, a small bag accessory can feel more useful than a toy-like trinket. If guests are travelling home by car, a small box may be fine; if they are walking or taking public transport, lighter favors are easier to carry.</p>
        <h2>Favor checklist</h2>
        <ol><li>Count confirmed guests and choose a modest buffer.</li><li>Check pack quantities rather than assuming one listing equals one guest.</li><li>Read age guidance and small-parts information.</li><li>Confirm what craft supplies or packaging are actually included.</li><li>Label each favor if different versions are intended for different guests.</li><li>Check the current seller, selected variation and return terms before ordering.</li></ol>
        <p>For the rest of the event, use the <a href="/tools/unicorn-party-planner.html">party planner</a>. If the birthday child still needs a present, the <a href="/guides/unicorn-birthday-gifts.html">unicorn birthday gifts guide</a> separates everyday, creative and room-focused ideas.</p>'''
    ))
    write("guides/unicorn-bedroom-ideas.html", guide_page(
        "Unicorn Bedroom Ideas | Unicorn Finds",
        "Plan a unicorn bedroom by focal point, zones, scale and colour. Use lighting, wall art, cushions and small accents without making every surface compete.",
        "/guides/unicorn-bedroom-ideas.html",
        "A unicorn bedroom can feel playful without feeling crowded when you plan the room in zones and let one or two pieces do most of the visual work.",
        '''<h2>Start with the room, not the shopping list</h2>
        <p>Look at what is already fixed: wall colour, bed position, storage, desk and available outlets. Then choose where the theme should be strongest. A wall above the bed, a reading corner or a desk shelf can become the focal zone. This is more flexible than trying to make every object in the room match.</p>
        <p>Take basic measurements before ordering anything. Wall width, shelf depth, cushion size and the space around a bedside table will tell you which ideas are realistic. Product photos are useful for style, but they do not show scale in your room.</p>
        <h2>Zone 1: create one focal point</h2>
        <p>A focal point can be wall art, a lamp or a larger lighting effect. If you choose wall art, check the dimensions of every piece and whether frames or hanging hardware are included. If you choose lighting, consider the power source and where cables will run. Keep the other nearby surfaces quieter so the focal point is easy to notice.</p>'''
        + inline_pick("wall-art", "A possible wall focal point; verify each print's dimensions and whether frames or hardware are included.")
        + '''<h2>Zone 2: add texture near the bed or chair</h2>
        <p>A cushion cover can repeat a colour from the focal point without repeating the exact same image. Check the cover size and whether an insert is included. One soft accent is often enough; using several different unicorn prints on bedding, cushions and curtains can make the room harder to update later.</p>'''
        + inline_pick("pillow-cover", "A smaller textile accent; confirm dimensions, fabric and whether an insert is sold separately.")
        + '''<h2>Zone 3: use lighting for atmosphere</h2>
        <p>A compact lamp suits a shelf or bedside surface, while a projector is designed for a wider effect. Decide whether the goal is a small decorative glow or a room-wide scene. Then check dimensions, controls, power requirements and the manufacturer's instructions for placement. For a child's room, follow the stated age and safety guidance rather than treating every decorative light as suitable for unattended overnight use.</p>'''
        + inline_pick("cloud-lamp", "A compact accent-light idea; check the current size, power method and controls.")
        + inline_pick("projector", "For a broader ceiling or wall effect; verify projection distance, controls and power.")
        + '''<h2>Zone 4: keep the desk useful</h2>
        <p>A desk can carry one small themed object without becoming a display shelf. A paintable planter or small accessory can work if there is enough clear working space. Check what the planter set includes and whether the finished item has a practical place after the craft is done.</p>'''
        + inline_pick("planters", "A creative desk or shelf accent; verify quantity, included supplies and finished dimensions.")
        + '''<h2>Use a simple colour rule</h2>
        <p>Pick two or three colours already present in the room and let new unicorn pieces repeat them. The items do not need to be from one set. A shared palette is usually enough to make different textures and shapes feel connected. Leave plain surfaces visible so the theme has contrast.</p>
        <h2>Build the room in stages</h2>
        <ol><li>Measure the room and choose one focal zone.</li><li>Add one focal item and live with it before filling other surfaces.</li><li>Repeat one or two colours in a textile or small accent.</li><li>Add lighting only after confirming placement and power.</li><li>Stop when each zone has a purpose; empty space is part of the design.</li></ol>
        <p>The existing <a href="/guides/unicorn-room-decor.html">room decor guide</a> focuses on individual decor choices. This bedroom guide is for planning how those choices work together across the whole room.</p>'''
    ))
    write("guides/small-unicorn-gifts-stocking-stuffers.html", guide_page(
        "Small Unicorn Gifts & Stocking Stuffers | Unicorn Finds",
        "Find small unicorn gift and stocking-stuffer ideas by usefulness, size and ease of gifting. Includes compact accessories, creative gifts and drinkware checks.",
        "/guides/small-unicorn-gifts-stocking-stuffers.html",
        "A small gift should feel intentionally chosen, not like a miniature version of a bigger present.",
        '''<h2>Define small by the situation</h2>
        <p>A stocking stuffer, classroom exchange, little thank-you gift and add-on birthday surprise all have different size limits. Before choosing, think about where the gift needs to fit and whether the recipient has to carry it home. Check actual dimensions rather than relying on close-up listing photos.</p>
        <p>Small also does not have to mean disposable. A useful accessory, a compact creative item or practical drinkware can feel more substantial than several novelty pieces.</p>
        <h2>For the smallest surprise</h2>
        <p>A keychain or bag charm is easy to wrap and does not require knowledge of the recipient's room measurements. The important checks are attachment style, physical size and whether any small parts make it unsuitable for the intended recipient. If it is going into a stocking, make sure the packaging itself will fit.</p>'''
        + inline_pick("keychain", "A compact accessory idea; verify the size and attachment style on the current listing.")
        + '''<h2>For a small creative gift</h2>
        <p>A paintable item can feel bigger than its footprint because it includes an activity. Check the number of pieces, finished dimensions and what painting supplies are included. If you are giving it to a child, follow the maker's current age guidance and instructions.</p>'''
        + inline_pick("planters", "A small craft-style present; check pack quantity, included supplies and stated age guidance.")
        + '''<h2>When drinkware still counts as a small gift</h2>
        <p>A mug is not a stocking stuffer in every household, but it can be a compact standalone present or part of a larger gift bag. A more decorative sculpted mug can take extra cabinet space, so check dimensions and care instructions. A standard-shaped mug may be easier to use every day.</p>'''
        + inline_pick("mug-set", "A compact everyday gift; check capacity, current design and washing guidance.")
        + inline_pick("sculpted-mug", "A more decorative option; verify dimensions, lid details and cleaning advice.")
        + '''<h2>Small room accents require measurement too</h2>
        <p>If you want a little decor gift, a cushion cover or compact light may still need information you do not know: insert size, shelf depth, power source or available outlets. When you are uncertain, a portable accessory is the lower-guesswork choice.</p>
        <h2>How to make a small gift feel complete</h2>
        <p>Presentation can do more than adding another product. A short note explaining why you chose the item, simple tissue paper or a reusable pouch can make one small gift feel finished. If you are combining several small pieces, use the <a href="/guides/unicorn-gift-basket-ideas.html">gift basket guide</a> so each item has a role instead of becoming filler.</p>
        <h2>Small-gift checklist</h2>
        <ol><li>Check the actual dimensions and packaging size.</li><li>Choose something that fits a real habit, hobby or place.</li><li>Read age guidance and small-parts information where relevant.</li><li>Confirm care instructions, included parts and selected variation.</li><li>Check the current Amazon seller, availability and return terms before checkout.</li></ol>
        <p>Shopping for an older recipient? The <a href="/guides/unicorn-gifts-for-teens.html">teen gift guide</a> focuses on subtle, practical ways to use the theme.</p>'''
    ))

    write("tools/unicorn-party-planner.html", party_planner())
    write("tools/unicorn-gift-finder.html", gift_finder())
    about_body = f'''<main id="main"><div class="page-intro"><div class="wrap"><span class="eyebrow">Behind the picks</span><h1>About Unicorn Finds</h1><p>A small independent guide to unicorn gifts, lighting and decor.</p></div></div>
      <div class="article wrap"><h2>How we choose what to show</h2>
      <p>We group existing product links by the job a gift or decoration can do. We write practical checklists to help you compare size, materials, cleaning, included parts and placement. We have not personally tested these products, and we do not reproduce Amazon customer ratings or reviews.</p>
      <p>Our collection is a starting point. Product pages, sellers, images, prices and availability can change. Please confirm that the item shown on Amazon matches the description and suits your needs before you purchase. One night-light link opens Amazon search results rather than a particular item, and we label it as such.</p>
      <h2>Affiliate disclosure</h2>{affiliate_note()}
      <p>We may receive a commission if you follow a paid link and make a qualifying purchase. This helps support the site; it does not add a charge to your order. We do not process orders or handle delivery and returns.</p>
      <h2>Independent, not official</h2><p>Unicorn Finds is not an official Amazon, Hasbro, My Little Pony or Netflix store. References to those names describe third-party products or brands; they do not imply a partnership.</p>
      <p><a href="/privacy.html">Read our privacy information</a> · <a href="/#shop">Browse the collection</a></p></div></main>'''
    write("about.html", page(
        "About & Affiliate Disclosure | Unicorn Finds",
        "Learn how Unicorn Finds selects product ideas, how Amazon affiliate links work and what we have and have not tested.",
        "/about.html", about_body, active="/about.html",
    ))
    privacy_body = '''<main id="main"><div class="page-intro"><div class="wrap"><span class="eyebrow">Site information</span><h1>Privacy</h1><p>What happens when you visit Unicorn Finds or follow a product link.</p></div></div>
      <div class="article wrap"><h2>On this site</h2><p>This is a static website. It does not have user accounts. The party planner processes numbers in your browser and does not send or save them. The hosting provider may process technical request data needed to serve pages; its own privacy terms apply.</p>
      <h2>Advertising</h2><p>Unicorn Finds uses Google AdSense to serve and measure advertising. Google and its advertising partners may use cookies, device identifiers or other local storage to select, deliver, measure and protect ads. Depending on your location and consent choices, ads may be personalised or non-personalised. Where consent is required, Google’s consent tools or another Google-certified consent management platform are used before personalised advertising is served.</p>
      <h2>When you follow a link</h2><p>Product links take you to Amazon. Amazon may process your visit and purchase according to its own privacy notice and affiliate program. We do not see your payment details or the contents of your order. The site also links to third-party information; their privacy notices apply when you visit them.</p>
      <h2>Changes</h2><p>This page is reviewed when advertising, analytics, newsletter or contact features change. Last revised: 3 October 2026.</p>
      <p><a href="/about.html">Read the affiliate disclosure</a> · <a href="/">Back to the home page</a></p></div></main>'''
    write("privacy.html", page(
        "Privacy | Unicorn Finds",
        "Read how this static gift guide works and what happens when you follow an Amazon affiliate link.",
        "/privacy.html", privacy_body,
    ))
    urls = ["/", "/guides/index.html", "/guides/unicorn-birthday-gifts.html", "/guides/unicorn-gifts-for-kids.html", "/guides/unicorn-gifts-for-adults.html", "/guides/unicorn-night-lights.html", "/guides/unicorn-room-decor.html", "/guides/unicorn-gift-basket-ideas.html", "/guides/unicorn-gifts-for-teens.html", "/guides/unicorn-party-favor-ideas.html", "/guides/unicorn-bedroom-ideas.html", "/guides/small-unicorn-gifts-stocking-stuffers.html", "/tools/unicorn-gift-finder.html", "/tools/unicorn-party-planner.html", "/about.html", "/privacy.html"]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(
        f'  <url><loc>{xml_escape(BASE + path)}</loc></url>\n' for path in urls
    ) + '</urlset>\n'
    write("sitemap.xml", sitemap)
    write("robots.txt", "User-agent: *\nAllow: /\nSitemap: https://unicornsite.online/sitemap.xml\n")
    write("ads.txt", "google.com, pub-8108579336605864, DIRECT, f08c47fec0942fa0\n")
    write("unicorn-store (2).html", '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex,follow"><link rel="canonical" href="https://unicornsite.online/"><meta http-equiv="refresh" content="0; url=/"><title>Unicorn Finds has moved</title></head><body><p>The store is now at <a href="/">Unicorn Finds</a>.</p></body></html>\n''')


if __name__ == "__main__":
    main()
