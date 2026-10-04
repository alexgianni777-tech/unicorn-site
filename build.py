"""Build the static Unicorn Finds site with Python's standard library.

Product titles and links live in products.json. Only publish a product after a
human has checked its destination against the label and image. No prices,
availability, Amazon ratings or customer reviews are stored here.
"""

from __future__ import annotations

import html
from activities import render as activities
from memory_game import render as memory_game
from treasure_hunt import render as treasure_hunt
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
        ("Free games", "/tools/free-unicorn-games.html"),
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
          <strong>Free games &amp; planning tools</strong>
          <a href="/tools/free-unicorn-games.html">All free activities</a>
          <a href="/tools/unicorn-memory-game.html">Play unicorn memory</a>
          <a href="/tools/unicorn-treasure-hunt.html">Printable treasure hunt</a>
          <a href="/tools/unicorn-party-games.html#bingo">Printable bingo</a>
          <a href="/tools/birthday-cake-servings-calculator.html">Cake guide &amp; servings calculator</a>
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
{header(active or path)}
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
          <div class="hero-actions"><a class="button" href="#quick-picks">Find a gift ↓</a><a class="button button-light" href="/tools/free-unicorn-games.html">Free games &amp; printables</a></div>
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
          <a class="guide-tile" href="/tools/unicorn-memory-game.html"><span class="tile-icon" aria-hidden="true">🦄</span><h3>Play unicorn memory</h3><p>Find six matching pairs in a free browser game. No timer or sign-up.</p><span class="tile-link">Play now →</span></a>
          <a class="guide-tile" href="/tools/unicorn-treasure-hunt.html"><span class="tile-icon" aria-hidden="true">✨</span><h3>Free unicorn treasure hunt</h3><p>Print six hiding cards and a picture-matching sheet for an easy party adventure.</p><span class="tile-link">Get the printable game →</span></a>
          <a class="guide-tile" href="/tools/unicorn-party-games.html"><span class="tile-icon" aria-hidden="true">🌈</span><h3>Party games &amp; free bingo</h3><p>Five easy games, printable cards and a word caller for your unicorn party.</p><span class="tile-link">Choose a game</span></a>
          <a class="guide-tile" href="/tools/birthday-cake-servings-calculator.html"><span class="tile-icon" aria-hidden="true">🎂</span><h3>Cake servings calculator</h3><p>Calculate how many cakes to order using your guest count and baker’s portion sizes.</p><span class="tile-link">Plan cake portions</span></a>
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
        image=article_image, published=article_published,
        modified="2026-10-03" if path == "/guides/unicorn-night-lights.html" else "2026-10-02",
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
        <p>Choose a gift type above to see three ideas. If the selector does not load, <a href="/#shop">browse all ten gifts here</a>.</p>
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
      <p class="field-help">Bookmark or copy the page address after selecting a gift type to return to the same category. No personal details are included.</p><p class="finder-next"><a href="/guides/unicorn-birthday-gifts.html">Shopping for a birthday? Read the birthday guide →</a></p>
    </div><script src="/assets/gift-finder.js?v=20261004" defer></script></main>'''
    return page(
        "Unicorn Gift Finder: Quick Gift Ideas | Unicorn Finds",
        "Use a free unicorn gift finder to narrow ten curated gift ideas to three starting points for everyday gifts, room lighting, creative gifts or small surprises.",
        "/tools/unicorn-gift-finder.html", body, active="/tools/unicorn-gift-finder.html",
    ).replace("</head>", '<link rel="stylesheet" href="/assets/gift-finder.css"></head>')


def party_planner() -> str:
    body = '''<main id="main"><div class="page-intro"><div class="wrap">
      <div class="breadcrumbs"><a href="/">Home</a> / Free tools</div>
      <span class="eyebrow">Plan, then play</span><h1>Free unicorn party planner</h1>
      <p>Estimate supplies and your own budget in one place. Print the result for a shopping trip or a conversation with another organiser.</p>
    </div></div><div class="article wrap party-page"><nav class="callout" aria-label="Unicorn party tools"><strong>Plan your unicorn party</strong><p><a href="/tools/unicorn-party-planner.html">Budget &amp; supplies</a> · <a href="/tools/unicorn-party-games.html">Games &amp; bingo</a> · <a href="/tools/birthday-cake-servings-calculator.html">Cake &amp; decorating tools</a></p></nav>
      <p>This planner runs in your browser. It does not send your numbers to us, save a guest list or assume current shop prices. Enter the prices you find and adjust the quantities for your particular party.</p>
      <form id="party-planner" class="planner-form">
        <fieldset><legend>People and supplies</legend><div class="planner-fields">
          <label>Invited guests <input id="party-guests" type="number" min="1" max="300" step="1" value="12" required></label>
          <label>Hosts and other people <input id="party-hosts" type="number" min="0" max="100" step="1" value="2" required></label>
          <label>Extra supplies (%) <input id="party-buffer" type="number" min="0" max="100" step="1" value="10" required></label>
        </div><p class="field-help">The supply estimate starts at one plate and one cup per person. Adjust it for reusable tableware, multiple servings and your guest list.</p></fieldset>
        <fieldset><legend>How many packs do you need?</legend><div class="planner-fields">
          <label>Plates in one pack <input id="party-plate-pack" type="number" min="1" max="1000" step="1" value="8" required></label>
          <label>Cups in one pack <input id="party-cup-pack" type="number" min="1" max="1000" step="1" value="8" required></label>
          <label>Favor bags in one pack <input id="party-bag-pack" type="number" min="1" max="1000" step="1" value="12" required></label>
        </div><p class="field-help">These pack sizes are examples. Replace them with the quantities in the listing you are considering. For mixed sets, count each item separately: a “100-piece set” may serve far fewer than 100 people.</p></fieldset>
        <fieldset><legend>Enter your own estimated costs</legend><div class="planner-fields">
          <label>Currency <select id="party-currency"><option value="USD">USD ($)</option><option value="GBP">GBP (£)</option><option value="EUR">EUR (€)</option><option value="SEK">SEK (kr)</option></select></label>
          <label>Food and drink per person <input id="party-food" type="number" min="0" max="100000" step="0.01" inputmode="decimal" placeholder="0.00"></label>
          <label>Favor per invited guest <input id="party-favor" type="number" min="0" max="100000" step="0.01" inputmode="decimal" placeholder="0.00"></label>
          <label>Cake or dessert, total <input id="party-cake" type="number" min="0" max="100000" step="0.01" inputmode="decimal" placeholder="0.00"></label>
          <label>Decorations, total <input id="party-decor" type="number" min="0" max="100000" step="0.01" inputmode="decimal" placeholder="0.00"></label>
          <label>Tableware and other costs, total <input id="party-other" type="number" min="0" max="100000" step="0.01" inputmode="decimal" placeholder="0.00"></label>
          <label>Target budget (optional) <input id="party-target" type="number" min="0" max="10000000" step="0.01" inputmode="decimal" placeholder="Your spending limit"></label>
          <label>Activities, total <input id="party-activities" type="number" min="0" max="100000" step="0.01" inputmode="decimal" placeholder="0.00"></label>
        </div><p class="field-help">These are planning inputs, not quotes or live prices. Leaving an amount blank counts it as zero.</p></fieldset>
      </form>
      <section id="party-result" class="planner-result" aria-live="polite" aria-atomic="true">
        <h2>Your starting list</h2><p>For 12 guests and 2 other people, start with 16 plates and 16 cups if using one of each per person. Plan 12 favors. Add your own estimated costs above to see a budget.</p>
      </section>
      <noscript><p>Enable JavaScript to calculate your quantities and budget. You can still use the shopping checklist and party outline below.</p></noscript>
      <button class="button planner-print" id="party-print" type="button">Print this plan</button>
      <section id="party-shopping"><h2>Your party shopping checklist</h2><p>Use the pack counts above, then check what you already own before buying. Tick items as you arrange them; ticks are kept only until you reload. Your printout includes this checklist.</p>''' + affiliate_note() + '''<div class="supply-grid"><article class="supply-card"><span aria-hidden="true">🍽️</span><h3>Plates</h3><p>Check the number of dinner plates, their size and whether smaller cake plates are separate.</p><label><input type="checkbox"> Plates sorted</label><a class="button" href="https://www.amazon.com/s?k=unicorn+party+plates&amp;tag=unicornmagic2-20" target="_blank" rel="sponsored nofollow noopener noreferrer">Find plates on Amazon</a><small>Paid link · Amazon search results</small></article><article class="supply-card"><span aria-hidden="true">🥤</span><h3>Cups</h3><p>Check the cup count, capacity and suitability for the drinks you will serve.</p><label><input type="checkbox"> Cups sorted</label><a class="button" href="https://www.amazon.com/s?k=unicorn+party+cups&amp;tag=unicornmagic2-20" target="_blank" rel="sponsored nofollow noopener noreferrer">Find cups on Amazon</a><small>Paid link · Amazon search results</small></article><article class="supply-card"><span aria-hidden="true">🎁</span><h3>Favor bags</h3><p>Check bag dimensions and pack count. Bags may be sold empty; fillings are a separate choice.</p><label><input type="checkbox"> Favor bags sorted</label><a class="button" href="https://www.amazon.com/s?k=unicorn+party+favor+bags&amp;tag=unicornmagic2-20" target="_blank" rel="sponsored nofollow noopener noreferrer">Find favor bags on Amazon</a><small>Paid link · Amazon search results</small></article></div><p>Finish with <a href="/tools/birthday-cake-servings-calculator.html#cake-tools">cake decorating tools</a>, <a href="/tools/unicorn-party-games.html#choose-game">game supplies</a> and <a href="/guides/unicorn-party-favor-ideas.html">favor filling ideas</a>.</p></section>
      <p>Ordering cake? Use the <a href="/tools/birthday-cake-servings-calculator.html">birthday cake servings calculator</a> to check portions and cake quantities.</p>
      <p>Choose activities from our <a href="/tools/unicorn-party-games.html">unicorn party games and free printable bingo</a>.</p><h2>A flexible 90-minute party outline</h2>
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
    </div><script src="/assets/party-planner.js?v=20261004" defer></script></main>'''
    return page(
        "Free Unicorn Birthday Party Planner & Budget | Unicorn Finds",
        "Plan a unicorn party with a free guest supply and budget calculator, a printable list and a flexible 90-minute outline. No account or live prices needed.",
        "/tools/unicorn-party-planner.html", body, active="/tools/unicorn-party-planner.html",
    ).replace("</head>", '<link rel="stylesheet" href="/assets/party-planner.css?v=20261004"></head>')


def cake_calculator() -> str:
    body = """<main id="main"><div class="page-intro"><div class="wrap">
      <div class="breadcrumbs"><a href="/">Home</a> / Free party tools</div>
      <h1>Plan your unicorn birthday cake</h1>
      <p>Work out how many cakes to order for a unicorn party or any birthday. Use your baker's stated servings instead of guessing from a photo.</p>
      <div class="hero-actions"><a class="button" href="#cake-calculator">Calculate servings</a><a class="button button-light" href="#cake-tools">Explore decorating tools</a></div>
    </div></div><div class="article wrap party-page"><nav class="callout" aria-label="Unicorn party tools"><strong>Plan your unicorn party</strong><p><a href="/tools/unicorn-party-planner.html">Budget &amp; supplies</a> · <a href="/tools/unicorn-party-games.html">Games &amp; bingo</a> · <a href="/tools/birthday-cake-servings-calculator.html">Cake &amp; decorating tools</a></p></nav>
      <figure class="cake-photo"><img src="https://images.unsplash.com/photo-1557164158-11e97f2bb220?auto=format&amp;fit=max&amp;w=1000&amp;q=85" alt="Real white birthday cake with pink drip icing, colourful decorations and a silver unicorn topper on a pink stand" width="1000" height="1675" fetchpriority="high"><figcaption>Unicorn cake inspiration. Photo by <a href="https://unsplash.com/photos/white-and-pink-unicorn-cake-on-a-pink-stand-TiSLq6Gbftg">Deva Williamson / Unsplash</a>, used under the <a href="https://unsplash.com/license">Unsplash License</a>. The photo does not show products sold through the links below.</figcaption></figure>
      <section id="cake-video" aria-labelledby="cake-video-title"><h2 id="cake-video-title">Watch: decorate a unicorn cake</h2>
      <p>Follow Cupcake Jemma's <em>Full Unicorn Cake Tutorial &amp; How-To</em> for the unicorn finish. This decorating tutorial starts with a baked, filled and crumb-coated cake. Use the cake and buttercream recipes linked in the creator's video description for the baking stage.</p>
      <div id="cake-video-player" class="cake-video-box"><button class="button" id="cake-video-load" type="button" hidden>Load YouTube tutorial</button><p>Loading the player connects to YouTube. The creator's video remains on YouTube.</p></div>
      <p><a href="https://www.youtube.com/watch?v=INsj_kdOVCE" target="_blank" rel="noopener noreferrer">Watch the tutorial and open its recipe links on YouTube</a></p>
      <p>Prefer a different style? See Cupcake Jemma's <a href="https://www.youtube.com/watch?v=wQlJniA_t88" target="_blank" rel="noopener noreferrer">sprinkle unicorn cake baking tutorial</a>, with ingredient quantities in its description.</p></section>
      <h2>Calculate your cake servings</h2>
      <form id="cake-calculator" class="planner-form">
        <fieldset><legend>Your cake plan</legend><div class="planner-fields">
          <label>People eating cake <input id="cake-guests" type="number" min="1" max="1000" step="1" value="20" required></label>
          <label>Extra servings (%) <input id="cake-buffer" type="number" min="0" max="100" step="1" value="10" required></label>
          <label>Servings per cake <input id="cake-servings" type="number" min="1" max="1000" step="1" value="12" required></label>
        </div><p class="field-help">Include adults who will eat cake. The default 12 servings is an example, not a standard cake size. Enter the portion count for the cake you are considering.</p></fieldset>
      </form>
      <section id="cake-result" class="planner-result" aria-live="polite" aria-atomic="true">
        <h2>Example: order 2 cakes</h2><p>For 20 people plus 10% extra, plan 22 servings. Two cakes with 12 servings each provide 24 servings, leaving 4 after one serving per person.</p>
      </section>
      <noscript><p>To calculate another plan without JavaScript: multiply people by (1 + extra percentage / 100), round up, then divide by servings per cake and round up again.</p></noscript>
      <button class="button planner-print" id="cake-print" type="button" hidden>Print cake plan</button>

      <section id="cake-tools" aria-labelledby="cake-tools-title"><h2 id="cake-tools-title">Tools for your unicorn cake</h2>
      <p>Start with the finish you want: a smooth base, a piped mane and a horn-and-ears topper. Check what you already own before buying a full kit.</p>
      """ + affiliate_note() + """
      <p>These paid links open Amazon.com search results, not specific tested products. Compare the exact contents, dimensions and delivery to your country.</p>
      <div class="cake-tools-grid"><article class="cake-tool"><span class="eyebrow">01 · Smooth the frosting</span><h3>Cake turntable and scraper</h3><p>A rotating stand, offset spatula and scraper can help you reach the sides of the cake. Compare stand diameter, stability and what the kit includes.</p><a class="button" href="https://www.amazon.com/s?k=cake+decorating+turntable+scraper+spatula+kit&amp;tag=unicornmagic2-20" target="_blank" rel="sponsored nofollow noopener noreferrer">Browse on Amazon</a><small>Paid link · Search results</small></article><article class="cake-tool"><span class="eyebrow">02 · Pipe a colourful mane</span><h3>Piping bags and tips</h3><p>Compare star tips and piping bags for swirls and rosettes. Check tip sizes, bag compatibility and whether couplers are included.</p><a class="button" href="https://www.amazon.com/s?k=cake+decorating+piping+bags+star+tips+set&amp;tag=unicornmagic2-20" target="_blank" rel="sponsored nofollow noopener noreferrer">Browse on Amazon</a><small>Paid link · Search results</small></article><article class="cake-tool"><span class="eyebrow">03 · Add the unicorn details</span><h3>Horn and ears cake toppers</h3><p>Look for a topper that suits the cake height and width. Confirm whether it is edible; remove non-edible decorations before serving.</p><a class="button" href="https://www.amazon.com/s?k=unicorn+cake+topper+horn+ears&amp;tag=unicornmagic2-20" target="_blank" rel="sponsored nofollow noopener noreferrer">Browse on Amazon</a><small>Paid link · Search results</small></article><article class="cake-tool"><span class="eyebrow">04 · Choose your cake shape</span><h3>Round cake pans</h3><p>Match pan dimensions and depth to your recipe. A pan diameter is not a serving guarantee; use the baker or recipe serving estimate above.</p><a class="button" href="https://www.amazon.com/s?k=round+cake+pans+set&amp;tag=unicornmagic2-20" target="_blank" rel="sponsored nofollow noopener noreferrer">Browse on Amazon</a><small>Paid link · Search results</small></article></div><p>For colour, choose products explicitly labelled for food use. Follow the recipe and product instructions; decorative craft glitter is not a substitute for edible decoration.</p></section>
      <h2>How much cake do you need for 20, 30 or 50 guests?</h2>
      <p>This example uses a 10% allowance and cakes labelled as 12 servings each. Substitute your baker's portion count; these figures are not a cake-diameter chart.</p>
      <div class="table-scroll"><table class="pick-table"><thead><tr><th>People</th><th>Target servings</th><th>12-serving cakes</th><th>Total servings</th></tr></thead>
      <tbody><tr><td>20</td><td>22</td><td>2</td><td>24</td></tr><tr><td>30</td><td>33</td><td>3</td><td>36</td></tr><tr><td>50</td><td>55</td><td>5</td><td>60</td></tr></tbody></table></div>
      <h2>Choose a cake size with your baker</h2>
      <p>Ask how many portions the exact cake serves and what size each portion is. Diameter alone does not tell you the serving count: height, shape and cutting pattern also matter. If one cake is too small, compare a larger cake with two smaller ones by changing the servings input.</p>
      <p>The calculator assumes cakes of the same serving capacity. For a mixed order, add the stated servings of each cake and compare the sum with the target servings shown above.</p>
      <h2>A worked example</h2>
      <p>For 20 people and 10% extra, the target is 22 servings. At 12 servings per cake, 22 divided by 12 is 1.83, so round up to 2 cakes. That provides 24 servings: 4 beyond the guest count and 2 beyond the target that already includes your allowance.</p>
      <h2>Plan the rest of the birthday</h2><p>Add <a href="/tools/unicorn-party-games.html">unicorn party games and free bingo</a> to your celebration.</p>
      <p>Use the <a href="/tools/unicorn-party-planner.html">free party budget and supplies planner</a> for plates, cups and your own estimated costs. For take-home gifts, see our <a href="/guides/unicorn-party-favor-ideas.html">unicorn party favor ideas</a>.</p>
      <section aria-labelledby="cake-checklist-title"><h2 id="cake-checklist-title">Your unicorn cake preparation checklist</h2>
      <p>Tick off your plan as you go, then use “Print cake plan” above. Ticks are not saved after you reload.</p>
      <div class="cake-checklist">
        <label><input type="checkbox" class="cake-task"> Confirm guests, portions and dietary requirements.</label>
        <label><input type="checkbox" class="cake-task"> Choose a tested cake and frosting recipe; check its yield and pan sizes.</label>
        <label><input type="checkbox" class="cake-task"> Check the tools you own before shopping for extras.</label>
        <label><input type="checkbox" class="cake-task"> Plan baking, cooling and decorating time from your recipe.</label>
        <label><input type="checkbox" class="cake-task"> Choose food-safe colours and confirm which decorations are edible.</label>
        <label><input type="checkbox" class="cake-task"> Arrange a suitable cake board, box and storage for the finished cake.</label>
      </div><p id="cake-task-progress" role="status">0 of 6 planning steps complete.</p></section>
      <h2>Choose how much you want to make yourself</h2>
      <div class="table-scroll"><table class="pick-table"><thead><tr><th>Approach</th><th>Your work</th><th>What to check</th></tr></thead><tbody>
      <tr><td>Decorate a ready-made cake</td><td>Add a suitable topper and your chosen finishing details.</td><td>Existing frosting, cake height, topping weight and storage instructions.</td></tr>
      <tr><td>Bake and decorate</td><td>Follow a tested recipe, then add the unicorn finish.</td><td>Recipe yield, pan sizes, cooling time and piping tools.</td></tr>
      <tr><td>Order from a baker</td><td>Agree portions, design and collection.</td><td>Written price, dietary requirements, serving size and transport.</td></tr>
      </tbody></table></div>
      <h2>Unicorn cake planning questions</h2>
      <details><summary>Do I need a special unicorn-shaped pan?</summary><p>A horn-and-ears design can be added to a round cake, as in the decorating tutorial above. Choose the pans required by the recipe rather than buying a novelty pan automatically.</p></details>
      <details><summary>What should a beginner buy first?</summary><p>Start with the recipe and design. Check whether you already have suitable pans, a spatula and a cake board. Add piping bags and the required tips if you want a piped mane; a ready-made topper is another option. Compare kit contents to avoid duplicates.</p></details>
      <details><summary>Can I use the photograph as a serving-size guide?</summary><p>No. The photo is style inspiration, not a portion chart or a tested recipe. Use your recipe's yield or your baker's portion estimate in the calculator.</p></details>
      <details><summary>How far ahead can I make the cake?</summary><p>Use the storage and make-ahead instructions for your exact cake, filling and frosting. Different fillings need different handling; the decoration does not determine a safe storage time.</p></details>
      <h2>Before ordering</h2>
      <ul><li>Confirm attendance and whether accompanying adults want cake.</li><li>Ask about dietary requirements and arrange suitable alternatives with your baker.</li><li>Confirm portion sizes, collection time, storage instructions and the final price.</li><li>A decorative cake and plain extra portions can be compared as a mixed order; ask the baker for a quote.</li></ul>
      <p>Your calculator inputs stay in your browser and are not saved or sent by this tool. See our <a href="/privacy.html">privacy notice</a> for information about advertising.</p>
    </div><script src="/assets/cake-calculator.js" defer></script></main>"""
    return page("Unicorn Cake Guide, Tools & Servings Calculator | Unicorn Finds",
        "Plan a unicorn birthday cake with real cake inspiration, decorating videos, an interactive checklist, baking-tool ideas and a free cake servings calculator.",
        "/tools/birthday-cake-servings-calculator.html", body).replace('/assets/style.css', '/assets/style.css?v=cake-20261003')


def party_games() -> str:
    games = [
        ("Pin the horn on the unicorn", "Suggested ages 5+ · 3–12 players · 10–15 minutes", "Draw a unicorn head on a large sheet of paper. Give each player a paper horn with reusable adhesive. Players take turns placing it while looking away; an optional blindfold needs adult supervision and a clear standing area. Do not spin players. The nearest horn wins; younger children can play with their eyes open.", "unicorn+pin+the+horn+party+game", "Browse ready-made horn games"),
        ("Rainbow treasure hunt", "Suggested ages 4+ · 2–12 players · 15–20 minutes", "Hide six coloured paper clues in an agreed area. Try these prompts: find somewhere shoes rest; look beside a storybook; check near a chair; look where coats hang; find a cushion; finish beside the party table. Adapt each clue to your space and keep clues away from roads, water and climbing spots. Let everyone share the final discovery.", "unicorn+party+favor+bags", "Browse unicorn favor bags"),
        ("Unicorn ring toss", "Suggested ages 5+ · 2–12 players · 10 minutes", "Use a floor-standing target and soft rings. Mark a throwing line, give each player three throws and award one point per ring that lands on the target. Bring the line closer for younger players. Keep the target off people's heads and let everyone finish throwing before collecting rings.", "unicorn+ring+toss+game", "Browse unicorn ring-toss sets"),
        ("Decorate your own unicorn", "Suggested ages 4+ with an adult · 2–12 players · 15–25 minutes", "Draw a simple unicorn outline on paper and offer crayons, paper shapes and washable colouring supplies. Invite each child to give their unicorn a name and one magical ability. Display everyone's creation rather than judging a winner. Choose age-appropriate supplies and follow their labels.", "unicorn+craft+kit+kids", "Browse unicorn craft kits"),
        ("Unicorn word bingo", "Suggested ages 6+ or with reading help · 2–12 players · 10–20 minutes", "Print one different card per player using the generator above. The host calls words at random and players mark matching squares. Agree the winning pattern first: four across, down or diagonally. No free square. Check each winning word against the host's called-word list.", "unicorn+bingo+game", "Browse ready-made unicorn bingo"),
    ]
    sections = "".join(f'<section class="game-rule" id="game-{number}"><h2>{esc(name)}</h2><p class="eyebrow">{esc(meta)}</p><p>{esc(rule)}</p><a class="button game-shop" href="https://www.amazon.com/s?k={query}&amp;tag=unicornmagic2-20" target="_blank" rel="sponsored nofollow noopener noreferrer">{esc(label)} (paid link)</a></section>' for number,(name,meta,rule,query,label) in enumerate(games, 1))
    comparisons = [
        ("A quick group game", "Paper picture, paper horns and reusable adhesive", "Check the number of horns and whether adhesive is included."),
        ("Exploring together", "Six paper clues; bags are optional", "Count one favor bag per child if you use them."),
        ("An active game", "Soft rings and a stable floor target", "Check target dimensions, ring count and age guidance."),
        ("A calm arrival activity", "Paper and crayons, or a craft kit", "Check usable pieces per child and whether colouring supplies are included."),
        ("A seated group game", "Our free cards and pencils, or a ready-made set", "Check how many different player cards the box contains."),
    ]
    shopping = '<section id="choose-game"><h2>Choose a game and its supplies</h2><p>Pick the activity first. Each option includes a version you can prepare yourself and an optional ready-made alternative.</p>' + affiliate_note() + '<p>Paid links open Amazon.com search results. Compare the selected item and delivery to your country before buying.</p><div class="game-choice-grid">'
    for number, ((name,meta,rule,query,label),(fit,diy,check)) in enumerate(zip(games, comparisons),1):
        shopping += f'<article class="game-choice"><span class="eyebrow">{esc(fit)}</span><h3>{esc(name)}</h3><p>{esc(meta)}</p><p><strong>Prepare it yourself:</strong> {esc(diy)}.</p><p><strong>If buying:</strong> {esc(check)}</p><a href="#game-{number}">Read the game rules</a><a class="button game-shop" href="https://www.amazon.com/s?k={query}&amp;tag=unicornmagic2-20" target="_blank" rel="sponsored nofollow noopener noreferrer">{esc(label)}</a><small>Paid link · Amazon search results</small></article>'
    shopping += '</div></section>'
    body = """<main id="main"><div class="page-intro"><div class="wrap">
      <div class="breadcrumbs"><a href="/">Home</a> / <a href="/tools/free-unicorn-games.html">Free games &amp; printables</a> / Party games</div><h1>Unicorn party games &amp; free printable bingo</h1>
      <p>Five easy party activities, with suggested ages, group sizes and instructions. Make different bingo cards for up to 12 players, then use the on-screen word caller to host.</p>
      <div class="hero-actions"><a class="button" href="#bingo">Make free bingo cards</a><a class="button button-light" href="#choose-game">Compare games &amp; supplies</a></div>
    </div></div><div class="article wrap games-page"><nav class="callout" aria-label="Unicorn party tools"><strong>Plan your unicorn party</strong><p><a href="/tools/unicorn-party-planner.html">Budget &amp; supplies</a> · <a href="/tools/unicorn-party-games.html">Games &amp; bingo</a> · <a href="/tools/birthday-cake-servings-calculator.html">Cake &amp; decorating tools</a></p></nav>
      <aside class="callout"><h2>New: free printable unicorn treasure hunt</h2><p>Hide six picture cards, then let children find and tick matching symbols. Includes a player sheet and simple setup instructions.</p><a class="button" href="/tools/unicorn-treasure-hunt.html">Get the free treasure hunt</a></aside><aside class="callout"><h2>Play unicorn memory online</h2><p>Find six matching pairs at your own pace, on a phone or computer.</p><a class="button" href="/tools/unicorn-memory-game.html">Play the free memory game</a></aside>
      """ + shopping + """
      <section id="bingo" aria-labelledby="bingo-title"><h2 id="bingo-title">Free unicorn bingo generator</h2>
      <p>Each card has 16 words in a 4 × 4 grid. Cards use different selections from the same 24-word pool. Children who are still learning to read can play with a helper.</p>
      <noscript><p>Enable JavaScript to generate cards. You can still use all five party-game instructions below without it.</p></noscript>
      <form id="bingo-form" class="planner-form"><label for="bingo-count">Number of players (1–12)</label>
        <input id="bingo-count" type="number" min="1" max="12" step="1" value="4" required>
        <button class="button" type="submit">Generate cards</button></form>
      <p id="bingo-status" role="status"></p>
      <button class="button planner-print" id="bingo-print" type="button" hidden>Print cards and host word list</button>
      <div id="bingo-cards"></div>
      <section id="bingo-host" hidden><h3>Host word caller</h3><p>Print the cards first, then call words here. Mark printed cards with a pencil. Generating new cards starts a new game and clears the caller.</p>
        <button class="button" id="bingo-call" type="button">Call next word</button>
        <p id="bingo-current" role="status">Ready for the first word.</p><p id="bingo-history"></p></section>
      <section class="bingo-word-list"><h3>Host word list</h3><p>Unicorn · Rainbow · Star · Moon · Cloud · Sparkle · Castle · Crown · Wand · Wings · Flower · Heart · Crystal · Meadow · Cupcake · Ribbon · Balloon · Wish · Magic · Sunshine · Butterfly · Jewel · Dream · Friendship</p><p>Winning pattern: four in a row across, down or diagonally. No free square.</p></section>
      <p class="field-help">Free for your personal party use. No account or download required. The tool does not save your cards or send your inputs; keep the page open while hosting. Printing can also save a PDF through your browser.</p></section>
      <h2>Pick games for your party</h2><p>These ages, group sizes and timings are planning suggestions, not product age ratings. Adjust for the children, space and available supervision.</p>
      """ + affiliate_note() + """<p>Amazon links below open search results for supplies, not specific reviewed products. Check age labels, pack quantities and delivery to your country. You can play the paper-based versions with supplies you already have.</p>""" + sections + """
      <h2>A simple three-activity plan</h2><ol><li>Start with decorating a unicorn while guests arrive.</li><li>Move to a short treasure hunt or ring toss after everyone has settled in.</li><li>Finish with bingo when a seated activity suits the group.</li></ol>
      <p>Leave room for food and breaks. Use the <a href="/tools/unicorn-party-planner.html">party budget and supplies planner</a> for quantities and the <a href="/tools/birthday-cake-servings-calculator.html">unicorn cake guide</a> for cake ideas, videos and portions.</p>
      <h2>Do you need prizes?</h2><p>No. Applause, choosing the next game or naming the group's unicorn can be enough. If you use take-home gifts, consider one for every child; our <a href="/guides/unicorn-party-favor-ideas.html">party favor guide</a> helps with quantities and age checks.</p>
    </div><script src="/assets/unicorn-bingo.js" defer></script></main>"""
    return page("Unicorn Party Games & Free Printable Bingo | Unicorn Finds", "Plan five unicorn party games and generate free printable bingo cards for up to 12 players. Includes a random word caller, rules and optional party supplies.", "/tools/unicorn-party-games.html", body).replace('</head>', '<link rel="stylesheet" href="/assets/unicorn-bingo.css?v=20261004"></head>')


def write(path: str, contents: str) -> None:
    destination = ROOT / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(contents, encoding="utf-8")


def main() -> None:
    write("index.html", home())
    write("tools/unicorn-party-games.html", party_games())
    write("tools/birthday-cake-servings-calculator.html", cake_calculator())
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
        '''<section aria-labelledby="lighting-shortlist"><h2 id="lighting-shortlist">Choose your room effect</h2>
        <p>Start with the space you want to light. These are curated ideas, not hands-on reviews. The links below go to Amazon.com; check delivery to your country.</p>'''
        + inline_pick("cloud-lamp", "For a bedside table or shelf: start with this decorative lamp if you want one compact focal point. Check dimensions, power supply and whether brightness can be adjusted.")
        + inline_pick("projector", "For a ceiling or wall: compare this projector if you want a broader room effect. Check projection distance, scenes, controls and any timer before choosing.")
        + inline_pick("night-light-search", "Still deciding? Browse Amazon search results for other unicorn night-light styles. Compare dimming and power options on the individual listings.")
        + '''<p><a href="#lighting-checklist">Check power, controls and placement before buying</a></p></section>
        <h2>Decide what the light needs to do</h2>
        <p>For a bedside table, a compact lamp keeps the effect local. For a large wall or ceiling, a projector changes the whole room. If the light will be used at bedtime, check whether it can be dimmed or switched off easily. For a decorative display, colour choices may matter more than brightness.</p>
        <h2 id="lighting-checklist">Check the practical details</h2>
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

    write("tools/unicorn-treasure-hunt.html", treasure_hunt(page, affiliate_note))
    write("tools/free-unicorn-games.html", activities(page))
    write("tools/unicorn-memory-game.html", memory_game(page))
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
    urls = ["/tools/free-unicorn-games.html", "/tools/unicorn-memory-game.html", "/tools/unicorn-treasure-hunt.html", "/tools/unicorn-party-games.html", "/tools/birthday-cake-servings-calculator.html", "/", "/guides/index.html", "/guides/unicorn-birthday-gifts.html", "/guides/unicorn-gifts-for-kids.html", "/guides/unicorn-gifts-for-adults.html", "/guides/unicorn-night-lights.html", "/guides/unicorn-room-decor.html", "/guides/unicorn-gift-basket-ideas.html", "/guides/unicorn-gifts-for-teens.html", "/guides/unicorn-party-favor-ideas.html", "/guides/unicorn-bedroom-ideas.html", "/guides/small-unicorn-gifts-stocking-stuffers.html", "/tools/unicorn-gift-finder.html", "/tools/unicorn-party-planner.html", "/about.html", "/privacy.html"]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(
        f'  <url><loc>{xml_escape(BASE + path)}</loc></url>\n' for path in urls
    ) + '</urlset>\n'
    write("sitemap.xml", sitemap)
    write("robots.txt", "User-agent: *\nAllow: /\nSitemap: https://unicornsite.online/sitemap.xml\n")
    write("ads.txt", "google.com, pub-8108579336605864, DIRECT, f08c47fec0942fa0\n")
    write("unicorn-store (2).html", '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex,follow"><link rel="canonical" href="https://unicornsite.online/"><meta http-equiv="refresh" content="0; url=/"><title>Unicorn Finds has moved</title></head><body><p>The store is now at <a href="/">Unicorn Finds</a>.</p></body></html>\n''')


if __name__ == "__main__":
    main()
