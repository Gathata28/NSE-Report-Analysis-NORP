# NSE Report Analysis Project (NORP)

NORP is a source-verifiable archive and analysis foundation for annual, semi-annual, quarterly, and related public reports of current and historical Nairobi Securities Exchange issuers. The repository preserves report metadata, issuer identity, source pages, direct URLs, source tiers, bounded validation evidence, downloaded-file checksums, historical-universe notes, and a relational SQLite database.

## Repository status

The current corpus contains 1,761 indexed report records across 68 issuer identities. The current-universe audit represents 65 of 66 rows, with TRFC / TRIFIC Green USD I-REIT retained as an explicit unresolved gap. The preliminary historical universe contains 64 candidates and is not an authoritative all-time delisting register.

The SQLite database imports the full normalized report index and adds issuer, report, source, validation, local-file, raw-text, qualitative, quantitative-candidate, and coverage-gap tables. Only two locally retrieved scanned PDFs were OCR-processed; 52 page records and 251 review-flagged numeric-line candidates are included. Candidate facts retain original text and page provenance, while normalized numeric values remain NULL until manually verified.

The database also includes 32 attached NSE market-data datasets, 381,400 price observations, and 577 sector-classification rows covering source releases from 2007 through June 2026. Every original market-data row is retained with its source archive, original path, checksum, release period, raw JSON representation, and parsing/anomaly status. The source records identify these datasets as Mendeley Data releases under CC BY 4.0; see `docs/market_data_licensing.md` for required attribution. The repository MIT license applies to code and documentation only.

## Layout

| Directory | Contents |
| --- | --- |
| `docs/` | Project documentation, schema explanation, research notes, and limitations |
| `scripts/` | Portable Python collection, normalization, validation, workbook, OCR, database, and test scripts |
| `schema/` | SQLite DDL and relational schema definitions |
| `data/indexes/` | CSV, XLSX, SQLite, and structured analysis artifacts |
| `data/sources/` | Preserved HTML, JSON, text, and PDF source materials |
| `data/retrieved/` | Locally retrieved PDFs and OCR sidecars/directories |
| `data/market_data/` | Attached NSE price/sector datasets, raw copies, manifests, and market-data documentation |
| `data/original/` | Original archive ZIP snapshots |
| `examples/` | Example queries and sample analysis workflows |

## Dependencies

Python dependencies are listed in `requirements.txt`; project metadata and pytest configuration are also available in `pyproject.toml`. PDF extraction and OCR require these system binaries to be installed and available on `PATH`:

| Binary | Package/source | Used by |
| --- | --- | --- |
| `pdftotext` | Poppler utilities (`poppler-utils` on Debian/Ubuntu) | Database report-text extraction |
| `pdftoppm` | Poppler utilities (`poppler-utils` on Debian/Ubuntu) | PDF page rendering for OCR |
| `tesseract` | Tesseract OCR (`tesseract-ocr` on Debian/Ubuntu) | OCR text extraction |

The extraction scripts fail explicitly with an actionable error when a required binary is unavailable or a subprocess fails. This prevents a missing system dependency from silently producing incomplete output.

## Quick start

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pytest -q
python scripts/test_nse_relational_db.py
```

The database is already included at `data/indexes/nse_reports_archive.sqlite`. To rebuild it from the normalized CSV, run `python scripts/build_nse_relational_db.py` with `NORP_ROOT` set to the repository root if executing from another directory. Install the system dependencies listed above before rebuilding or running OCR.

Useful views include `vw_report_catalog`, `vw_periodic_core_reports`, `vw_fact_panel`, `vw_data_quality_flags`, `vw_market_price_panel`, `vw_market_sector_panel`, `vw_market_dataset_catalog`, and `vw_market_quality_flags`.

## Filtered public PDF downloads

Use `scripts/download_reports.py` to download all reports or any combination of sector, company, ticker, year range, report frequency, and document subtype filters. The command writes a resumable checksum manifest and can optionally create a ZIP archive. See [`docs/DOWNLOAD_REPORTS.md`](docs/DOWNLOAD_REPORTS.md) for examples, output statuses, landing-page behavior, and responsible handling of blocked hosts.

```bash
python scripts/download_reports.py \
  --output-dir ./downloads/banking-2020-2025 \
  --sector BANKING \
  --year-from 2020 \
  --year-to 2025 \
  --csv-manifest ./downloads/banking-2020-2025.csv
```

Use `--dry-run` first to inspect the exact selection without making network requests.

## Install the tools as a Python package

NORP also provides a pip-installable wheel and source distribution. Install the tools with `python -m pip install norp-nse-report-analysis` when a package release is available. The large SQLite archive is distributed separately through GitHub Releases, so installed users pass its path with `--database`. See [`docs/PACKAGING_AND_RELEASES.md`](docs/PACKAGING_AND_RELEASES.md) for beginner and maintainer instructions.

```bash
python -m pip install norp-nse-report-analysis
norp-download-reports --database ./nse_reports_archive_0.2.0.sqlite --output-dir ./downloads/kplc --ticker KPLC
```

Maintainers publish versioned assets by pushing a tag such as `v0.2.0`. The tagged workflow builds the wheel and source distribution, stages the database and index ZIP outside Git history, generates checksums and a release manifest, and publishes the GitHub Release. The manifest contract is defined in [`docs/release_manifest.schema.json`](docs/release_manifest.schema.json), and the release-note template is [`docs/release_notes_template.md`](docs/release_notes_template.md).

## Provenance and responsible use

Issuer pages, issuer-controlled APIs/CDNs, and exact NSE/CMA fallback documents are distinguished in `source_tier`. A bounded HTTP sample is not a full-corpus download verification. Secondary sources are retained only as discovery or status leads. No delisting, successor identity, or report period is inferred from absence alone. The attached market-data import preserves anomalies rather than imputing or silently dropping values. This is research infrastructure, not investment advice.

The public repository contains only the permitted NORP archive and market-data extracts. The permitted source materials only are included; unrelated private materials are excluded.

## Citation

Please cite the project using `CITATION.cff` and preserve the source URL and page locator when using any report or fact.
