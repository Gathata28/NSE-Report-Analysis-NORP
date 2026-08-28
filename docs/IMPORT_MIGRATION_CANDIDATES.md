# Config-Driven Import Migration Candidates

## Scope

This migration set validates `scripts/norp_import.py` against real legacy source patterns before any broader collection-engine work. The candidates were selected from the existing `scripts/add_*` and `scripts/parse_*` inventory and represent different source and normalization behaviors rather than eight copies of the same clean CSV case.

| Candidate | Source pattern | Local/live input | Why selected |
|---|---|---|---|
| `parse_family_annual_links.py` | Issuer annual-report page with direct links | Saved issuer HTML | Tests ordinary issuer annual-link extraction and annual classification |
| `parse_kplc_links.py` | Issuer investor/report archive | Saved issuer HTML | Tests an older issuer page with inconsistent link text and filename conventions |
| `parse_ncba_quarterly.py` | Quarterly earnings page | Saved or fetched issuer page | Tests quarterly classification and publication-date normalization |
| `parse_limuru_nse_fallback_links.py` | NSE announcements fallback | Saved NSE HTML snapshot | Tests exchange fallback tier and issuer filtering |
| `parse_newgold_api_links.py` | JSON download API response | Saved JSON | Tests structured API records, ID-derived PDF URLs, and ETF/security coverage |
| `parse_bk_group_links.py` | Nested issuer pages and PDF/API links | Saved document-center and API snapshots | Tests multi-page discovery, deduplication, structured-source normalization, and source-page provenance |
| `parse_unga_links.py` | Multiple archive pages with download detail pages | Saved pages with live fallback | Tests pagination/archive-page aggregation and detail-page PDF resolution |
| `parse_nse_issuer_annual_links.py` | NSE annual archive | Saved NSE HTML snapshot | Tests central exchange annual archive and source-tier normalization |

## Migration acceptance criteria

Each candidate will be represented by a configuration and an input fixture or existing saved source. The importer must produce normalized records with issuer, ticker, source page, source tier, title, reporting period, report type, and download URL fields. Re-running the same configuration must be idempotent by download URL, and `--dry-run` must not modify the output index.

The migration does not claim that the legacy scripts are interchangeable. Candidates with live HTTP behavior or API-specific URL construction will first be adapted into deterministic input records, preserving the original source URL and source tier. Live retrieval and retry behavior are intentionally deferred to the later fetch-layer phase.

## Retirement policy

After the migrated configurations pass tests and their outputs are compared with the legacy outputs, the selected legacy scripts will be moved to `scripts/legacy/` with a README documenting their historical provenance. The current eight-script proof set includes `parse_bk_group_links.py`; `parse_transcentury_links.py` remains active and is tracked for a later migration batch. No legacy script will be deleted until its output comparison and repository tests pass.
