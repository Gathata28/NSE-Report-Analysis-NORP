"""Collect Kenya Power financial-report links using the shared NORP fetch layer."""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from norp_engine import fetch_with_retry, normalize_source_records, write_index

LOGGER = logging.getLogger("collect_kplc_live")
SOURCE_PAGE = "https://www.kplc.co.ke/investor-relations/"


def collect_links() -> list[dict[str, str]]:
    session = __import__("requests").Session()
    response = fetch_with_retry(
        SOURCE_PAGE,
        source_tier="Issuer website",
        session=session,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    records: list[dict[str, str]] = []
    seen: set[str] = set()
    for anchor in soup.find_all("a", href=True):
        url = urljoin(SOURCE_PAGE, anchor["href"])
        title = " ".join(anchor.get_text(" ", strip=True).split())
        context = anchor
        for _ in range(7):
            context = context.parent
            if context is None:
                break
            nearby_text = " ".join(context.get_text(" ", strip=True).split())
            if len(nearby_text) < 700 and any(
                term in nearby_text.lower()
                for term in ("annual report", "financial results", "financial statements", "financials", "trading results")
            ):
                title = nearby_text
                break
        evidence = f"{title} {url}".lower()
        if not url.lower().split("?", 1)[0].endswith(".pdf"):
            continue
        if not any(
            term in evidence
            for term in (
                "annual report",
                "integrated report",
                "financial results",
                "financial statements",
                "financials",
                "trading results",
                "quarterly",
                "half-year",
                "interim",
            )
        ):
            continue
        if url in seen:
            continue
        seen.add(url)
        records.append({"title": title or "Kenya Power financial report", "url": url})
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect Kenya Power report links live.")
    parser.add_argument("--output", type=Path, default=Path("data/migrated_indexes/kplc_live.csv"))
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level), format="%(levelname)s %(message)s")

    normalized = normalize_source_records(
        collect_links(),
        issuer="The Kenya Power and Lighting Company PLC",
        ticker="KPLC",
        source_page=SOURCE_PAGE,
        source_tier="Issuer website",
    )
    write_index(args.output, normalized)
    LOGGER.info("collected=%d wrote=%s", len(normalized), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
