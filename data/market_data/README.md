# Integrated NSE Market Data

This directory contains the 32 CSV datasets imported from the user-supplied NSE market-data archive. Raw copies are stored in `raw/` under collision-safe SHA-256-prefixed names. `market_data_manifest.json` maps every stored copy to its original filename, source archive, source-relative path, release period, checksum, row count, source URL, attribution, and rights status.

The SQLite database stores price observations in `market_observation`, sector classifications in `market_sector_classification`, dataset provenance in `market_dataset`, file metadata in `market_import_file`, and parsing issues in `market_data_anomaly`. Use `vw_market_price_panel`, `vw_market_sector_panel`, `vw_market_dataset_catalog`, and `vw_market_quality_flags` for analysis.

Every source row is retained in the preserved raw CSV copies. SQLite stores compact normalized fields and retains `raw_row_json` for rows that require anomaly review. Missing values remain NULL; no prices, dates, tickers, or sectors are imputed. The importer supports the attached date formats, including `1/2/2007` and `2-Jan-13`, and flags only rows that remain ambiguous or structurally incomplete. Duplicate source packages remain separate datasets even when their checksums match.

The source records identify all 32 imported datasets as Mendeley Data releases under CC BY 4.0. See `docs/market_data_licensing.md` for the release-level URLs and attribution requirements. The repository’s MIT license applies to code and documentation only; it does not replace the data license.
