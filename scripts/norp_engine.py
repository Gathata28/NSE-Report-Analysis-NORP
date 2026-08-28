"""Shared normalization, validation, retry, and indexing helpers for NORP.

The module is intentionally dependency-light and is used by the configuration-driven
importer and public report downloader. Network requests retain normal TLS verification,
and source-tier policies control retry and host-concurrency behavior.
"""

from __future__ import annotations

import csv
import re
import time
from dataclasses import dataclass
from threading import BoundedSemaphore, Lock
from urllib.parse import urlparse
from datetime import date, datetime
from pathlib import Path
from typing import Callable, Iterable, Mapping

import requests

REPORT_FIELDS = [
    "record_id", "issuer", "ticker", "report_frequency", "document_subtype",
    "report_year_label", "webpage_title", "source_page_url", "download_url",
    "http_status", "content_type", "source_tier",
]


def parse_date(value: object) -> date | None:
    """Parse the date formats used by attached NSE market datasets.

    Args:
        value: A date-like value or a missing/malformed placeholder.

    Returns:
        A ``datetime.date`` when one of the supported formats matches; otherwise
        ``None``. The function never guesses or imputes a date.
    """
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
    """Parse a numeric value without imputing placeholders or malformed text.

    Percentage signs and thousands separators are removed. Empty values and
    explicit missing-value markers remain ``None``.
    """
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
    """Return explicit anomaly flags without modifying or dropping the source row.

    The returned strings are stable machine-readable labels suitable for storing
    beside the original observation and reviewing later.
    """
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
    """Classify a disclosure conservatively from title and URL evidence.

    Quarterly and half-year evidence takes precedence over generic financial-
    statement wording. Unclear material is classified as periodic results
    rather than being promoted to an annual report.
    """
    text = f"{title} {url}".lower()
    if re.search(r"\b(q[1-4]|quarter|quarterly|three months|9 months)\b", text):
        return "Quarterly"
    if re.search(r"\b(h[12]|half[- ]year|semi[- ]annual|interim|six months|six-month)\b", text):
        return "Semi-annual / half-year"
    if re.search(r"\b(annual|full[- ]year|integrated[- ]report|year ended|financial[- ]statements)\b", text):
        return "Annual / full-year"
    return "Periodic results material"


def infer_year(title: str = "", url: str = "") -> str:
    """Return the first four-digit year in disclosure evidence, if present."""
    match = re.search(r"(20\d{2})", f"{title} {url}")
    return match.group(1) if match else ""


def deduplicate_records(records: Iterable[Mapping[str, str]], issuer: str | None = None) -> list[dict[str, str]]:
    """Deduplicate records by issuer and download URL, preserving first-seen order.

    ``download_url``, ``direct_url``, and ``url`` are accepted as input aliases;
    missing links are skipped rather than converted into fabricated records.
    """
    result: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for record in records:
        row = dict(record)
        row_issuer = str(row.get("issuer") or issuer or "")
        url = str(row.get("download_url") or row.get("direct_url") or row.get("url") or "")
        key = (row_issuer.strip().lower(), url.strip())
        if not url.strip() or key in seen:
            continue
        seen.add(key)
        row["issuer"] = row_issuer
        row["download_url"] = url
        result.append(row)
    return result


def normalize_source_records(records: Iterable[Mapping[str, str]], *, issuer: str, ticker: str, source_page: str, source_tier: str = "Issuer website") -> list[dict[str, str]]:
    """Map source records into the canonical NORP flat-index schema.

    The normalizer preserves source URLs and derives frequency and year labels
    only from visible title/URL evidence. It does not download or inspect PDFs.
    """
    normalized: list[dict[str, str]] = []
    for record in deduplicate_records(records, issuer=issuer):
        title = (record.get("title") or record.get("document_title") or "").strip()
        url = (record.get("download_url") or record.get("direct_url") or record.get("url") or "").strip()
        page = (record.get("source_page") or record.get("source_page_url") or source_page).strip()
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
    """Load a UTF-8 or UTF-8-with-BOM CSV as dictionaries."""
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_index(path: Path, records: Iterable[Mapping[str, str]]) -> None:
    """Write canonical records with deterministic sequential record IDs.

    The destination directory is created automatically and unknown input fields
    are ignored so source-specific columns do not leak into the canonical index.
    """
    rows = [dict(record) for record in records]
    for number, row in enumerate(rows, start=1):
        row["record_id"] = f"NSE-{number:05d}"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=REPORT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


@dataclass(frozen=True)
class RetryPolicy:
    """Retry settings for one source tier."""

    max_attempts: int
    backoff_factor: float
    timeout: float
    max_backoff: float = 30.0


RETRY_POLICIES: dict[str, RetryPolicy] = {
    "issuer": RetryPolicy(max_attempts=3, backoff_factor=0.5, timeout=30.0),
    "nse": RetryPolicy(max_attempts=4, backoff_factor=1.0, timeout=45.0),
    "secondary": RetryPolicy(max_attempts=2, backoff_factor=2.0, timeout=30.0),
}
RETRYABLE_STATUS_CODES = {408, 425, 429, 500, 502, 503, 504}


def retry_policy_for_tier(source_tier: str) -> RetryPolicy:
    """Return a conservative policy based on the source tier label.

    Exchange/CMA sources receive the most attempts but the lowest host cap;
    secondary aggregators receive fewer attempts because they are discovery leads.
    """
    label = (source_tier or "").lower()
    if "nse" in label or "exchange" in label or "cma" in label:
        return RETRY_POLICIES["nse"]
    if "secondary" in label or "aggregator" in label:
        return RETRY_POLICIES["secondary"]
    return RETRY_POLICIES["issuer"]


class HostConcurrencyLimiter:
    """Maintain independent concurrency caps for each destination host."""

    def __init__(self, *, default_cap: int = 2, cap_by_tier: Mapping[str, int] | None = None) -> None:
        if default_cap < 1:
            raise ValueError("default_cap must be at least 1")
        self.default_cap = default_cap
        self.cap_by_tier = dict(cap_by_tier or {"issuer": 2, "nse": 1, "secondary": 1})
        self._semaphores: dict[str, BoundedSemaphore] = {}
        self._lock = Lock()

    def _cap_for_tier(self, source_tier: str) -> int:
        policy_key = "issuer"
        label = (source_tier or "").lower()
        if "nse" in label or "exchange" in label or "cma" in label:
            policy_key = "nse"
        elif "secondary" in label or "aggregator" in label:
            policy_key = "secondary"
        return max(1, int(self.cap_by_tier.get(policy_key, self.default_cap)))

    def semaphore_for(self, url: str, source_tier: str) -> BoundedSemaphore:
        """Return the shared semaphore for the URL's hostname.

        Semaphores are keyed by hostname, so a slow or restrictive issuer does
        not consume the concurrency budget of an unrelated host.
        """
        host = (urlparse(url).hostname or "").lower()
        if not host:
            raise ValueError(f"URL has no hostname: {url!r}")
        with self._lock:
            if host not in self._semaphores:
                self._semaphores[host] = BoundedSemaphore(self._cap_for_tier(source_tier))
            return self._semaphores[host]


DEFAULT_HOST_LIMITER = HostConcurrencyLimiter()


def fetch_with_retry(
    url: str,
    *,
    source_tier: str = "Issuer website",
    session: requests.Session | None = None,
    limiter: HostConcurrencyLimiter | None = None,
    policy: RetryPolicy | None = None,
    sleep: Callable[[float], None] = time.sleep,
    headers: Mapping[str, str] | None = None,
) -> requests.Response:
    """Fetch a public URL with tiered retries and a per-host concurrency cap.

    The function preserves normal TLS certificate verification by relying on the
    requests default (`verify=True`). It retries transient network errors and
    selected HTTP statuses, but returns non-retryable responses unchanged so the
    caller can record the source-specific status and provenance.
    """
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"Only absolute HTTP(S) URLs are supported: {url!r}")
    selected_policy = policy or retry_policy_for_tier(source_tier)
    if selected_policy.max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")
    request_session = session or requests.Session()
    host_limiter = limiter or DEFAULT_HOST_LIMITER
    request_headers = {"User-Agent": "NORP-public-archive/1.0"}
    if headers:
        request_headers.update(headers)
    last_error: Exception | None = None

    for attempt in range(1, selected_policy.max_attempts + 1):
        try:
            semaphore = host_limiter.semaphore_for(url, source_tier)
            with semaphore:
                response = request_session.get(
                    url,
                    headers=request_headers,
                    timeout=selected_policy.timeout,
                )
            if response.status_code not in RETRYABLE_STATUS_CODES:
                return response
            last_error = requests.HTTPError(
                f"retryable HTTP status {response.status_code} for {url}",
                response=response,
            )
        except requests.RequestException as error:
            last_error = error

        if attempt < selected_policy.max_attempts:
            delay = min(selected_policy.max_backoff, selected_policy.backoff_factor * (2 ** (attempt - 1)))
            sleep(delay)

    if last_error is not None:
        raise last_error
    raise requests.RequestException(f"request failed without a response: {url}")
