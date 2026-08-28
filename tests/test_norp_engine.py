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
