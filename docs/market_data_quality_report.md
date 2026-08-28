# Attached NSE Market-Data Integration Quality Report

**Input basis:** attached user-supplied archive, extracted for passive inspection; permitted source datasets only are included in the NORP integration.

## Imported scope

| Layer | Count |
| --- | ---: |
| Original CSV datasets preserved | 32 |
| Imported files | 32 |
| Price observations | 381400 |
| Sector rows | 577 |
| Review anomalies | 8 |
| Distinct tickers in observations | 111 |
| Duplicate checksum groups preserved | 5 |

## License and provenance

| Rights status | Datasets |
| --- | ---: |
| cc_by_4_0 | 32 |

The attached source records identify all 32 imported CSV datasets as Mendeley Data releases under CC BY 4.0 and provide release URLs and attribution for the 2007–2026 coverage. Duplicate files from separate source packages are preserved with distinct archive provenance and checksums.

## Anomaly interpretation

| Anomaly type | Rows |
| --- | ---: |
| missing_day_price | 4 |
| missing_ticker | 2 |
| invalid_or_unparsed_date | 2 |

Anomalies are review flags, not dropped records. The importer preserves every original row in the raw CSV copies and retains `raw_row_json` for anomaly rows; it does not impute missing prices, coerce unparsed dates into guesses, or remove apparent data-quality issues. Duplicate files from separate archives remain separate datasets with archive and relative-path provenance.

## Coverage

Observed date bounds are `2007-01-02` to `2026-06-30` across 4848 distinct parsed trading dates. The source files include 2007–2026 releases, with 2026 identified as January–June in the source naming and attribution notes. Exact row-level use should respect each dataset’s `release_period` and original filename.

## Privacy boundary

The NORP repository contains the permitted market-data extracts and source attribution metadata only. Only the permitted source datasets and attribution metadata are included in the public repository.
