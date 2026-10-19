"""Fail a site build when a direct Amazon affiliate link loses attribution."""

from __future__ import annotations

from html import unescape
from pathlib import Path
import re
from urllib.parse import parse_qs, urlsplit


ANCHOR_RE = re.compile(r"<a\b[^>]*\bhref\s*=\s*([\"'])(.*?)\1[^>]*>", re.IGNORECASE | re.DOTALL)
REL_RE = re.compile(r"\brel\s*=\s*([\"'])(.*?)\1", re.IGNORECASE | re.DOTALL)
TARGET_BLANK_RE = re.compile(r"\btarget\s*=\s*([\"'])_blank\1", re.IGNORECASE)
AFFILIATE_TAG = "unicornfin0a9-20"


def main(root: Path = Path(".")) -> None:
    checked = 0
    errors: list[str] = []
    for path in sorted(root.rglob("*.html")):
        source = path.read_text(encoding="utf-8")
        for match in ANCHOR_RE.finditer(source):
            anchor = match.group(0)
            url = unescape(match.group(2))
            host = (urlsplit(url).hostname or "").lower()
            if not (host == "amazon.com" or host.startswith("amazon.") or ".amazon." in host):
                continue
            checked += 1
            tags = parse_qs(urlsplit(url).query).get("tag", [])
            if tags != [AFFILIATE_TAG]:
                errors.append(f"{path}: missing or incorrect Amazon tag: {url}")
            rel_match = REL_RE.search(anchor)
            rel = set(rel_match.group(2).lower().split()) if rel_match else set()
            if "sponsored" not in rel:
                errors.append(f"{path}: Amazon link missing rel=sponsored: {url}")
            if TARGET_BLANK_RE.search(anchor) and "noopener" not in rel:
                errors.append(f"{path}: target=_blank Amazon link missing rel=noopener: {url}")

    if checked == 0:
        errors.append("No direct Amazon affiliate links were found in HTML output")
    if errors:
        raise SystemExit("Affiliate link validation failed:\n" + "\n".join(errors))
    print(f"Validated {checked} direct Amazon affiliate links across HTML output.")


if __name__ == "__main__":
    main()
