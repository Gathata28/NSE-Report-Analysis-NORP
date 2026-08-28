"""Quality gate for the relational report and provenance index."""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
from pathlib import Path

ALLOWED_FREQUENCIES = {
    "Annual / full-year",
    "Semi-annual / half-year",
    "Quarterly",
    "Periodic results material",
}
REQUIRED_TABLES = {
    "report",
    "report_source",
    "report_validation",
    "report_file",
    "report_text",
    "report_fact",
    "report_qualitative",
}


def default_database() -> Path:
    root = Path(os.environ.get("NORP_ROOT", Path(__file__).resolve().parents[1]))
    candidate = root / "data" / "indexes" / "nse_reports_archive.sqlite"
    return candidate if candidate.exists() else root / "nse_reports_archive.sqlite"


def run_quality_checks(database: Path) -> tuple[dict[str, int], list[str]]:
    connection = sqlite3.connect(database)
    connection.execute("PRAGMA foreign_keys=ON")
    checks: dict[str, int] = {}
    errors: list[str] = []

    tables = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    missing_tables = REQUIRED_TABLES - tables
    if missing_tables:
        errors.append(f"missing required tables: {', '.join(sorted(missing_tables))}")
        connection.close()
        return checks, errors

    checks["reports"] = connection.execute("SELECT COUNT(*) FROM report").fetchone()[0]
    checks["sources"] = connection.execute("SELECT COUNT(*) FROM report_source").fetchone()[0]
    checks["validations"] = connection.execute("SELECT COUNT(*) FROM report_validation").fetchone()[0]
    checks["reports_without_source"] = connection.execute(
        """SELECT COUNT(*) FROM report r
           LEFT JOIN report_source s ON s.report_id = r.report_id
           WHERE s.report_id IS NULL"""
    ).fetchone()[0]
    checks["sources_without_url"] = connection.execute(
        """SELECT COUNT(*) FROM report_source
           WHERE COALESCE(TRIM(source_page_url), '') = ''
             AND COALESCE(TRIM(download_url), '') = ''"""
    ).fetchone()[0]
    checks["sources_without_tier"] = connection.execute(
        "SELECT COUNT(*) FROM report_source WHERE COALESCE(TRIM(source_tier), '') = ''"
    ).fetchone()[0]
    checks["reports_without_frequency"] = connection.execute(
        "SELECT COUNT(*) FROM report WHERE COALESCE(TRIM(report_frequency), '') = ''"
    ).fetchone()[0]
    checks["reports_without_title"] = connection.execute(
        "SELECT COUNT(*) FROM report WHERE COALESCE(TRIM(document_title), '') = ''"
    ).fetchone()[0]
    checks["duplicate_report_ids"] = connection.execute(
        "SELECT COUNT(*) FROM (SELECT report_id FROM report GROUP BY report_id HAVING COUNT(*) > 1)"
    ).fetchone()[0]
    checks["duplicate_download_urls"] = connection.execute(
        """SELECT COUNT(*) FROM (
             SELECT download_url FROM report_source
             WHERE COALESCE(TRIM(download_url), '') <> ''
             GROUP BY download_url HAVING COUNT(*) > 1
           )"""
    ).fetchone()[0]

    orphan_queries = {
        "orphan_sources": "SELECT COUNT(*) FROM report_source s LEFT JOIN report r ON r.report_id=s.report_id WHERE r.report_id IS NULL",
        "orphan_validations": "SELECT COUNT(*) FROM report_validation v LEFT JOIN report r ON r.report_id=v.report_id WHERE r.report_id IS NULL",
        "orphan_files": "SELECT COUNT(*) FROM report_file f LEFT JOIN report r ON r.report_id=f.report_id WHERE r.report_id IS NULL",
        "orphan_text": "SELECT COUNT(*) FROM report_text t LEFT JOIN report r ON r.report_id=t.report_id WHERE r.report_id IS NULL",
        "orphan_facts": "SELECT COUNT(*) FROM report_fact f LEFT JOIN report r ON r.report_id=f.report_id WHERE r.report_id IS NULL",
        "orphan_qualitative": "SELECT COUNT(*) FROM report_qualitative q LEFT JOIN report r ON r.report_id=q.report_id WHERE r.report_id IS NULL",
    }
    for name, query in orphan_queries.items():
        checks[name] = connection.execute(query).fetchone()[0]

    invalid_frequency = connection.execute(
        "SELECT DISTINCT report_frequency FROM report WHERE report_frequency IS NOT NULL"
    ).fetchall()
    invalid_values = sorted({row[0] for row in invalid_frequency if row[0] not in ALLOWED_FREQUENCIES})
    checks["invalid_frequency_values"] = len(invalid_values)
    if invalid_values:
        errors.append(f"invalid report_frequency values: {', '.join(invalid_values)}")

    foreign_key_violations = connection.execute("PRAGMA foreign_key_check").fetchall()
    checks["foreign_key_violations"] = len(foreign_key_violations)

    hard_failure_keys = {
        "reports_without_source",
        "sources_without_url",
        "sources_without_tier",
        "reports_without_frequency",
        "reports_without_title",
        "duplicate_report_ids",
        "invalid_frequency_values",
        "foreign_key_violations",
    }
    hard_failures = {
        key for key, value in checks.items()
        if (key.startswith("orphan_") or key in hard_failure_keys) and value > 0
    }
    errors.extend(f"{key}={checks[key]}" for key in sorted(hard_failures))
    connection.close()
    return checks, errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate relational report-index quality.")
    parser.add_argument("--database", type=Path, default=default_database())
    args = parser.parse_args()
    checks, errors = run_quality_checks(args.database)
    print(json.dumps(checks, indent=2, sort_keys=True))
    if errors:
        print("Report-index quality gate failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Report-index quality gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
