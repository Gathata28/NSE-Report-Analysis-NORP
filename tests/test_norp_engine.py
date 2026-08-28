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


def test_bundle_outputs_stages_release_assets_outside_tree(tmp_path):
    import json
    from bundle_outputs import build_bundle

    root = tmp_path / "NORP"
    (root / "data" / "indexes").mkdir(parents=True)
    (root / "data" / "migrated_indexes").mkdir(parents=True)
    (root / "data" / "indexes" / "nse_reports_archive.sqlite").write_bytes(b"sqlite-test")
    (root / "data" / "indexes" / "sample.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    output = tmp_path / "release"
    result = build_bundle(root, output, "2026.08.28")
    manifest = json.loads(Path(result["manifest"]).read_text(encoding="utf-8"))
    assert manifest["artifact_host"] == "GitHub Releases"
    assert all(item["sha256"] for item in manifest["artifacts"])
    assert all("releases/download/v2026.08.28/" in item["stable_url"] for item in manifest["artifacts"])
    assert all(item["license_metadata"] for item in manifest["artifacts"])


def test_bundle_outputs_rejects_working_tree_destination(tmp_path):
    import pytest
    from bundle_outputs import build_bundle

    root = tmp_path / "NORP"
    (root / "data" / "indexes").mkdir(parents=True)
    (root / "data" / "indexes" / "nse_reports_archive.sqlite").write_bytes(b"sqlite-test")
    with pytest.raises(ValueError, match="outside the project working tree"):
        build_bundle(root, root / "release", "2026.08.28")


def test_kplc_live_collector_filters_financial_pdfs_from_noise(monkeypatch):
    from types import SimpleNamespace
    import collect_kplc_live

    fixture = Path(__file__).parent / "fixtures" / "kplc_investor_relations.html"
    response = SimpleNamespace(text=fixture.read_text(encoding="utf-8"), raise_for_status=lambda: None)
    monkeypatch.setattr(collect_kplc_live, "fetch_with_retry", lambda *args, **kwargs: response)

    rows = collect_kplc_live.collect_links()
    urls = [row["url"] for row in rows]
    titles = [row["title"].lower() for row in rows]

    assert len(rows) == 11
    assert len(urls) == len(set(urls))
    assert any("annual report" in title or "financial results" in title for title in titles)
    assert not any("e-mobility" in title for title in titles)
    assert not any("conference" in title for title in titles)


def test_deduplicate_skips_nullable_urls_without_crashing():
    from norp_engine import deduplicate_records

    rows = deduplicate_records([
        {"issuer": "Carbacid Investments PLC", "url": None, "title": "missing"},
        {"issuer": "Carbacid Investments PLC", "url": "https://example.test/report.pdf", "title": "valid"},
    ])
    assert len(rows) == 1
    assert rows[0]["download_url"] == "https://example.test/report.pdf"


def test_download_filter_combines_ticker_sector_year_and_frequency():
    from download_reports import DEFAULT_DB, select_reports

    rows = select_reports(
        DEFAULT_DB,
        sectors=["BANKING"],
        tickers=["SCBK"],
        companies=[],
        year_from=2020,
        year_to=2025,
        frequencies=["Annual / full-year"],
        subtypes=[],
        limit=3,
    )
    assert rows
    assert len(rows) <= 3
    assert all(row["ticker"] == "SCBK" for row in rows)
    assert all(row["sector"] == "BANKING" for row in rows)
    assert all(2020 <= int(row["report_year"]) <= 2025 for row in rows)
    assert all(row["report_frequency"] == "Annual / full-year" for row in rows)


def test_sector_aliases_are_canonicalized():
    from download_reports import canonical_sector

    assert canonical_sector("MANUFACTURING & ALLIED") == "MANUFACTURING AND ALLIED"
    assert canonical_sector("  banking ") == "BANKING"


def test_landing_page_candidates_rank_matching_pdf_links():
    from download_reports import pdf_candidates

    html = """
    <a href='/other.pdf'>Other document</a>
    <a href='/SCBK-Annual-Report-2024.pdf'>SCBK Annual Report 2024</a>
    <a href='/notice.html'>Notice</a>
    """
    candidates = pdf_candidates(html, "https://example.test/reports/", "SCBK Annual Report 2024")
    assert candidates[0][1] == "https://example.test/SCBK-Annual-Report-2024.pdf"


def test_download_one_records_http_403_without_bypass(monkeypatch, tmp_path):
    from types import SimpleNamespace
    import download_reports

    blocked = SimpleNamespace(
        status_code=403,
        url="https://issuer.example/report.pdf",
        headers={"content-type": "text/html"},
        content=b"Access denied",
        text="Access denied",
    )
    monkeypatch.setattr(download_reports, "fetch_with_retry", lambda *args, **kwargs: blocked)
    result = download_reports.download_one(
        {"report_id": "NSE-TEST", "issuer": "Example PLC", "ticker": "EXM", "sector": "BANKING", "report_year": "2024", "report_frequency": "Annual / full-year", "title": "Example Annual Report", "download_url": "https://issuer.example/report.pdf", "source_tier": "Issuer website"},
        tmp_path,
        SimpleNamespace(),
    )
    assert result.status == "blocked_or_not_pdf"
    assert result.http_status == 403
    assert not list(tmp_path.rglob("*.pdf"))


def test_download_one_resolves_static_landing_page(monkeypatch, tmp_path):
    from types import SimpleNamespace
    import download_reports

    landing = SimpleNamespace(
        status_code=200,
        url="https://issuer.example/reports/2024",
        headers={"content-type": "text/html"},
        content=b"<html>",
        text='<a href="/files/example-annual-report-2024.pdf">Example Annual Report 2024</a>',
    )
    pdf = SimpleNamespace(
        status_code=200,
        url="https://issuer.example/files/example-annual-report-2024.pdf",
        headers={"content-type": "application/pdf"},
        content=b"%PDF-1.7 test",
        text="",
    )
    responses = iter([landing, pdf])
    monkeypatch.setattr(download_reports, "fetch_with_retry", lambda *args, **kwargs: next(responses))
    result = download_reports.download_one(
        {"report_id": "NSE-TEST2", "issuer": "Example PLC", "ticker": "EXM", "sector": "BANKING", "report_year": "2024", "report_frequency": "Annual / full-year", "title": "Example Annual Report", "download_url": "https://issuer.example/reports/2024", "source_tier": "Issuer website"},
        tmp_path,
        SimpleNamespace(),
    )
    assert result.status == "downloaded"
    assert result.resolved_url.endswith("example-annual-report-2024.pdf")
    assert result.sha256
    assert next(tmp_path.rglob("*.pdf")).read_bytes().startswith(b"%PDF-")


def test_download_one_rejects_invalid_url(tmp_path):
    from types import SimpleNamespace
    import download_reports

    result = download_reports.download_one(
        {"report_id": "NSE-TEST3", "issuer": "Example PLC", "ticker": "EXM", "sector": "", "report_year": "", "report_frequency": "", "title": "Example", "download_url": "javascript:void(0)", "source_tier": "Issuer website"},
        tmp_path,
        SimpleNamespace(),
    )
    assert result.status == "invalid_url"
    assert result.error == "URL is not absolute HTTP(S)"
