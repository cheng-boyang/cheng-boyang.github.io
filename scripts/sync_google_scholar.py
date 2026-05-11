#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from scholarly import scholarly, ProxyGenerator


DEFAULT_USER_ID = "QHEX6EcAAAAJ"


def setup_proxy() -> None:
    pg = ProxyGenerator()
    pg.FreeProxies()
    scholarly.use_proxy(pg)


def fetch_publications(user_id: str) -> tuple[str, str, List[dict]]:
    author = scholarly.search_author_id(user_id)
    author = scholarly.fill(author, sections=["publications"])

    profile_name = author.get("name", "")
    source_url = f"https://scholar.google.com/citations?user={user_id}&hl=en"

    publications = []
    for pub in author.get("publications", []):
        filled = scholarly.fill(pub)
        bib = filled.get("bib", {})
        publications.append({
            "title": bib.get("title", ""),
            "authors": bib.get("author", ""),
            "venue": bib.get("venue", "") or bib.get("journal", "") or bib.get("booktitle", "") or "",
            "year": int(bib["pub_year"]) if bib.get("pub_year") else None,
            "citations": filled.get("num_citations", 0) or 0,
            "scholar_url": filled.get("pub_url") or f"https://scholar.google.com/citations?view_op=view_citation&user={user_id}&citation_for_view={filled.get('author_pub_id', '')}",
        })
        time.sleep(1)

    publications.sort(
        key=lambda p: (p["year"] is None, -(p["year"] or 0), p["title"].lower())
    )
    return profile_name, source_url, publications


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


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync publications from Google Scholar.")
    parser.add_argument("--user-id", default=DEFAULT_USER_ID, help="Google Scholar user ID")
    parser.add_argument("--output", default="assets/data/publications.json")
    parser.add_argument("--js-output", default="assets/js/publications-data.js")
    args = parser.parse_args()

    output_path = Path(args.output)
    try:
        setup_proxy()
        profile_name, source_url, publications = fetch_publications(args.user_id)
        payload = {
            "profile_id": args.user_id,
            "profile_name": profile_name,
            "source_url": source_url,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "publications": publications,
        }
    except Exception as error:
        cached = load_cached_payload(output_path)
        if cached is None:
            raise
        payload = cached
        print(
            f"Warning: Google Scholar sync failed ({error!r}); "
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
