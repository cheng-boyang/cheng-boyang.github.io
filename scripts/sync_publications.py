#!/usr/bin/env python3
"""Sync publications from Semantic Scholar API.

To find your Semantic Scholar author ID:
  1. Go to https://www.semanticscholar.org and search your name.
  2. Open your author profile page.
  3. Copy the numeric ID from the URL: /author/<NAME>/<ID>
"""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


S2_BASE_URL = "https://api.semanticscholar.org/graph/v1"
# Set your Semantic Scholar author ID here, or pass --author-id at runtime.
DEFAULT_AUTHOR_ID = ""
PAGE_LIMIT = 100
REQUEST_DELAY = 1.0  # seconds between paginated requests


def make_request(url: str, api_key: str | None = None) -> dict:
    headers = {"Accept": "application/json"}
    if api_key:
        headers["x-api-key"] = api_key
    request = Request(url, headers=headers)
    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        raise


def fetch_author(author_id: str, api_key: str | None = None) -> dict:
    url = f"{S2_BASE_URL}/author/{author_id}?fields=name,url"
    return make_request(url, api_key)


def fetch_papers(author_id: str, api_key: str | None = None) -> List[dict]:
    papers: List[dict] = []
    offset = 0

    while True:
        params = urlencode({
            "fields": "title,authors,year,citationCount,venue,url",
            "limit": PAGE_LIMIT,
            "offset": offset,
        })
        url = f"{S2_BASE_URL}/author/{author_id}/papers?{params}"
        data = make_request(url, api_key)

        batch = data.get("data", [])
        papers.extend(batch)

        if "next" not in data or len(batch) < PAGE_LIMIT:
            break

        offset += PAGE_LIMIT
        time.sleep(REQUEST_DELAY)

    return papers


def format_publication(paper: dict) -> dict:
    authors = ", ".join(a["name"] for a in paper.get("authors", []))
    return {
        "title": paper.get("title") or "",
        "authors": authors,
        "venue": paper.get("venue") or "",
        "year": paper.get("year"),
        "citations": paper.get("citationCount") or 0,
        "scholar_url": paper.get("url") or "",
    }


def load_cached_payload(output_path: Path) -> dict | None:
    if not output_path.exists():
        return None
    try:
        payload = json.loads(output_path.read_text())
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    if not isinstance(payload.get("publications"), list):
        return None
    return payload


def build_payload(author_id: str, api_key: str | None = None) -> dict:
    author = fetch_author(author_id, api_key)
    time.sleep(REQUEST_DELAY)

    raw_papers = fetch_papers(author_id, api_key)
    publications = [format_publication(p) for p in raw_papers]
    publications.sort(
        key=lambda p: (p["year"] is None, -(p["year"] or 0), p["title"].lower())
    )

    profile_url = author.get("url") or f"https://www.semanticscholar.org/author/{author_id}"
    return {
        "profile_id": author_id,
        "profile_name": author.get("name") or "",
        "source_url": profile_url,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "publications": publications,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync publications from Semantic Scholar.")
    parser.add_argument(
        "--author-id",
        default=os.environ.get("S2_AUTHOR_ID", DEFAULT_AUTHOR_ID),
        help="Semantic Scholar numeric author ID",
    )
    parser.add_argument("--output", default="assets/data/publications.json")
    parser.add_argument("--js-output", default="assets/js/publications-data.js")
    parser.add_argument(
        "--api-key",
        default=os.environ.get("S2_API_KEY"),
        help="Semantic Scholar API key (optional, increases rate limit)",
    )
    args = parser.parse_args()

    if not args.author_id:
        raise SystemExit(
            "Error: Semantic Scholar author ID is required.\n"
            "Set DEFAULT_AUTHOR_ID in the script, pass --author-id, or set S2_AUTHOR_ID env var.\n"
            "Find your ID at https://www.semanticscholar.org (numeric part of your profile URL)."
        )

    output_path = Path(args.output)
    try:
        payload = build_payload(args.author_id, args.api_key)
    except Exception as error:
        cached = load_cached_payload(output_path)
        if cached is None:
            raise
        payload = cached
        print(
            f"Warning: Semantic Scholar sync failed ({error!r}); "
            "using cached publication data instead."
        )

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
