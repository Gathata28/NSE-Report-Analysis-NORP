"""Download filtered public NSE report PDFs from the NORP SQLite archive.

This tool downloads only public URLs already present in the archive. It does not
bypass authentication, CAPTCHA, robots controls, or HTTP 403 responses. Landing
pages are resolved conservatively by looking for PDF links in returned HTML.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import re
import sqlite3
import sys
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
import requests

from norp_engine import fetch_with_retry

LOGGER = logging.getLogger("norp_download")
DEFAULT_DB = Path(__file__).resolve().parents[1] / "data/indexes/nse_reports_archive.sqlite"
SECTOR_ALIASES = {
    "AUTOMOBILES & ACCESSORIES": "AUTOMOBILES AND ACCESSORIES",
    "COMMERCIAL & SERVICES": "COMMERCIAL AND SERVICES",
    "CONSTRUCTION & ALLIED": "CONSTRUCTION AND ALLIED",
    "ENERGY & PETROLEUM": "ENERGY AND PETROLEUM",
    "MANUFACTURING & ALLIED": "MANUFACTURING AND ALLIED",
}


@dataclass
class DownloadResult:
    report_id: str
    issuer: str
    ticker: str
    sector: str
    report_year: str
    report_frequency: str
    title: str
    source_url: str
    resolved_url: str
    status: str
    http_status: int | None
    local_path: str
    byte_size: int | None
    sha256: str | None
    error: str | None
    retrieved_at: str


def canonical_sector(value: str | None) -> str:
    normalized = re.sub(r"\s+", " ", (value or "").strip().upper())
    normalized = SECTOR_ALIASES.get(normalized, normalized)
    return normalized


def safe_name(value: str, fallback: str = "unknown") -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip()).strip("._")
    return value[:120] or fallback


def parse_year(value: str | None) -> int | None:
    match = re.search(r"20\d{2}", value or "")
    return int(match.group()) if match else None


def select_reports(
    db_path: Path,
    *,
    sectors: list[str],
    tickers: list[str],
    companies: list[str],
    year_from: int | None,
    year_to: int | None,
    frequencies: list[str],
    subtypes: list[str],
    limit: int | None,
) -> list[dict[str, str]]:
    """Select one preferred source per report using issuer_id, never ticker joins."""
    conditions: list[str] = []
    params: list[str | int] = []
    if tickers:
        conditions.append("upper(coalesce(r.ticker, i.canonical_ticker, '')) IN (%s)" % ",".join("?" * len(tickers)))
        params.extend(t.upper() for t in tickers)
    if companies:
        conditions.append("lower(i.canonical_name) IN (%s)" % ",".join("?" * len(companies)))
        params.extend(c.lower() for c in companies)
    if frequencies:
        conditions.append("r.report_frequency IN (%s)" % ",".join("?" * len(frequencies)))
        params.extend(frequencies)
    if subtypes:
        conditions.append("r.document_subtype IN (%s)" % ",".join("?" * len(subtypes)))
        params.extend(subtypes)
    # Prefer an explicitly preferred source and fall back to the first source.
    query = """
        SELECT r.report_id, i.canonical_name AS issuer, coalesce(r.ticker, i.canonical_ticker, '') AS ticker,
               coalesce(nullif(i.sector, ''), (SELECT i2.sector FROM issuer AS i2 WHERE lower(i2.canonical_ticker) = lower(coalesce(r.ticker, i.canonical_ticker, '')) AND i2.sector IS NOT NULL AND trim(i2.sector) <> '' ORDER BY i2.issuer_id ASC LIMIT 1), '') AS sector,
               coalesce(r.report_year_label, '') AS report_year,
               coalesce(r.report_frequency, '') AS report_frequency, coalesce(r.document_subtype, '') AS document_subtype,
               coalesce(r.document_title, r.webpage_title, '') AS title,
               s.source_page_url, s.download_url, s.source_tier, s.content_type, s.http_status,
               s.is_preferred
        FROM report AS r
        JOIN issuer AS i ON i.issuer_id = r.issuer_id
        JOIN report_source AS s ON s.source_id = (
            SELECT s2.source_id FROM report_source AS s2
            WHERE s2.report_id = r.report_id
            ORDER BY s2.is_preferred DESC, s2.source_id ASC LIMIT 1
        )
    """
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY canonical_name COLLATE NOCASE, report_year, r.report_id"
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        rows = [dict(row) for row in connection.execute(query, params)]
    requested_sectors = {canonical_sector(s) for s in sectors}
    filtered: list[dict[str, str]] = []
    for row in rows:
        row["sector"] = canonical_sector(row.get("sector"))
        year = parse_year(row.get("report_year"))
        if requested_sectors and row["sector"] not in requested_sectors:
            continue
        if year_from is not None and (year is None or year < year_from):
            continue
        if year_to is not None and (year is None or year > year_to):
            continue
        filtered.append(row)
    return filtered[:limit] if limit is not None else filtered


def pdf_candidates(html: str, landing_url: str, expected: str) -> list[tuple[int, str]]:
    soup = BeautifulSoup(html, "html.parser")
    expected_tokens = {t for t in re.findall(r"[a-z0-9]+", expected.lower()) if len(t) > 2}
    candidates: list[tuple[int, str]] = []
    for anchor in soup.find_all("a", href=True):
        url = urljoin(landing_url, anchor["href"])
        if url.lower().startswith(("javascript:", "mailto:", "#")):
            continue
        text = " ".join(anchor.get_text(" ", strip=True).split())
        evidence = f"{text} {url}".lower()
        if ".pdf" not in evidence:
            continue
        score = sum(2 for token in expected_tokens if token in evidence)
        if ".pdf" in url.lower():
            score += 3
        candidates.append((score, url))
    return sorted(set(candidates), reverse=True)


def is_pdf(response: requests.Response) -> bool:
    content_type = (response.headers.get("content-type") or "").lower()
    return response.content[:5] == b"%PDF-" or "application/pdf" in content_type


def download_one(row: dict[str, str], output_dir: Path, session: requests.Session, *, force: bool = False) -> DownloadResult:
    report_id = row["report_id"]
    title = row.get("title") or report_id
    sector_dir = output_dir / safe_name(row.get("sector") or "UNCLASSIFIED")
    company_dir = sector_dir / safe_name(row.get("issuer") or row.get("ticker") or report_id)
    year = row.get("report_year") or "undated"
    filename = safe_name(f"{row.get('ticker') or 'NSE'}_{year}_{row.get('report_frequency') or 'report'}_{report_id}") + ".pdf"
    destination = company_dir / filename
    now = datetime.now(timezone.utc).isoformat()
    if destination.exists() and not force and destination.stat().st_size > 0:
        digest = hashlib.sha256(destination.read_bytes()).hexdigest()
        return DownloadResult(report_id, row["issuer"], row.get("ticker", ""), row.get("sector", ""), year, row.get("report_frequency", ""), title, row.get("download_url", ""), row.get("download_url", ""), "skipped_existing", None, str(destination), destination.stat().st_size, digest, None, now)

    source_url = row.get("download_url") or ""
    if not source_url.startswith(("http://", "https://")):
        return DownloadResult(report_id, row["issuer"], row.get("ticker", ""), row.get("sector", ""), year, row.get("report_frequency", ""), title, source_url, source_url, "invalid_url", None, "", None, None, "URL is not absolute HTTP(S)", now)
    try:
        response = fetch_with_retry(source_url, source_tier=row.get("source_tier", "Issuer website"), session=session)
        resolved_url = response.url or source_url
        if not is_pdf(response):
            content_type = (response.headers.get("content-type") or "").lower()
            if response.status_code != 200 or "html" not in content_type:
                return DownloadResult(report_id, row["issuer"], row.get("ticker", ""), row.get("sector", ""), year, row.get("report_frequency", ""), title, source_url, resolved_url, "blocked_or_not_pdf", response.status_code, "", None, None, f"HTTP {response.status_code}; content-type={content_type}", now)
            candidates = pdf_candidates(response.text, resolved_url, f"{title} {year} {row.get('ticker', '')}")
            if not candidates:
                return DownloadResult(report_id, row["issuer"], row.get("ticker", ""), row.get("sector", ""), year, row.get("report_frequency", ""), title, source_url, resolved_url, "landing_page_unresolved", response.status_code, "", None, None, "No matching public PDF link found in landing page", now)
            resolved_url = candidates[0][1]
            response = fetch_with_retry(resolved_url, source_tier=row.get("source_tier", "Issuer website"), session=session)
        if response.status_code != 200 or not is_pdf(response):
            return DownloadResult(report_id, row["issuer"], row.get("ticker", ""), row.get("sector", ""), year, row.get("report_frequency", ""), title, source_url, resolved_url, "not_pdf", response.status_code, "", None, None, "Resolved URL did not return a valid PDF", now)
        company_dir.mkdir(parents=True, exist_ok=True)
        payload = response.content
        digest = hashlib.sha256(payload).hexdigest()
        destination.write_bytes(payload)
        return DownloadResult(report_id, row["issuer"], row.get("ticker", ""), row.get("sector", ""), year, row.get("report_frequency", ""), title, source_url, resolved_url, "downloaded", response.status_code, str(destination), len(payload), digest, None, now)
    except requests.RequestException as exc:
        status = getattr(getattr(exc, "response", None), "status_code", None)
        return DownloadResult(report_id, row["issuer"], row.get("ticker", ""), row.get("sector", ""), year, row.get("report_frequency", ""), title, source_url, source_url, "request_failed", status, "", None, None, str(exc), now)


def write_manifest(path: Path, results: Iterable[DownloadResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for result in results:
            handle.write(json.dumps(asdict(result), ensure_ascii=False) + "\n")


def write_csv(path: Path, results: list[DownloadResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(results[0]).keys()) if results else list(DownloadResult.__annotations__.keys()))
        writer.writeheader()
        writer.writerows(asdict(r) for r in results)


def make_zip(output_dir: Path, zip_path: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(output_dir.rglob("*.pdf")):
            archive.write(file, file.relative_to(output_dir))


def main() -> int:
    parser = argparse.ArgumentParser(description="Download filtered public NSE report PDFs from the NORP archive.")
    parser.add_argument("--database", type=Path, default=DEFAULT_DB)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--csv-manifest", type=Path)
    parser.add_argument("--zip", dest="zip_path", type=Path)
    parser.add_argument("--sector", action="append", default=[])
    parser.add_argument("--ticker", action="append", default=[])
    parser.add_argument("--company", action="append", default=[])
    parser.add_argument("--year-from", type=int)
    parser.add_argument("--year-to", type=int)
    parser.add_argument("--frequency", action="append", default=[])
    parser.add_argument("--subtype", action="append", default=[])
    parser.add_argument("--limit", type=int)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level), format="%(levelname)s %(message)s")
    if args.year_from is not None and args.year_to is not None and args.year_from > args.year_to:
        parser.error("--year-from cannot be greater than --year-to")
    rows = select_reports(args.database, sectors=args.sector, tickers=args.ticker, companies=args.company, year_from=args.year_from, year_to=args.year_to, frequencies=args.frequency, subtypes=args.subtype, limit=args.limit)
    LOGGER.info("selected=%d", len(rows))
    if args.dry_run:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return 0
    args.output_dir.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    results = [download_one(row, args.output_dir, session, force=args.force) for row in rows]
    manifest = args.manifest or args.output_dir / "download_manifest.jsonl"
    write_manifest(manifest, results)
    if args.csv_manifest:
        write_csv(args.csv_manifest, results)
    if args.zip_path:
        make_zip(args.output_dir, args.zip_path)
    counts: dict[str, int] = {}
    for result in results:
        counts[result.status] = counts.get(result.status, 0) + 1
    print(json.dumps({"selected": len(rows), "results": counts, "manifest": str(manifest), "output_dir": str(args.output_dir), "zip": str(args.zip_path) if args.zip_path else None}, indent=2))
    return 0 if not any(k in counts for k in ("request_failed", "invalid_url")) else 1


if __name__ == "__main__":
    raise SystemExit(main())
