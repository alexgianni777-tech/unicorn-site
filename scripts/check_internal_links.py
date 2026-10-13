#!/usr/bin/env python3
"""Fail when a local HTML link points to a missing file or fragment."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urljoin, urlparse


ROOT = Path(".").resolve()
IGNORED_SCHEMES = {"data", "javascript", "mailto", "tel"}


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []
        self.anchors: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag.lower() == "a" and values.get("href") is not None:
            self.links.append(values["href"] or "")
        for attribute in ("id", "name"):
            if values.get(attribute):
                self.anchors.add(values[attribute] or "")


def parse_html(path: Path) -> LinkParser:
    parser = LinkParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def target_for(source: Path, href: str) -> tuple[Path, str] | None:
    parsed = urlparse(href.strip())
    if parsed.scheme.lower() in IGNORED_SCHEMES or parsed.netloc:
        return None

    source_url = "https://site.invalid/" + source.relative_to(ROOT).as_posix()
    resolved = urlparse(urljoin(source_url, href))
    relative = unquote(resolved.path).lstrip("/")
    if not relative or resolved.path.endswith("/"):
        relative = str(PurePosixPath(relative) / "index.html")
    return (ROOT / relative).resolve(), unquote(resolved.fragment)


def main() -> None:
    pages = sorted(ROOT.rglob("*.html"))
    parsed_pages = {page: parse_html(page) for page in pages}
    errors: list[str] = []
    checked = 0

    for source, document in parsed_pages.items():
        for href in document.links:
            target_info = target_for(source, href)
            if target_info is None:
                continue
            checked += 1
            target, fragment = target_info
            label = source.relative_to(ROOT).as_posix()
            try:
                target.relative_to(ROOT)
            except ValueError:
                errors.append(f"{label}: {href!r} escapes the site root")
                continue
            if not target.is_file():
                errors.append(f"{label}: {href!r} points to missing {target.relative_to(ROOT)}")
                continue
            if fragment and target.suffix.lower() == ".html":
                target_document = parsed_pages.get(target)
                if target_document is None or fragment not in target_document.anchors:
                    errors.append(f"{label}: {href!r} points to a missing fragment")

    if checked == 0:
        errors.append("No internal links were found")
    if errors:
        raise SystemExit("Internal link validation failed:\n- " + "\n- ".join(errors))
    print(f"Internal link validation passed: {checked} link placements across {len(pages)} HTML pages.")


if __name__ == "__main__":
    main()
