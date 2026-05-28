#!/usr/bin/env python3
"""Fetch the latest arXiv papers for a given category.

Usage:
    python get_arxiv_id.py <category>

Example:
    python get_arxiv_id.py cs.SD

The script scrapes ``https://arxiv.org/list/<category>/new`` and prints a
JSON list of objects with the keys ``id``, ``title`` and ``abstract``.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import List, Dict

import requests
from bs4 import BeautifulSoup, Tag


ARXIV_LIST_URL = "https://arxiv.org/list/{category}/new"
USER_AGENT = (
    "Mozilla/5.0 (compatible; jinbridge-daily-arxiv/1.0; "
    "+https://arxiv.org)"
)


def _clean_text(text: str) -> str:
    """Collapse whitespace and trim a chunk of text."""
    return re.sub(r"\s+", " ", text).strip()


def _extract_arxiv_id(dt: Tag) -> str:
    """Extract the arXiv identifier (e.g. ``2605.27840``) from a ``<dt>``."""
    # Prefer the abstract anchor, which has both an ``id`` attribute and an
    # ``href`` like ``/abs/2605.27840``.
    link = dt.find("a", title="Abstract")
    if link is not None:
        href = link.get("href", "")
        match = re.search(r"/abs/([\w.\-/]+)", href)
        if match:
            return match.group(1)
        if link.get("id"):
            return str(link["id"])
        # Fall back to the visible "arXiv:..." text.
        return _clean_text(link.get_text()).replace("arXiv:", "").strip()

    # Generic fallback: any link to /abs/ in the dt.
    any_link = dt.find("a", href=re.compile(r"/abs/"))
    if any_link is not None:
        match = re.search(r"/abs/([\w.\-/]+)", any_link.get("href", ""))
        if match:
            return match.group(1)
    return ""


def _extract_title(dd: Tag) -> str:
    """Extract the title text from a ``<dd>`` block."""
    title_div = dd.find("div", class_="list-title")
    if title_div is None:
        return ""
    # Drop the "Title:" descriptor span if present.
    descriptor = title_div.find("span", class_="descriptor")
    if descriptor is not None:
        descriptor.extract()
    return _clean_text(title_div.get_text(" "))


def _extract_abstract(dd: Tag) -> str:
    """Extract the abstract paragraph from a ``<dd>`` block."""
    paragraph = dd.find("p", class_="mathjax")
    if paragraph is None:
        return ""
    return _clean_text(paragraph.get_text(" "))


def fetch_arxiv_papers(category: str, timeout: int = 30) -> List[Dict[str, str]]:
    """Return the list of new papers in ``category`` from arXiv."""
    url = ARXIV_LIST_URL.format(category=category)
    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT},
        timeout=timeout,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    papers: List[Dict[str, str]] = []
    seen_ids: set[str] = set()

    # The page can contain several ``<dl id="articles">`` blocks: one for
    # new submissions and additional ones for cross-listed / replacement
    # papers. We walk all of them.
    for dl in soup.find_all("dl", id="articles"):
        dts = dl.find_all("dt", recursive=False)
        dds = dl.find_all("dd", recursive=False)
        for dt, dd in zip(dts, dds):
            arxiv_id = _extract_arxiv_id(dt)
            if not arxiv_id or arxiv_id in seen_ids:
                continue
            seen_ids.add(arxiv_id)

            papers.append({
                "id": arxiv_id,
                "title": _extract_title(dd),
                "abstract": _extract_abstract(dd),
            })

    return papers


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fetch the latest arXiv papers for a category.",
    )
    parser.add_argument(
        "category",
        help="arXiv category, e.g. cs.SD, cs.CL, eess.AS",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="HTTP timeout in seconds (default: 30)",
    )
    args = parser.parse_args(argv)

    try:
        papers = fetch_arxiv_papers(args.category, timeout=args.timeout)
    except requests.RequestException as exc:
        print(f"Failed to fetch arXiv listing: {exc}", file=sys.stderr)
        return 1

    json.dump(papers, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
