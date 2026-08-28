# Contributing

Contributions are welcome when they improve source coverage, provenance, reproducibility, or data quality. Additions must include the issuer or ticker, report taxonomy and period as supported by the document, source page URL, direct download URL when available, source tier, and validation evidence. Do not infer report periods from upload dates or issuer status from absence from a current list.

## Workflow

Use a feature branch, preserve the original source artifact, add or update a reproducible parser or source CSV, run the canonical rebuild and downstream normalization/validation scripts, run the SQLite integrity tests, and document any unresolved ambiguity. Never overwrite a source PDF or replace a failed URL with an unverified search snippet.

## Review standard

Reviewers should check exact titles, issuer identity, fiscal-period discipline, duplicate handling, source tier, HTTP evidence, checksums where files are downloaded, and whether any numeric or qualitative extraction is clearly marked as validated or review-required.
