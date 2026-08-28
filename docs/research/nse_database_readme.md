# NSE Reports Relational Database

## Files

`nse_reports_archive.sqlite` is the primary SQLite database. `nse_archive_schema.sql` is the DDL, and `build_nse_relational_db.py` is the reproducible importer. `test_nse_relational_db.py` verifies foreign keys, orphan records, duplicate report IDs, and view cardinality. `nse_database_quality_report.md` documents the current extraction and validation boundary.

## Main tables

The `issuer`, `issuer_alias`, and `listing_event` tables preserve identity and status evidence. The `report` and `report_source` tables preserve the 1,761-row report catalog and source hierarchy. `report_validation` stores bounded HTTP evidence. `report_file` stores the two locally retrieved and checksum-verified PDFs. `report_text` and `report_qualitative` preserve 52 OCR page records. `report_fact` contains 251 conservative numeric-line candidates; all remain `needs_review` with `value_numeric` intentionally `NULL`. `coverage_gap` contains the open TRIFIC current-universe gap.

## Recommended queries

```sql
SELECT * FROM vw_report_catalog LIMIT 100;
SELECT * FROM vw_periodic_core_reports LIMIT 100;
SELECT * FROM vw_fact_panel WHERE quality_status='needs_review' LIMIT 100;
SELECT * FROM vw_data_quality_flags WHERE period_flag IS NOT NULL LIMIT 100;
```

The database is designed to be analysis-ready, not error-free. It preserves original text, source URLs, source tiers, HTTP evidence, local checksums, OCR method, page numbers, and review status so an analyst can promote facts only after checking the underlying report page and table context.
