# Contributing

Contributions are welcome when they improve source coverage, provenance, reproducibility, or data quality. Additions must include the issuer or ticker, report taxonomy and period as supported by the document, source page URL, direct download URL when available, source tier, and validation evidence. Do not infer report periods from upload dates or issuer status from absence from a current list.

## Workflow

Use a feature branch, preserve the original source artifact, add or update a reproducible parser or source CSV, run the canonical rebuild and downstream normalization/validation scripts, run the SQLite integrity tests, and document any unresolved ambiguity. For new report-link imports, prefer the config-driven workflow in `docs/config_driven_ingestion.md` and `scripts/norp_import.py` rather than creating another issuer-specific copy. Never overwrite a source PDF or replace a failed URL with an unverified search snippet.

Before rebuilding or running OCR, install the Python dependencies from `requirements.txt` and ensure `pdftotext`, `pdftoppm`, and `tesseract` are available on `PATH`. Missing binaries now produce explicit errors. Run `pytest -q` and `python scripts/test_nse_relational_db.py` before opening a pull request; the same checks run in GitHub Actions.

## Review standard

Reviewers should check exact titles, issuer identity, fiscal-period discipline, duplicate handling, source tier, HTTP evidence, checksums where files are downloaded, and whether any numeric or qualitative extraction is clearly marked as validated or review-required.
