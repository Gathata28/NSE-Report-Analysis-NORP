# Filtered Public Report Downloads

NORP includes `scripts/download_reports.py`, a resumable command-line downloader for the public report catalog. It selects reports from the SQLite archive using any combination of sector, ticker, company, report year range, report frequency, document subtype, and result limit. It downloads only URLs already recorded in NORP; it does not bypass authentication, CAPTCHA, robots controls, paywalls, or HTTP 403 protections.

## Verified catalog coverage

The current database contains **1,761 reports** and **1,761 report sources**. A database audit found **1,688 URLs containing `.pdf`** and **73 non-PDF URLs**, so the latter require a landing-page resolution attempt or manual review. The audit also found 189 issuer identity rows and 75 distinct canonical tickers. Sector filtering therefore uses the report's `issuer_id` first and a conservative canonical-ticker fallback when the linked issuer row has no sector. Ampersand/`AND` sector spellings are normalized before filtering.

## Installation

From the repository root, install the documented dependencies:

```bash
python -m pip install -r requirements.txt
```

The downloader requires Python, `requests`, `beautifulsoup4`, and the NORP SQLite database. It reuses `norp_engine.fetch_with_retry()` with source-tier retry policies and per-host concurrency limits.

## Examples

Download every catalogued report:

```bash
python scripts/download_reports.py \
  --output-dir ./downloads/all-reports \
  --csv-manifest ./downloads/all-reports.csv \
  --zip ./downloads/all-reports.zip
```

Download all reports for a company or ticker:

```bash
python scripts/download_reports.py --output-dir ./downloads/scbk --ticker SCBK
python scripts/download_reports.py --output-dir ./downloads/kcb --company "KCB Group PLC"
```

Download a sector and year range together:

```bash
python scripts/download_reports.py \
  --output-dir ./downloads/banking-2020-2025 \
  --sector BANKING \
  --year-from 2020 \
  --year-to 2025
```

Combine multiple filters. Repeating `--ticker`, `--sector`, `--frequency`, or `--subtype` means “match any selected value” within that dimension; different dimensions are combined with “and”:

```bash
python scripts/download_reports.py \
  --output-dir ./downloads/selected \
  --sector BANKING \
  --ticker SCBK \
  --year-from 2020 \
  --year-to 2025 \
  --frequency "Annual / full-year" \
  --subtype "Annual report"
```

Preview the exact catalog selection without making network requests:

```bash
python scripts/download_reports.py \
  --output-dir ./downloads/preview \
  --sector "MANUFACTURING & ALLIED" \
  --year-from 2018 \
  --year-to 2024 \
  --dry-run
```

Use `--force` to replace an existing local PDF. Without `--force`, a non-empty file is treated as already downloaded and its SHA-256 is recomputed in the manifest.

## Output and verification

Files are stored under normalized sector and company directories. Each run writes a JSON Lines manifest by default at `<output-dir>/download_manifest.jsonl`; `--csv-manifest` adds a tabular copy. Each result records the report ID, issuer, ticker, sector, report year, source URL, resolved URL, status, HTTP status, local path, byte size, SHA-256 checksum, timestamp, and error text.

The main statuses are:

| Status | Meaning |
|---|---|
| `downloaded` | A valid PDF response was saved and checksummed. |
| `skipped_existing` | A local non-empty PDF already existed and was checksummed. |
| `landing_page_unresolved` | The catalog URL returned HTML but no matching public PDF link was found. |
| `blocked_or_not_pdf` | The response was blocked or returned a non-HTML/non-PDF response. |
| `not_pdf` | A resolved candidate URL did not return a valid PDF. |
| `request_failed` | The retry policy exhausted network attempts. |
| `invalid_url` | The catalog value was not an absolute HTTP(S) URL. |

A response beginning with `%PDF-` or carrying an `application/pdf` content type is accepted as a PDF. The downloader does not infer that an arbitrary HTML page is a PDF merely because its title says “annual report.”

## Responsible public operation

The database may contain issuer sites with anti-automation controls. A 403 response is recorded as a failure; the tool does not rotate identities, spoof browser fingerprints, disable TLS verification, or attempt to defeat a bot-management service. Users should respect the target site's terms, robots guidance, rate limits, and copyright or redistribution conditions. The archive's source links remain the authoritative access path when a file cannot be retrieved automatically.

For a public web interface, the recommended design is to let a user submit filters to a server-side job, show the selected count and an estimated download size, and return a generated ZIP only after the job completes. The server should impose per-user quotas, per-host pacing, maximum selection sizes, and a visible manifest. It should not download the entire archive on every page request.

## Current scope and limitations

The downloader is intentionally a local/public-repository CLI rather than an always-on service. It resolves ordinary HTML landing pages with static anchor links; JavaScript-only microsites, authentication-gated pages, and blocked hosts remain manifest-visible exceptions for manual review. A future hosted interface should use a background queue and object storage rather than keeping large ZIP files in Git history. GitHub Releases remains NORP's selected location for versioned database and archive snapshots.

## Extracting downloaded PDFs

Downloading a PDF only proves that a public file was retrieved and checksummed. It does not mean the report has been read or that its numbers have been verified. After a bundle is downloaded, run the text-layer-first extractor:

```bash
norp-extract-pdfs \
  --input-dir ./downloads/banking \
  --manifest ./downloads/banking/extraction_manifest.jsonl
```

The extractor recursively finds PDFs, tries `pdftotext` first, and uses `pdftoppm` plus Tesseract only when the direct text layer is empty or too short to be useful. This is faster and generally more accurate for modern born-digital reports. Use `--keep-pages` only when OCR page images are needed for review. Extracted text is evidence; it does not automatically create validated financial facts.

## Reviewing bundle completion

Generate a concise status report after download and extraction:

```bash
norp-bundle-report \
  --download-manifest ./downloads/banking/download_manifest.jsonl \
  --extraction-manifest ./downloads/banking/extraction_manifest.jsonl \
  --output ./downloads/banking/BUNDLE_STATUS.md \
  --title "BANKING bundle status"
```

The report separates catalog rows selected, files retrieved or already present, checksum-bearing files, blocked or unresolved rows, and extraction methods. Keep the status report next to the bundle so future users can distinguish **not attempted**, **not retrievable**, **retrieved**, and **text-extracted** records.

For large sectors, use `--dry-run` and then split the work by sector, ticker, or year range. A full selection can contain hundreds of issuer-hosted files and may take substantial time because NORP deliberately respects source-host pacing and records 403 or timeout outcomes instead of bypassing them.
