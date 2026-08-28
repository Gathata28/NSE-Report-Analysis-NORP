# Config-Driven Ingestion

New issuer-report ingestion should use `scripts/norp_import.py` and the shared helpers in `scripts/norp_engine.py`. This avoids creating another issuer-specific copy of the same load, classify, deduplicate, and write logic.

## Configuration

Copy `examples/issuer_import.example.json` and set the issuer, ticker, source page, source tier, input CSV, and output CSV. The input CSV should contain a `title` and `url` column, although `document_title` and `download_url` are also accepted.

## Usage

```bash
python scripts/norp_import.py --config examples/issuer_import.example.json --dry-run
python scripts/norp_import.py --config examples/issuer_import.example.json --log-level INFO
```

The importer uses `argparse`, standard `logging`, deterministic record IDs, conservative report-frequency classification, year inference only when a four-digit year appears in the title or URL, and deduplication by issuer and download URL. It does not claim that a source is downloadable merely because a URL is present. Existing per-issuer scripts are retained as historical collection records; the config-driven engine is the recommended path for new additions and future consolidation.

## Testable helper layer

`norp_engine.py` exposes `parse_date`, `parse_number`, `classify_frequency`, `infer_year`, `deduplicate_records`, `normalize_source_records`, `load_csv`, and `write_index`. These functions are covered by `tests/test_norp_engine.py` and can be imported by future collection tools.
