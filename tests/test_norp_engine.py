from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from norp_engine import classify_frequency, deduplicate_records, parse_date, parse_number, infer_year, market_anomaly_flags


def test_parse_attached_dataset_dates():
    assert parse_date("1/2/2007").isoformat() == "2007-02-01"
    assert parse_date("2-Jan-13").isoformat() == "2013-01-02"
    assert parse_date("2-Jan-25").isoformat() == "2025-01-02"
    assert parse_date("-") is None


def test_parse_numbers_preserves_placeholders_as_missing():
    assert parse_number("7,800") == 7800.0
    assert parse_number("1.95%") == 1.95
    assert parse_number("-") is None
    assert parse_number("not-a-number") is None


def test_frequency_classification_is_conservative():
    assert classify_frequency("2025 Annual Report", "") == "Annual / full-year"
    assert classify_frequency("Unaudited Half-Year Results 2025", "") == "Semi-annual / half-year"
    assert classify_frequency("Q3 Results 2025", "") == "Quarterly"
    assert classify_frequency("Investor Update", "") == "Periodic results material"
    assert infer_year("Q3 Results 2025", "") == "2025"


def test_deduplicate_keeps_first_source_record():
    records = [
        {"issuer": "Example PLC", "download_url": "https://example.test/a.pdf", "title": "A"},
        {"issuer": "Example PLC", "download_url": "https://example.test/a.pdf", "title": "Duplicate"},
        {"issuer": "Example PLC", "download_url": "https://example.test/b.pdf", "title": "B"},
        {"issuer": "Example PLC", "download_url": "", "title": "No link"},
    ]
    result = deduplicate_records(records)
    assert [row["title"] for row in result] == ["A", "B"]


def test_market_anomaly_rules_are_explicit():
    flags = market_anomaly_flags(trading_date=None, ticker="", day_price=None, day_low=None, day_high=None)
    assert flags == ["invalid_or_unparsed_date", "missing_ticker", "missing_day_price"]
    assert market_anomaly_flags(trading_date=parse_date("2-Jan-25"), ticker="ABC", day_price=10.0, day_low=12.0, day_high=10.0) == ["day_low_above_day_high"]


def test_normalization_accepts_direct_url_and_source_page_url_aliases():
    from norp_engine import normalize_source_records

    rows = normalize_source_records(
        [{
            "title": "NCBA Group PLC Q3 Results 2025",
            "direct_url": "https://example.test/ncba-q3-2025.pdf",
            "source_page_url": "https://example.test/quarterly-earnings/",
        }],
        issuer="NCBA Group PLC",
        ticker="NCBA",
        source_page="https://example.test/fallback",
    )
    assert len(rows) == 1
    assert rows[0]["download_url"] == "https://example.test/ncba-q3-2025.pdf"
    assert rows[0]["source_page_url"] == "https://example.test/quarterly-earnings/"
    assert rows[0]["report_frequency"] == "Quarterly"


def test_hyphenated_integrated_report_is_annual():
    assert classify_frequency("Integrated-Report-Financial-Statements-2024", "") == "Annual / full-year"


def test_retry_policy_is_tier_specific():
    from norp_engine import retry_policy_for_tier

    assert retry_policy_for_tier("Issuer website").max_attempts == 3
    assert retry_policy_for_tier("NSE/exchange fallback").max_attempts == 4
    assert retry_policy_for_tier("Secondary aggregator").max_attempts == 2


def test_fetch_with_retry_retries_transient_status_and_preserves_tls_default():
    import requests
    from norp_engine import RetryPolicy, fetch_with_retry

    class FakeSession:
        def __init__(self):
            self.calls = []
            self.responses = [requests.Response(), requests.Response()]
            self.responses[0].status_code = 503
            self.responses[1].status_code = 200

        def get(self, url, **kwargs):
            self.calls.append((url, kwargs))
            return self.responses.pop(0)

    session = FakeSession()
    delays = []
    response = fetch_with_retry(
        "https://issuer.example/report.pdf",
        session=session,
        sleep=delays.append,
        policy=RetryPolicy(max_attempts=3, backoff_factor=0.25, timeout=5.0),
    )
    assert response.status_code == 200
    assert len(session.calls) == 2
    assert delays == [0.25]
    assert "verify" not in session.calls[0][1]
    assert session.calls[0][1]["timeout"] == 5.0


def test_fetch_with_retry_returns_non_retryable_response_without_sleep():
    import requests
    from norp_engine import RetryPolicy, fetch_with_retry

    class FakeSession:
        def get(self, url, **kwargs):
            response = requests.Response()
            response.status_code = 404
            return response

    delays = []
    response = fetch_with_retry(
        "https://issuer.example/missing.pdf",
        session=FakeSession(),
        sleep=delays.append,
        policy=RetryPolicy(max_attempts=4, backoff_factor=1.0, timeout=5.0),
    )
    assert response.status_code == 404
    assert delays == []


def test_host_limiter_keeps_hosts_independent():
    from norp_engine import HostConcurrencyLimiter

    limiter = HostConcurrencyLimiter(default_cap=2)
    first = limiter.semaphore_for("https://one.example/a.pdf", "Issuer website")
    same_host = limiter.semaphore_for("https://one.example/b.pdf", "Issuer website")
    second = limiter.semaphore_for("https://two.example/a.pdf", "Issuer website")
    assert first is same_host
    assert first is not second
