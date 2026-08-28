# NSE Report Archive Relational Schema

## Scope and integrity principle

The database preserves the existing source-verifiable report index and adds structured tables for validation, local files, extracted content, qualitative disclosures, and quantitative facts. It does not manufacture financial values where the underlying report is not locally available or where the period, unit, currency, or source locator is ambiguous. Unavailable fields remain `NULL`, with a quality or extraction status explaining why.

## Core entities

| Table | Purpose | Primary key | Important relationships |
|---|---|---|---|
| `issuer` | Canonical issuer identity and current/historical coverage state | `issuer_id` | One issuer to many aliases, listings, reports, gaps |
| `issuer_alias` | Historical names, predecessor/successor names, and ticker aliases | `alias_id` | Many aliases to one issuer |
| `listing_event` | Listing, suspension, delisting, absorption, or unconfirmed historical status evidence | `listing_event_id` | Many events to one issuer; every event has source evidence and confidence |
| `report` | One indexed annual, semi-annual, quarterly, or related report record | `report_id` | Many reports to one issuer; one report to many sources, validations, facts |
| `report_source` | Source page, direct download URL, tier, title, and publication evidence | `source_id` | Many source rows to one report |
| `report_validation` | Bounded HTTP/content-type validation evidence | `validation_id` | Many validations to one report/source |
| `report_file` | Locally retrieved file, bytes, checksum, storage path, and retrieval evidence | `file_id` | Zero or many files to one report |
| `report_text` | Extracted text or section text from locally available reports | `text_id` | Many text sections to one report/file |
| `report_fact` | Structured quantitative or categorical fact extracted from report content | `fact_id` | Many facts to one report; every fact has a source locator and quality status |
| `report_qualitative` | Structured narrative disclosure, including topic, text, and source locator | `qualitative_id` | Many qualitative items to one report |
| `coverage_gap` | Current or historical issuer/report route not resolved in the archive | `gap_id` | Many gaps to one issuer |
| `source_artifact` | Preserved CSV, HTML, JSON, script, or other collection artifact | `artifact_id` | Supports reproducibility and source lineage |
| `extraction_run` | Pipeline execution, input/output counts, and quality-check results | `run_id` | Parent for imported records and validation summaries |

## Data-quality conventions

`source_tier` uses `issuer_first_party`, `issuer_controlled_api_or_cdn`, `nse_fallback`, `cma_fallback`, `secondary_discovery_only`, or `unknown`. `verification_status` distinguishes `sample_validated`, `downloaded_checksum_verified`, `issuer_link_pending`, `http_error`, `http_403`, `http_404`, and `not_tested`. `confidence` is `high`, `medium`, `low`, or `unresolved`, and is not a claim that the underlying issuer information is error-free.

Financial facts require `metric_name`, `value_numeric` where parseable, `value_text` as the original displayed value, `unit`, `currency`, `period_start`, `period_end`, `comparative_period_end`, `fact_type`, `source_page`, and `quality_status`. The original text is retained because normalization can otherwise hide signs, parentheses, scale labels, restatements, or presentation-specific definitions. Facts that cannot be safely normalized are stored with `value_numeric = NULL` and `quality_status = 'needs_review'`.

## Intended analytical views

`vw_report_catalog` joins issuer, report, best source, validation, and file status. `vw_current_issuer_coverage` joins the official 66-row current universe to indexed reports and explicit gaps. `vw_periodic_core_reports` limits the catalog to annual, half-year, and quarterly core reports. `vw_fact_panel` presents normalized quantitative facts with provenance. `vw_data_quality_flags` exposes unresolved periods, missing units/currencies, weak source tiers, failed links, duplicates, and unvalidated records.

## Attached market-data layer

The market-data extension preserves every attached CSV as a `market_dataset` and `market_import_file` record, including source archive, original relative path, checksum, release period, source URL, attribution, and rights status. Price rows are stored in `market_observation`; sector snapshots are stored in `market_sector_classification`; parsing issues are retained in `market_data_anomaly`. The importer does not silently deduplicate identical files from separate archives.

The main analysis views are `vw_market_price_panel`, `vw_market_sector_panel`, `vw_market_dataset_catalog`, and `vw_market_quality_flags`. The attached source records identify the imported releases as Mendeley Data datasets under CC BY 4.0; the release URLs and required attribution are documented in `docs/market_data_licensing.md`. The repository MIT license applies only to code and documentation.
