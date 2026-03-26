#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import List
from urllib.parse import urljoin
from urllib.request import Request, urlopen


SCHOLAR_BASE_URL = "https://scholar.google.com"
DEFAULT_USER_ID = "QHEX6EcAAAAJ"
DEFAULT_PAGESIZE = 100
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36"
)

ROW_RE = re.compile(r'<tr class="gsc_a_tr">(.*?)</tr>', re.S)
TITLE_RE = re.compile(
    r'<a href="(?P<href>[^"]+)" class="gsc_a_at">(?P<title>.*?)</a>',
    re.S,
)
GRAY_RE = re.compile(r'<div class="gs_gray">(.*?)</div>', re.S)
CITATION_RE = re.compile(r'class="gsc_a_ac(?:\s+gs_ibl)?"[^>]*>(.*?)<', re.S)
YEAR_RE = re.compile(r'<td class="gsc_a_y">.*?>(\d{4})<', re.S)
PROFILE_TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)
DETAIL_FIELD_RE = re.compile(
    r'<div class="gsc_oci_field">(.*?)</div>\s*<div class="gsc_oci_value">(.*?)</div>',
    re.S,
)
YEAR_IN_TEXT_RE = re.compile(r"\b(19|20)\d{2}\b")


def fetch_html(url: str) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", "ignore")


def strip_tags(value: str) -> str:
    cleaned = re.sub(r"<[^>]+>", "", unescape(value)).replace("\xa0", " ").strip()
    return cleaned.replace("\u202a", "").replace("\u202c", "").strip()


def remove_ellipsis(value: str) -> str:
    if not value:
        return value
    return value.replace("...", "").replace("\u2026", "").strip(" ,")


def parse_detail_fields(html: str) -> dict:
    details = {}
    for raw_key, raw_value in DETAIL_FIELD_RE.findall(html):
        key = strip_tags(raw_key)
        value = remove_ellipsis(strip_tags(raw_value))
        if key and value:
            details[key] = value
    return details


def extract_year_from_text(value: str) -> int | None:
    if not value:
        return None
    match = YEAR_IN_TEXT_RE.search(value)
    if not match:
        return None
    return int(match.group(0))


def resolve_venue(details: dict, fallback: str) -> str:
    patent_office = details.get("Patent office", "").strip()
    patent_number = details.get("Patent number", "").strip()
    if patent_number:
        if patent_office:
            return remove_ellipsis(f"Patent {patent_number} ({patent_office})")
        return remove_ellipsis(f"Patent {patent_number}")

    for key in (
        "Journal",
        "Conference",
        "Book",
        "Source",
        "Publisher",
    ):
        value = details.get(key, "").strip()
        if value:
            return remove_ellipsis(value)
    if patent_office:
        return remove_ellipsis(f"Patent ({patent_office})")
    return remove_ellipsis(fallback)


def enrich_publication(publication: dict) -> dict:
    try:
        detail_html = fetch_html(publication["scholar_url"])
        details = parse_detail_fields(detail_html)
    except Exception:
        # Keep list-page data when detail page fetch fails.
        publication["authors"] = remove_ellipsis(publication.get("authors", ""))
        publication["venue"] = remove_ellipsis(publication.get("venue", ""))
        return publication

    authors = details.get("Authors", publication.get("authors", ""))
    venue = resolve_venue(details, publication.get("venue", ""))
    detail_year = extract_year_from_text(details.get("Publication date", ""))

    publication["authors"] = remove_ellipsis(authors)
    publication["venue"] = remove_ellipsis(venue)
    if detail_year is not None:
        publication["year"] = detail_year
    return publication


def parse_publications(html: str) -> List[dict]:
    publications: List[dict] = []

    for row in ROW_RE.findall(html):
        title_match = TITLE_RE.search(row)
        if not title_match:
            continue

        gray_parts = [strip_tags(part) for part in GRAY_RE.findall(row)]
        citation_match = CITATION_RE.search(row)
        year_match = YEAR_RE.search(row)

        citations_text = strip_tags(citation_match.group(1)) if citation_match else "0"
        citations = int(citations_text) if citations_text.isdigit() else 0
        year = int(year_match.group(1)) if year_match else None

        publications.append(
            {
                "title": strip_tags(title_match.group("title")),
                "authors": remove_ellipsis(gray_parts[0]) if len(gray_parts) > 0 else "",
                "venue": remove_ellipsis(gray_parts[1]) if len(gray_parts) > 1 else "",
                "year": year,
                "citations": citations,
                "scholar_url": urljoin(SCHOLAR_BASE_URL, unescape(title_match.group("href"))),
            }
        )

    return [enrich_publication(publication) for publication in publications]


def fetch_all_publications(user_id: str, pagesize: int) -> List[dict]:
    publications: List[dict] = []
    offset = 0

    while True:
        url = (
            f"{SCHOLAR_BASE_URL}/citations?user={user_id}&hl=en"
            f"&cstart={offset}&pagesize={pagesize}&sortby=pubdate"
        )
        html = fetch_html(url)
        page_items = parse_publications(html)
        if not page_items:
            break

        publications.extend(page_items)

        if len(page_items) < pagesize:
            break

        offset += pagesize

    publications.sort(
        key=lambda item: (
            item["year"] is None,
            -(item["year"] or 0),
            item["title"].lower(),
        )
    )
    return publications


def extract_profile_name(html: str) -> str:
    title_match = PROFILE_TITLE_RE.search(html)
    if not title_match:
        return "Google Scholar Profile"
    title = strip_tags(title_match.group(1))
    return title.replace(" - Google Scholar", "").strip()


def build_payload(user_id: str, pagesize: int) -> dict:
    profile_url = f"{SCHOLAR_BASE_URL}/citations?user={user_id}&hl=en"
    first_page_html = fetch_html(
        f"{profile_url}&cstart=0&pagesize={pagesize}&sortby=pubdate"
    )
    publications = parse_publications(first_page_html)

    if len(publications) == pagesize:
        publications = fetch_all_publications(user_id, pagesize)

    return {
        "profile_id": user_id,
        "profile_name": extract_profile_name(first_page_html),
        "source_url": profile_url,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "publications": publications,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync publications from Google Scholar.")
    parser.add_argument("--user-id", default=DEFAULT_USER_ID, help="Google Scholar user ID")
    parser.add_argument(
        "--output",
        default="assets/data/publications.json",
        help="Output JSON path",
    )
    parser.add_argument(
        "--js-output",
        default="assets/js/publications-data.js",
        help="Output JS path",
    )
    parser.add_argument("--pagesize", type=int, default=DEFAULT_PAGESIZE)
    args = parser.parse_args()

    payload = build_payload(args.user_id, args.pagesize)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n")

    js_output_path = Path(args.js_output)
    js_output_path.parent.mkdir(parents=True, exist_ok=True)
    js_output_path.write_text(
        "window.PUBLICATIONS_DATA = "
        + json.dumps(payload, indent=2, ensure_ascii=True)
        + ";\n"
    )


if __name__ == "__main__":
    main()
