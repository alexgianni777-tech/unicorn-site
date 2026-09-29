# Unicorn Finds

Static, English-language Amazon affiliate gift guide for `unicornsite.online`.

The free unicorn party planner at `/tools/unicorn-party-planner.html` estimates
supplies and a visitor-entered budget locally in the browser. It does not send
or save form values. The numbers are a starting point, not retailer prices.

## Build

Run `python build.py` from any directory. The script reads `products.json` and
generates the HTML pages, sitemap and robots file. Commit generated files along
with the source when you change content. GitHub Pages serves the static files;
`CNAME` remains in the repository root.

## Editing products

1. Confirm that the Amazon destination matches the title, image and country.
   The night-light search link is deliberately labelled as a search link.
2. Update `products.json` and the related buying guidance. Never paste Amazon
   customer reviews, star ratings, a static price or a shipping promise into a
   page. Product images must be used only when you have the appropriate rights.
3. Run `python build.py`; check every outbound link and the generated pages.
4. Keep the exact Amazon Associate disclosure and `rel="sponsored"` on paid
   links. Add any new domain to the Associates account before using it.

The old home page mixed product images with links that did not always match.
This refresh uses original category illustrations rather than presenting
unverified photos as exact items. Two mismatched titles were corrected after
checking the Amazon redirects. Recheck the destinations and exact listings
periodically. No new product or entertainment affiliate links were invented.

## Organic traffic

See [TRAFFIC.md](TRAFFIC.md) for a practical launch checklist, content ideas and
measurement. The sitemap helps discovery but cannot guarantee indexing or
search rankings. The site currently installs no first-party analytics or display
ads. Any ad integration needs a reviewed ad account and an updated privacy notice.
