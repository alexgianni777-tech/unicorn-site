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
        ("Gift guides", "/#guides"),
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
          <a href="/#shop">All picks</a><a href="/guides/unicorn-gifts-for-adults.html">Gift ideas</a>
          <a href="/guides/unicorn-night-lights.html">Night lights</a><a href="/guides/unicorn-room-decor.html">Room decor</a>
          <a href="/tools/unicorn-party-planner.html">Free party planner</a></div>
        <div class="footer-links"><strong>Information</strong>
          <a href="/about.html">About and affiliate disclosure</a><a href="/privacy.html">Privacy</a></div>
      </div><div class="footer-bottom">As an Amazon Associate I earn from qualifying purchases. © 2026 Unicorn Finds. Independent site; not affiliated with Amazon, Hasbro or Netflix.</div>
    </div></footer>'''


def page(title: str, description: str, path: str, body: str, *, active: str = "", kind: str = "website") -> str:
    canonical = BASE + path
    json_ld = {
        "@context": "https://schema.org",
        "@type": "WebPage" if kind == "website" else "Article",
        "name": title,
        "description": description,
        "url": canonical,
        "isPartOf": {"@type": "WebSite", "name": "Unicorn Finds", "url": BASE + "/"},
    }
    structured = json.dumps(json_ld, ensure_ascii=False).replace("<", "\\u003c")
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
  <meta name="twitter:card" content="summary">
  <script type="application/ld+json">{structured}</script>
</head>
<body>
{header(active)}
{body}
{footer()}
</body>
</html>
'''


def product_card(product: dict) -> str:
    return f'''<article class="product" id="{esc(product['id'])}">
      <div class="product-picture">
        <img src="/{esc(product['image'])}" alt="{esc(product['alt'])}" loading="lazy" width="560" height="500">
        <span class="product-type">{esc(product['label'])}</span>
      </div>
      <div class="product-content"><h3>{esc(product['title'])}</h3>
        <p>{esc(product['description'])}</p>
        <a class="button product-cta" href="{esc(product['url'])}" rel="sponsored nofollow noopener noreferrer" target="_blank">{('Compare options on Amazon' if product['id'] == 'night-light-search' else 'Check current Amazon listing')} <span aria-hidden="true">↗</span></a>
        <span class="product-footnote">Paid link · Check the current listing</span>
      </div>
    </article>'''


def inline_pick(product_id: str, why: str) -> str:
    product = BY_ID[product_id]
    return f'''<aside class="inline-pick">
      <img src="/{esc(product['image'])}" alt="{esc(product['alt'])}" loading="lazy" width="90" height="90">
      <div><strong>{esc(product['title'])}</strong><p>{esc(why)}</p>
      <a href="{esc(product['url'])}" target="_blank" rel="sponsored nofollow noopener noreferrer">{('Browse on Amazon' if product_id == 'night-light-search' else 'See on Amazon')} ↗ (paid link)</a></div>
    </aside>'''


def category(category_id: str, heading: str, intro: str) -> str:
    cards = "".join(product_card(product) for product in PRODUCTS if product["section"] == category_id)
    return f'''<section class="category" id="{category_id}">
      <h2>{heading}</h2><p class="category-intro">{intro}</p>
      <div class="product-grid">{cards}</div>
    </section>'''


def quick_pick(product_id: str, badge: str, why: str) -> str:
    product = BY_ID[product_id]
    cta = "Compare options on Amazon" if product_id == "night-light-search" else "Check current Amazon listing"
    return f'''<article class="quick-pick">
      <div class="quick-pick-icon"><img src="/{esc(product['image'])}" alt="" loading="lazy" width="88" height="78"></div>
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
        <div><div class="eyebrow">Unicorn gifts made easier</div>
          <h1>Find a unicorn gift <em>without the guesswork.</em></h1>
          <p class="hero-lede">Start with four quick picks, compare what each is good for, or browse all ten unicorn-themed ideas for mugs, lights and room decor.</p>
          <div class="hero-actions"><a class="button" href="#quick-picks">See the quick picks ↓</a><a class="button button-light" href="#shop">Browse all ten</a></div>
          <p class="hero-note">Independent gift guide · Amazon affiliate links are clearly marked</p>
        </div>
        <div class="hero-collage" aria-label="Illustrations of unicorn-inspired gift ideas">
          <div class="hero-image"><img src="/assets/mugs.svg" alt="Illustrated unicorn mug" width="560" height="500" fetchpriority="high"></div>
          <div class="hero-image"><img src="/assets/lights.svg" alt="Illustrated unicorn night light" width="560" height="500"></div>
          <span class="hero-stamp" aria-hidden="true">Make room for wonder ✦</span>
        </div>
      </div></section>
      <div class="jump wrap" aria-label="Jump to a category"><span>Browse by mood</span>
        <a href="#drinkware">☕ Mugs &amp; drinkware</a><a href="#lights">✦ Night lights</a><a href="#decor">♡ Decor &amp; little gifts</a>
      </div>
      <section class="section wrap quick-section" id="quick-picks">
        <div class="section-heading"><span class="eyebrow">Short on time?</span><h2>Four easy places to start</h2>
          <p>Choose by the kind of gift you want to give. These are shortcuts into the collection, not rankings or hands-on reviews.</p></div>
        <div class="quick-grid">
          {quick_pick('mug-set','Coffee & tea gift','A small, playful gift for someone who already uses mugs. Check the current design and care instructions.')}
          {quick_pick('cloud-lamp','Bedside glow','A compact room accent when you want a decorative light rather than a large room effect.')}
          {quick_pick('projector','Bigger room effect','A starting point for someone who wants light across a wall or ceiling rather than one small lamp.')}
          {quick_pick('planters','Creative gift','A craft-style option for someone who enjoys painting or small desk and shelf projects.')}
        </div>
        <div class="compare-block">
          <div class="compare-heading"><h3>Compare the quick picks</h3><p>Use the last column to check the current Amazon listing before deciding.</p></div>
          <div class="table-scroll"><table class="pick-table">
            <thead><tr><th>Pick</th><th>Good when you want…</th><th>Check before buying</th><th>Current listing</th></tr></thead>
            <tbody>
              {comparison_row('mug-set','a small everyday gift','capacity and care instructions')}
              {comparison_row('cloud-lamp','a compact bedside accent','power method and dimensions')}
              {comparison_row('projector','a room-wide lighting effect','projection distance and controls')}
              {comparison_row('planters','a hands-on craft gift','set quantity and included supplies')}
            </tbody>
          </table></div>
        </div>
      </section>
      <section class="section section-tint" id="guides"><div class="wrap">
        <div class="section-heading"><span class="eyebrow">Start with an idea</span><h2>Find the right kind of magic</h2>
          <p>Three short guides for different decisions. Each explains what matters before you head to a retailer.</p></div>
        <div class="guide-grid">
          <a class="guide-tile" href="/guides/unicorn-gifts-for-adults.html"><span class="tile-icon" aria-hidden="true">🎁</span><h3>Unicorn gifts for adults</h3><p>How to pick a present that feels personal without guessing at size or style.</p><span class="tile-link">Read the gift guide →</span></a>
          <a class="guide-tile" href="/guides/unicorn-night-lights.html"><span class="tile-icon" aria-hidden="true">🌙</span><h3>Choosing a night light</h3><p>Compare a bedside glow, an accent lamp and a room projector.</p><span class="tile-link">Compare lighting →</span></a>
          <a class="guide-tile" href="/guides/unicorn-room-decor.html"><span class="tile-icon" aria-hidden="true">🏡</span><h3>Unicorn room decor</h3><p>Build a playful room with a few pieces that work together.</p><span class="tile-link">Explore room ideas →</span></a>
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
        "Unicorn Gifts: 10 Easy Gift Ideas, Lights & Decor | Unicorn Finds",
        "Find unicorn gift ideas faster with four quick picks, a simple comparison and ten curated mugs, lights and room decor ideas with clearly marked Amazon links.",
        "/", body,
    )


def guide_page(title: str, description: str, path: str, intro: str, article: str) -> str:
    body = f'''<main id="main"><div class="page-intro"><div class="wrap">
      <div class="breadcrumbs"><a href="/">Home</a> / Guides</div>
      <span class="eyebrow">Unicorn Finds guide</span><h1>{esc(title.split(' | ')[0])}</h1><p>{esc(intro)}</p>
    </div></div><article class="article wrap">
      {affiliate_note()}
      {article}
      <div class="callout"><p><strong>One last check:</strong> Retail listings can change. Confirm the exact item, size, seller, price, availability and return terms on Amazon before purchasing.</p></div>
      <p><a class="button button-light" href="/#shop">Browse all ten picks →</a></p>
    </article></main>'''
    return page(title, description, path, body, kind="article")


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
        "Unicorn Gifts for Adults: A Practical Gift Guide | Unicorn Finds",
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
    write("tools/unicorn-party-planner.html", party_planner())
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
      <div class="article wrap"><h2>On this site</h2><p>This is a static website. It does not have accounts or first-party analytics scripts, and the site code does not set its own cookies. The party planner processes numbers in your browser and does not send or save them. The hosting provider may process technical request data needed to serve pages; its own privacy terms apply.</p>
      <h2>When you follow a link</h2><p>Product links take you to Amazon. Amazon may process your visit and purchase according to its own privacy notice and affiliate program. We do not see your payment details or the contents of your order. The site also links to third-party information; their privacy notices apply when you visit them.</p>
      <h2>Changes</h2><p>If we add analytics, a newsletter or a contact form, this page will need to be updated before those features go live. Last revised: 29 September 2026.</p>
      <p><a href="/about.html">Read the affiliate disclosure</a> · <a href="/">Back to the home page</a></p></div></main>'''
    write("privacy.html", page(
        "Privacy | Unicorn Finds",
        "Read how this static gift guide works and what happens when you follow an Amazon affiliate link.",
        "/privacy.html", privacy_body,
    ))
    urls = ["/", "/guides/unicorn-gifts-for-adults.html", "/guides/unicorn-night-lights.html", "/guides/unicorn-room-decor.html", "/tools/unicorn-party-planner.html", "/about.html", "/privacy.html"]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(
        f'  <url><loc>{xml_escape(BASE + path)}</loc></url>\n' for path in urls
    ) + '</urlset>\n'
    write("sitemap.xml", sitemap)
    write("robots.txt", "User-agent: *\nAllow: /\nSitemap: https://unicornsite.online/sitemap.xml\n")
    write("unicorn-store (2).html", '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex,follow"><link rel="canonical" href="https://unicornsite.online/"><meta http-equiv="refresh" content="0; url=/"><title>Unicorn Finds has moved</title></head><body><p>The store is now at <a href="/">Unicorn Finds</a>.</p></body></html>\n''')


if __name__ == "__main__":
    main()
