# NSE Relational Database Quality Report

**Reference date:** 27 August 2026

## Scope

This SQLite database imports the complete 1,761-row normalized report index and its provenance fields. It adds structured issuer, report, source, validation, coverage-gap, local-file, raw-text, qualitative, and quantitative-fact tables. The database is analysis-ready but is not represented as error-free or as a complete extraction of every PDF: most URLs were not downloaded, and only two local scanned PDFs were OCR-processed.

## Counts

| Layer | Rows |
| --- | ---: |
| Issuers | 189 |
| Reports | 1761 |
| Report sources | 1761 |
| Validation records | 1761 |
| Verified local files | 2 |
| OCR/text pages | 52 |
| Raw qualitative page records | 52 |
| Candidate quantitative facts | 251 |
| Open coverage gaps | 1 |

## Validation and extraction interpretation

| Validation status | Rows |
| --- | ---: |
| Linked from official issuer page; direct HTTP validation pending | 1549 |
| sample_validated | 212 |

| Extraction method | Rows |
| --- | ---: |
| tesseract-ocr | 52 |

The 251 quantitative rows are conservative line-level candidates from OCR text. Their numeric field is intentionally `NULL`, their original OCR line is retained in `value_text`, and every row is marked `needs_review` / `unresolved`. They are not audited financial metrics and must not be used as validated numeric data without manual review against the PDF page and table context.

The 52 qualitative rows preserve page-level OCR text as `unclassified_ocr_text` with `needs_review` / `unresolved` status. This preserves narrative evidence without asserting an automated topic classification.

## Safe use

Use `vw_report_catalog` for report and source provenance, `vw_periodic_core_reports` for core periodic records, `vw_fact_panel` for review-flagged candidate facts, and `vw_data_quality_flags` for unresolved periods, weak sources, and validation issues. Always retain the original source URL and page locator when promoting a fact to a validated analysis field.

## Limitations

The current-NSE coverage audit represents 65 of 66 current rows; TRFC / TRIFIC Green USD I-REIT remains an explicit gap. The historical universe has 64 preliminary candidates, including secondary-only discovery leads; it is not an authoritative all-time delisting register. Source-link HTTP validation is a bounded representative sample rather than a full crawl. Absence from a current list is not treated as proof of delisting, suspension, absorption, or insolvency.
