"""Reusable helpers for NORP report-ingestion workflows."""
from __future__ import annotations

import csv
import re
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Mapping

REPORT_FIELDS = [
    "record_id", "issuer", "ticker", "report_frequency", "document_subtype",
    "report_year_label", "webpage_title", "source_page_url", "download_url",
    "http_status", "content_type", "source_tier",
]


def parse_date(value: object) -> date | None:
    """Parse the date formats used by the attached NSE market datasets."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%Y/%m/%d", "%d %b %Y", "%d-%b-%Y", "%d-%b-%y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def parse_number(value: object) -> float | None:
    """Parse a numeric value without imputing placeholders or malformed text."""
    if value is None:
        return None
    text = str(value).strip().replace(",", "").replace("%", "")
    if text in {"", "-", "—", "NA", "N/A", "null", "None"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def market_anomaly_flags(*, trading_date: date | None, ticker: object, day_price: float | None, day_low: float | None, day_high: float | None) -> list[str]:
    """Return explicit anomaly flags without modifying or dropping the source row."""
    flags: list[str] = []
    if trading_date is None:
        flags.append("invalid_or_unparsed_date")
    if not str(ticker or "").strip():
        flags.append("missing_ticker")
    if day_price is None:
        flags.append("missing_day_price")
    if day_low is not None and day_high is not None and day_low > day_high:
        flags.append("day_low_above_day_high")
    return flags


def classify_frequency(title: str = "", url: str = "") -> str:
    """Classify a disclosure conservatively from title and URL evidence."""
    text = f"{title} {url}".lower()
    if re.search(r"\b(q[1-4]|quarter|quarterly|three months|9 months)\b", text):
        return "Quarterly"
    if re.search(r"\b(h[12]|half[- ]year|semi[- ]annual|interim|six months|six-month)\b", text):
        return "Semi-annual / half-year"
    if re.search(r"\b(annual|full[- ]year|integrated report|year ended|financial statements)\b", text):
        return "Annual / full-year"
    return "Periodic results material"


def infer_year(title: str = "", url: str = "") -> str:
    """Return the first four-digit year in disclosure evidence, if present."""
    match = re.search(r"(20\d{2})", f"{title} {url}")
    return match.group(1) if match else ""


def deduplicate_records(records: Iterable[Mapping[str, str]], issuer: str | None = None) -> list[dict[str, str]]:
    """Deduplicate records by issuer and download URL, preserving first-seen order."""
    result: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for record in records:
        row = dict(record)
        row_issuer = row.get("issuer", issuer or "")
        url = row.get("download_url", row.get("url", ""))
        key = (row_issuer.strip().lower(), url.strip())
        if not url.strip() or key in seen:
            continue
        seen.add(key)
        row["issuer"] = row_issuer
        row["download_url"] = url
        result.append(row)
    return result


def normalize_source_records(records: Iterable[Mapping[str, str]], *, issuer: str, ticker: str, source_page: str, source_tier: str = "Issuer website") -> list[dict[str, str]]:
    """Map source records into the canonical NORP flat-index schema."""
    normalized: list[dict[str, str]] = []
    for record in deduplicate_records(records, issuer=issuer):
        title = (record.get("title") or record.get("document_title") or "").strip()
        url = (record.get("download_url") or record.get("url") or "").strip()
        page = (record.get("source_page") or source_page).strip()
        normalized.append({
            "record_id": "",
            "issuer": issuer,
            "ticker": ticker,
            "report_frequency": classify_frequency(title, url),
            "document_subtype": "Annual report" if classify_frequency(title, url) == "Annual / full-year" else "Financial results / statements",
            "report_year_label": infer_year(title, url),
            "webpage_title": (record.get("webpage_title") or record.get("page_title") or title or "NORP source page").strip(),
            "source_page_url": page,
            "download_url": url,
            "http_status": record.get("http_status", "linked from source page"),
            "content_type": record.get("content_type", "application/pdf (inferred from URL)"),
            "source_tier": source_tier,
        })
    return normalized


def load_csv(path: Path) -> list[dict[str, str]]:
    """Load a UTF-8 CSV as dictionaries."""
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_index(path: Path, records: Iterable[Mapping[str, str]]) -> None:
    """Write canonical records with deterministic sequential record IDs."""
    rows = [dict(record) for record in records]
    for number, row in enumerate(rows, start=1):
        row["record_id"] = f"NSE-{number:05d}"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=REPORT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
