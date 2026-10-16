#!/usr/bin/env python3
"""Validate alignment between HTML indexability, canonicals and sitemap.xml."""

from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
from xml.etree import ElementTree


ROOT = Path(".").resolve()


class HeadParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.canonical = ""
        self.robots = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        if tag.lower() == "link" and "canonical" in values.get("rel", "").lower().split():
            self.canonical = values.get("href", "").strip()
        if tag.lower() == "meta" and values.get("name", "").lower() == "robots":
            self.robots = values.get("content", "").lower()


def read_head(path: Path) -> HeadParser:
    parser = HeadParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def local_path(url: str, origin: str) -> Path | None:
    parsed = urlparse(url)
    if f"{parsed.scheme}://{parsed.netloc}".rstrip("/") != origin:
        return None
    relative = unquote(parsed.path).lstrip("/")
    if not relative or parsed.path.endswith("/"):
        relative = str(Path(relative) / "index.html")
    return ROOT / relative


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: check_search_indexing.py https://example.com")
    origin = sys.argv[1].rstrip("/")
    sitemap_path = ROOT / "sitemap.xml"
    document = ElementTree.parse(sitemap_path)
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locations = [(node.text or "").strip() for node in document.findall("sm:url/sm:loc", namespace)]
    errors: list[str] = []
    if len(locations) != len(set(locations)):
        errors.append("sitemap.xml contains duplicate <loc> URLs")
    sitemap_urls = set(locations)
    parsed_pages = {path: read_head(path) for path in sorted(ROOT.rglob("*.html"))}

    for url in locations:
        parsed_url = urlparse(url)
        if parsed_url.query or parsed_url.fragment:
            errors.append(f"Sitemap URL must not contain a query or fragment: {url}")
        path = local_path(url, origin)
        if path is None:
            errors.append(f"Sitemap URL uses the wrong origin: {url}")
            continue
        if not path.is_file():
            errors.append(f"Sitemap URL has no local HTML file: {url}")
            continue
        page = parsed_pages.get(path)
        if page is None:
            errors.append(f"Sitemap URL is not an HTML page: {url}")
            continue
        if "noindex" in page.robots:
            errors.append(f"Sitemap includes a noindex page: {url}")
        if page.canonical != url:
            errors.append(f"Sitemap/canonical mismatch: {url} != {page.canonical or '(missing)'}")

    checked = 0
    for path, page in parsed_pages.items():
        if "noindex" in page.robots:
            continue
        if not page.canonical:
            text = path.read_text(encoding="utf-8")
            if path.name.startswith("google") and "google-site-verification:" in text:
                continue
            errors.append(f"Indexable page has no canonical: {path.relative_to(ROOT)}")
            continue
        if local_path(page.canonical, origin) is None:
            errors.append(f"Indexable page canonical uses the wrong origin: {path.relative_to(ROOT)}")
            continue
        checked += 1
        if page.canonical not in sitemap_urls:
            errors.append(f"Indexable canonical is missing from sitemap.xml: {page.canonical}")

    if checked == 0:
        errors.append("No indexable canonical pages were checked")
    if errors:
        raise SystemExit("Search indexing validation failed:\n- " + "\n- ".join(errors))
    print(f"Search indexing validation passed: {checked} indexable pages and {len(locations)} sitemap URLs.")


if __name__ == "__main__":
    main()
